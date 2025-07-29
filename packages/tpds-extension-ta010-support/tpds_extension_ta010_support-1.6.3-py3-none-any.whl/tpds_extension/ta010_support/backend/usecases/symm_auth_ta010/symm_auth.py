# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

import os
import cryptoauthlib as cal
from ..secure_element import TA010_ECC204
from ...api.model import UsecaseResponseModel
from ..proto_provision.symm_auth import SymmAuth
from ..proto_provision.helper.defines import KeySize
from ..proto_provision.helper.keys import save_symmetric_key
from ..proto_provision.helper.helper import check_board_status, generate_diversified_key
from tpds.settings import TrustPlatformSettings
from tpds.helper import UsecaseLogger
from tpds.tp_utils.tp_utils import pretty_print_hex


class TA010SymmAuth(TA010_ECC204):
    def __init__(self, usecase_dir: str = None) -> None:
        self.usecase_dir = usecase_dir if usecase_dir else \
            os.path.join(TrustPlatformSettings().get_base_folder(), "symm_auth_ta010")
        os.makedirs(self.usecase_dir, exist_ok=True)
        self.logger = UsecaseLogger(self.usecase_dir)
        self.master_key_slot = 0x05
        self.enc_slot = 0x06
        self.accessory_key_slot = 0x03
        self.master_key_name = "master_symm_key"
        self.master_key_bytes = None
        self.diversified_key = None
        self.interface = None

    def generate_resources(self, user_inputs: dict) -> UsecaseResponseModel:
        response = UsecaseResponseModel()
        current_dir = os.getcwd()
        os.chdir(self.usecase_dir)
        try:
            self.logger.log("Generating/Loading Symmetric Keys")
            self.interface = user_inputs.get("interface")
            assert self.interface, "Interface is required for Symmetric Authentication"
            self.logger.log(f"Selected {self.interface} Interface")
            assert len(user_inputs.get("keys")), "Keys are required for Symmetric Authentication"

            self.master_key = SymmAuth()
            if key := user_inputs.get("keys").get(self.master_key_name).get("value"):
                key = bytes.fromhex(key)
            self.master_key.generate_symmetric_key(key, KeySize.AES256)
            self.master_key_bytes = self.master_key.symm_bytes
            self.logger.log(f"Master Symmetric Key: \n{pretty_print_hex(self.master_key_bytes, 8)}")
            save_symmetric_key(self.master_key_bytes, self.master_key_name, ["PEM", "BIN"])
            self.logger.log(f"Master Symmetric key saved in {self.master_key_name}.h")

            self.enc_key = SymmAuth()
            self.enc_key.generate_symmetric_key(
                key=None,
                key_size=KeySize.AES256,
            )
            self.enc_key = self.enc_key.symm_bytes
            self.fw_resources()

            response.status = True
            response.message = "Resource generation is successful"
        except Exception as e:
            response.message = f"Resource generation has failed with: {e}"
        finally:
            os.chdir(current_dir)
            self.logger.log(response.message)
            response.log = self.logger.get_log()
        return response

    def proto_provision(self, user_inputs: dict) -> UsecaseResponseModel:
        """
        Provisions the prototyping Secure Element by loading the IO key and symmetric key.

        This method changes the current working directory to the use case directory,
        checks the board status, connects to the Secure Element, and loads secret keys
        into specified slots. It logs the process and returns a response indicating
        success or failure.

        Args:
            user_inputs (dict): A dictionary containing user inputs, including the selected board.

        Returns:
            UsecaseResponseModel: An object containing the status, message, and log of the provisioning process.

        Raises:
            Exception: If any error occurs during the provisioning process, it is caught and logged in the response message.
        """
        response = UsecaseResponseModel()
        current_dir = os.getcwd()
        os.chdir(self.usecase_dir)
        try:
            check_board_status(user_inputs.get("selectedBoard", None), self.logger)
            self.logger.log("Connecting to Secure Element...")
            super().__init__(address="0x6C")
            self.logger.log("Connected to ATECC608")
            self.load_secret_key(self.enc_slot, self.enc_key)
            self.logger.log(f"Success loading IO Key into ATECC608's slot: {self.enc_slot: 02X}")
            self.load_secret_key(
                self.master_key_slot, self.master_key_bytes, self.enc_slot, self.enc_key
            )
            self.logger.log(
                f"Success loading Secret Key into ATECC608's slot: {self.master_key_slot: 02X}"
            )

            self.logger.log("Connecting to Secure Element...")
            super().__init__(
                interface=user_inputs.get("interface"),
                address="0x72",
                devtype=cal.get_device_type_id("TA010"),
            )
            self.logger.log("Connected to TA010")
            self.logger.log(f"Generating diversified key and loading to TA010's Slot{self.accessory_key_slot: 02X}...")
            self.accessory_sernum = self.get_device_serial_number()
            self.logger.log(f"Accessory Serial Number: {self.accessory_sernum.hex()}")
            self.diversified_key = generate_diversified_key(self.accessory_sernum, self.master_key_bytes)
            self.load_secret_key(self.accessory_key_slot, self.diversified_key)
            self.logger.log("Success loading Diversified key")
            response.status = True
            response.message = "Proto Provision Success"
        except Exception as e:
            response.message = f"Proto Provision failed with: {e}"
        finally:
            os.chdir(current_dir)
            self.logger.log(response.message)
            response.log = self.logger.get_log()
        return response

    def fw_resources(self):
        """
        Generates a C header file with interface selection
        """
        with open('project_config.h', 'w') as f:
            f.write('#ifndef _PROJECT_CONFIG_H\n')
            f.write('#define _PROJECT_CONFIG_H\n\n')
            f.write('#ifdef __cplusplus\n')
            f.write('extern "C" {\n')
            f.write('#endif\n\n')
            f.write(
                f"#define SELECTED_TA010_SWI {1 if self.interface == 'SWI' else 0} \n\n")
            f.write('#ifdef __cplusplus\n')
            f.write('}\n')
            f.write('#endif\n')
            f.write('#endif\n')

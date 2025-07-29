# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.
import os
import cryptoauthlib as cal
from ..secure_element import TA010_ECC204
from ...api.model import UsecaseResponseModel
from ..proto_provision.helper.helper import check_board_status
from ..proto_provision.helper.keys import generate_key_pair, get_public_key, get_public_pem, get_private_pem, get_public_key_from_numbers
from ..proto_provision.certs.certs import (
    save_cert_pem, is_certificate_chain_valid
)
from ..proto_provision.helper.defines import KeyAlgorithms
from ..proto_provision.wpc_auth import WPCAuth
from tpds.settings import TrustPlatformSettings
from tpds.helper import UsecaseLogger
from tpds.certs.cert_utils import get_cert_print_bytes


class TA010WPCAuth(TA010_ECC204):
    def __init__(self, usecase_dir: str = None) -> None:
        self.usecase_dir = usecase_dir if usecase_dir else \
            os.path.join(TrustPlatformSettings().get_base_folder(), "wpc_auth_ta010")
        os.makedirs(self.usecase_dir, exist_ok=True)
        self.logger = UsecaseLogger(self.usecase_dir)
        self.pu_ser_num = bytes.fromhex("0123000000000000EE")
        self.ptmc_code, self.qi_id, self.ca_seqid = None, None, None
        self.root_key, self.mfg_key, self.wpc = None, None, None
        self.pu_pubkey = None
        self.wpc_root_crt_file = "wpc_root_cert.crt"
        self.wpc_root_key_file = "wpc_root_key.pem"
        self.wpc_mfg_crt_file = f"wpc_mfg_{self.ptmc_code}-{self.ca_seqid}.crt"
        self.wpc_mfg_key_file = f"wpc_mfg_{self.ptmc_code}-{self.ca_seqid}_key.pem"
        self.wpc_puc_crt_file = f"wpc_puc_ta010_{self.pu_ser_num.hex().upper()}.crt"
        self.wpc_puc_key_file = f"wpc_puc_ta010_{self.pu_ser_num.hex().upper()}.pem"

    def generate_resources(self, user_inputs: dict) -> UsecaseResponseModel:
        response = UsecaseResponseModel()
        current_dir = os.getcwd()
        os.chdir(self.usecase_dir)
        try:
            self.logger.log("Generating Resources....")
            self.parese_user_inputs(user_inputs)
            self.wpc = WPCAuth(ptmc_code=self.ptmc_code, qi_id=self.qi_id, ca_seqid=self.ca_seqid)
            self.logger.log("Generating WPC Root Certificate")
            self.wpc.generate_wpc_root_cert(self.root_key)
            self.logger.log(f"WPC Root Certificate: \n{get_cert_print_bytes(self.wpc.root_cert_pem)}")
            get_private_pem(self.wpc.root_key, self.wpc_root_key_file)
            self.logger.log(f"WPC Root Private key saved in {self.wpc_root_key_file}")

            self.logger.log("Generating WPC Manufacturer Certificate")
            self.wpc.generate_mfg_cert(self.mfg_key)
            self.logger.log(f"WPC Manufacturer Certificate: \n{get_cert_print_bytes(self.wpc.mfg_cert_pem)}")
            get_private_pem(self.wpc.mfg_key, self.wpc_mfg_key_file)
            self.logger.log(f"WPC Manufacturer Private key saved in {self.wpc_mfg_key_file}")

            self.logger.log("Generating Product Unit Certificate with a dummy Public Key")
            self.pu_pubkey = get_public_key(generate_key_pair(KeyAlgorithms.ECC_P256))
            self.wpc.generate_puc_cert(pu_pubkey=get_public_pem(self.pu_pubkey).encode('utf-8'))
            self.logger.log(f"Dummy WPC Product Unit Certificate: \n{get_cert_print_bytes(self.wpc.mfg_cert_pem)}")

            assert is_certificate_chain_valid(
                self.wpc.root_cert, self.wpc.mfg_cert, self.wpc.puc_cert
            ), "Invalid WPC Ceritificate chain"
            self.wpc.calculate_wpc_digests()
            self.wpc.fw_resources("ta010")
            save_cert_pem(self.wpc.root_cert, self.wpc_root_crt_file)
            self.logger.log(f"Root Certificate Saved in {self.wpc_root_crt_file}")
            save_cert_pem(self.wpc.mfg_cert, self.wpc_mfg_crt_file)
            self.logger.log(f"Manufacturer Certificate Saved in {self.wpc_mfg_crt_file}")
            save_cert_pem(self.wpc.puc_cert, self.wpc_puc_crt_file)
            self.logger.log(f"Product Unit Certificate Saved in {self.wpc_puc_crt_file}")
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
            super().__init__(
                address="0x70",
                devtype=cal.get_device_type_id("TA010"),
            )
            self.logger.log("Connected to TA010-TFLXAUTH")
            self.pu_ser_num = self.get_device_serial_number()
            self.logger.log("Reading Public Key from device")
            self.pu_pubkey = get_public_key_from_numbers(KeyAlgorithms.ECC_P256, self.get_pubkey(0))
            self.pu_pubkey = get_public_pem(
                self.pu_pubkey, self.wpc_puc_key_file).encode("utf-8")
            self.logger.log(f"Device Public Key : \n {self.pu_pubkey.decode('utf-8')}")
            self.logger.log("Generating Product Unit Certificate")
            self.wpc.generate_puc_cert(self.pu_pubkey)
            self.logger.log(f"WPC Product Unit Certificate: \n{get_cert_print_bytes(self.wpc.mfg_cert_pem)}")

            assert is_certificate_chain_valid(
                self.wpc.root_cert, self.wpc.mfg_cert, self.wpc_puc_crt_file
            ), "Invalid WPC Ceritificate chain"

            self.wpc.calculate_wpc_digests()
            self.logger.log("Loading Certifcates into Device Slots...")
            self.provision_wpc_slots(self.wpc.root_cert, self.wpc.mfg_cert, self.wpc.puc_cert, self.wpc.chain_digest)
            self.wpc.fw_resources("ta010")
            response.status = True
            response.message = "Proto Provision Success"
        except Exception as e:
            response.message = f"Proto Provision failed with: {e}"
        finally:
            os.chdir(current_dir)
            self.logger.log(response.message)
            response.log = self.logger.get_log()
        return response

    def parese_user_inputs(self, user_inputs: dict):
        ptmc_code = user_inputs.get("ptmc_code")
        self.ptmc_code = int(ptmc_code if ptmc_code else "004E", 16)
        self.logger.log(f"PTMC Code: {hex(self.ptmc_code)}")
        qi_id = user_inputs.get("qi_id")
        self.qi_id = int(qi_id if qi_id else "11430")
        self.logger.log(f"Qi ID: {self.qi_id}")
        ca_seqid = user_inputs.get("ca_seqid")
        self.ca_seqid = int(ca_seqid if ca_seqid else "01", 16)
        self.logger.log(f"CA Sequence ID: {hex(self.ca_seqid)}")
        self.root_key = user_inputs.get("keys").get("root_key").get("value")
        self.mfg_key = user_inputs.get("keys").get("mfg_key").get("value")
        self.wpc_mfg_crt_file = f"wpc_mfg_{self.ptmc_code:04X}-{self.ca_seqid:02X}.crt"
        self.wpc_mfg_key_file = f"wpc_mfg_{self.ptmc_code:04X}-{self.ca_seqid:02X}_key.pem"
        self.wpc_puc_crt_file = f"wpc_puc_ta010_{self.pu_ser_num.hex().upper()}.crt"
        self.wpc_puc_key_file = f"wpc_puc_ta010_{self.pu_ser_num.hex().upper()}.pem"

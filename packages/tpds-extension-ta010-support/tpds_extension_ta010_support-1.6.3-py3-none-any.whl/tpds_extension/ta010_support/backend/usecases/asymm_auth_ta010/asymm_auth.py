# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

import os
import cryptoauthlib as cal
from ..secure_element import TA010_ECC204
from ...api.model import UsecaseResponseModel
from ..proto_provision.certs.certs import (
    save_cert_pem, is_certificate_chain_valid, save_tflx_c_definations, get_tflex_py_definitions
)
from ..proto_provision.helper.helper import check_board_status
from ..proto_provision.helper.keys import (
    generate_key_pair,
    get_public_key,
    get_public_pem,
    get_private_pem,
    get_public_key_from_numbers,
    get_private_key_from_file_bytes,
)
from ..proto_provision.asymm_auth.asymm_auth import AsymmAuth
from tpds.settings import TrustPlatformSettings
from tpds.helper import UsecaseLogger
from tpds.certs.cert_utils import get_cert_print_bytes


class TA010AsymmAuth(TA010_ECC204):
    def __init__(self, usecase_dir: str = None) -> None:
        self.usecase_dir = usecase_dir if usecase_dir else \
            os.path.join(TrustPlatformSettings().get_base_folder(), "asymm_auth_ta010")
        os.makedirs(self.usecase_dir, exist_ok=True)
        self.device_name = "ECC204"
        self.logger = UsecaseLogger(self.usecase_dir)
        self.interface, self.org_name, self.certsOption = None, None, None
        self.root_key, self.signer_key, self.device_key = None, None, None
        self.root_validity, self.signer_validity, self.device_validity = 28, 28, 28
        self.root_cert, self.signer_cert, self.device_cert = None, None, None

    def generate_resources(self, user_inputs: dict) -> UsecaseResponseModel:
        """
        Generates Asymmetric Authentication resources based on user inputs.

        Args:
            user_inputs (dict): A dictionary containing user inputs required for generating Secureboot resources.

        Returns:
            UsecaseResponseModel: A response model containing the status and message of the resource generation process

        Raises:
            AssertionError: If required user inputs are missing or invalid.
            Exception: If any other error occurs during the resource generation process.
                these are caught and logged in the response message.
        """
        response = UsecaseResponseModel()
        current_dir = os.getcwd()
        os.chdir(self.usecase_dir)
        try:
            self.logger.log("Generating/Loading Resources Keys")
            self.parse_user_inputs(user_inputs)
            self.fw_resources()
            self.asymm_auth = AsymmAuth(signer_cn="Microchip SignerFFFF", device_cn="sn0123000000000000EE")
            if self.certsOption == "Generate":
                self.asymm_auth.org_name = self.org_name
                self.logger.log("Generating Root Certificate....")
                self.asymm_auth.generate_root_cert(root_key=self.root_key, validity=self.root_validity)
                self.logger.log(f"Root Certificate: \n{get_cert_print_bytes(self.asymm_auth.root_cert_pem)}")
                get_private_pem(self.asymm_auth.root_key, file := "Root_key.pem")
                get_public_pem(get_public_key(self.asymm_auth.root_key), file := "Root_Public_key.pem")
                self.logger.log(f"Root Private key saved in {file}")
                self.logger.log("Generating Signer Certificate....")
                self.asymm_auth.generate_signer_cert(
                    signer_key=self.signer_key,
                    validity=self.signer_validity,
                    is_pub_hash_sn=True,
                )
                self.logger.log(f"Signer Certificate: \n{get_cert_print_bytes(self.asymm_auth.signer_cert_pem)}")
                get_private_pem(self.asymm_auth.signer_key, file := "Signer_key.pem")
                get_public_pem(get_public_key(self.asymm_auth.signer_key), file := "Signer_Public_key.pem")
                self.logger.log(f"Signer Private key saved in {file}")
            else:
                self.logger.log("Parsing Root Certificate...")
                self.asymm_auth.set_root_cert(self.root_cert)
                self.logger.log(f"Root Certificate: \n{get_cert_print_bytes(self.asymm_auth.root_cert_pem)}")
                self.logger.log("Parsing Signer Certificate..")
                self.asymm_auth.set_signer_cert(self.signer_cert)
                self.asymm_auth.is_signer_tflx_cert()
                self.logger.log(f"Signer Certificate: \n{get_cert_print_bytes(self.asymm_auth.signer_cert_pem)}")
                self.asymm_auth.signer_key = self.signer_key
            self.logger.log("Generating Device Certificate with a Dummy Public Key")
            device_key = get_public_key(generate_key_pair("ECC_P256"))
            self.asymm_auth.generate_device_cert(
                device_key=get_public_pem(device_key).encode("utf-8"),
                validity=self.device_validity,
                is_pub_hash_sn=True,
            )
            self.logger.log(f"Dummy Device Certificate: \n{get_cert_print_bytes(self.asymm_auth.device_cert_pem)}")

            assert is_certificate_chain_valid(
                self.asymm_auth.root_cert, self.asymm_auth.signer_cert, self.asymm_auth.device_cert
            ), "Invalid Ceritificate chain"
            save_tflx_c_definations(
                self.asymm_auth.root_cert,
                self.asymm_auth.signer_cert,
                self.asymm_auth.device_cert, "ECC204")
            save_cert_pem(self.asymm_auth.root_cert, file := "Root_cert.pem")
            self.logger.log(f"Root Certificate Saved in {file}")
            save_cert_pem(self.asymm_auth.signer_cert, file := "Signer_cert.pem")
            self.logger.log(f"Signer Certificate Saved in {file}")
            save_cert_pem(self.asymm_auth.device_cert, file := "Device_cert_Dummy.pem")
            self.logger.log(f"Dummy Device Certificate Saved in {file}")
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
                interface=self.interface,
                address="0x72",
                devtype=cal.get_device_type_id("TA010"),
            )
            self.logger.log("Connected to TA010!")

            serial_number = self.get_device_serial_number()
            self.asymm_auth.device_cn = f"sn{serial_number.hex().upper()}"
            device_pubkey = get_public_key_from_numbers("ECC_P256", self.get_pubkey(0))
            device_pubkey = get_public_pem(
                device_pubkey, f"device_pub_key_{serial_number.hex().upper()}.pem").encode("utf-8")
            self.logger.log(f"Device Public Key : \n {device_pubkey.decode('utf-8')}")
            self.logger.log("Generating Device Certificate")
            self.asymm_auth.generate_device_cert(
                device_key=device_pubkey,
                validity=self.device_validity,
                is_pub_hash_sn=True,
            )
            self.logger.log(f"Device Certificate: \n{get_cert_print_bytes(self.asymm_auth.device_cert_pem)}")

            assert is_certificate_chain_valid(
                self.asymm_auth.root_cert, self.asymm_auth.signer_cert, self.asymm_auth.device_cert
            ), "Invalid Ceritificate chain"
            save_cert_pem(self.asymm_auth.device_cert, file := f"Device_cert_{serial_number.hex().upper()}.pem")
            self.logger.log(f"Device Certificate Saved in {file}")
            save_tflx_c_definations(
                self.asymm_auth.root_cert,
                self.asymm_auth.signer_cert,
                self.asymm_auth.device_cert, self.device_name)
            py_defs = get_tflex_py_definitions(
                self.asymm_auth.root_cert, self.asymm_auth.signer_cert,
                self.asymm_auth.device_cert, self.device_name)
            self.logger.log("Loading Signer Certificate into Device....")
            self.write_cert(py_defs.get("signer"), self.asymm_auth.signer_cert_bytes)
            self.logger.log("Loading Device Certificate into Device....")
            self.write_cert(py_defs.get("device"), self.asymm_auth.device_cert_bytes)

            response.status = True
            response.message = "Proto Provision Success"
        except Exception as e:
            response.message = f"Proto Provision failed with: {e}"
        finally:
            os.chdir(current_dir)
            self.logger.log(response.message)
            response.log = self.logger.get_log()
        return response

    def parse_user_inputs(self, user_inputs: dict):
        """
        Parses user inputs from the UI and assigns them to self.
        """
        self.interface = user_inputs.get("interface")
        assert self.interface, "Interface is required for Asymmetric Authentication"

        self.certsOption = user_inputs.get("certsOption")
        certs = user_inputs.get("certs")
        if self.certsOption == "Generate":
            self.org_name = certs.get("Org")
            self.root_validity = certs.get("Root")
            self.signer_validity = certs.get("Signer")
            self.device_validity = certs.get("Device")
            self.root_key = user_inputs.get("keys").get("root_key").get("value")
            self.signer_key = user_inputs.get("keys").get("signer_key").get("value")
        else:
            self.root_cert = bytes.fromhex(certs.get("Root").get("value"))
            self.signer_cert = bytes.fromhex(certs.get("Signer").get("value"))
            # get Signer Priv Key from user to generate Device Cert
            self.signer_key = get_private_key_from_file_bytes(bytes.fromhex(certs.get("Device").get("value")))

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

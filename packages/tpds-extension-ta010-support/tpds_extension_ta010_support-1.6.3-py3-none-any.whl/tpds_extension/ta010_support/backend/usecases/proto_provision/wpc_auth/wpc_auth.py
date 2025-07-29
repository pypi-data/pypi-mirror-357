# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.
import os
import asn1crypto
import struct
from .wpc_certs import create_wpc_root_cert, create_wpc_mfg_cert, create_wpc_puc_cert
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from ..certs.certs import get_certificate_der, get_certificate_pem
from ..helper.keys import generate_private_key, get_public_key, get_public_key_from_pem
from ..helper.defines import KeyAlgorithms
from ..helper.utils import get_c_array
from ..certs.x509_find_elements import (
    public_key_location,
    signature_location,
    tbs_location,
)


class WPCAuth:
    """
    WPCAuth class for WPC authentication and WPC certificates generation.

    This class provides methods to generate root, Manufacturer, and product unit certificates,
    as well as to load assets into a device instance.

    Methods:
        generate_mfg_cert(mfg_key: str = "") -> None:
            Generates a manufacturer certificate using the specified manufacturer key.

        generate_puc_cert(pu_pubkey: bytes, rsid: int = int.from_bytes(os.urandom(4), byteorder="big")) -> None:
            Generates a product unit certificate using the specified public key and random serial ID.

        calculate_wpc_digests() -> None:
            Calculates the SHA-256 digests for the root certificate and the certificate chain.

        fw_resources(device: str = "ecc204") -> None:
            Generates a firmware resources header file for the specified device.

        load_asset(asset: str, asset_handler: str) -> None:
            Loads an asset using the specified asset handler in the device instance.
    """
    def __init__(self, **kwargs) -> None:
        self.dev_inst = kwargs.get("dev_inst", None)
        self.key_algo = kwargs.get("key_algo", KeyAlgorithms.ECC_P256)
        self.ptmc_code = kwargs.get("ptmc_code", 0x004E)
        self.qi_id = kwargs.get("qi_id", 11430)
        self.ca_seqid = kwargs.get("ca_seqid", 0x01)
        self.root_key, self.root_cert = None, None
        self.mfg_key, self.mfg_pub_key, self.mfg_cert = None, None, None
        self.puc_cert, self.pu_pubkey = None, None
        self.root_digest, self.chain_digest = None, None
        self.root_cert_bytes, self.mfg_cert_bytes, self.puc_cert_bytes = None, None, None

    def generate_wpc_root_cert(
        self,
        root_key: str = "",
        root_cn: str = "WPCCA1",
        root_sn: int = 0x776112B411479AAC,
    ) -> None:
        """
        Generate a WPC root certificate.

        Args:
            root_key (str, optional): The root key to be used for generating the private key.
                                    Defaults to an empty string, which indicates that a new key will be generated.
            root_cn (str, optional): The common name for the root certificate. Defaults to "WPCCA1".
            root_sn (int, optional): The serial number for the root certificate. Defaults to 0x776112B411479AAC.

        Returns:
            None
        """
        self.root_key = generate_private_key(root_key, self.key_algo)
        self.root_cert = create_wpc_root_cert(self.root_key, root_cn, root_sn)
        self.root_cert_pem = get_certificate_pem(self.root_cert)
        self.root_cert_bytes = get_certificate_der(self.root_cert)

    def generate_mfg_cert(self, mfg_key: str = "") -> None:
        """
        Generate a manufacturer (MFG) certificate.

        Args:
            mfg_key (str, optional): The manufacturer key to be used for generating the private key.
                                    Defaults to an empty string, which indicates that a new key will be generated.

        Raises:
            AssertionError: If the root key and certificate have not been established prior to calling this method.

        Returns:
            None
        """
        assert self.root_key and self.root_cert, "Root Key and Certificate should be established first"
        self.mfg_key = generate_private_key(mfg_key, self.key_algo)
        self.mfg_pub_key = get_public_key(self.mfg_key)
        self.mfg_cert = create_wpc_mfg_cert(
            self.ptmc_code,
            self.ca_seqid,
            self.qi_id,
            self.mfg_pub_key,
            self.root_key,
            self.root_cert,
        )
        self.mfg_cert_pem = get_certificate_pem(self.mfg_cert)
        self.mfg_cert_bytes = get_certificate_der(self.mfg_cert)

    def generate_puc_cert(self, pu_pubkey: bytes, rsid: int = int.from_bytes(os.urandom(4), byteorder="big")) -> None:
        """
        Generate a Product unit (PUC) certificate.

        Args:
            pu_pubkey (bytes): The device public key, provided as a byte sequence in PEM format.
            rsid (int, optional): A random serial ID for the certificate.
                                Defaults to a randomly generated 4-byte integer.

        Raises:
            AssertionError: If the manufacturer key and certificate have not been established prior
                            to calling this method.

        Returns:
            None
        """
        assert self.mfg_key and self.mfg_cert, "Manufacturer Key and Certificate should be established first"
        self.pu_pubkey = get_public_key_from_pem(pu_pubkey)
        self.puc_cert = create_wpc_puc_cert(
            self.qi_id,
            rsid,
            self.pu_pubkey,
            self.mfg_key,
            self.mfg_cert,
        )
        self.puc_cert_pem = get_certificate_pem(self.puc_cert)
        self.puc_cert_bytes = get_certificate_der(self.puc_cert)

    def calculate_wpc_digests(self):
        """
        Calculates WPC Chain digest based on root, mfg and puc bytes
        """
        root_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        root_hash.update(self.root_cert_bytes)
        self.root_digest = root_hash.finalize()[:32]

        length = 2 + len(self.root_digest) + len(self.mfg_cert_bytes) + len(self.puc_cert_bytes)
        cert_chain = b""
        cert_chain += struct.pack(">H", length)
        cert_chain += self.root_digest + self.mfg_cert_bytes + self.puc_cert_bytes
        chain_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        chain_hash.update(cert_chain)
        self.chain_digest = chain_hash.finalize()[:32]

    def fw_resources(self, device: str = "ecc204"):
        """
        Generate firmware resources header file for a specified device.

        Args:
            device (str, optional): The device name for which the header file is generated. Defaults to "ecc204".

        Returns:
            None
        """
        with open(os.path.join(f"{device}_tflxwpc.h"), "w") as f:
            f.write(f"#ifndef _{device.upper()}_TFLXWPC_DATA_H\n")
            f.write(f"#define _{device.upper()}TFLXWPC_DATA_H\n\n")
            f.write("#ifdef __cplusplus\n")
            f.write('extern "C" {\n')
            f.write("#endif\n\n")

            asn1_cert = asn1crypto.x509.Certificate().load(self.root_cert_bytes, strict=True)
            pk_offset, pk_count = public_key_location(asn1_cert)
            sig_offset, sig_count = signature_location(asn1_cert)
            tbs_offset, tbs_count = tbs_location(asn1_cert)
            f.write(f"#define ROOT_PUBLIC_KEY_OFFSET        {pk_offset}\n")
            f.write(f"#define ROOT_PUBLIC_KEY_SIZE          {pk_count}\n")
            f.write(f"#define ROOT_SIGNATURE_OFFSET         {sig_offset}\n")
            f.write(f"#define ROOT_SIGNATURE_SIZE           {sig_count}\n")
            f.write(f"#define ROOT_TBS_OFFSET               {tbs_offset}\n")
            f.write(f"#define ROOT_TBS_SIZE                 {tbs_count}\n")
            f.write("\n\n")

            asn1_cert = asn1crypto.x509.Certificate().load(self.mfg_cert_bytes, strict=True)
            pk_offset, pk_count = public_key_location(asn1_cert)
            sig_offset, sig_count = signature_location(asn1_cert)
            tbs_offset, tbs_count = tbs_location(asn1_cert)
            f.write(f"#define MFG_PUBLIC_KEY_OFFSET         {pk_offset}\n")
            f.write(f"#define MFG_PUBLIC_KEY_SIZE           {pk_count}\n")
            f.write(f"#define MFG_SIGNATURE_OFFSET          {sig_offset}\n")
            f.write(f"#define MFG_SIGNATURE_SIZE            {sig_count}\n")
            f.write(f"#define MFG_TBS_OFFSET                {tbs_offset}\n")
            f.write(f"#define MFG_TBS_SIZE                  {tbs_count}\n")
            f.write("\n\n")

            asn1_cert = asn1crypto.x509.Certificate().load(self.puc_cert_bytes, strict=True)
            pk_offset, pk_count = public_key_location(asn1_cert)
            sig_offset, sig_count = signature_location(asn1_cert)
            tbs_offset, tbs_count = tbs_location(asn1_cert)
            f.write(f"#define PUC_PUBLIC_KEY_OFFSET         {pk_offset}\n")
            f.write(f"#define PUC_PUBLIC_KEY_SIZE           {pk_count}\n")
            f.write(f"#define PUC_SIGNATURE_OFFSET          {sig_offset}\n")
            f.write(f"#define PUC_SIGNATURE_SIZE            {sig_count}\n")
            f.write(f"#define PUC_TBS_OFFSET                {tbs_offset}\n")
            f.write(f"#define PUC_TBS_SIZE                  {tbs_count}\n")
            f.write("\n\n")

            # Root Cert
            f.write(get_c_array("root_cert", self.root_cert_bytes))
            # mfg cert
            f.write(get_c_array("mfg_cert", self.mfg_cert_bytes))
            # Root digest
            f.write(get_c_array("root_digest", self.root_digest))

            f.write("#ifdef __cplusplus\n")
            f.write("}\n")
            f.write("#endif\n")
            f.write("#endif\n")

    def load_asset(self, asset: str, asset_handler: str) -> None:
        """
        Loads an asset using the specified asset handler.

        This method verifies that the asset and asset handler are valid attributes
        and that the asset has been loaded or generated. It then uses the device
        instance to load the asset via the asset handler.

        Args:
            asset (str): The name of the asset to be loaded.
            asset_handler (str): The name of the handler method in the device instance
                                 that will be used to load the asset.

        Raises:
            AssertionError: If the asset is not an attribute of the class, if the asset
                            has not been loaded or generated, if the device instance is
                            not set, if the asset handler is not an attribute of the
                            device instance, or if the loading of the asset fails.
        """
        assert hasattr(self, asset), f"{asset} is not an attribute in the class"
        assert getattr(self, asset), f"{asset} should be loaded / generated first"
        assert self.dev_inst, "Device instance is required to load WPC certs"
        assert getattr(self.dev_inst, asset_handler), f"{asset_handler} is not an attribute in device instance"
        status = getattr(self.dev_inst, asset_handler)(getattr(self, asset))
        assert status == 0, f"Loading of {asset} has failed with {status: 02X}"

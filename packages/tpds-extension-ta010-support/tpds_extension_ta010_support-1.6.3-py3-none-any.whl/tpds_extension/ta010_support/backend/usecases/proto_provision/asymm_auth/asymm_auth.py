# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import ExtensionOID
from ..certs import build_cert
from ..certs.certs import get_certificate_der, get_certificate_pem
from ..helper.keys import generate_private_key, get_public_key, get_public_key_from_pem
from ..helper.defines import KeyAlgorithms
from tpds.cert_tools.cert import Cert
from tpds.cert_tools.ext_builder import TimeFormat


class AsymmAuth():
    """
    AsymmAuth class for asymmetric authentication and certificate generation.

    This class provides methods to generate root, signer, and device certificates,
    as well as to load assets into a device instance.

    Attributes:
        dev_inst: The device instance.
        org_name (str): The organization name. Defaults to "Microchip Technology Inc".
        root_cn (str): The root common name. Defaults to "Microchip RootCA".
        signer_cn (str): The signer common name. Defaults to "Microchip Signer".
        device_cn (str): The device common name. Defaults to "sn01230000000000EE".
        root_key: The root private key.
        root_pubkey: The root public key.
        root_cert: The root certificate.
        signer_key: The signer private key.
        signer_pubkey: The signer public key.
        signer_cert: The signer certificate.
        device_pubkey: The device public key.
        device_cert: The device certificate.

    Methods:
        generate_root_cert(root_key: str = "") -> None:

        generate_signer_cert(signer_key: str = "") -> None:

        generate_device_cert(device_key: str = "") -> None:
            Generates a device certificate.

        load_asset(asset: str, asset_handler: str) -> None:

        build_cert(public_key, signing_key, sub_cn: str = 'AsymmAuthRoot', issuer_cn: str = 'AsymmAuthRoot',
                   hash_algo: HashAlgorithm = hashes.SHA256(), is_ca: bool = True, valid_days: int = 1825) -> bytes:
    """
    def __init__(self, **kwargs) -> None:
        """
        Initialize the AsymmAuth class with the given keyword arguments.

        Args:
            dev_inst (optional): The device instance.
            key_algo (str, optional): The key algorithm to be used. Defaults to ECCP256.
            hash_algo (str, optional): The hash algorithm to be used. Defaults to SHA256.
            org_name (str, optional): The organization name. Defaults to "Microchip Technology Inc".
            root_cn (str, optional): The root common name. Defaults to "Microchip RootCA".
            signer_cn (str, optional): The signer common name. Defaults to "Microchip Signer".
            device_cn (str, optional): The device common name. Defaults to "sn01230000000000EE".

        Raises:
            AssertionError: If key_algo or hash_algo is not provided.
        """
        self.dev_inst = kwargs.get("dev_inst", None)
        self.key_algo = kwargs.get("key_algo", KeyAlgorithms.ECC_P256)
        self.hash_algo = kwargs.get("hash_algo", hashes.SHA256())
        self.org_name = kwargs.get("org_name", "Microchip Technology Inc")
        self.root_cn = kwargs.get("root_cn", "Microchip RootCA")
        self.signer_cn = kwargs.get("signer_cn", "Microchip Signer")
        self.device_cn = kwargs.get("device_cn", "sn01230000000000EE")
        self.root_key, self.root_pubkey, self.root_cert = None, None, None
        self.signer_key, self.signer_pubkey, self.signer_cert = None, None, None
        self.device_pubkey, self.device_cert = None, None

    def generate_root_cert(self, root_key: str = "", validity: int = 0, extensions=[]) -> None:
        """
        Generates a root certificate.

        This method generates a root certificate by creating a private key,
        extracting the corresponding public key, and then building the certificate
        using the provided parameters.

        Args:
            root_key (str): The root key to use for generating the private key.
                            Defaults to an empty string.

        Returns:
            None
        """
        self.root_key = generate_private_key(root_key, self.key_algo)
        self.root_pubkey = get_public_key(self.root_key)
        self.root_cert = build_cert(
            public_key=self.root_pubkey,
            signing_key=self.root_key,
            validity=validity,
            org_name=self.org_name,
            issuer_cn=self.root_cn,
            sub_cn=self.root_cn,
            extensions=extensions,
            hash_algo=self.hash_algo
        )
        self.root_cert_pem = get_certificate_pem(self.root_cert)
        self.root_cert_bytes = get_certificate_der(self.root_cert)

    def set_root_cert(self, root_cert: bytes) -> None:
        """
        Set root certificate.

        Args:
            root_cert (bytes): Root Certificate Bytes

        Returns:
            None
        """
        self.root_cert = Cert()
        self.root_cert.set_certificate(root_cert)
        self.root_cert = self.root_cert.certificate
        self.root_cert_pem = get_certificate_pem(self.root_cert)
        self.root_cert_bytes = get_certificate_der(self.root_cert)

    def generate_signer_cert(
        self,
        signer_key: str = "",
        validity: int = 0,
        is_pub_hash_sn: bool = False,
        extensions=[],
    ) -> None:
        """
        Generates a signer certificate.

        This method generates a private key for the signer, derives the public key from it,
        and then builds a certificate using the signer's public key and the root key.

        Args:
            signer_key (str): The private key for the signer. If not provided, a new key will be generated.

        Raises:
            AssertionError: If the root key is not established before calling this method.

        Returns:
            None
        """
        assert self.root_key, "Root Key should be established first"
        self.signer_key = generate_private_key(signer_key, self.key_algo)
        self.signer_pubkey = get_public_key(self.signer_key)
        self.signer_cert = build_cert(
            public_key=self.signer_pubkey,
            signing_key=self.root_key,
            validity=validity,
            org_name=self.org_name,
            issuer_cn=self.root_cn,
            sub_cn=self.signer_cn,
            time_format=TimeFormat.GENERALIZED_TIME,
            extensions=extensions,
            hash_algo=self.hash_algo,
            ca_cert=self.root_cert,
            is_pub_hash_sn=is_pub_hash_sn,
        )
        self.signer_cert_pem = get_certificate_pem(self.signer_cert)
        self.signer_cert_bytes = get_certificate_der(self.signer_cert)

    def set_signer_cert(self, signer_cert: bytes) -> None:
        """
        Set Signer certificate.

        Args:
            signer_cert (bytes): Signer Certificate Bytes

        Returns:
            None
        """
        self.signer_cert = Cert()
        self.signer_cert.set_certificate(signer_cert)
        self.signer_cert = self.signer_cert.certificate
        for name in self.signer_cert.subject:
            if name.oid == x509.oid.NameOID.ORGANIZATION_NAME:
                self.org_name = name.value
        self.signer_cert_pem = get_certificate_pem(self.signer_cert)
        self.signer_cert_bytes = get_certificate_der(self.signer_cert)

    def generate_device_cert(
        self,
        device_key: str = "",
        validity: int = 0,
        is_pub_hash_sn: bool = False,
        extensions=[],
    ) -> None:
        """
        Generates a device certificate using the provided device key.

        Args:
            device_key (str): The PEM-encoded device key. Defaults to an empty string.

        Raises:
            AssertionError: If the signer key is not established.

        Returns:
            None
        """
        assert self.signer_key, "Signer Key should be established first"
        self.device_pubkey = get_public_key_from_pem(device_key)
        self.device_cert = build_cert(
            public_key=self.device_pubkey,
            signing_key=self.signer_key,
            validity=validity,
            org_name=self.org_name,
            issuer_cn=self.signer_cn,
            sub_cn=self.device_cn,
            time_format=TimeFormat.GENERALIZED_TIME,
            extensions=extensions,
            hash_algo=self.hash_algo,
            is_ca=False,
            ca_cert=self.signer_cert,
            is_pub_hash_sn=is_pub_hash_sn,
        )
        self.device_cert_pem = get_certificate_pem(self.device_cert)
        self.device_cert_bytes = get_certificate_der(self.device_cert)

    def set_device_cert(self, device_cert: bytes) -> None:
        """
        Set Device certificate.

        Args:
            device_cert (bytes): Device Certificate Bytes

        Returns:
            None
        """
        self.device_cert = Cert()
        self.device_cert.set_certificate(device_cert)
        self.device_cert = self.device_cert.certificate
        self.device_cert_pem = get_certificate_pem(self.device_cert)
        self.device_cert_bytes = get_certificate_der(self.device_cert)

    def is_signer_tflx_cert(self):
        """
        Determine if the signer certificate is a valid TFLX certificate by checking specific extensions.

        Raises:
            AssertionError: If the certificate is not a CA certificate or if any required extension
                            is missing, an AssertionError is raised with a descriptive message.

        Exceptions:
            Exception: If any error occurs during the parsing of the signer certificate, an AssertionError
                    is raised with the error message.

        Note:
            This method assumes that `self.signer_cert` is an instance of a certificate object.
        """
        try:
            # Check if it's a CA certificate (basicConstraints extension)
            basic_constraints = self.signer_cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
            assert basic_constraints or basic_constraints.value.ca, "Certificate is not a CA certificate."
            self.signer_cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_KEY_IDENTIFIER)
            self.signer_cert.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
        except Exception as e:
            assert False, f"Parsing Signer certificate failed with {e}"

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
        assert self.dev_inst, "Device instance is required to load symmetric key"
        assert getattr(self.dev_inst, asset_handler), f"{asset_handler} is not an attribute in device instance"
        status = getattr(self.dev_inst, asset_handler)(getattr(self, asset))
        assert status == 0, f"Loading of {asset} has failed with {status: 02X}"

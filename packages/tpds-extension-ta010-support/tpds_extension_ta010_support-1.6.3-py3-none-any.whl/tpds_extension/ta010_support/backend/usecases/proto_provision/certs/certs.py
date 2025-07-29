# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.
from pathlib import Path
from datetime import datetime, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.asymmetric.types import (
    PRIVATE_KEY_TYPES, PUBLIC_KEY_TYPES)
from .create_cert_defs import CertDef
from ..helper.keys import get_public_key
from tpds.cert_tools.cert import Cert
from tpds.cert_tools.ext_builder import TimeFormat
from tpds.cert_tools.cert_utils import random_cert_sn, add_signer_extensions, pubkey_cert_sn


def build_cert(
    public_key: PUBLIC_KEY_TYPES,
    signing_key: PRIVATE_KEY_TYPES,
    validity: int,
    org_name: str = "Microchip Technology Inc",
    issuer_cn: str = "Microchip RootCA",
    sub_cn: str = "Microchip RootCA",
    sn: int = random_cert_sn(16),
    time_format: TimeFormat = TimeFormat.AUTO,
    extensions=[],
    hash_algo: hashes.HashAlgorithm = hashes.SHA256(),
    is_ca: bool = True,
    ca_cert: x509.Certificate = None,
    is_pub_hash_sn: bool = False,
) -> x509.Certificate:
    """
    Generates an X.509 certificate.

    Args:
        public_key: The public key to be included in the certificate.
        signing_key: The private key used to sign the certificate.
        sub_cn (str, optional): The subject common name. Defaults to 'AsymmAuthRoot'.
        issuer_cn (str, optional): The issuer common name. Defaults to 'AsymmAuthRoot'.
        hash_algo (HashAlgorithm, optional): The hash algorithm to use for signing. Defaults to hashes.SHA256().
        is_ca (bool, optional): Whether the certificate is for a Certificate Authority. Defaults to True.
        valid_days (int, optional): The number of days the certificate is valid for. Defaults to 1825.

    Returns:
        bytes: The DER-encoded certificate.
    """
    cert = Cert()
    cert.builder = cert.builder.issuer_name(
        x509.Name(
            [
                x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, org_name),
                x509.NameAttribute(x509.NameOID.COMMON_NAME, issuer_cn),
            ]
        )
    )
    cert.builder = cert.builder.subject_name(
        x509.Name(
            [
                x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, org_name),
                x509.NameAttribute(x509.NameOID.COMMON_NAME, sub_cn),
            ]
        )
    )
    cert.builder = cert.builder.not_valid_before(
        datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0,)
    )
    if validity == 0:
        cert.builder = cert.builder.not_valid_after(
            datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
            format=time_format
        )
    else:
        cert.builder = cert.builder.not_valid_after(
            cert.builder._not_valid_before.replace(
                year=cert.builder._not_valid_before.year + validity
            ),
            format=time_format,
        )
    cert.builder = cert.builder.public_key(public_key)
    if is_pub_hash_sn:
        cert.builder = cert.builder.serial_number(
            pubkey_cert_sn(16, cert.builder, True)
        )
    else:
        cert.builder = cert.builder.serial_number(sn)
    if is_ca:
        cert.builder = add_signer_extensions(cert.builder, public_key, ca_cert)
    else:
        cert.builder = cert.builder.add_extension(x509.BasicConstraints(ca=is_ca, path_length=None), critical=True)
        cert.builder = cert.builder.add_extension(
            x509.SubjectKeyIdentifier.from_public_key(public_key), critical=False
        )
        if ca_cert:
            cert.builder = cert.builder.add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(
                    ca_cert.extensions.get_extension_for_class(
                        x509.SubjectKeyIdentifier
                    ).value
                ),
                critical=False,
            )
        else:
            cert.builder = cert.builder.add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_public_key(get_public_key(signing_key)),
                critical=False,
            )
    for extval, critical in extensions:
        cert.builder = cert.builder.add_extension(extval, critical)
    cert.sign_builder(signing_key, hash_algo)
    return cert.certificate


def build_custom_extension(oid: str, value: bytes):
    return x509.UnrecognizedExtension(x509.ObjectIdentifier(oid), value)


def get_certificate_from_pem(cert_pem: bytes) -> x509.Certificate:
    """
    Get the X.509 Certificate from the PEM

    Args:
        cert_pem (bytes): PEM formatted certificate

    Returns:
        x509.Certificate: X.509 Certificate object
    """
    return x509.load_pem_x509_certificate(cert_pem, default_backend())


def get_certificate_pem(cert: x509.Certificate) -> bytes:
    """
    Get the PEM format of the X.509 Certificate

    Args:
        cert (x509.Certificate): X.509 Certificate object

    Returns:
        bytes: PEM format of the X.509 Certificate
    """
    return cert.public_bytes(Encoding.PEM)


def get_certificate_from_der(cert_der: bytes) -> x509.Certificate:
    """
    Get the X.509 Certificate from the DER

    Args:
        cert_pem (bytes): DER formatted certificate

    Returns:
        x509.Certificate: X.509 Certificate object
    """
    return x509.load_der_x509_certificate(cert_der, default_backend())


def get_certificate_der(cert: x509.Certificate) -> bytes:
    """
    Get the DER format of the X.509 Certificate

    Args:
        cert (x509.Certificate): X.509 Certificate object

    Returns:
        bytes: DER format of the X.509 Certificate
    """
    return cert.public_bytes(Encoding.DER)


def get_certificate_from_file_bytes(cert: bytes) -> x509.Certificate:
    """
    Attempts to load an x509 certificate from a byte sequence.

    This function tries to load the certificate using both PEM and DER formats.
    If the certificate is successfully loaded in either format, it returns the
    corresponding x509.Certificate object. If neither format is successful, it
    raises a ValueError indicating that the Certificate is invalid.

    Args:
        cert (bytes): The byte sequence representing the certificate.

    Returns:
        x509.Certificate: The loaded x509 certificate.

    Raises:
        ValueError: If the certificate cannot be loaded in either PEM or DER format.
    """
    for loader in (get_certificate_from_pem, get_certificate_from_der):
        try:
            if certificate := loader(cert):
                return certificate
        except Exception:
            continue
    raise ValueError("Invalid Certificate")


def save_cert_pem(cert: x509.Certificate, file: str):
    """
    Save a given X.509 certificate in PEM format to a specified file.

    Args:
        cert (x509.Certificate): The X.509 certificate to be saved.
        file (str): The file path where the PEM-encoded certificate will be written.

    """
    cert_pem = get_certificate_pem(cert)
    Path(file).write_bytes(cert_pem)


def is_certificate_chain_valid(
        root_cert: x509.Certificate,
        signer_cert: x509.Certificate,
        device_cert: x509.Certificate):
    """
    Validate a certificate chain consisting of a root certificate, a signer certificate, and a device certificate.

    Args:
        root_cert (x509.Certificate): The root certificate in the chain.
        signer_cert (x509.Certificate): The signer certificate, issued by the root certificate.
        device_cert (x509.Certificate): The device certificate, issued by the signer certificate.

    Returns:
        bool: True if the certificate chain is valid, i.e., all signatures are verified successfully;
              False otherwise.
    """
    root = Cert()
    root.set_certificate(root_cert)

    signer = Cert()
    signer.set_certificate(signer_cert)

    device = Cert()
    device.set_certificate(device_cert)

    return (
        root.is_signature_valid(root_cert.public_key())
        and signer.is_signature_valid(root_cert.public_key())
        and device.is_signature_valid(signer_cert.public_key())
    )


def save_tflx_c_definations(
    root_cert: x509.Certificate,
    signer_cert: x509.Certificate,
    device_cert: x509.Certificate,
    device_name,
):
    """
    Generate and save compressed certificate C definitions for TFLX certificates,
    including signer and device certificates.

    Args:
        root_cert (x509.Certificate): The root certificate used for validation.
        signer_cert (x509.Certificate): The signer certificate to generate the compressed certificate C definition.
        device_cert (x509.Certificate): The device certificate to generate the compressed certificate C definition.
        device_name (str): The name of the device.

    """
    signer_cert_def = CertDef(device_name)
    signer_cert_def.set_certificate(signer_cert, root_cert, 1)
    signer_cert_def.get_c_definition(True)

    device_cert_def = CertDef(device_name)
    device_cert_def.set_certificate(device_cert, signer_cert, 3)
    device_cert_def.get_c_definition(True)


def get_tflex_py_definitions(
    root_cert: x509.Certificate,
    signer_cert: x509.Certificate,
    device_cert: x509.Certificate,
    device_name,
):
    """
    Generate Python compressed certificate definitions for TFLX certificates, including signer and device certificates.

    Args:
        root_cert (x509.Certificate): The root certificate used for validation.
        signer_cert (x509.Certificate): The signer certificate to generate the Python definition for.
        device_cert (x509.Certificate): The device certificate to generate the Python definition for.
        device_name (str): The name of the device.

    Returns:
        dict: A dictionary containing the Python definitions for the signer and device certificates.
    """
    py_def = dict()

    signer_cert_def = CertDef(device_name)
    signer_cert_def.set_certificate(signer_cert, root_cert, 1)
    py_def.update({"signer": signer_cert_def.get_py_definition()})

    device_cert_def = CertDef(device_name)
    device_cert_def.set_certificate(device_cert, signer_cert, 3)
    py_def.update({"device": device_cert_def.get_py_definition()})
    return py_def


def build_hsm_cert(
    cert_template: x509.Certificate,
    signer_key: PRIVATE_KEY_TYPES,
    subject_key: PUBLIC_KEY_TYPES,
    hash_algo: hashes.HashAlgorithm
) -> x509.Certificate:
    """
    Build a HSM certificate based on a given certificate template.

    Args:
        cert_template (x509.Certificate): The template certificate to base the new HSM certificate on.
        signer_key (PRIVATE_KEY_TYPES): The private key used to sign the new HSM certificate.
        subject_key (PUBLIC_KEY_TYPES): The public key to be included in the new HSM certificate.
        hash_algo (hashes.HashAlgorithm): The hash algorithm to use for signing the certificate.

    Returns:
        x509.Certificate: The newly created HSM certificate.
    """
    hsm_cert = Cert()
    hsm_cert.builder = hsm_cert.builder.serial_number(
        random_cert_sn(((cert_template.serial_number.bit_length() + 7) // 8))
    )
    hsm_cert.builder = hsm_cert.builder.subject_name(cert_template.subject)
    hsm_cert.builder = hsm_cert.builder.issuer_name(cert_template.issuer)
    hsm_cert.builder = hsm_cert.builder.not_valid_before(
        datetime.utcnow().replace(
            minute=0, second=0, microsecond=0, tzinfo=timezone.utc
        )
    )
    if cert_template.not_valid_after.year == 9999:
        hsm_cert.builder = hsm_cert.builder.not_valid_after(
            datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
            format=TimeFormat.GENERALIZED_TIME,
        )
    else:
        validity = cert_template.not_valid_after.year - cert_template.not_valid_before.year
        hsm_cert.builder = hsm_cert.builder.not_valid_after(
            hsm_cert.builder._not_valid_before.replace(
                year=hsm_cert.builder._not_valid_before.year + validity
            ),
            format=TimeFormat.GENERALIZED_TIME,
        )
    hsm_cert.builder = hsm_cert.builder.public_key(subject_key)
    for extension in cert_template.extensions:
        hsm_cert.builder = hsm_cert.builder.add_extension(
            extension.value, extension.critical
        )
    hsm_cert = hsm_cert.builder.sign(signer_key, hash_algo)

    return hsm_cert

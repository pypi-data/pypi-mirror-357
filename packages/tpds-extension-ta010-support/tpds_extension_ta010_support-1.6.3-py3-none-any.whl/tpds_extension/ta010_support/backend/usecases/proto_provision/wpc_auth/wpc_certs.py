# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

from cryptography import x509
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import ec
from tpds.cert_tools.cert import Cert
from tpds.cert_tools.ext_builder import TimeFormat
from tpds.cert_tools.cert_utils import random_cert_sn, pubkey_cert_sn


def create_wpc_root_cert(
    ca_private_key: ec.EllipticCurvePrivateKey, root_cn: str, root_sn: int
) -> x509.Certificate:
    """
    Create a root CA certificate that looks like the WPCCA1 real
    root, but with a different key for testing purposes.
    """
    cert = Cert()
    if root_sn:
        cert.builder = cert.builder.serial_number(root_sn)
    else:
        cert.builder = cert.builder.serial_number(random_cert_sn(8))
    cert.builder = cert.builder.subject_name(
        x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, root_cn)])
    )
    # Names are the same for a self-signed certificate
    cert.builder = cert.builder.issuer_name(cert.builder._subject_name)
    cert.builder = cert.builder.not_valid_before(
        datetime(2021, 3, 3, 16, 4, 1, tzinfo=timezone.utc)
    )
    cert.builder = cert.builder.not_valid_after(
        datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    )
    cert.builder = cert.builder.public_key(ca_private_key.public_key())
    cert.builder = cert.builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True
    )
    cert.sign_builder(private_key=ca_private_key)
    return cert.certificate


def create_wpc_mfg_cert(
    ptmc: int,
    sequence_id: int,
    qi_policy: int,
    public_key: ec.EllipticCurvePublicKey,
    ca_private_key: ec.EllipticCurvePrivateKey,
    ca_certificate: x509.Certificate,
    old_certificate: x509.Certificate = None,
) -> x509.Certificate:
    cert = Cert()
    cert.builder = cert.builder.issuer_name(ca_certificate.subject)
    if old_certificate:
        cert.builder = cert.builder.not_valid_before(old_certificate.not_valid_before)
    else:
        # CA will assign date and won't conform to CompressedCert format with minutes and seconds set to 0, so
        # we use the full date and will store it on the device
        cert.builder = cert.builder.not_valid_before(datetime.now(timezone.utc))
    cert.builder = cert.builder.not_valid_after(
        datetime(year=9999, month=12, day=31, hour=23, minute=59, second=59, tzinfo=timezone.utc,)
    )
    cert.builder = cert.builder.subject_name(
        x509.Name(
            [
                x509.NameAttribute(
                    x509.oid.NameOID.COMMON_NAME, f"{ptmc:04X}-{sequence_id:02X}"
                )
            ]
        )
    )
    cert.builder = cert.builder.public_key(public_key)
    cert.builder = cert.builder.serial_number(random_cert_sn(8))  # SN must be 9 bytes or less per WPC spec
    cert.builder = cert.builder.add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
    # id-at-wpcQiPolicy extension is an octet string (tag 0x04)
    qi_policy_bytes = qi_policy.to_bytes(4, "big")
    wpc_qi_policy_extension_value = bytes([0x04, len(qi_policy_bytes)]) + qi_policy_bytes
    cert.builder = cert.builder.add_extension(
        x509.UnrecognizedExtension(
            x509.ObjectIdentifier("2.23.148.1.1"), wpc_qi_policy_extension_value
        ),
        critical=True,
    )
    cert.sign_builder(private_key=ca_private_key)
    return cert.certificate


def create_wpc_puc_cert(
    qi_id: int,
    rsid: int,
    public_key: ec.EllipticCurvePublicKey,
    ca_private_key: ec.EllipticCurvePrivateKey,
    ca_certificate: x509.Certificate,
    old_certificate: x509.Certificate = None,
) -> x509.Certificate:
    cert = Cert()
    cert.builder = cert.builder.issuer_name(ca_certificate.subject)
    if old_certificate:
        cert.builder = cert.builder.not_valid_before(
            old_certificate.not_valid_before, format=TimeFormat.GENERALIZED_TIME
        )
    else:
        # Force times to use generalized time regardless of year so there are no issues at the 2050 transition
        cert.builder = cert.builder.not_valid_before(
            datetime.utcnow().replace(tzinfo=timezone.utc, minute=0, second=0),
            format=TimeFormat.GENERALIZED_TIME,
        )
    cert.builder = cert.builder.not_valid_after(
        datetime(year=9999, month=12, day=31, hour=23, minute=59, second=59, tzinfo=timezone.utc,)
    )
    cert.builder = cert.builder.public_key(public_key)
    cert.builder = cert.builder.serial_number(pubkey_cert_sn(8, cert.builder))
    cert.builder = cert.builder.subject_name(
        x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, f"{qi_id:06d}")])
    )
    # Raw RSID value is stored as big endian bytes in the certificate extension
    rsid_bytes = rsid.to_bytes(9, byteorder="big", signed=False)
    # Extension is an octet string (tag 0x04)
    rsid_extension_value = bytes([0x04, len(rsid_bytes)]) + rsid_bytes
    cert.builder = cert.builder.add_extension(
        x509.UnrecognizedExtension(
            x509.ObjectIdentifier("2.23.148.1.2"), rsid_extension_value
        ),
        critical=True,
    )
    cert.sign_builder(private_key=ca_private_key)
    return cert.certificate

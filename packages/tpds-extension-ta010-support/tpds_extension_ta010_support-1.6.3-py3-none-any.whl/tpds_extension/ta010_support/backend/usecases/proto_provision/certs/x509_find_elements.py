# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

import asn1crypto.core
import asn1crypto.keys
import asn1crypto.x509


def diff_offset(base, diff):
    """Return the index where the two parameters differ."""
    base = base.dump()
    diff = diff.dump()
    if len(base) != len(diff):
        raise ValueError("len(base)=%d != len(diff)=%d" % (len(base), len(diff)))
    for i in range(0, len(base)):
        if base[i] != diff[i]:
            return i
    raise ValueError("base and diff are identical")


def sn_location(cert):
    """
    Determines the offset and length of the serial number within a given X.509 certificate.

    Args:
        cert (asn1crypto.x509.Certificate): The X.509 certificate to be processed.

    Returns:
        tuple: A tuple containing:
            - int: The offset of the serial number within the certificate.
            - int: The length of the serial number in bytes.
    """
    cert_mod = cert.copy()
    sn = bytearray(cert_mod["tbs_certificate"]["serial_number"].contents)
    # Alter the serial number to find offset, but retain encoding size
    sn[0] = 0x01 if sn[0] != 0x01 else 0x02
    cert_mod["tbs_certificate"]["serial_number"] = asn1crypto.core.Integer(
        int().from_bytes(sn, byteorder="big", signed=True)
    )
    return (diff_offset(cert, cert_mod), len(cert["tbs_certificate"]["serial_number"].contents))


def validity_location(cert, name):
    """
    Determines the offset and length of the validity field name ('not_before' or 'not_after')
    within a given X.509 certificate.

    Args:
        cert (asn1crypto.x509.Certificate): The X.509 certificate to be processed.
        name (str): The name of the validity field to modify ('not_before' or 'not_after').

    Returns:
        tuple: A tuple containing the offset validity in certificate, and the length of the
               contents of the chosen validity field.

    Raises:
        ValueError: If the tag value of the validity field is unexpected.
    """
    cert_mod = cert.copy()
    time = cert["tbs_certificate"]["validity"][name]
    if time.chosen.tag == asn1crypto.core.UTCTime.tag:
        if time.chosen.native.year >= 2000 and time.chosen.native.year < 2010:
            new_time = time.chosen.native.replace(year=2010)
        else:
            new_time = time.chosen.native.replace(year=2000)
        cert_mod["tbs_certificate"]["validity"][name] = asn1crypto.x509.Time(
            name="utc_time", value=asn1crypto.core.UTCTime(new_time)
        )
    elif time.chosen.tag == asn1crypto.core.GeneralizedTime.tag:
        if time.chosen.native.year >= 2000 and time.chosen.native.year < 3000:
            new_time = time.chosen.native.replace(year=3000)
        else:
            new_time = time.chosen.native.replace(year=2000)
        cert_mod["tbs_certificate"]["validity"][name] = asn1crypto.x509.Time(
            name="general_time", value=asn1crypto.core.GeneralizedTime(new_time)
        )
    else:
        raise ValueError("Unexpected tag value ({}) for validity {}".format(time.chosen.tag, name))
    return (
        diff_offset(cert, cert_mod),
        len(cert["tbs_certificate"]["validity"][name].chosen.contents),
    )


def public_key_location(cert):
    """
    Determines the offset and length of the Public Key within a given X.509 certificate.

    Args:
        cert (asn1crypto.x509.Certificate): The X.509 certificate to be processed.

    Returns:
        tuple: A tuple containing:
            - int: The offset of the public key
            - int: The length of the public key.
    """
    cert_mod = cert.copy()
    public_key = bytearray(cert["tbs_certificate"]["subject_public_key_info"]["public_key"].native)
    # Change the first byte of the public key skipping the key-compression byte
    public_key[1] ^= 0xFF
    cert_mod["tbs_certificate"]["subject_public_key_info"][
        "public_key"
    ] = asn1crypto.keys.ECPointBitString(bytes(public_key))
    return (
        diff_offset(cert, cert_mod),
        len(cert["tbs_certificate"]["subject_public_key_info"]["public_key"].native) - 1,
    )


def name_search_location(cert, name, search):
    """
    Searches for a specific text within a certificate's name field and modifies it,
    then calculates the offset and the length.

    Args:
        cert (asn1crypto.x509.Certificate): The X.509 certificate to be processed.
        name (str): The name field within the certificate to search and modify (e.g., 'subject', 'issuer').
        search (str): The text to search for within the specified name field.

    Returns:
        tuple: A tuple containing:
            - int: The offset of the search text.
            - int: The length of the search text.

    Raises:
        ValueError: If the search text is not found within the specified name field of the certificate.
    """
    cert_mod = cert.copy()
    # Change the first character of the search text for the replacement text
    search = search.encode()
    replace = (b"F" if search[0] != ord(b"F") else b"0") + search[1:]
    name_der = cert["tbs_certificate"][name].dump()
    if search not in name_der:
        raise ValueError('Could not find "{}" in certificate {} name.'.format(search, name))
    cert_mod["tbs_certificate"][name] = asn1crypto.x509.Name().load(
        name_der.replace(search, replace)
    )
    return (diff_offset(cert, cert_mod), len(search))


def name_search_location_last(cert, name, search):
    """
    Searches for the last occurrence of a specific text within a certificate's name field,
    and calculates the offset and the length.

    Args:
        cert (asn1crypto.x509.Certificate): The X.509 certificate to be processed.
        name (str): The name field within the certificate to search (e.g., 'subject', 'issuer').
        search (str): The text to search for within the specified name field.

    Returns:
        tuple: A tuple containing:
            - int: The offset of the search text.
            - int: The length of the search text.

    Raises:
        ValueError: If the search text is not found within the specified name field of the certificate.
    """
    # Gives offset and length information of certain search string, searched from
    # right to left and finds the first instance.
    cert_mod = cert.copy()
    # Change the first character of the search text for the replacement text
    search = search.encode()
    replace = (b"F" if search[0] != ord(b"F") else b"0") + search[1:]
    name_der = cert["tbs_certificate"][name].dump()
    if search not in name_der:
        raise ValueError('Could not find "{}" in certificate {} name.'.format(search, name))
    cert_mod["tbs_certificate"][name] = asn1crypto.x509.Name().load(
        replace.join(name_der.rsplit(search, 1))
    )
    return (diff_offset(cert, cert_mod), len(search))


def auth_key_id_location(cert):
    """
    Locates the authority key identifier extension within a certificate,
    then calculates the offset and the length authority key identifier.

    Args:
        cert (asn1crypto.x509.Certificate): The X.509 certificate to be processed.

    Returns:
        tuple: A tuple containing:
            - int: The offset of the key identifier.
            - int: The length of the key identifier.

    If the "authority_key_identifier" extension is not found, the function returns (0, 0).
    """
    cert_mod = cert.copy()
    oid = asn1crypto.x509.ExtensionId("authority_key_identifier")
    is_found = False
    for extension in cert_mod["tbs_certificate"]["extensions"]:
        if extension["extn_id"] == oid:
            is_found = True
            break
    if not is_found:
        return (0, 0)

    # Modify the first byte of the key ID value
    mod_key_id = bytearray(extension["extn_value"].parsed["key_identifier"].native)
    mod_key_id[0] ^= 0xFF
    mod_auth_key_id = extension["extn_value"].parsed.copy()
    mod_auth_key_id["key_identifier"] = asn1crypto.core.OctetString(bytes(mod_key_id))
    extension["extn_value"] = mod_auth_key_id

    return (diff_offset(cert, cert_mod), len(mod_key_id))


def subj_key_id_location(cert):
    """
    Locates the subject key identifier extension within a certificate,
    then calculates the offset and the length of the subject key identifier.

    Args:
        cert (asn1crypto.x509.Certificate): The X.509 certificate to be processed.

    Returns:
        tuple: A tuple containing:
            - int: The offset of the key subject identifier.
            - int: The length of the key subject identifier.

    If the "subject_key_identifier" extension is not found, the function returns (0, 0).
    """
    cert_mod = cert.copy()
    oid = asn1crypto.x509.ExtensionId("key_identifier")
    is_found = False
    for extension in cert_mod["tbs_certificate"]["extensions"]:
        if extension["extn_id"] == oid:
            is_found = True
            break
    if not is_found:
        return (0, 0)

    # Modify the first byte of the key ID value
    mod_key_id = bytearray(extension["extn_value"].parsed.native)
    mod_key_id[0] ^= 0xFF
    mod_auth_key_id = asn1crypto.core.OctetString(bytes(mod_key_id))
    extension["extn_value"] = mod_auth_key_id

    return (diff_offset(cert, cert_mod), len(mod_key_id))


def signature_location(cert):
    """
    Determine the location and length of the signature within a given X.509 certificate.

    Args:
        cert (asn1crypto.x509.Certificate): The X.509 certificate to be processed.

    Returns:
        tuple: A tuple containing the offset (int) where the signature is located
               within the DER-encoded certificate and the length (int) of the signature.
    """
    signature_der = cert["signature_value"].dump()
    return (cert.dump().find(signature_der), len(signature_der))


def tbs_location(cert):
    """
    Determine the location and length of the "to-be-signed" (TBS) portion within a given X.509 certificate.

    Args:
        cert (asn1crypto.x509.Certificate): The X.509 certificate to be processed.

    Returns:
        tuple: A tuple containing the offset (int) where the TBS portion is located
               within the DER-encoded certificate and the length (int) of the TBS portion.
    """
    tbs_der = cert["tbs_certificate"].dump()
    return (cert.dump().find(tbs_der), len(tbs_der))


def cert_search(cert, search):
    """
    Search for a specific byte sequence within a given X.509 certificate and return its location and length.

    Args:
        cert (asn1crypto.x509.Certificate): The X.509 certificate to be searched.
        search (bytes): The byte sequence to search for within the certificate.

    Returns:
        tuple: A tuple containing the offset (int) where the byte sequence is located
               within the DER-encoded certificate and the length (int) of the byte sequence.
    """
    return (cert.dump().find(search), len(search))

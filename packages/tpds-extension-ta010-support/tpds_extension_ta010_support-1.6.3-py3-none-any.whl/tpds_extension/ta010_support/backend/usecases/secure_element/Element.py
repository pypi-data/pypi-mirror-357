# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

import cryptoauthlib as cal
from ..proto_provision.connect import Connect
from ..proto_provision.certs.certs import is_certificate_chain_valid, get_certificate_der


class TA010_ECC204(Connect):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def get_device_serial_number(self):
        """
        Returns device serial number from connected device
        """
        serial_num = bytearray(9)
        status = cal.atcab_read_serial_number(serial_num)
        assert cal.Status.ATCA_SUCCESS == status, f"Reading Serial Number failed with: {status:02X}"
        return serial_num

    def load_secret_key(
        self, slot, secret_key, encryption_slot=None, encryption_key: bytes = None
    ):
        """
        Load a secret key into a specified slot. If encryption parameters are provided,
        the key will be encrypted before being written to the slot.

        Args:
            slot (int): The slot number where the secret key will be loaded.
            secret_key (bytes): The secret key to be loaded into the slot.
            encryption_slot (int, optional): The slot number containing the encryption key.
                                             Required if encryption_key is provided.
            encryption_key (bytes, optional): The encryption key used to encrypt the secret key
                                              before loading it into the slot.

        Raises:
            AssertionError: If loading the key into the slot fails.
        """
        if encryption_slot and encryption_key:
            status = cal.atcab_write_enc(
                slot,
                0,
                secret_key,
                encryption_key,
                encryption_slot,
            )
        else:
            status = cal.atcab_write_bytes_zone(
                0x02,
                slot,
                0,
                secret_key,
                len(secret_key),
            )
        assert (
            status == cal.Status.ATCA_SUCCESS
        ), f"Loading key into slot{slot} failed with error code {status:02X}"

    def get_pubkey(self, slot):
        """
        Retrieve the public key from a specified slot on the secure element.

        Args:
            slot (int): The slot number from which to retrieve the public key on the secure element.

        Returns:
            bytearray: The public key retrieved from the specified slot as a bytearray.

        Raises:
            AssertionError: If the status is not `ATCA_SUCCESS`, indicating
                            a failure in reading the device public key.
        """
        device_pubkey = bytearray()
        status = cal.atcab_get_pubkey(slot, device_pubkey)
        assert (status == cal.Status.ATCA_SUCCESS), f"Reading device public key is failed with {status:02X}"
        return device_pubkey

    def write_cert(self, cert_def, cert: bytes):
        """
        Write a certificate to the secure element using the specified certificate definition.

        Args:
            cert_def (object): The compressed certificate definition.
            cert (bytes): The certificate to be written.

        Raises:
            AssertionError: If the status is not `ATCA_SUCCESS`, indicating
                            a failure in writing the certificate to the secure element.
        """
        status = cal.atcacert_write_cert(cert_def, cert, len(cert))
        assert status == cal.Status.ATCA_SUCCESS, f"Loading certificate into slot failed with {status:02X}"

    def perform_slot_write(self, slot, data, offset: int = 0):
        """
        Write data to a specified slot in the secure element at a given offset.

        Args:
            slot (int): The slot number where the data should be written in the secure element.
            data (bytes): The data to be written.
            offset (int, optional): The offset within the slot where the writing should begin. Defaults to 0.

        Raises:
            AssertionError: If the status is not `ATCA_SUCCESS`, indicating
                            a failure in writing the data to the specified slot.
        """
        status = cal.atcab_write_bytes_zone(0x02, slot, offset, data, len(data))
        assert status == cal.Status.ATCA_SUCCESS, f"Slot Write failed with {status}"

    def provision_wpc_slots(self, root_cert, mfg_cert, puc_cert, wpc_chain_digest):
        """
        Provision the secure element with WPC certificate chain and digest data.

        Args:
            root_cert (object): The root certificate in the WPC certificate chain.
            mfg_cert (object): The manufacturer certificate in the WPC certificate chain.
            puc_cert (object): The product unit certificate in the WPC certificate chain.
            wpc_chain_digest (bytes): The digest of the WPC certificate chain.

        Raises:
            AssertionError: If the certificate chain is invalid, indicating a failure in the integrity check.
        """
        assert is_certificate_chain_valid(root_cert, mfg_cert, puc_cert), "Invalid WPC Ceritificate chain"
        puc_bytes = get_certificate_der(puc_cert)

        # Write Slot1 and Slot2 data to device
        # Adjust to Slot1 size (320)
        puc_slot_data = puc_bytes + bytearray(b"\0" * (320 - len(puc_bytes)))
        self.perform_slot_write(1, puc_slot_data)
        self.perform_slot_write(2, wpc_chain_digest)

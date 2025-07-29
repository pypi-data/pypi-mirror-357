# Symmetric Authentication - TA010-TFLXAUTH

Accessory / Disposable Symmetric Authentication is a process in which a Host generate a challenge that is computed by the Device (accessory / disposable) which send back a response that will be verified by Host to authenticate the Device. The purpose of authentication is to prevent cloning and counterfeiting and to ensure that an accessory / disposable is genuine and authorized to connect to a Host.

## Implementation:

- **Diversified Key authentication** - requires to integrate a Secure Element on the Device (Accessory / Disposable) and the Host side. Device Secure Element will be provisioned with a unique symmetric key (derived from a root symmetric key and the Secure Element serial number. Host Secure Element will be provisioned with the root symmetric key)

This use case describes how Microchip TA010 TrustFLEX AUTH device can be used for Accessory / Disposable authentication using Diversified symmetric Key authentication method.
The Master symmetric key in this case is stored on ATECC608 for implementing diversified authentication usecase. TA010 will be provisioned with a unique symmetric (derived from a master symmetric key and the TA010 serial number)
# WPC Authentication - TA010-TFLXWPC

The purpose of this Use Case is to authentify a Qi 1.3 Wireless Power Charger from a mobile phone, as Qi 1.3 specification mandate the usage of a Secure subsystem (Secure Element) on the charger side. It is based on a standard asymmetric authentication

Asymmetric Authentication is a process based on a custom PKI (Public Key Infrastructure) where a Host (mobile phone) will authenticate that the WPC charger (device) is genuine. The Host will first verify the Signer certificate (Manufacturer ) device certificates (Product Unit Certificate – PUC) based on the Root CA Public key and will generate a challenge to be signed by the charger private key. The Host will then perform an ECDSA verify command to ensure that the signed challenge is valid.

This use case describes how Microchip TA010 TrustFLEX WPC Secure Subsystem can be used for Qi 1.3 WPC authentication using asymmetric authentication (Custom PKI based).
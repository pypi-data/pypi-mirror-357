# AES message encryption - ATECC608-TFLXTLS

The usecase demonstrates AES encryption being run on Host MCU or MPU while having the master symmetric key held securely in ECC608 secure element.

This is done in cases where the higher encryption speed is required. The master symmetric key is stored in ECC608 and a derived key is generated using KDF command. The parameters used to calculate the derived key are then shared to the Cloud/remote host so it can calculate the same derived key to perform AES operations.

Depending on the hardware doing AES operaions on MCU/MPU may not secure but storing the symmetric key in ECC608 ensures that master key is never exposed. The derived key can also be set to expire (ephemeral key) after a set timeframe in the software. Once the current key expires, the remost host and MCU/MPU system can agree on parameters and generate a fresh ephemeral key
# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

import os
import cryptoauthlib as cal
from tpds.settings import TrustPlatformSettings
from tpds.helper import UsecaseLogger
from tpds.tp_utils.tp_utils import pretty_print_hex
from ...api.model import UsecaseResponseModel
from ..proto_provision.symm_auth import SymmAuth
from ..proto_provision.connect import Connect
from ..proto_provision.helper.defines import KeySize
from ..proto_provision.helper.utils import get_c_array
from ..proto_provision.helper.helper import check_board_status
from ..proto_provision.helper.keys import save_symmetric_key


class AesMessageEncryption(Connect):
    """
    AesMessageEncryption is a use case class for AES message encryption using ECC608 .

    Attributes:
        symm_slot (int): Slot number for the symmetric key.
        enc_slot (int): Slot number for the encryption key.
        usecase_dir (str): Working Directory for use case and use case files.
        logger (UsecaseLogger): Logger for the use case.
        symm_key_name (str): Variable name for the symmetric key.
        enc_key_name (str): Variable name for the encryption key.

    Methods:
        generate_resources(user_inputs):
            Generates or loads symmetric keys and saves them in PEM and header files.

        proto_provision(user_inputs):
            Provisions the secure element with the generated keys.

        load_secret_key(slot, secret_key, encryption_slot=None, encryption_key=None):
            Loads a secret key into a specified slot, optionally using encryption.

        fw_resources(key, var):
            Writes the key to a header file in C array format.
    """

    def __init__(self, usecase_dir=None) -> None:
        """
        Initialize the AES message encryption use case with specified or default directory.

        Args:
            usecase_dir (str, optional): The directory to use for the use case.
                                         If None, a default directory is used.

        Attributes:
            symm_slot (int): Slot number for the symmetric key.
            enc_slot (int): Slot number for the encryption key.
            usecase_dir (str): Working Directory for the use case files.
            logger (UsecaseLogger): Logger instance for the use case.
            symm_key_name (str): Variable name for the symmetric key.
            enc_key_name (str): Variable name for the encryption key.
        """
        self.symm_slot = 0x05
        self.enc_slot = 0x06
        if usecase_dir is None:
            self.usecase_dir = os.path.join(
                TrustPlatformSettings().get_base_folder(), "aes_message_encryption"
            )
        else:
            self.usecase_dir = usecase_dir
        os.makedirs(self.usecase_dir, exist_ok=True)
        self.logger = UsecaseLogger(self.usecase_dir)
        self.symm_key_name = "slot_5_secret_key"
        self.enc_key_name = "slot_6_secret_key"

    def generate_resources(self, user_inputs):
        """
        Generates and loads symmetric keys based on user inputs, and saves them in PEM format.

        This method performs the following steps:
        1. Changes the current working directory to the use case directory.
        2. Generates or loads a master symmetric key from user inputs.
        3. Saves the master symmetric key in PEM format and logs its value.
        4. Generates an encryption key.
        5. Saves the encryption key in PEM format.
        6. Generates firmware resources
        7. Sets the response status and message based on the success or failure of the process.
        8. Changes the working directory back to the original directory.
        9. Logs the response message and returns the response object.

        Args:
            user_inputs (dict): A dictionary containing user inputs, including keys for symmetric key generation.

        Returns:
            UsecaseResponseModel: An object containing the status, message, and log of the resource generation process.
        """
        response = UsecaseResponseModel()
        current_dir = os.getcwd()
        os.chdir(self.usecase_dir)
        try:
            self.logger.log("Generating/Loading Symmetric Keys")
            assert len(
                user_inputs.get("keys")
            ), "Keys are required for AES message encryption"

            self.symm_key = SymmAuth()
            if key := user_inputs.get("keys").get(self.symm_key_name).get("value"):
                key = bytes.fromhex(key)
            self.symm_key.generate_symmetric_key(
                key=key,
                key_size=KeySize.AES256,
            )
            self.symm_key = self.symm_key.symm_bytes
            save_symmetric_key(self.symm_key, self.symm_key_name, ["PEM", "BIN"])
            self.logger.log("Master Symmetric key:")
            self.logger.log("\n" + pretty_print_hex(self.symm_key, li=8, indent=""))
            self.logger.log(f"Master Symmetric key saved in {self.symm_key_name}.h")

            self.enc_key = SymmAuth()
            self.enc_key.generate_symmetric_key(
                key=None,
                key_size=KeySize.AES256,
            )
            self.enc_key = self.enc_key.symm_bytes
            save_symmetric_key(self.enc_key, self.enc_key_name, ["PEM", "BIN"])
            self.fw_resources(self.symm_key, self.symm_key_name)
            self.fw_resources(self.enc_key, self.enc_key_name)
            response.status = True
            response.message = "Resource generation is successful"
        except Exception as e:
            response.message = f"Resource Generation Failed with: {e}"
        finally:
            os.chdir(current_dir)
            self.logger.log(response.message)
            response.log = self.logger.get_log()
        return response

    def proto_provision(self, user_inputs):
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
                interface="I2C",
                address="0x6C",
                devtype=cal.ATCADeviceType.ATECC608,
            )
            self.load_secret_key(self.enc_slot, self.enc_key)
            self.logger.log(f"Success loading IO Key into slot: {self.enc_slot: 02X}")
            self.load_secret_key(
                self.symm_slot, self.symm_key, self.enc_slot, self.enc_key
            )
            self.logger.log(
                f"Success loading Secret Key into slot: {self.symm_slot: 02X}"
            )
            response.status = True
            response.message = "Proto Provision Success"
        except Exception as e:
            response.message = f"Proto Provision failed with: {e}"
        finally:
            os.chdir(current_dir)
            self.logger.log(response.message)
            response.log = self.logger.get_log()
        return response

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

    def fw_resources(self, key: bytes, var: str):
        """
        Generates a C header file with the given variable name and key data.

        Args:
            key (bytes): The binary data to be included in the C array.
            var (str): The name of the variable to be used in the header file.
        """
        with open(f"{var}.h", "w") as f:
            f.write(f"\n#ifndef _{var.upper()}_H\n")
            f.write(f"#define _{var.upper()}\n")
            f.write("\n#ifdef __cplusplus\n")
            f.write('extern "C" {\n')
            f.write("#endif\n\n")
            f.write(get_c_array(var, key))
            f.write("#ifdef __cplusplus\n")
            f.write("}\n")
            f.write("#endif\n")
            f.write("#endif\n")

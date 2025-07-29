# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

import os
from typing import Any, Union
from ..helper.defines import KeySize
from ..helper.keys import load_symmetric_key


class SymmAuth:
    """
    A class used to handle symmetric authentication operations.

    Attributes
    ----------
    dev_inst : Any
        The device instance used for loading the symmetric key.
    symm_bytes : bytes or None
        The symmetric key bytes.

    Methods
    -------
    generate_symmetric_key(key: Union[str, os.PathLike, None] = "", key_size: KeySize = KeySize.AES128)
        Generates or loads a symmetric key from a PEM file or generates a new one based on the specified key size.

    load_asset(asset: str, asset_handler: Any)
        Loads the specified asset into the device instance using the provided asset handler.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initializes the SymmAuth class with optional keyword arguments.

        Args:
            **kwargs: Arbitrary keyword arguments.
                - dev_inst: Optional; The device instance to be used. Defaults to None.

        Attributes:
            dev_inst: The device instance provided in the keyword arguments or None if not provided.
            symm_bytes: Initialized to None.
        """
        self.dev_inst = kwargs.get("dev_inst", None)
        self.symm_bytes = None

    def generate_symmetric_key(
        self,
        key: Union[bytes, bytearray, os.PathLike, None] = None,
        key_size: KeySize = KeySize.AES128,
    ) -> None:
        self.symm_bytes = load_symmetric_key(key, key_size)

    def load_asset(self, asset: str, asset_handler: Any) -> None:
        """
        Loads the specified asset using the provided asset handler.

        Args:
            asset (str): The name of the asset to be loaded.
            asset_handler (Any): The handler function or method to load the asset.

        Raises:
            AssertionError: If the asset is not an attribute of the class.
            AssertionError: If the asset is not loaded or generated.
            AssertionError: If the device instance is not available.
            AssertionError: If the asset handler is not an attribute of the device instance.
            AssertionError: If loading the asset fails, with the status code.

        """
        assert hasattr(self, asset), f"{asset} is not an attribute in the class"
        assert getattr(self, asset), f"{asset} should be loaded / generated first"
        assert self.dev_inst, "Device instance is required to load symmetric key"
        assert getattr(self.dev_inst, asset_handler), f"{asset_handler} is not an attribute in device instance"
        status = getattr(self.dev_inst, asset_handler)(getattr(self, asset))
        assert status == 0, f"Loading of {asset} has failed with {status: 02X}"

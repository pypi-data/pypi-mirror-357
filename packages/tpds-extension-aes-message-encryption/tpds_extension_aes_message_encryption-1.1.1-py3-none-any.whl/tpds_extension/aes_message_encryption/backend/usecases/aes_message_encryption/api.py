# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

from fastapi.routing import APIRouter
from fastapi import Body
from .aes_message_encryption import AesMessageEncryption
from ...api.model import UsecaseResponseModel

aes_msg_enc_router = APIRouter(
    prefix="/aes_message_encryption", tags=["aes_message_encryption_APIs"]
)
uc_object = None


@aes_msg_enc_router.post("/setup")
def setup():
    """
    Sets up AES Message Encryption usecase.

    Returns:
        UsecaseResponseModel: An instance of UsecaseResponseModel indicating the status, message, and log of the setup process.
    """
    global uc_object
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        uc_object = AesMessageEncryption()
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response


@aes_msg_enc_router.post("/generate_resources")
def generate_resources(user_inputs=Body()):
    """
    Generate AES Message Encryption resources based on user inputs.

    Args:
        user_inputs (dict): The input data provided by the user, expected to be in the form of a dictionary.

    Returns:
        UsecaseResponseModel: The response model containing the result of AES Message Encryption resources generation.
    """
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        assert uc_object is not None, "AES Message Encryption usecase object is not initialized. Please restart usecase!"
        response = uc_object.generate_resources(user_inputs)
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response


@aes_msg_enc_router.post("/proto_provision")
def proto_provision(user_inputs=Body()):
    """
    Provisions AES Message Encryption protocol for the given user inputs.

    Args:
        user_inputs (Body): The user inputs required for provisioning the AES Message Encryption.

    Returns:
        UsecaseResponseModel: The response model containing the result of the provisioning process.
    """
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        assert uc_object is not None, "AES Message Encryption usecase object is not initialized. Please restart usecase!"
        response = uc_object.proto_provision(user_inputs)
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response


@aes_msg_enc_router.post("/teardown")
def teardown():
    """
    Teardown function for AES Message Encryption.

    This function performs the necessary cleanup for AES Message Encryption
    and returns a UsecaseResponseModel indicating the status of the operation.

    Returns:
        UsecaseResponseModel: An object containing the status, message, and log
        of the teardown operation.
    """
    global uc_object
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        assert uc_object is not None, "AES Message Encryption usecase object is not initialized. Teardown failed!"
        uc_object.logger.close()
        uc_object = None
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response

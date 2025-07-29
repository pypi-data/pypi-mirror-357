# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

from fastapi.routing import APIRouter
from ..usecases.aes_message_encryption.api import aes_msg_enc_router

usecase = APIRouter()
usecase.include_router(aes_msg_enc_router)

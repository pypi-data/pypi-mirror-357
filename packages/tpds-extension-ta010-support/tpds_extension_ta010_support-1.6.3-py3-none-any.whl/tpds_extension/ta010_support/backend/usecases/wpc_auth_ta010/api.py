# This file is governed by the terms outlined in the LICENSE file located in the root directory of
#  this repository. Please refer to the LICENSE file for comprehensive information.

from fastapi.routing import APIRouter
from fastapi import Body
from .wpc_auth import TA010WPCAuth
from ...api.model import UsecaseResponseModel

wpc_auth_ta010_router = APIRouter(
    prefix="/wpc_auth_ta010", tags=["TA010_WPC_AUTH_APIs"]
)
uc_object = None


@wpc_auth_ta010_router.post("/setup")
def setup():
    """
    Sets up TA010 WPC Authentication usecase.

    Returns:
        UsecaseResponseModel: An instance of UsecaseResponseModel indicating the status, message, and log of the setup process.
    """
    global uc_object
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        uc_object = TA010WPCAuth()
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response


@wpc_auth_ta010_router.post("/generate_resources")
def generate_resources(user_inputs=Body()):
    """
    Generate TA010 WPC Authentication resources based on user inputs.

    Args:
        user_inputs (dict): The input data provided by the user, expected to be in the form of a dictionary.

    Returns:
        UsecaseResponseModel: The response model containing the result of TA010 WPC Authentication resources generation.
    """
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        assert (
            uc_object is not None
        ), "TA010 WPC Authentication usecase object is not initialized. Please restart usecase!"
        response = uc_object.generate_resources(user_inputs)
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response


@wpc_auth_ta010_router.post("/proto_provision")
def proto_provision(user_inputs=Body()):
    """
    Provisions TA010 WPC Authentication protocol for the given user inputs.

    Args:
        user_inputs (Body): The user inputs required for provisioning the TA010 WPC Authentication.

    Returns:
        UsecaseResponseModel: The response model containing the result of the provisioning process.
    """
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        assert (
            uc_object is not None
        ), "TA010 WPC Authentication usecase object is not initialized. Please restart usecase!"
        response = uc_object.proto_provision(user_inputs)
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response


@wpc_auth_ta010_router.post("/teardown")
def teardown():
    """
    Teardown function for TA010 WPC Authentication.

    This function performs the necessary cleanup for TA010 WPC Authentication
    and returns a UsecaseResponseModel indicating the status of the operation.

    Returns:
        UsecaseResponseModel: An object containing the status, message, and log
        of the teardown operation.
    """
    global uc_object
    try:
        response = UsecaseResponseModel(status=True, message="", log="")
        assert (
            uc_object is not None
        ), "TA010 WPC Authentication usecase object is not initialized. Teardown failed!"
        uc_object.logger.close()
        uc_object = None
    except Exception as e:
        response.status = False
        response.message = str(e)
    return response

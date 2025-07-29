from fastapi.routing import APIRouter
from ecc204_support.api.models import ConfiguratorMessageReponse, TFLXAUTHConfiguratorMessage, TFLXWPCConfiguratorMessage
from ecc204_support.api.tflxauth_ecc204 import ECC204TFLXAuthPackage, ecc204_tflxauth_proto_prov_handle
from ecc204_support.api.tflxwpc_ecc204 import ECC204TFLXWPCPackage, ecc204_tflxwpc_proto_prov_handle
from ..usecases import symm_auth_ta010_router, asymm_auth_ta010_router, wpc_auth_ta010_router

router = APIRouter(prefix="/ta010", tags=["TA010_APIs"])
router.include_router(symm_auth_ta010_router)
router.include_router(asymm_auth_ta010_router)
router.include_router(wpc_auth_ta010_router)


@router.post('/generate_tflxauth_xml', response_model=ConfiguratorMessageReponse)
def generate_tflxauth_xml(config_string: TFLXAUTHConfiguratorMessage):
    resp = ECC204TFLXAuthPackage(config_string.json(), "TA010_TFLXAUTH")
    return resp.get_response()


@router.post('/provision_tflxauth_device')
def provision_tflxauth_device(config_string: TFLXAUTHConfiguratorMessage) -> None:
    resp = ecc204_tflxauth_proto_prov_handle(config_string.json(), "TA010_TFLXAUTH")
    return resp


@router.post('/generate_tflxwpc_xml', response_model=ConfiguratorMessageReponse)
def generate_tflxwpc_xml(config_string: TFLXWPCConfiguratorMessage):
    resp = ECC204TFLXWPCPackage(config_string.json(), "TA010_TFLXWPC")
    return resp.get_response()


@router.post('/provision_tflxwpc_device')
def provision_tflxwpc_device(config_string: TFLXWPCConfiguratorMessage) -> None:
    resp = ecc204_tflxwpc_proto_prov_handle(config_string.json(), "TA010_TFLXWPC")
    return resp

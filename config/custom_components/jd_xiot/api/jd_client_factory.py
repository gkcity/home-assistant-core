"""JingDong Client Factory."""

from homeassistant.core import HomeAssistant

from .jd_client import JingDongClient
from .jd_client_account import JingdongClientAccountImpl
from .jd_client_account_with_signature import JingdongClientAccountWithSignatureImpl
from .jd_client_local import JingDongClientLocalImpl
from .jd_config_data import JdConfigData


def create_jd_client(hass: HomeAssistant, data: JdConfigData) -> JingDongClient:
    """Create Jingdong Client."""
    match data.auth_type:
        case "screen":
            return JingDongClientLocalImpl(hass = hass, data = data)

        case "account":
            return JingdongClientAccountImpl(hass = hass, data = data)

        case "account-with-signature":
            return JingdongClientAccountWithSignatureImpl(hass = hass, data = data)

        case _:
            return JingDongClientLocalImpl(hass = hass, data= data)

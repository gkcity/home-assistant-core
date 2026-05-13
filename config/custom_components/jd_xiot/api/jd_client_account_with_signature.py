"""JingDong Client Account implementation."""

import logging
import time

from aiohttp import ClientError, ClientResponse
from xiot_core.spec.typedef.operation.action_operation import ActionOperation
from xiot_core.spec.typedef.operation.property_operation import PropertyOperation

from homeassistant.core import HomeAssistant

from .color.color_signer import generate_signature
from .jd_client import JingDongClient
from .jd_config_data import JdConfigData
from .typedef.joy_device_detail import JoyDeviceDetail
from .typedef.joy_house import JoyHouse, joy_house_decode_array

_LOGGER = logging.getLogger(__name__)

class JingdongClientAccountWithSignatureImpl(JingDongClient):
    """JingDong Client Account implementation."""

    def __init__(self, hass: HomeAssistant, data: JdConfigData) -> None:
        """Initialize the API client."""
        super().__init__(hass, data)

    async def async_get_houses(self) -> tuple[bool, list[JoyHouse]]:
        """Get Houses."""
        try:
            resp = await self.__get("smarthome_screen_getHouseInfo", {})
            if resp.status != 200:
                _LOGGER.error("Error get houses, status: %s", resp.status)
                return False, []

            data = await resp.json(content_type=None)
            if data.get("code") != 0:
                _LOGGER.error("Error get houses: %s", data)
                return False, []

            houses: list[JoyHouse] = joy_house_decode_array(data.get("data", {}).get("houses", []))
        except ClientError as e:
            _LOGGER.error("Error get houses: %s", e)
            return False, []
        else:
            return True, houses

    async def async_get_devices(self) -> list[JoyDeviceDetail]:
        """Get Devices."""
        return []

    async def async_get_devices_info(self, deviceIds: list[str]) -> list[JoyDeviceDetail]:
        """Get Device."""
        return []

    async def set_property(self, p: PropertyOperation) -> PropertyOperation:
        """Set Property."""
        return p

    async def get_property(self, p: PropertyOperation) -> PropertyOperation:
        """Get Property."""
        return p

    async def invoke_action(self, a: ActionOperation) -> ActionOperation:
        """Invoke Action."""
        return a

    async def __get(self, function_id: str, arguments: dict[str, str]) -> ClientResponse:
        """Make an HTTP request with the cookie."""

        params: dict[str, str] = {}
        params["functionId"] = function_id
        params["appid"] = "AIPC"
        params["t"] = str(int(time.time() * 1000))

        # 字典合并
        params = {**params, **arguments}

        params["loginType"] = "10"

        params["sign"] = generate_signature(params, "d00bb53524514c97b8c050307f4391ab")

        headers: dict[str, str] = {}
        headers["Cookie"] = self.data.account_cookie

        url = "https://api.m.jd.com/api"

        # for key, value in params.items():
        #     _LOGGER.info("%s: %s", key, value)

        return await self.session.request(method = "get", url = url, params = params, headers = headers)

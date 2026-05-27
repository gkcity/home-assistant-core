"""JingDong Client Account implementation."""

import json
import logging
import time
from urllib.parse import quote

from aiohttp import ClientError, ClientResponse
from xiot_core.spec.codec.operation.action_operation_codec import ActionOperationCodec
from xiot_core.spec.codec.operation.property_operation_codec import (
    PropertyOperationCodec,
)
from xiot_core.spec.typedef.operation.action_operation import ActionOperation
from xiot_core.spec.typedef.operation.property_operation import PropertyOperation
from xiot_core.spec.typedef.status.status import Status

from homeassistant.core import HomeAssistant

from .color.color_signer import generate_signature
from .jd_client import JingDongClient
from .jd_config_data import JdConfigData
from .typedef.joy_device_detail import (
    JoyDeviceDetail,
    joy_device_detail_decode_array_from_cloud,
)
from .typedef.joy_house import JoyHouse, get_all_user_device_ids, joy_house_decode_array

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
        valid, houses = await self.async_get_houses()
        if valid and houses:
            house = next((h for h in houses if h["id"] == self.data.account_house_id), None)
            if house is not None:
                return await self.__async_get_devices_by_house(self.data.account_cookie, house)
            _LOGGER.error("GetHouse Failed, House not exist!")
            return []

        _LOGGER.error("GetHouses Failed!")
        return []

    async def async_get_devices_info(self, deviceIds: list[str]) -> list[JoyDeviceDetail]:
        """Get Device."""
        devices: list[JoyDeviceDetail] = await self.async_get_devices()
        return [d for d in devices if d["did"] in deviceIds]

    async def set_property(self, p: PropertyOperation) -> PropertyOperation:
        """Set Property."""
        body_dict = {
            "userDeviceId": p.context,
            "properties": PropertyOperationCodec.Set.QUERY.encode([p]),
        }
        body_json = json.dumps(body_dict, separators=(",", ":"))
        _LOGGER.debug("SetProperty: %s", body_json)

        body_encoded = quote(body_json)  # URL 编码

        try:
            resp = await self.__get("smarthome_app_writeDeviceProperty", { "body" : body_encoded})
            if resp.status != 200:
                _LOGGER.error("Error SetProperty, status: %s", resp.status)
                p.status = Status.INTERNAL_ERROR
                p.description = "status error: " + resp.status
                return p

            data = await resp.json(content_type=None)
            _LOGGER.debug("SetProperty.Response: %s", data)

            if data.get("code") != "0":
                _LOGGER.error("Error SetProperty: %s", data)
                p.status = Status.INTERNAL_ERROR
                p.description = "code: " + data.get("code")
                return p

            properties: list[PropertyOperation] = (
                PropertyOperationCodec.Set.RESULT.decode(
                    data.get("result", {}).get("properties", [])
                )
            )

            result: PropertyOperation | None = properties[0]
            if result is None:
                p.status = Status.UNDEFINED
                p.description = "result is empty"
                return p
        except ClientError as e:
            _LOGGER.error("Error SetProperty: %s", e)
            p.status = Status.UNDEFINED
            p.description = "ClientError"
            return p
        else:
            return result

    async def get_property(self, p: PropertyOperation) -> PropertyOperation:
        """Get Property from cloud."""
        body_dict = {
            "userDeviceId": p.context,
            "pids": PropertyOperationCodec.Get.QUERY.encode([p]),
        }
        body_json = json.dumps(body_dict, separators=(",", ":"))
        _LOGGER.debug("GetProperty: %s", body_json)

        body_encoded = quote(body_json)  # URL 编码

        try:
            resp = await self.__get("smarthome_app_debug_getProperties", { "body" : body_encoded})
            if resp.status != 200:
                _LOGGER.error("Error SetProperty, status: %s", resp.status)
                p.status = Status.INTERNAL_ERROR
                p.description = "status error: " + resp.status
                return p

            data = await resp.json(content_type=None)
            _LOGGER.debug("SetProperty.Response: %s", data)

            if data.get("code") != "0":
                _LOGGER.error("Error SetProperty: %s", data)
                p.status = Status.INTERNAL_ERROR
                p.description = "code: " + data.get("code")
                return p

            properties: list[PropertyOperation] = (
                PropertyOperationCodec.Get.RESULT.decode(
                    data.get("result", {}).get("properties", [])
                )
            )

            result: PropertyOperation | None = properties[0]
            if result is None:
                p.status = Status.UNDEFINED
                p.description = "result is empty"
                return p
        except ClientError as e:
            _LOGGER.error("Error SetProperty: %s", e)
            p.status = Status.UNDEFINED
            p.description = "ClientError"
            return p
        else:
            return result

    async def invoke_action(self, a: ActionOperation) -> ActionOperation:
        """Invoke Action."""
        body_dict = {
            "userDeviceId": a.context,
            "actions": ActionOperationCodec.QUERY.encode([a]),
        }
        body_json = json.dumps(body_dict, separators=(",", ":"))
        _LOGGER.debug("InvokeAction: %s", body_json)

        body_encoded = quote(body_json)  # URL 编码

        try:
            resp = await self.__get("smarthome_app_invokeDeviceAction", { "body" : body_encoded})
            if resp.status != 200:
                _LOGGER.error("Error InvokeAction, status: %s", resp.status)
                a.status = Status.INTERNAL_ERROR
                a.description = "status error: " + resp.status
                return a

            data = await resp.json(content_type=None)
            _LOGGER.debug("InvokeAction.Response: %s", data)

            if data.get("code") != "0":
                _LOGGER.error("Error InvokeAction: %s", data)
                a.status = Status.INTERNAL_ERROR
                a.description = "code: " + data.get("code")
                return a

            actions: list[ActionOperation] = (
                ActionOperationCodec.RESULT.decode(
                    data.get("result", {}).get("actions", [])
                )
            )

            result: ActionOperation | None = actions[0]
            if result is None:
                a.status = Status.UNDEFINED
                a.description = "result is empty"
                return a
        except ClientError as e:
            _LOGGER.error("Error InvokeAction: %s", e)
            a.status = Status.UNDEFINED
            a.description = "ClientError"
            return a
        else:
            return result

    async def __async_get_devices_by_house(self, cookie: str, house: JoyHouse) -> list[JoyDeviceDetail]:
        """Get device list under a specific house."""

        device_ids: list[int]  = get_all_user_device_ids(house)
        if len(device_ids) == 0:
            return []

        body_dict = {"userDeviceIds": device_ids}
        body_json = json.dumps(body_dict, separators=(",", ":"))
        _LOGGER.debug("GetDevices: %s", body_json)

        body_encoded = quote(body_json)  # URL 编码

        try:
            resp = await self.__get("smarthome_screen_getDeviceInfo", { "body" : body_encoded})
            if resp.status != 200:
                _LOGGER.error("Error GetDevices, status: %s", resp.status)
                return []

            data = await resp.json(content_type=None)
            _LOGGER.debug("GetDevices.Response: %s", data)

            if data.get("code") != 0:
                _LOGGER.error("Error GetDevices: %s", data)
                return []

            devices: list[JoyDeviceDetail] = joy_device_detail_decode_array_from_cloud(
                data.get("data", {}).get("devices", [])
            )
            _LOGGER.debug("Devices.length: %d", len(devices))
        except ClientError as e:
            _LOGGER.error("Error GetDevices: %s", e)
            return []
        else:
            return devices

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

"""JingDong Client Account implementation."""

import json
import logging
from urllib.parse import quote

from aiohttp import ClientError, ClientResponse
from xiot_core.spec.codec.operation.action_operation_codec import ActionOperationCodec
from xiot_core.spec.codec.operation.property_operation_codec import (
    PropertyOperationCodec,
)
from xiot_core.spec.typedef.operation.action_operation import ActionOperation
from xiot_core.spec.typedef.operation.property_operation import PropertyOperation
from xiot_core.spec.typedef.status.status import Status

from .jd_client import JingDongClient
from .typedef.joy_device_detail import (
    JoyDeviceDetail,
    joy_device_detail_decode_array_from_cloud,
)
from .typedef.joy_house import JoyHouse, get_all_user_device_ids, joy_house_decode_array

_LOGGER = logging.getLogger(__name__)

class JingdongClientAccountImpl(JingDongClient):
    """JingDong Client Account implementation."""

    async def async_get_houses(self) -> tuple[bool, list[JoyHouse]]:
        """Get Houses from Cloud API."""
        headers = {"Cookie": self.data.account_cookie}
        try:
            async with self.session.get(
                    "https://api.m.jd.com/api?functionId=smarthome_screen_getHouseInfo&appid=device-debugger",
                    headers=headers,
            ) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if data.get("code") == 0:
                        houses = joy_house_decode_array(
                            data.get("data", {}).get("houses", [])
                        )
                        return True, houses
                return False, []
        except ClientError as e:
            _LOGGER.error("Error get houses: %s", e)
            return False, []

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
        _LOGGER.debug("SetProperty to cloud: %s", body_json)
        body_encoded = quote(body_json)  # URL 编码
        url = (
                "https://api.m.jd.com/api?functionId=smarthome_app_writeDeviceProperty&appid=device-debugger&body="
                + body_encoded
        )
        resp = await self.__request("get", url)
        data = await resp.json(content_type=None)
        _LOGGER.debug("SetProperty.Response: %s", data)
        if data.get("code") == "0":
            properties: list[PropertyOperation] = (
                PropertyOperationCodec.Set.RESULT.decode(
                    data.get("result", {}).get("properties", [])
                )
            )
            result: PropertyOperation | None = properties[0]
            if result is not None:
                return result
            p.status = Status.UNDEFINED
            p.description = "result is empty"
        else:
            p.status = Status.INTERNAL_ERROR
            p.description = "result error"
        return p

    async def get_property(self, p: PropertyOperation) -> PropertyOperation:
        """Get Property from cloud."""
        body_dict = {
            "userDeviceId": p.context,
            "pids": PropertyOperationCodec.Get.QUERY.encode([p]),
        }
        body_json = json.dumps(body_dict, separators=(",", ":"))
        _LOGGER.debug("GetProperty from Cloud: %s", body_json)
        body_encoded = quote(body_json)  # URL 编码
        url = (
                "https://api.m.jd.com/api?functionId=smarthome_app_debug_getProperties&appid=device-debugger&body="
                + body_encoded
        )
        resp = await self.__request("get", url)
        data = await resp.json(content_type=None)
        _LOGGER.debug("GetProperty.Response: %s", data)
        if data.get("code") == "0":
            properties: list[PropertyOperation] = (
                PropertyOperationCodec.Get.RESULT.decode(
                    data.get("result", {}).get("properties", [])
                )
            )
            result: PropertyOperation | None = properties[0]
            if result is not None:
                return result
            p.status = Status.UNDEFINED
            p.description = "result is empty"
        else:
            p.status = Status.INTERNAL_ERROR
            p.description = "result error"
        return p

    async def invoke_action(self, a: ActionOperation) -> ActionOperation:
        """Invoke Action."""
        _LOGGER.info("Invoke Action to Cloud")
        body_dict = {
            "userDeviceId": a.context,
            "actions": ActionOperationCodec.QUERY.encode([a]),
        }
        body_json = json.dumps(body_dict, separators=(",", ":"))
        _LOGGER.debug("InvokeAction: %s", body_json)
        body_encoded = quote(body_json)  # URL 编码
        url = (
                "https://api.m.jd.com/api?functionId=smarthome_app_invokeDeviceAction&appid=device-debugger&body="
                + body_encoded
        )
        resp = await self.__request("get", url)
        data = await resp.json(content_type=None)
        _LOGGER.debug("InvokeAction.Response: %s", data)
        if data.get("code") == "0":
            actions: list[ActionOperation] = (
                ActionOperationCodec.RESULT.decode(
                    data.get("result", {}).get("actions", [])
                )
            )
            result: ActionOperation | None = actions[0]
            if result is not None:
                return result
            a.status = Status.UNDEFINED
            a.description = "result is empty"
        else:
            a.status = Status.INTERNAL_ERROR
            a.description = "result error"
        return a

    async def __async_get_devices_by_house(self, cookie: str, house: JoyHouse) -> list[JoyDeviceDetail]:
        """Get device list under a specific house."""
        headers = {"Cookie": cookie}
        body_dict = {"userDeviceIds": get_all_user_device_ids(house)}
        body_json = json.dumps(body_dict, separators=(",", ":"))
        body_encoded = quote(body_json)  # URL 编码
        url = (
                "https://api.m.jd.com/api?functionId=smarthome_screen_getDeviceInfo&appid=device-debugger&body="
                + body_encoded
        )
        try:
            async with self.session.get(url=url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if data.get("code") == 0:
                        devices: list[JoyDeviceDetail] = joy_device_detail_decode_array_from_cloud(
                            data.get("data", {}).get("devices", [])
                        )
                        _LOGGER.debug("Devices.length: %d", len(devices))
                        return devices
                    _LOGGER.error(
                        "GetDevicesByHouse, code: %d, message: %s",
                        data.get("code"),
                        data.get("message"),
                    )
                else:
                    _LOGGER.debug("Status: %d", resp.status)
                return []
        except ClientError as e:
            _LOGGER.error("Error get devices by house: %s", e)
            return []

    async def __request(self, method: str, url: str, **kwargs) -> ClientResponse:
        """Make an HTTP request with the cookie."""
        headers = kwargs.pop("headers", {})

        if self.data is not None:
            headers["Cookie"] = self.data.account_cookie
        else:
            _LOGGER.error("Cookie is None")

        kwargs["headers"] = headers
        return await self.session.request(method, url, **kwargs)

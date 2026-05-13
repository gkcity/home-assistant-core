"""JingDong Client."""

import json
import logging
from urllib.parse import quote

from aiohttp import ClientError, ClientResponse, ClientSession, ClientTimeout
from xiot_core.spec.codec.operation.action_operation_codec import ActionOperationCodec
from xiot_core.spec.codec.operation.property_operation_codec import (
    PropertyOperationCodec,
)
from xiot_core.spec.typedef.operation.action_operation import ActionOperation
from xiot_core.spec.typedef.operation.property_operation import PropertyOperation
from xiot_core.spec.typedef.status.status import Status

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .const import JD_AUTH_TYPE_SCREEN
from .jd_config_data import JdConfigData
from .typedef.joy_device_detail import (
    JoyDeviceDetail,
    joy_device_detail_decode_array,
    joy_device_detail_decode_array_local,
)
from .typedef.joy_house import JoyHouse, get_all_user_device_ids, joy_house_decode_array

_LOGGER = logging.getLogger(__name__)


class JingDongClient:
    """JingDong Client Session."""

    def __init__(
        self, hass: HomeAssistant, cookie: str | None = None, data: JdConfigData | None = None, session: ClientSession | None = None
    ) -> None:
        """Initialize the API client."""
        self._hass = hass
        self._data: JdConfigData | None = data
        self._timeout = ClientTimeout(connect=3.0, sock_read=3.0, total=6.0)
        if session is None:
            _LOGGER.info("Initialize a new session")
            self._session = aiohttp_client.async_get_clientsession(hass)
        else:
            _LOGGER.info("Use existing session")
            self._session = session

    @property
    def data(self) -> JdConfigData | None:
        """Get Config Data."""
        return self._data

    async def _request(self, method: str, url: str, **kwargs) -> ClientResponse:
        """Make an HTTP request with the cookie."""
        headers = kwargs.pop("headers", {})

        if self._data is not None:
            headers["Cookie"] = self._data.account_cookie
        else:
            _LOGGER.error("Cookie is None")

        kwargs["headers"] = headers
        return await self._session.request(method, url, **kwargs)

    async def async_test(self) -> tuple[bool, list[JoyHouse]]:
        """Get house list."""
        url = "https://api.m.jd.com/api?functionId=smarthome_screen_getHouseInfo&appid=device-debugger"
        resp = await self._request("get", url)
        data = await resp.json(content_type=None)
        if data.get("code") == 0:
            houses = joy_house_decode_array(data.get("data", {}).get("houses", []))
            return True, houses
        return False, []

    # 实现调用京东 API 获取房屋列表，并验证 Cookie
    # 返回 (True, [{"id": "xxx", "name": "我家"}, ...]) 或 (False, [])
    async def async_get_houses(self, cookie: str, signature: bool) -> tuple[bool, list[JoyHouse]]:
        """Get Houses from Cloud API."""
        headers = {"Cookie": cookie}
        try:
            async with self._session.get(
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
        """Get Devices from Cloud or Local."""
        if self._data is None:
            return []

        if self._data.auth_type == "screen":
            return await self.async_get_devices_by_local(self._data.screen_ip)

        valid, houses = await self.async_get_houses(self._data.account_cookie, False)
        if valid and houses:
            house = next((h for h in houses if h["id"] == self._data.account_house_id), None)
            if house is not None:
                return await self.async_get_devices_by_house(self._data.account_cookie, house, False)
            _LOGGER.error("GetHouse Failed, House not exist!")
            return []

        _LOGGER.error("GetHouses Failed!")
        return []


    async def async_get_devices_by_house(self, cookie: str, house: JoyHouse, signature: bool) -> list[JoyDeviceDetail]:
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
            async with self._session.get(url=url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if data.get("code") == 0:
                        devices: list[JoyDeviceDetail] = joy_device_detail_decode_array(
                            data.get("data", {}).get("devices", [])
                        )
                        _LOGGER.info("Devices.length: %d", len(devices))
                        return devices
                    _LOGGER.error(
                        "GetDevicesByHouse, code: %d, message: %s",
                        data.get("code"),
                        data.get("message"),
                    )
                else:
                    _LOGGER.info("Status: %d", resp.status)
                return []
        except ClientError as e:
            _LOGGER.error("Error get devices by house: %s", e)
            return []

    # GET http://10.10.10.141:8080/device/v1/devices
    async def async_get_devices_by_local(self, ip: str) -> list[JoyDeviceDetail]:
        """Get Devices from Central Screen."""
        _LOGGER.info("Get Devices By Local: %s", ip)
        url = f'http://{ip}:8080/device/v1/devices'
        try:
            async with self._session.get(url = url, timeout = self._timeout) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if data.get("msg") == 'ok':
                        devices: list[JoyDeviceDetail] = joy_device_detail_decode_array_local(data.get("data", []))
                        _LOGGER.info("Devices.length: %d", len(devices))
                        return devices
                    _LOGGER.error("Get Device By Local: %s", data.get("msg", ""))
                else:
                    _LOGGER.info("Status: %d", resp.status)
                return []
        except ClientError as e:
            _LOGGER.error("Error get devices by local: %s", e)
            return []

    async def async_get_device_by_house(self, cookie: str, house: JoyHouse) -> list[JoyDeviceDetail]:
        """Get Devices from Cloud API."""
        _LOGGER.info("Get Device By House")
        headers = {"Cookie": cookie}
        body_dict = {"userDeviceIds": get_all_user_device_ids(house)}
        body_json = json.dumps(body_dict, separators=(",", ":"))
        body_encoded = quote(body_json)  # URL 编码
        url = (
            "https://api.m.jd.com/api?functionId=smarthome_screen_getDeviceInfo&appid=device-debugger&body="
            + body_encoded
        )
        try:
            async with self._session.get(url=url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if data.get("code") == 0:
                        devices: list[JoyDeviceDetail] = joy_device_detail_decode_array(
                            data.get("data", {}).get("devices", [])
                        )
                        _LOGGER.info("Devices.length: %d", len(devices))
                        return devices
                    _LOGGER.error(
                        "GetDevicesByHouse, code: %d, message: %s",
                        data.get("code"),
                        data.get("message"),
                    )
                else:
                    _LOGGER.info("Status: %d", resp.status)
                return []
        except ClientError as e:
            _LOGGER.error("Error get devices by house: %s", e)
            return []

    async def async_get_devices_info(self, deviceIds: list[str]) -> list[JoyDeviceDetail]:
        """Get devices info."""
        return await self.async_get_devices_info_local(deviceIds)

    async def async_get_devices_info_local(self, deviceIds: list[str]) -> list[JoyDeviceDetail]:
        """Get devices info from local."""

        if self._data is None:
            _LOGGER.error("GetDevicesInfo, data is None")
            return []

        devices: list[JoyDeviceDetail] = await self.async_get_devices_by_local(self._data.screen_ip)
        device_ids_set = set(deviceIds)
        return [d for d in devices if d['did'] in device_ids_set]

    async def set_property(self, p: PropertyOperation) -> PropertyOperation:
        """Set Property."""
        if self._data is None:
            _LOGGER.error("set_property error, data is None")
            p.status = -1000
            p.description = "data is None"
            return p

        if self._data.auth_type == JD_AUTH_TYPE_SCREEN:
            return await self._set_property_local(p)
        return await self._set_property_local(p)

    async def _set_property_local(self, p: PropertyOperation) -> PropertyOperation:
        """Set Property to Local."""
        try:
            # 1. 编码得到字典后，转为JSON字符串
            body_dict = PropertyOperationCodec.Set.QUERY.encode([p])
            body_json = json.dumps(body_dict, separators=(",", ":"))
            _LOGGER.info("SetProperty.Request: %s", body_json)
            url = f'http://{self._data.screen_ip}:8080/device/v1/properties'
            # 2. 设置JSON请求头 + 传入字符串类型的body
            headers = {"Content-Type": "application/json"}
            async with self._session.put(url=url, data = body_json, headers = headers, timeout = self._timeout) as resp:
                data = await resp.json(content_type=None)
                _LOGGER.info("SetProperty.Response: %s", data)
                if data.get("msg", "error") == "ok":
                    properties: list[PropertyOperation] = PropertyOperationCodec.Set.RESULT.decode(data.get("data", []))
                    result: PropertyOperation | None = properties[0]
                    if result is not None:
                        return result
                    p.status = Status.UNDEFINED
                    p.description = "result is empty"
                else:
                    p.status = Status.INTERNAL_ERROR
                    p.description = "result error"
                return p
        except ClientError as e:
            # 3. 补充网络异常捕获
            _LOGGER.error("SetProperty Local Network Error: %s", e)
            p.status = Status.INTERNAL_ERROR
            p.description = f"network error: {e!s}"
        return p

    async def _set_property_cloud(self, p: PropertyOperation) -> PropertyOperation:
        """Set Property to Cloud."""
        body_dict = {
            "userDeviceId": p.context,
            "properties": PropertyOperationCodec.Set.QUERY.encode([p]),
        }
        body_json = json.dumps(body_dict, separators=(",", ":"))
        _LOGGER.info("_set_property_cloud: %s", body_json)
        body_encoded = quote(body_json)  # URL 编码
        url = (
            "https://api.m.jd.com/api?functionId=smarthome_app_writeDeviceProperty&appid=device-debugger&body="
            + body_encoded
        )
        resp = await self._request("get", url)
        data = await resp.json(content_type=None)
        _LOGGER.info("SetProperty.Response: %s", data)
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
        """Get Property."""

        if self._data is None:
            _LOGGER.error("get_property error, data is None")
            p.status = -1000
            p.description = "data is None"
            return p

        if self._data.auth_type == JD_AUTH_TYPE_SCREEN:
            return await self._get_property_local(p)
        return await self._get_property_cloud(p)

    async def _get_property_local(self, p: PropertyOperation) -> PropertyOperation:
        """Get Property from local."""
        _LOGGER.info("Get Property from Local")
        try:
            pid = str(p.pid)
            _LOGGER.info("GetProperty.Request: %s", pid)
            url = f'http://{self._data.screen_ip}:8080/device/v1/properties?pid={quote(pid)}'
            headers = {"Content-Type": "application/json"}
            async with self._session.get(url=url, headers = headers, timeout = self._timeout) as resp:
                data = await resp.json(content_type=None)
                _LOGGER.info("GetProperty.Response: %s", data)
                if data.get("msg", "error") == "ok":
                    properties: list[PropertyOperation] = PropertyOperationCodec.Get.RESULT.decode(data.get("data", []))
                    result: PropertyOperation | None = properties[0]
                    if result is not None:
                        return result
                    p.status = Status.UNDEFINED
                    p.description = "result is empty"
                else:
                    p.status = Status.INTERNAL_ERROR
                    p.description = "result error"
                return p
        except ClientError as e:
            # 3. 补充网络异常捕获
            _LOGGER.error("GetProperty Local Network Error: %s", e)
            p.status = Status.INTERNAL_ERROR
            p.description = f"network error: {e!s}"
        return p

    async def _get_property_cloud(self, p: PropertyOperation) -> PropertyOperation:
        """Get Property from cloud."""
        _LOGGER.info("Get Property from Cloud")
        p.status = -1
        p.description = "not implemented"
        return p

    async def invoke_action(self, p: ActionOperation) -> ActionOperation:
        """Invoke Action."""
        if self._data is None:
            _LOGGER.error("invoke_action error, data is None")
            p.status = -1000
            p.description = "data is None"
            return p

        if self._data.auth_type == JD_AUTH_TYPE_SCREEN:
            return await self._invoke_action_local(p)
        return await self._invoke_action_cloud(p)

    async def _invoke_action_local(self, a: ActionOperation) -> ActionOperation:
        """Invoke Action to local."""
        try:
            # 1. 编码得到字典后，转为JSON字符串
            body_dict = ActionOperationCodec.QUERY.encode([a])
            body_json = json.dumps(body_dict, separators=(",", ":"))
            _LOGGER.info("InvokeAction.Request: %s", body_json)
            url = f'http://{self._data.screen_ip}:8080/device/v1/actions'
            # 2. 设置JSON请求头 + 传入字符串类型的body
            headers = {"Content-Type": "application/json"}
            async with self._session.put(url=url, data = body_json, headers = headers) as resp:
                data = await resp.json(content_type=None)
                _LOGGER.info("InvokeAction.Response: %s", data)
                if data.get("msg", "error") == "ok":
                    actions: list[ActionOperation] = ActionOperationCodec.RESULT.decode(data.get("data", []))
                    result: ActionOperation | None = actions[0]
                    if result is not None:
                        return result
                    a.status = Status.UNDEFINED
                    a.description = "result is empty"
                else:
                    a.status = Status.INTERNAL_ERROR
                    a.description = "result error"
                return a
        except ClientError as e:
            # 3. 补充网络异常捕获
            _LOGGER.error("SetProperty Local Network Error: %s", e)
            a.status = Status.INTERNAL_ERROR
            a.description = f"network error: {e!s}"
        return a

    async def _invoke_action_cloud(self, a: ActionOperation) -> ActionOperation:
        """Invoke Action to cloud."""
        _LOGGER.info("Invoke Action to Cloud")
        body_dict = {
            "userDeviceId": a.context,
            "actions": ActionOperationCodec.QUERY.encode([a]),
        }
        body_json = json.dumps(body_dict, separators=(",", ":"))
        _LOGGER.info("InvokeAction: %s", body_json)
        body_encoded = quote(body_json)  # URL 编码
        url = (
            "https://api.m.jd.com/api?functionId=smarthome_app_invokeDeviceAction&appid=device-debugger&body="
            + body_encoded
        )
        resp = await self._request("get", url)
        data = await resp.json(content_type=None)
        _LOGGER.info("InvokeAction.Response: %s", data)
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

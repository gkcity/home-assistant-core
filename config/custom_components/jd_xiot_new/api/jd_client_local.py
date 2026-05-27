"""JingDong Client Local implementation."""

import json
import logging
from urllib.parse import quote

from aiohttp import ClientError
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
    joy_device_detail_decode_array_from_local,
)
from .typedef.joy_house import JoyHouse

_LOGGER = logging.getLogger(__name__)

class JingDongClientLocalImpl(JingDongClient):
    """JingDong Client Local implementation."""

    async def async_get_houses(self) -> tuple[bool, list[JoyHouse]]:
        """Get Houses."""
        return False, []

    async def async_get_devices(self) -> list[JoyDeviceDetail]:
        """Get Devices."""
        _LOGGER.debug("GetDevices from: %s", self.data.screen_ip)
        url = f'http://{self.data.screen_ip}:8080/device/v1/devices'
        try:
            async with self.session.get(url=url, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    if data.get("msg") == 'ok':
                        devices: list[JoyDeviceDetail] = joy_device_detail_decode_array_from_local(data.get("data", []))
                        _LOGGER.debug("Devices.length: %d", len(devices))
                        return devices
                    _LOGGER.error("Get Device By Local: %s", data.get("msg", ""))
                else:
                    _LOGGER.debug("Status: %d", resp.status)
                return []
        except ClientError as e:
            _LOGGER.error("Error get devices by local: %s", e)
            return []

    async def async_get_devices_info(self, deviceIds: list[str]) -> list[JoyDeviceDetail]:
        """Get Device."""
        devices: list[JoyDeviceDetail] = await self.async_get_devices()
        return [d for d in devices if d["did"] in deviceIds]

    async def set_property(self, p: PropertyOperation) -> PropertyOperation:
        """Set Property."""
        try:
            # 1. 编码得到字典后，转为JSON字符串
            body_dict = PropertyOperationCodec.Set.QUERY.encode([p])
            body_json = json.dumps(body_dict, separators=(",", ":"))
            _LOGGER.debug("SetProperty to local: %s", body_json)
            url = f'http://{self.data.screen_ip}:8080/device/v1/properties'
            # 2. 设置JSON请求头 + 传入字符串类型的body
            headers = {"Content-Type": "application/json"}
            async with self.session.put(url=url, data=body_json, headers=headers, timeout=self.timeout) as resp:
                data = await resp.json(content_type=None)
                _LOGGER.debug("SetProperty.Response: %s", data)
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

    async def get_property(self, p: PropertyOperation) -> PropertyOperation:
        """Get Property."""
        _LOGGER.debug("GetProperty from Local")
        try:
            pid = str(p.pid)
            _LOGGER.debug("GetProperty.Request: %s", pid)
            url = f'http://{self.data.screen_ip}:8080/device/v1/properties?pid={quote(pid)}'
            headers = {"Content-Type": "application/json"}
            async with self.session.get(url=url, headers=headers, timeout=self.timeout) as resp:
                data = await resp.json(content_type=None)
                _LOGGER.debug("GetProperty.Response: %s", data)
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

    async def invoke_action(self, a: ActionOperation) -> ActionOperation:
        """Invoke Action."""
        try:
            # 1. 编码得到字典后，转为JSON字符串
            body_dict = ActionOperationCodec.QUERY.encode([a])
            body_json = json.dumps(body_dict, separators=(",", ":"))
            _LOGGER.debug("InvokeAction.Request: %s", body_json)
            url = f'http://{self.data.screen_ip}:8080/device/v1/actions'
            # 2. 设置JSON请求头 + 传入字符串类型的body
            headers = {"Content-Type": "application/json"}
            async with self.session.put(url=url, data=body_json, headers=headers) as resp:
                data = await resp.json(content_type=None)
                _LOGGER.debug("InvokeAction.Response: %s", data)
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

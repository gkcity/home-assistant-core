"""API for JingDong XIoT using Cookie."""

import json
import logging
from urllib.parse import quote

from aiohttp import ClientResponse, ClientSession
from xiot_core.spec.typedef.operation.action_operation import ActionOperation
from xiot_core.spec.typedef.operation.property_operation import PropertyOperation

from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .typedef.joy_device_detail import JoyDeviceDetail, joy_device_detail_decode_array
from .typedef.joy_house import JoyHouse, joy_house_decode_array

_LOGGER = logging.getLogger(__name__)


class JingDongXiotApi:
    """API client for JingDong XIoT."""

    def __init__(
        self, hass: HomeAssistant, cookie: str, session: ClientSession = None
    ) -> None:
        """Initialize the API client."""
        self.hass = hass
        self._cookie = cookie
        if session is None:
            self._session = aiohttp_client.async_get_clientsession(hass)
        else:
            self._session = session

    async def _request(self, method: str, url: str, **kwargs) -> ClientResponse:
        """Make an HTTP request with the cookie."""
        headers = kwargs.pop("headers", {})
        headers["Cookie"] = self._cookie
        kwargs["headers"] = headers
        return await self._session.request(method, url, **kwargs)

    async def async_get_house(self) -> tuple[bool, list[JoyHouse]]:
        """Get house list."""
        url = "https://api.m.jd.com/api?functionId=smarthome_screen_getHouseInfo&appid=device-debugger"
        resp = await self._request("get", url)
        data = await resp.json(content_type=None)
        if data.get("code") == 0:
            houses = joy_house_decode_array(data.get("data").get("houses"))
            return True, [houses]
        return False, []

    async def async_get_devices_info(
        self, userDeviceIds: list[int]
    ) -> list[JoyDeviceDetail]:
        """Get devices info."""
        body_dict = {"userDeviceIds": userDeviceIds}
        body_json = json.dumps(body_dict, separators=(",", ":"))
        body_encoded = quote(body_json)  # URL 编码
        url = (
            "https://api.m.jd.com/api?functionId=smarthome_screen_getDeviceInfo&appid=device-debugger&body="
            + body_encoded
        )
        resp = await self._request("get", url)
        data = await resp.json(content_type=None)
        if data.get("code") == 0:
            devices: list[JoyDeviceDetail] = joy_device_detail_decode_array(
                data.get("data", {}).get("devices", [])
            )
            return devices
        return []

    async def set_property(self, p: PropertyOperation) -> PropertyOperation:
        """Set Property."""
        _LOGGER.info("SetProperty")
        return p

    async def get_property(self, p: PropertyOperation) -> PropertyOperation:
        """Get Property."""
        _LOGGER.info("GetProperty")
        p.status = -1
        return p

    async def invoke_action(self, a: ActionOperation) -> ActionOperation:
        """Invoke Action."""
        _LOGGER.info("InvokeAction")
        a.status = -1
        return a

    # 根据京东 XIoT API 文档实现具体方法
    async def async_get_devices(self):
        """Get device list."""

        # 1. getHouses
        # GET https://api.m.jd.com/api?functionId=smarthome_screen_getHouseInfo&appid=device-debugger
        # 应答
        # {
        #    "traceId": "7692701.80569.17751935324687181",
        #    "code": 0,
        #       "data": {
        #          "houses": [
        #            {
        #                "rooms": [
        #                    {
        #                        "isDefault": true,
        #                        "devices": [
        #                            {
        #                                "userDeviceId": 12632,
        #                                "did": "00@10wXH"
        #                            },
        #                        ],
        #                        "name": "默认",
        #                        "config": "",
        #                        "roomId": 4994
        #                    }
        #                ],
        #                "houseId": 4450,
        #                "name": "我的房屋"
        #            }
        #        ]
        #    },
        #    "message": ""
        # }
        url = "https://api.m.jd.com/api?functionId=smarthome_screen_getHouseInfo&appid=device-debugger"
        resp = await self._request("post", url)
        # return await resp.json()
        data = await resp.json(content_type=None)
        return data.get("code") == 0

        # 2. getDevices
        # POST https://api.m.jd.com/api?functionId=smarthome_screen_getDeviceInfo&appid=device-debugger&body=%7B%22userDeviceIds%22:%5B12632,11324,10743,10609,10600,10599,10517,10466,10465,10463,10358,10356,10352,10345,10339,10322,10321,10315,10199,8727,6669,4681%5D%7D
        # body = { "userDeviceIds": [12632, 11324] }
        # 应答
        # {
        #    "traceId": "7693258.80569.17751935326326840",
        #    "code": 0,
        #    "data": {
        #        "devices": [
        #            {
        #                "summary": {
        #                    "members": [],
        #                    "online": false,
        #                    "type": "urn:jd-spec:device:gateway:0000012d:jd:jdzhp02qs:1"
        #                },
        #                "additional": {
        #                    "productId": 14775695,
        #                    "modelId": 0,
        #                    "name": "京东生活家智慧屏12英寸",
        #                    "userDeviceId": 4681,
        #                    "favorite": false,
        #                    "jdMpAppId": "",
        #                    "isFavorite": false
        #                },
        #                "shadows": [],
        #                "userDeviceId": 8727,
        #                "did": "00@10wKo"
        #            }
        #        ],
        #        "products": [
        #            {
        #                "productId": 6765636,
        #                "upgrade": [
        #                    "gateway"
        #                ],
        #                "icon": "https://smart-static-small.jd.com/xiot/product/firmware/6765636/371b20eeb1bc4d61/KGtV0D.svg",
        #                "jdMpAppId": "",
        #                "organization": "jd",
        #                "recommendNames": [
        #                    "开关"
        #                ],
        #                "name": "京东生活家智能开关双开",
        #                "model": "jdzn2kg02lf",
        #                "provisioning": "subdevice"
        #            }
        #        ]
        #    },
        #    "message": ""
        # }

        # url = "https://api.m.jd.com/api?functionId=smarthome_screen_getDeviceInfo&appid=device-debugger&body="
        # resp = await self._request("post", url)
        # return await resp.json()

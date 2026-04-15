"""Config flow for JingDong XIoT."""

import json
import logging
from urllib.parse import quote

from aiohttp import ClientError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import aiohttp_client, config_validation as cv

from .core.const import DOMAIN, JD_COOKIE, SELECTED_DEVICE_IDS, SELECTED_HOUSE_ID
from .core.typedef.joy_device_detail import (
    JoyDeviceDetail,
    joy_device_detail_decode_array,
)
from .core.typedef.joy_house import (
    JoyHouse,
    get_all_user_device_ids,
    joy_house_decode_array,
)

_LOGGER = logging.getLogger(__name__)

# 配置流程的数据结构
DATA_SCHEMA_COOKIE = vol.Schema({vol.Required(JD_COOKIE): str})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JingDong XIoT."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._cookie: str = None
        self._houses: list[JoyHouse] = None  # 房屋列表
        self._selected_house: JoyHouse = None
        self._devices: list[JoyDeviceDetail] = None  # 设备列表
        self._selected_device_ids: list[int] = []

    async def async_step_user(self, user_input=None):
        """Step 1: Input cookie."""
        errors = {}

        if user_input is not None:
            self._cookie = user_input[JD_COOKIE]  # 保存cookie

            # 验证 Cookie 是否有效（并顺便获取房屋列表，以便下一步使用）
            valid, houses = await self._test_and_get_houses(self._cookie)
            if valid:
                self._houses = houses
                return await self.async_step_house()
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA_COOKIE,
            errors=errors,
            description_placeholders={"url": "https://xiot-debugger.jd.com/"},
        )

    async def async_step_house(self, user_input=None):
        """Step 2: Select a house."""
        if user_input is not None:
            selected_house_id = user_input[SELECTED_HOUSE_ID]

            # 根据ID找到对应的JoyHouse对象
            self._selected_house = next(
                (h for h in self._houses if h["id"] == selected_house_id), None
            )

            if self._selected_house is None:
                return self.async_abort(reason="house_not_found")

            # 根据选中的房屋获取设备列表
            self._devices = await self._get_devices_by_house(
                self._cookie, self._selected_house
            )
            return await self.async_step_devices()

        # 构建房屋选择表单
        house_options = {house["id"]: house["name"] for house in self._houses}

        return self.async_show_form(
            step_id="house",
            data_schema=vol.Schema(
                {vol.Required(SELECTED_HOUSE_ID): vol.In(house_options)}
            ),
        )

    async def async_step_devices(self, user_input=None):
        """Step 3: Select devices to add."""
        if user_input is not None:
            self._selected_device_ids = [
                int(id_str) for id_str in user_input[SELECTED_DEVICE_IDS]
            ]
            # 创建配置条目
            return self.async_create_entry(
                title="JingDong XIoT",
                data={
                    JD_COOKIE: self._cookie,
                    SELECTED_HOUSE_ID: self._selected_house["id"],
                    SELECTED_DEVICE_IDS: self._selected_device_ids,
                },
            )

        # 构建设备多选框
        device_options = {
            str(
                device["userDeviceId"]
            ): f"{device['additional']['name']} ({device['summary']['type']})"
            for device in self._devices
        }

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(
                {vol.Required(SELECTED_DEVICE_IDS): cv.multi_select(device_options)}
            ),
        )

    # 辅助方法, 实现调用京东 API 获取房屋列表，并验证 Cookie
    # 返回 (True, [{"id": "xxx", "name": "我家"}, ...]) 或 (False, [])
    async def _test_and_get_houses(self, cookie: str) -> tuple[bool, list[JoyHouse]]:
        """Test cookie and return (is_valid, houses_list)."""
        session = aiohttp_client.async_get_clientsession(self.hass)
        headers = {"Cookie": cookie}
        try:
            async with session.get(
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
            _LOGGER.error("Error testing cookie: %s", e)
            return False, []

    async def _get_devices_by_house(
        self, cookie: str, house: JoyHouse
    ) -> list[JoyDeviceDetail]:
        """Get device list under a specific house."""
        _LOGGER.info("GetDevicesByHouse")
        session = aiohttp_client.async_get_clientsession(self.hass)
        headers = {"Cookie": cookie}
        body_dict = {"userDeviceIds": get_all_user_device_ids(house)}
        body_json = json.dumps(body_dict, separators=(",", ":"))
        body_encoded = quote(body_json)  # URL 编码
        url = (
            "https://api.m.jd.com/api?functionId=smarthome_screen_getDeviceInfo&appid=device-debugger&body="
            + body_encoded
        )
        try:
            async with session.get(url=url, headers=headers) as resp:
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

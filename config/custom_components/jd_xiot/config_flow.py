"""Config flow for JingDong XIoT."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_validation as cv

from .api.const import DOMAIN, JD_CENTRAL_SCREEN_IP, SELECTED_DEVICE_IDS
from .api.jd_client import JingDongClient
from .api.typedef.joy_device_detail import JoyDeviceDetail

_LOGGER = logging.getLogger(__name__)

# 中控屏IP输入schema
DATA_SCHEMA_CENTRAL_SCREEN_IP = vol.Schema({vol.Required(JD_CENTRAL_SCREEN_IP): str})

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JingDong XIoT."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        # 核心修复：确保hass不是None（Config Flow类会自动注入hass属性）
        self._session: JingDongClient | None = None
        self._auth_type: str = None  # 授权类型
        self._central_screen_ip: str = None  # 中控屏IP
        self._devices: list[JoyDeviceDetail] = None  # 设备列表
        self._selected_device_ids: list[str] = []

    async def async_step_user(self, user_input=None):
        """Step 0. User Input."""
        return await self.async_step_central_screen_ip()

    async def async_step_central_screen_ip(self, user_input=None):
        """Step 1. Input Central Screen IP."""
        errors = {}

        if user_input is not None:
            # 只有在用户输入后才初始化session（此时hass已正确注入）
            self._session = JingDongClient(self.hass)

            self._central_screen_ip = user_input[JD_CENTRAL_SCREEN_IP]

            # # 这里可以添加中控屏IP的验证逻辑（可选）
            # # 示例：简单的IP格式验证
            # try:
            #     cv.ip
            #     cv.ipv4(self._central_screen_ip)
            # except vol.Invalid:
            #     errors["base"] = "invalid_ip"
            #     return self.async_show_form(
            #         step_id="central_screen_ip",
            #         data_schema=DATA_SCHEMA_CENTRAL_SCREEN_IP,
            #         errors=errors,
            #     )

            self._devices = await self._session.async_get_devices_by_local(self._central_screen_ip)

            return await self.async_step_devices()

        return self.async_show_form(
            step_id="central_screen_ip",
            data_schema=DATA_SCHEMA_CENTRAL_SCREEN_IP,
            errors=errors,
        )

    async def async_step_devices(self, user_input=None):
        """Step 2: Select devices to add."""
        if user_input is not None:
            self._selected_device_ids = user_input[SELECTED_DEVICE_IDS]

            # 创建配置条目
            return self.async_create_entry(
                title="JingDong XIoT",
                data={
                    JD_CENTRAL_SCREEN_IP: self._central_screen_ip,
                    SELECTED_DEVICE_IDS: self._selected_device_ids,
                },
            )

        # 构建设备多选框
        device_options = {
            str(
                device["did"]
            ): f"{device['additional']['name']} (str({device['summary'].type}))"
            for device in self._devices
        }

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(
                {vol.Required(SELECTED_DEVICE_IDS): cv.multi_select(device_options)}
            ),
        )

"""Config flow for JingDong XIoT."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .api.const import (
    DOMAIN,
    JD_AUTH_TYPE,
    JD_AUTH_TYPE_ACCOUNT,
    JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE,
    JD_AUTH_TYPE_SCREEN,
    JD_COOKIE,
    JD_SCREEN_IP,
    JD_SELECTED_DEVICE_IDS,
    JD_SELECTED_HOUSE_ID,
    JD_WSKEY,
)
from .api.jd_client import JingDongClient
from .api.jd_client_factory import create_jd_client
from .api.jd_config_data import (
    JdConfigData,
    jd_config_data_decode,
    jd_config_data_encode,
)

_LOGGER = logging.getLogger(__name__)

# 1. 认证类型选择Schema
DATA_SCHEMA_AUTH_TYPE = vol.Schema({
    vol.Required(JD_AUTH_TYPE): vol.In({
        JD_AUTH_TYPE_SCREEN: "中控屏认证",
        JD_AUTH_TYPE_ACCOUNT: "账号认证",
        JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE: "账号认证（AIPC）",
    })
})

# 2. 中控屏IP输入Schema
DATA_SCHEMA_SCREEN_IP = vol.Schema({
    vol.Required(JD_SCREEN_IP): str
})

# 3. Cookie输入Schema
DATA_SCHEMA_COOKIE = vol.Schema({
    vol.Required(JD_COOKIE): str
})

# 4. Wskey输入Schema（加上前缀就变成Cookie，不过这个cookie访问api需要签名）
DATA_SCHEMA_WSKEY = vol.Schema({
    vol.Required(JD_WSKEY): str
})

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JingDong XIoT."""

    VERSION = 1
    MINOR_VERSION = 0
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize flow."""
        self._client: JingDongClient | None = None
        self._config_data: JdConfigData = JdConfigData()

    async def async_step_user(self, user_input=None):
        """Step 0: 入口步骤，直接跳转到认证类型选择步骤."""
        return await self.async_step_auth()

    # 方法名称必须是：async_step_{id}
    async def async_step_auth(self, user_input=None):
        """Step 1: 选择认证类型 (入口步骤)."""
        errors = {}

        if user_input is not None:
            self._config_data.auth_type = user_input[JD_AUTH_TYPE]
            # 根据认证类型跳转到对应步骤
            if self._config_data.auth_type == JD_AUTH_TYPE_SCREEN:
                return await self.async_step_screen()
            if self._config_data.auth_type == JD_AUTH_TYPE_ACCOUNT:
                return await self.async_step_account()
            if self._config_data.auth_type == JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE:
                return await self.async_step_account_with_signature()

        # 显示认证类型选择表单，step_id必须和方法保持一致
        return self.async_show_form(
            step_id="auth",
            data_schema=DATA_SCHEMA_AUTH_TYPE,
            errors=errors,
        )

    # ==================== 中控屏认证分支 ====================
    async def async_step_screen(self, user_input=None):
        """Step 2 (中控屏): 输入中控屏IP."""
        errors = {}

        if user_input is not None:
            self._config_data.screen_ip = user_input[JD_SCREEN_IP]

            # 只有在用户输入后才初始化client（此时hass已正确注入）
            self._client = create_jd_client(self.hass, self._config_data)
            self._config_data.selected_devices = await self._client.async_get_devices()

            return await self.async_step_devices()

        return self.async_show_form(
            step_id="screen",
            data_schema=DATA_SCHEMA_SCREEN_IP,
            errors=errors,
        )

    # ==================== 账号认证分支 ====================
    async def async_step_account(self, user_input=None):
        """Step 2 (账号): 输入JD Cookie."""
        errors = {}

        if user_input is not None:
            self._config_data.account_cookie = user_input[JD_COOKIE]

            # 只有在用户输入后才初始化client（此时hass已正确注入）
            self._client = create_jd_client(self.hass, self._config_data)

            # 验证Cookie并获取房屋列表
            valid, houses = await self._client.async_get_houses()
            if valid and houses:
                self._config_data.runtime_houses = houses
                return await self.async_step_account_house()
            if not valid:
                errors["base"] = "invalid_cookie"
            else:
                errors["base"] = "no_houses_found"

        # 显示Cookie输入表单
        return self.async_show_form(
            step_id="account",
            data_schema=DATA_SCHEMA_COOKIE,
            errors=errors,
            description_placeholders={
                "url": "https://xiot-debugger.jd.com/"
            },
        )

    # ==================== 账号认证分支(AIPC) ====================
    async def async_step_account_with_signature(self, user_input=None):
        """Step 2 (账号): 输入AIPC上的wskey."""
        errors = {}

        if user_input is not None:
            self._config_data.account_cookie = "wskey=" + user_input[JD_WSKEY]

            # 只有在用户输入后才初始化session（此时hass已正确注入）
            self._client = create_jd_client(self.hass, self._config_data)

            # 验证Cookie并获取房屋列表
            valid, houses = await self._client.async_get_houses()
            if valid and houses:
                self._config_data.runtime_houses = houses
                return await self.async_step_account_house()
            if not valid:
                errors["base"] = "invalid_wskey"
            else:
                errors["base"] = "no_houses_found"

        # 显示Cookie输入表单
        return self.async_show_form(
            step_id="account_with_signature",
            data_schema=DATA_SCHEMA_WSKEY,
            errors=errors,
        )

    # ==================== 账号认证：通用房屋选择步骤 ====================
    async def async_step_account_house(self, user_input=None):
        """Step 3 (账号): 选择房屋."""
        errors = {}

        if user_input is not None:
            selected_house_id = user_input[JD_SELECTED_HOUSE_ID]

            # 查找选中的房屋
            self._config_data.runtime_selected_house = next(
                (h for h in self._config_data.runtime_houses if h["id"] == selected_house_id), None
            )

            if not self._config_data.runtime_selected_house:
                return self.async_abort(reason="house_not_found")

            # 获取该房屋下的设备列表
            self._config_data.selected_devices = await self._client.async_get_devices()

            # 跳转到设备选择步骤
            return await self.async_step_devices()

        # 构建房屋选择选项
        house_options = {house["id"]: house["name"] for house in self._config_data.runtime_houses}
        return self.async_show_form(
            step_id="account_house",
            data_schema=vol.Schema({
                vol.Required(JD_SELECTED_HOUSE_ID): vol.In(house_options)
            }),
            errors=errors,
        )

    # ==================== 通用设备选择步骤 ====================
    async def async_step_devices(self, user_input=None):
        """Step 2: Select devices to add."""
        errors = {}

        if user_input is not None:
            self._config_data.selected_devices = user_input[JD_SELECTED_DEVICE_IDS]

            # 构建最终的配置数据
            config_data = jd_config_data_encode(self._config_data)

            # 创建配置条目
            return self.async_create_entry(
                title=self._config_data.entry_title,
                data=config_data
            )

        # 构建设备多选框
        device_options = {
            str(device["did"]): f"{device['additional']['name']} ({device['summary'].type})"
            for device in self._config_data.runtime_devices
        }
        default_selected = list(device_options.keys())

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        JD_SELECTED_DEVICE_IDS,
                        default=default_selected
                    ): cv.multi_select(device_options)
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry: config_entries.ConfigEntry):
        """Options Flow."""
        return OptionsFlowHandler(entry)

# ================== 运行过程中，可以重新选择设备列表 ==================
class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for JingDong XIoT."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_data: JdConfigData = jd_config_data_decode(config_entry.data)
        self._client: JingDongClient | None = None

    async def async_step_init(self, user_input=None):
        """Initialize options flow (入口)."""

        # 重新拉取最新设备列表
        self._client = create_jd_client(self.hass, self._config_data)
        self._config_data.runtime_devices = await self._client.async_get_devices()

        # 进入设备选择步骤
        return await self.async_step_devices()

    async def async_step_devices(self, user_input=None):
        """Options flow: 重新选择设备."""
        if user_input is not None:
            self._config_data.selected_devices = user_input[JD_SELECTED_DEVICE_IDS]
            new_data = jd_config_data_encode(self._config_data)
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
            # 重载集成使新选择生效
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        # 构建设备多选框
        device_options = {
            str(device["did"]): f"{device['additional']['name']} ({device['summary'].type})"
            for device in self._config_data.runtime_devices
        }
        default_selected = self._config_data.selected_devices
        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema({
                vol.Required(JD_SELECTED_DEVICE_IDS, default=default_selected): cv.multi_select(device_options)
            }),
        )

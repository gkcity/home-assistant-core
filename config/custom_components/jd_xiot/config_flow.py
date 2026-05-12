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
from .api.jd_config_data import JdConfigData, jd_config_data_encode
from .api.typedef.joy_device_detail import JoyDeviceDetail
from .api.typedef.joy_house import JoyHouse

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
DATA_SCHEMA_CENTRAL_SCREEN_IP = vol.Schema({
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

    def __init__(self) -> None:
        """Initialize flow."""

        # 通用属性
        self._session: JingDongClient | None = None
        self._auth_type: str = ""          # 认证类型 (screen/account/account-with-signature)
        self._devices: list[JoyDeviceDetail] = []  # 设备列表
        self._selected_device_ids: list[str] = []  # 选中的设备ID

        # 中控屏认证相关
        self._screen_ip: str = ""          # 中控屏IP

        # 账号认证相关
        self._cookie: str = ""             # JD Cookie
        self._houses: list[JoyHouse] = []  # 房屋列表
        self._selected_house: JoyHouse | None = None  # 选中的房屋

    async def async_step_user(self, user_input=None):
        """Step 1: 选择认证类型 (入口步骤)."""
        if user_input is not None:
            self._auth_type = user_input[JD_AUTH_TYPE]
            # 根据认证类型跳转到对应步骤
            if self._auth_type == JD_AUTH_TYPE_SCREEN:
                return await self.async_step_screen_ip()
            if self._auth_type == JD_AUTH_TYPE_ACCOUNT:
                return await self.async_step_account()
            if self._auth_type == JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE:
                return await self.async_step_account_with_signature()

        # 显示认证类型选择表单
        return self.async_show_form(
            step_id="auth",
            data_schema=DATA_SCHEMA_AUTH_TYPE,
        )

    # ==================== 中控屏认证分支 ====================
    async def async_step_screen_ip(self, user_input=None):
        """Step 2 (中控屏): 输入中控屏IP."""
        errors = {}

        if user_input is not None:
            # 只有在用户输入后才初始化session（此时hass已正确注入）
            self._session = JingDongClient(self.hass)

            self._screen_ip = user_input[JD_SCREEN_IP]

            self._devices = await self._session.async_get_devices_by_local(self._screen_ip)

            return await self.async_step_devices()

        return self.async_show_form(
            step_id="screen",
            data_schema=DATA_SCHEMA_CENTRAL_SCREEN_IP,
            errors=errors,
        )

    # ==================== 账号认证分支 ====================
    async def async_step_account(self, user_input=None):
        """Step 2 (账号): 输入JD Cookie."""
        errors = {}

        if user_input is not None:
            # 只有在用户输入后才初始化session（此时hass已正确注入）
            self._session = JingDongClient(self.hass)
            self._cookie = user_input[JD_COOKIE]

            # 验证Cookie并获取房屋列表
            valid, houses = await self._session.async_get_houses(self._cookie, False)
            if valid and houses:
                self._houses = houses
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
            description_placeholders={"url": "https://xiot-debugger.jd.com/"},
        )

    # ==================== 账号认证分支(AIPC) ====================
    async def async_step_account_with_signature(self, user_input=None):
        """Step 2 (账号): 输入AIPC上的wskey."""
        errors = {}

        if user_input is not None:
            # 只有在用户输入后才初始化session（此时hass已正确注入）
            self._session = JingDongClient(self.hass)
            self._cookie = "wskey=" + user_input[JD_COOKIE]

            # 验证Cookie并获取房屋列表
            valid, houses = await self._session.async_get_houses(self._cookie, True)
            if valid and houses:
                self._houses = houses
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
        if user_input is not None:
            selected_house_id = user_input[JD_SELECTED_HOUSE_ID]

            # 查找选中的房屋
            self._selected_house = next(
                (h for h in self._houses if h["id"] == selected_house_id), None
            )

            if not self._selected_house:
                return self.async_abort(reason="house_not_found")

            # 是否需要签名
            signature = self._auth_type == JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE

            # 获取该房屋下的设备列表
            self._devices = await self._session.async_get_devices_by_house(self._cookie, self._selected_house, signature)

            # 跳转到设备选择步骤
            return await self.async_step_devices()

        # 构建房屋选择选项
        house_options = {house["id"]: house["name"] for house in self._houses}
        return self.async_show_form(
            step_id="house",
            data_schema=vol.Schema({
                vol.Required(JD_SELECTED_HOUSE_ID): vol.In(house_options)
            }),
        )

    # ==================== 通用设备选择步骤 ====================
    async def async_step_devices(self, user_input=None):
        """Step 2: Select devices to add."""
        if user_input is not None:
            self._selected_device_ids = user_input[JD_SELECTED_DEVICE_IDS]

            # 构建最终的配置数据
            config_data = self._build_config_data()

            # 创建配置条目
            return self.async_create_entry(
                title=self._build_entry_title(),
                data=config_data
            )

            # # 创建配置条目
            # return self.async_create_entry(
            #     title="JingDong XIoT (" + self._screen_ip + ")",
            #     data={
            #         JD_SCREEN_IP: self._screen_ip,
            #         JD_SELECTED_DEVICE_IDS: self._selected_device_ids,
            #     },
            # )

        # 构建设备多选框
        device_options = {
            str(
                device["did"]
            ): f"{device['additional']['name']} (str({device['summary'].type}))"
            for device in self._devices
        }

        default_selected = list(device_options.keys())  # 提取所有设备ID作为默认选中项

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(
                {
                    vol.Required(JD_SELECTED_DEVICE_IDS, default=default_selected): cv.multi_select(device_options)
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry: config_entries.ConfigEntry):
        """Options Flow."""
        return OptionsFlowHandler(entry)

    # ==================== 辅助方法 ====================
    def _build_config_data(self) -> dict[str, object]:
        """构建最终的配置数据（统一格式）."""

        data: JdConfigData = JdConfigData()
        data.auth_type = self._auth_type
        data.devices = self._selected_device_ids

        # 根据认证类型填充auth字段
        if self._auth_type == JD_AUTH_TYPE_SCREEN:
            data.screen_ip = self._screen_ip

        if self._auth_type in (JD_AUTH_TYPE_ACCOUNT, JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE):
            data.account_cookie = self._cookie
            data.account_house_id = self._selected_house["id"]

        return jd_config_data_encode(data)

    def _build_entry_title(self) -> str:
        """构建配置条目标题."""
        if self._auth_type == JD_AUTH_TYPE_SCREEN:
            return f"京东IoT (中控屏 {self._screen_ip})"

        if self._auth_type in (JD_AUTH_TYPE_ACCOUNT, JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE):
            return f"京东IoT (账号 {self._selected_house['name']})"

        return "京东IoT"

# ================== 运行过程中，可以重新选择设备列表 ==================
class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for JingDong XIoT."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

        # 通用属性
        self._session: JingDongClient | None = None
        self._devices: list[JoyDeviceDetail] = []  # 设备列表
        self._selected_device_ids: list[str] = []  # 选中的设备ID

    async def async_step_init(self, user_input=None):
        """Initialize options flow (入口)."""

        # 从现有配置条目获取已保存的配置
        self._selected_device_ids = self._config_entry.data.get(JD_SELECTED_DEVICE_IDS, [])

        # 重新拉取最新设备列表
        self._session = JingDongClient(self.hass)
        # self._devices = await self._session.async_get_devices_by_local(self._screen_ip)
        self._devices = await self._session.async_get_devices()

        # 进入设备选择步骤
        return await self.async_step_devices()

    async def async_step_devices(self, user_input=None):
        """Options flow: 重新选择设备."""
        if user_input is not None:
            # 更新配置条目的 data（也可以使用 options，这里与你现有逻辑保持一致）
            new_data = {**self.config_entry.data, JD_SELECTED_DEVICE_IDS: user_input[JD_SELECTED_DEVICE_IDS]}
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
            # 重载集成使新选择生效
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        # 构建设备多选框
        device_options = {
            str(device["did"]): f"{device['additional']['name']} ({device['summary'].type})"
            for device in self._devices
        }
        default_selected = self._selected_device_ids
        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema({
                vol.Required(JD_SELECTED_DEVICE_IDS, default=default_selected): cv.multi_select(device_options)
            }),
        )

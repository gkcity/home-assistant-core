"""Configuration Data JingDong XIoT integration."""

from types import MappingProxyType
from typing import Any

from .const import (
    JD_AUTH_TYPE_ACCOUNT,
    JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE,
    JD_AUTH_TYPE_SCREEN,
    JD_COOKIE,
)
from .typedef.joy_device_detail import JoyDeviceDetail
from .typedef.joy_house import JoyHouse


class JdConfigData:
    """JingDong Config Data."""

    def __init__(self):
        """Init Config Data."""
        self.__auth_type: str = ""
        self.__screen_ip: str = ""
        self.__account_cookie: str = ""
        self.__account_house_id: int = 0
        self.__selected_device_ids: list[str] = []

        # 房屋列表（运行时的数据，不保存）
        self.__runtime_houses: list[JoyHouse] = []

        # 设备列表（运行时的数据，不保存）
        self.__runtime_devices: list[JoyDeviceDetail] = []

        # 选中的房屋（运行时的数据，不保存）
        self.__runtime_selected_house: JoyHouse | None = None

    @property
    def auth_type(self) -> str:
        """Get Auth Type."""
        return self.__auth_type

    @auth_type.setter
    def auth_type(self, value: str) -> None:
        """Set Auth Type."""
        self.__auth_type = value

    @property
    def screen_ip(self) -> str:
        """Get IP."""
        return self.__screen_ip

    @screen_ip.setter
    def screen_ip(self, value: str) -> None:
        """Set IP."""
        self.__screen_ip = value

    @property
    def account_cookie(self) -> str:
        """Get Cookie."""
        return self.__account_cookie

    @account_cookie.setter
    def account_cookie(self, value: str) -> None:
        """Set Cookie."""
        self.__account_cookie = value

    @property
    def account_house_id(self) -> int:
        """Get House ID."""
        return self.__account_house_id

    @account_house_id.setter
    def account_house_id(self, value: int) -> None:
        """Set House ID."""
        self.__account_house_id = value

    @property
    def selected_devices(self) -> list[str]:
        """Get Selected Devices."""
        return self.__selected_device_ids

    @selected_devices.setter
    def selected_devices(self, value: list[str]) -> None:
        """Set Selected Devices."""
        self.__selected_device_ids = value

    @property
    def runtime_devices(self) -> list[JoyDeviceDetail]:
        """Get All Devices for runtime."""
        return self.__runtime_devices

    @runtime_devices.setter
    def runtime_devices(self, value: list[JoyDeviceDetail]) -> None:
        """Set All Devices for runtime."""
        self.__runtime_devices = value

    @property
    def runtime_houses(self) -> list[JoyHouse]:
        """Get Houses for runtime."""
        return self.__runtime_houses

    @runtime_houses.setter
    def runtime_houses(self, value: list[JoyHouse]) -> None:
        """Set Houses for runtime."""
        self.__runtime_houses = value

    @property
    def runtime_selected_house(self) -> JoyHouse | None:
        """Get Selected House for runtime."""
        return self.__runtime_selected_house

    @runtime_selected_house.setter
    def runtime_selected_house(self, value: JoyHouse) -> None:
        """Set Selected House for runtime."""
        self.__runtime_selected_house = value

    @property
    def entry_title(self) -> str:
        """Get Entry Title."""
        if self.__auth_type == JD_AUTH_TYPE_SCREEN:
            return f"京东IoT (中控屏 {self.__screen_ip})"

        if self.__auth_type == JD_AUTH_TYPE_ACCOUNT:
            return f"京东IoT (账号 {self.__runtime_selected_house['name']})"

        if self.__auth_type == JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE:
            return f"京东IoT (AIPC账号 {self.__runtime_selected_house['name']})"

        return "京东IoT"

def jd_config_data_decode(data: MappingProxyType[str, Any]) -> JdConfigData:
    """Decode from dict."""

    config = JdConfigData()

    config.auth_type = data.get("auth_type", "")
    config.selected_devices = data.get("devices", [])
    if config.auth_type == JD_AUTH_TYPE_SCREEN:
        config.screen_ip = data.get(JD_AUTH_TYPE_SCREEN, "")
    elif config.auth_type == JD_AUTH_TYPE_ACCOUNT:
        config.account_cookie = data.get(JD_AUTH_TYPE_ACCOUNT, {}).get(JD_COOKIE, "")
        config.account_house_id = data.get(JD_AUTH_TYPE_ACCOUNT, {}).get("house_id", 0)
    elif config.auth_type == JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE:
        config.account_cookie = data.get(JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE, {}).get(JD_COOKIE, "")
        config.account_house_id = data.get(JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE, {}).get("house_id", 0)

    return config

def jd_config_data_encode(data: JdConfigData) -> dict[str, object]:
    """Encode to dict."""

    o: dict[str, object] = {
        "auth_type": data.auth_type,
        "devices": data.selected_devices
    }

    if data.auth_type == JD_AUTH_TYPE_SCREEN:
        o[JD_AUTH_TYPE_SCREEN] = data.screen_ip
    elif data.auth_type == JD_AUTH_TYPE_ACCOUNT:
        o[JD_AUTH_TYPE_ACCOUNT] = {
            "cookie": data.account_cookie,
            "house_id": data.account_house_id
        }
    elif data.auth_type == JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE:
        o[JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE] = {
            "cookie": data.account_cookie,
            "house_id": data.account_house_id
        }
    return o

"""Configuration Data JingDong XIoT integration."""

from types import MappingProxyType
from typing import Any

from .const import (
    JD_AUTH_TYPE_ACCOUNT,
    JD_AUTH_TYPE_ACCOUNT_WITH_SIGNATURE,
    JD_AUTH_TYPE_SCREEN,
    JD_COOKIE,
)


class JdConfigData:
    """JingDong Config Data."""

    def __init__(self):
        """Init Config Data."""
        self._auth_type: str = ""
        self._screen_ip: str = ""
        self._account_cookie: str = ""
        self._account_house_id: int = 0
        self._selected_device_ids: list[str] = []

    @property
    def auth_type(self) -> str:
        """Get Auth Type."""
        return self._auth_type

    @auth_type.setter
    def auth_type(self, value: str) -> None:
        """Set Auth Type."""
        self._auth_type = value

    @property
    def screen_ip(self) -> str:
        """Get IP."""
        return self._screen_ip

    @screen_ip.setter
    def screen_ip(self, value: str) -> None:
        """Set IP."""
        self._screen_ip = value

    @property
    def account_cookie(self) -> str:
        """Get Cookie."""
        return self._account_cookie

    @account_cookie.setter
    def account_cookie(self, value: str) -> None:
        """Set Cookie."""
        self._account_cookie = value

    @property
    def account_house_id(self) -> int:
        """Get House ID."""
        return self._account_house_id

    @account_house_id.setter
    def account_house_id(self, value: int) -> None:
        """Set House ID."""
        self._account_house_id = value

    @property
    def devices(self) -> list[str]:
        """Get Devices."""
        return self._selected_device_ids

    @devices.setter
    def devices(self, value: list[str]) -> None:
        """Set Devices."""
        self._selected_device_ids = value

def jd_config_data_decode(data: MappingProxyType[str, Any]) -> JdConfigData:
    """Decode from dict."""

    config = JdConfigData()

    config.auth_type = data.get("auth_type", "")
    config.devices = data.get("devices", [])
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
        "devices": data.devices
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

"""The JingDong XIoT integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .core import api
from .core.const import JD_COOKIE

_LOGGER = logging.getLogger(__name__)

# 支持的设备类型列表
_PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SWITCH, Platform.COVER]

# 定义配置条目的类型
type JdXiotConfigEntry = ConfigEntry[api.JingDongXiotApi]


async def async_setup_entry(hass: HomeAssistant, entry: JdXiotConfigEntry) -> bool:
    """Set up JingDong XIoT from a config entry."""
    cookie = entry.data[JD_COOKIE]

    # 初始化 API 客户端
    api_client = api.JingDongXiotApi(hass, cookie)

    # 测试 API 连接是否正常
    try:
        await api_client.async_get_house()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to connect to JD API: {err}") from err

    # 将 API 客户端存入 runtime_data，供后续平台文件（如 light.py）使用
    entry.runtime_data = api_client

    # 将选中的设备 ID 列表存入 entry 的 options 或 data 中，供平台使用
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # 保存设备类型列表
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: JdXiotConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Async_unload_entry")
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    _LOGGER.info("Update_listener")
    await hass.config_entries.async_reload(entry.entry_id)

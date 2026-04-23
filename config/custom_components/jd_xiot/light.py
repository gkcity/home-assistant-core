"""Platform for light integration."""

from __future__ import annotations

import logging
from typing import TypedDict

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.api import JingDongXiotApi
from .core.const import SELECTED_DEVICE_IDS
from .core.typedef.joy_device_detail import JoyDeviceDetail
from .entities.light.jd_light_mapping import create_light_entity

_LOGGER = logging.getLogger(__name__)

# 定义配置条目的类型
type JdXiotConfigEntry = ConfigEntry[JingDongXiotApi]


class DeviceCapabilities(TypedDict, total=False):
    """Device Capabilities."""

    brightness: bool
    color_temperature_kelvin: bool  # 是否支持开尔文色温
    color: bool


class DeviceState(TypedDict, total=False):
    """Device State."""

    power: str  # "on" / "off"
    brightness: int  # 0-100
    color_temperature: int  # 开尔文值 (K)
    color: str  # 十六进制 "#RRGGBB"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: JdXiotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light platform."""
    _LOGGER.info("Set up the light platform")

    # 1. 从 entry.runtime_data 获取 API 客户端
    api: JingDongXiotApi = entry.runtime_data

    # 2. 从 entry.data 获取保存的设备ID列表（添加集成时选择的设备）
    selected_device_ids: list[int] = entry.data.get(SELECTED_DEVICE_IDS, [])

    _LOGGER.info("Selected device IDs for JD XIoT: %s", selected_device_ids)

    if not selected_device_ids:
        _LOGGER.warning("No devices selected for JD XIoT integration")
        async_add_entities([])
        return

    # 3. 批量获取设备详细信息
    details: list[JoyDeviceDetail] = await api.async_get_devices_info(
        selected_device_ids
    )

    if not details:
        _LOGGER.error("Failed to retrieve device info from JD API")
        async_add_entities([])
        return

    # 4. 实体列表
    entities: list[LightEntity] = []

    # 5. 创建实体
    for detail in details:
        device_type: str = detail.get("summary", {}).get("type", "").lower()
        entity = create_light_entity(device_type, api, detail)
        if entity is not None:
            _LOGGER.info("Add light: %s", device_type)
            entities.append(entity)
        else:
            _LOGGER.info(
                "Skipping non-light device %s (type: %s)",
                detail.get("did"),
                device_type,
            )

    if not entities:
        _LOGGER.warning("No light devices found among selected device IDs")

    # 5. 将实体添加到 HA
    async_add_entities(entities)

"""Platform for light integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core import api

_LOGGER = logging.getLogger(__name__)

# 定义配置条目的类型
type JdXiotConfigEntry = ConfigEntry[api.JingDongXiotApi]


# async def async_setup_entry(hass: HomeAssistant, config_entry: JdXiotConfigEntry, async_add_entities):
#     HassEntry.init(hass, config_entry).new_adder(ENTITY_DOMAIN, async_add_entities)
#     await async_setup_config_entry(hass, config_entry, async_setup_platform, async_add_entities, ENTITY_DOMAIN)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: JdXiotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light platform."""
    _LOGGER.info("Set up the light platform")
    # # 1. 从 entry.runtime_data 获取 API 客户端
    # api = entry.runtime_data

    # # 2. 调用 API 获取设备列表
    # devices = await api.async_get_devices()

    # # 3. 过滤出属于 light 平台的设备
    # lights = [device for device in devices if device["type"] == "light"]

    # # 4. 创建实体列表
    # entities = [JdLightEntity(api, device) for device in lights]

    # # 5. 将实体添加到 HA
    # async_add_entities(entities)
    async_add_entities([])

#
# 修改 light.py：只创建被选中的设备
#
# async def async_setup_entry(hass, entry, async_add_entities):
#     api = entry.runtime_data
#     selected_ids = set(entry.data.get(CONF_DEVICE_IDS, []))
#     all_devices = await api.async_get_devices_by_house(entry.data[CONF_HOUSE_ID])
#     devices_to_add = [d for d in all_devices if d["id"] in selected_ids]
#     entities = [JdLightEntity(api, d) for d in devices_to_add if d["type"] == "light"]
#     async_add_entities(entities)

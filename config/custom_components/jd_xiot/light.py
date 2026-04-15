"""Platform for light integration."""

from __future__ import annotations

import logging
from typing import Any, TypedDict

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.api import JingDongXiotApi
from .core.const import SELECTED_DEVICE_IDS
from .core.typedef.joy_device_detail import JoyDeviceDetail

_LOGGER = logging.getLogger(__name__)

# 定义配置条目的类型
type JdXiotConfigEntry = ConfigEntry[JingDongXiotApi]

# async def async_setup_entry(hass: HomeAssistant, config_entry: JdXiotConfigEntry, async_add_entities):
#     HassEntry.init(hass, config_entry).new_adder(ENTITY_DOMAIN, async_add_entities)
#     await async_setup_config_entry(hass, config_entry, async_setup_platform, async_add_entities, ENTITY_DOMAIN)


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

    # 4. 创建实体列表
    entities: list[JdLightEntity] = []

    # 过滤出属于 light 平台的设备
    for detail in details:
        deviceType: str = detail.get("summary", {}).get("type", "").lower()
        if deviceType == "light":
            entities.append(JdLightEntity(api, detail))
        else:
            _LOGGER.info(
                "Skipping non-light device %s (type: %s)",
                detail.get("did"),
                deviceType,
            )

    if not entities:
        _LOGGER.warning("No light devices found among selected device IDs")

    # 5. 将实体添加到 HA
    async_add_entities(entities)


class JdLightEntity(LightEntity):
    """JD XIoT light using Kelvin color temperature."""

    _attr_has_entity_name = True
    _attr_supported_color_modes: set[ColorMode]

    def __init__(self, api: JingDongXiotApi, device_info: JoyDeviceDetail) -> None:
        """Initialize light entity."""
        self._api: JingDongXiotApi = api
        self._user_device_id: int = device_info["userDeviceId"]
        self._device_id: str = device_info["did"]
        self._device_info: JoyDeviceDetail = device_info
        self._attr_name: str = device_info.get("additional", {}).get(
            "name", self._device_id
        )
        self._attr_unique_id: str = f"jd_xiot_light_{self._device_id}"

        caps: DeviceCapabilities = self._parse_capabilities(device_info)
        self._attr_supported_color_modes = self._determine_color_modes(caps)

        # 初始状态
        self._attr_is_on: bool = False
        self._attr_brightness: int | None = None  # 0-255
        self._attr_color_temp_kelvin: int | None = None  # 开尔文值
        self._attr_hs_color: tuple[float, float] | None = None
        self._attr_available: bool = True

    @property
    def device_info(self) -> dict[str, Any]:
        """Device information."""
        return {
            "identifiers": {("jd_xiot", self._device_id)},
            "name": self._attr_name,
            "manufacturer": "JD XIoT",
            "model": self._device_info.get("summary", {}).get("model", "Unknown"),
        }

    def _parse_capabilities(self, device: JoyDeviceDetail) -> DeviceCapabilities:
        caps_raw: dict[str, Any] = device.get("capabilities", {})
        return DeviceCapabilities(
            brightness=caps_raw.get("brightness", False),
            color_temperature_kelvin=caps_raw.get("color_temperature", False),
            color=caps_raw.get("color", False),
        )

    def _determine_color_modes(self, caps: DeviceCapabilities) -> set[ColorMode]:
        modes: set[ColorMode] = set()
        if caps.get("brightness"):
            modes.add(ColorMode.BRIGHTNESS)
        if caps.get("color_temperature_kelvin"):
            modes.add(ColorMode.COLOR_TEMP_KELVIN)  # 使用开尔文模式
        if caps.get("color"):
            modes.add(ColorMode.HS)
        if not modes:
            modes.add(ColorMode.ONOFF)
        return modes

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn ON."""
        if not self._attr_is_on:
            success = await self._api.async_control_device(
                self._device_id, "power", "on"
            )
            if not success:
                _LOGGER.error("Failed to turn on light %s", self._device_id)
                return
            self._attr_is_on = True

        # 2. 亮度
        if (
            ATTR_BRIGHTNESS in kwargs
            and ColorMode.BRIGHTNESS in self._attr_supported_color_modes
        ):
            ha_brightness: int = kwargs[ATTR_BRIGHTNESS]
            percent: int = int(ha_brightness * 100 / 255)
            await self._api.async_control_device(self._device_id, "brightness", percent)
            self._attr_brightness = ha_brightness

        # 3. 色温 (开尔文)
        if (
            ATTR_COLOR_TEMP_KELVIN in kwargs
            and ColorMode.COLOR_TEMP_KELVIN in self._attr_supported_color_modes
        ):
            kelvin: int = kwargs[ATTR_COLOR_TEMP_KELVIN]
            await self._api.async_control_device(
                self._device_id, "color_temperature", kelvin
            )
            self._attr_color_temp_kelvin = kelvin

        # # 4. HS 颜色
        # if ATTR_HS_COLOR in kwargs and ColorMode.HS in self._attr_supported_color_modes:
        #     hue, sat = kwargs[ATTR_HS_COLOR]
        #     rgb = color_hs_to_rgb(hue, sat)
        #     hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)
        #     await self._api.async_control_device(self._device_id, "color", hex_color)
        #     self._attr_hs_color = (hue, sat)

        await self.async_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn OFF."""
        success = await self._api.async_control_device(self._device_id, "power", "off")
        if success:
            self._attr_is_on = False
            self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update Status."""
        devices = await self._api.async_get_devices_info([self._device_id])
        if not devices:
            self._attr_available = False
            return

        state_data = devices[0]
        self._attr_available = True
        state: DeviceState = state_data.get("state", {})

        # 电源
        self._attr_is_on = state.get("power") == "on"

        # 亮度 (0-100 -> 0-255)
        if (
            "brightness" in state
            and ColorMode.BRIGHTNESS in self._attr_supported_color_modes
        ):
            self._attr_brightness = int(state["brightness"] * 255 / 100)
        else:
            self._attr_brightness = None

        # 色温 (开尔文)
        if (
            "color_temperature" in state
            and ColorMode.COLOR_TEMP_KELVIN in self._attr_supported_color_modes
        ):
            self._attr_color_temp_kelvin = state["color_temperature"]
        else:
            self._attr_color_temp_kelvin = None

        # 颜色
        # if "color" in state and ColorMode.HS in self._attr_supported_color_modes:
        #     hex_color = state["color"].lstrip("#")
        #     if len(hex_color) == 6:
        #         r = int(hex_color[0:2], 16)
        #         g = int(hex_color[2:4], 16)
        #         b = int(hex_color[4:6], 16)
        #         self._attr_hs_color = color_rgb_to_hs(r, g, b)
        # else:
        #     self._attr_hs_color = None

        self.async_write_ha_state()

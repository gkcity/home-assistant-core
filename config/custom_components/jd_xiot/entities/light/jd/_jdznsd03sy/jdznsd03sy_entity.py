"""Light DeviceJdznsd03sy."""

import asyncio
import logging

from custom_components.jd_xiot.api.const import DOMAIN
from custom_components.jd_xiot.api.jd_client import JingDongClient
from custom_components.jd_xiot.api.typedef.joy_device_detail import JoyDeviceDetail
from custom_components.jd_xiot.entities.light.jd_light_mapping import (
    register_light_entity,
)
from xiot_core.support.typedef.controller.device_controller import DeviceController
from xiot_core_device_controller.jd._light._jdznsd03sy.device_jdznsd03sy import (
    DeviceJdznsd03sy,
)

from homeassistant.components.light import ColorMode, LightEntity, LightEntityFeature
from homeassistant.helpers.device_registry import DeviceInfo

_LOGGER = logging.getLogger(__name__)


# ------------------------------
# 第一步：定义你的灯光实体类
# ------------------------------
@register_light_entity
class DeviceJdznsd03syEntity(LightEntity):
    """DeviceJdznsd03sy Entity."""

    TYPE: str = DeviceJdznsd03sy.TYPE

    # ------------------------------
    # 第二步：初始化方法（存储灯的状态、设备信息）
    # ------------------------------
    def __init__(
        self,
        controller: DeviceController,
        client: JingDongClient,
        detail: JoyDeviceDetail,
    ) -> None:
        """Init Light Entity."""

        # 保存
        self._client: JingDongClient = client
        self._detail: JoyDeviceDetail = detail
        self._device: DeviceJdznsd03sy | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_light_{controller.did}"

        # 必须：实体名称
        self._attr_name: str = detail.get("additional", {}).get("name", detail["did"])

        # 实体可用
        self._attr_available: bool = True

        self._attr_color_mode = ColorMode.COLOR_TEMP

        # 必须：声明这个灯支持哪些**颜色模式**（核心！）
        # 2026 最新标准：用 ColorMode 枚举，不要用旧版 SUPPORT_*
        self._attr_supported_color_modes: set[ColorMode] = {
            ColorMode.COLOR_TEMP,  # 支持色温
        }

        # 可选：支持的额外功能（场景、效果等）
        self._attr_supported_features = LightEntityFeature(0)

        # 初始状态
        self._attr_is_on: bool = False
        self._attr_brightness: int | None = 80  # 0-255
        self._attr_color_temp_kelvin: int | None = 2700
        self._attr_min_color_temp_kelvin = 2700
        self._attr_max_color_temp_kelvin = 6500
        self._attr_hs_color: tuple[float, float] | None = None

        # 设备信息
        self._attr_device_info = DeviceInfo(
            identifiers = {(DOMAIN, detail["did"])},
            name = detail['additional']['name'],
            manufacturer = "京东智能",
            model = f"Cover {detail["did"]}",
        )

        if isinstance(controller, DeviceJdznsd03sy):
            self._device: DeviceJdznsd03sy = controller
            self._device.set_operator(
                client.get_property,
                client.set_property,
                client.invoke_action,
                detail["userDeviceId"]
            )
            _LOGGER.info("Init: %s", detail["did"])
        else:
            self._device = None
            self._attr_available: bool = False
            _LOGGER.error("Init error: %s ", {type(controller).__name__})

    # ------------------------------
    # 第四步：必须实现的控制方法（HA 操作灯时调用）
    # ------------------------------
    async def async_turn_on(self, **kwargs) -> None:
        """Set On."""
        _LOGGER.info("Turn On: %s", kwargs)

        try:
            # 1. 开
            await self._device.service_light().property_on().set(True)

            # 2. 色温
            if color_temp := kwargs.get("color_temp_kelvin"):
                await self._device.service_light().property_color_temperature().set(color_temp)
                self._attr_color_temp_kelvin = color_temp

            # 3. 亮度
            if brightness := kwargs.get("brightness"):
                brightness_percentage: int = brightness * 100 // 255
                await self._device.service_light().property_brightness().set(brightness_percentage)
                self._attr_brightness = brightness
        except ValueError as e:
            _LOGGER.error("Turn On Error: %s", e)

        self._attr_is_on = True

        # 通知 HA：状态已更新，刷新界面
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Set Off."""
        _LOGGER.info("Turn Off: %s", kwargs)

        try:
            await self._device.service_light().property_on().set(False)
        except ValueError as e:
            _LOGGER.error("Turn Off Error: %s", e)

        self._attr_is_on = False

        # 通知 HA：状态已更新
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update Status."""
        _LOGGER.info("Update")

        try:
            await asyncio.sleep(1)

            onoff = await self._device.service_light().property_on().get()
            self._attr_is_on = bool(onoff)

            brightness = await self._device.service_light().property_brightness().get()
            self._attr_brightness = round(brightness * 255 / 100) if brightness else 0

            color_temperature = await self._device.service_light().property_color_temperature().get()
            self._attr_color_temp_kelvin = color_temperature

            self._attr_available = True
        except ValueError as e:
            _LOGGER.error("Update Error: %s", e)
            self._attr_available = False

        self.async_write_ha_state()

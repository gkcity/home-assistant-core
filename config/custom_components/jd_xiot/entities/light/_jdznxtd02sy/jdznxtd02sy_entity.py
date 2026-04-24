"""Light Jdznxtd02sy."""

import logging

from custom_components.jd_xiot.core.api import JingDongXiotApi
from custom_components.jd_xiot.core.typedef.joy_device_detail import JoyDeviceDetail
from custom_components.jd_xiot.entities.light.jd_light_mapping import (
    register_light_entity,
)
from xiot_core.support.typedef.controller.device_controller import DeviceController
from xiot_core_device_controller.jd._light._jdznxtd02sy.jdznxtd02sy import Jdznxtd02sy

from homeassistant.components.light import ColorMode, LightEntity, LightEntityFeature

_LOGGER = logging.getLogger(__name__)


# ------------------------------
# 第一步：定义你的灯光实体类
# ------------------------------
@register_light_entity
class Jdznxtd02syEntity(LightEntity):
    """Jdznxtd02sy Entity."""

    TYPE: str = Jdznxtd02sy.TYPE

    # ------------------------------
    # 第二步：初始化方法（存储灯的状态、设备信息）
    # ------------------------------
    def __init__(
        self,
        controller: DeviceController,
        api: JingDongXiotApi,
        detail: JoyDeviceDetail,
    ) -> None:
        """Init Light Entity."""

        # 保存
        self._api: JingDongXiotApi = api
        self._detail: JoyDeviceDetail = detail
        self._device: Jdznxtd02sy | None = None

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

        if isinstance(controller, Jdznxtd02sy):
            self._device: Jdznxtd02sy = controller
            self._device.set_operator(
                api.set_property, api.invoke_action, detail["userDeviceId"]
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
            await self._device.light_().on_().set(True)
            self._attr_is_on = True

            # 2. 色温
            if color_temp := kwargs.get("color_temp_kelvin"):
                await self._device.light_().color_temperature_().set(color_temp)
                self._attr_color_temp_kelvin = color_temp

            # 3. 亮度
            if brightness := kwargs.get("brightness"):
                await self._device.light_().brightness_().set(brightness)
                self._attr_brightness = brightness
        except ValueError as e:
            _LOGGER.error("Turn On Error: %s", e)

        # 通知 HA：状态已更新，刷新界面
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Set Off."""
        _LOGGER.info("Turn Off: %s", kwargs)

        try:
            await self._device.light_().on_().set(False)
            self._attr_is_on = False
        except ValueError as e:
            _LOGGER.error("Turn Off Error: %s", e)

        # 通知 HA：状态已更新
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update Status."""
        _LOGGER.info("Update")
        # ================================================
        # HA会调用async_update, 在这里更新属性值
        # ================================================
        self._attr_available = True
        self.async_write_ha_state()

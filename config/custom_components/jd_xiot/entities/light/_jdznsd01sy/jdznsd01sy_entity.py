"""Light Jdznsd01sy."""

import logging

# from ....core.api import JingDongXiotApi
# from ....core.typedef.joy_device_detail import JoyDeviceDetail
# from ..jd_light_mapping import register_light_entity
from custom_components.jd_xiot.core.api import JingDongXiotApi
from custom_components.jd_xiot.core.typedef.joy_device_detail import JoyDeviceDetail
from custom_components.jd_xiot.entities.light.jd_light_mapping import (
    register_light_entity,
)
from xiot_core.support.typedef.controller.device_controller import DeviceController
from xiot_core_device_controller.jd._light._jdznsd01sy.jdznsd01sy import Jdznsd01sy

from homeassistant.components.light import ColorMode, LightEntity, LightEntityFeature

_LOGGER = logging.getLogger(__name__)


# ------------------------------
# 第一步：定义你的灯光实体类
# ------------------------------
@register_light_entity
class Jdznsd01syEntity(LightEntity):
    """Jdznsd01sy Entity."""

    TYPE: str = Jdznsd01sy.TYPE

    # ------------------------------
    # 第二步：初始化方法（存储灯的状态、设备信息）
    # ------------------------------
    def __init__(
        self,
        controller: DeviceController,
        api: JingDongXiotApi,
        device_info: JoyDeviceDetail,
    ) -> None:
        """Init Light Entity."""
        super().__init__()

        # 保存
        self._did = device_info["did"]
        self._api: JingDongXiotApi = api
        self._info: JoyDeviceDetail = device_info
        self._device: Jdznsd01sy | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_light_{self._did}"

        # 必须：实体名称
        self._attr_name: str = device_info.get("additional", {}).get("name", self._did)

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

        # if not device_info["summary"]["online"]:
        #     self._attr_available: bool = False

        if isinstance(controller, Jdznsd01sy):
            self._device: Jdznsd01sy = controller
            _LOGGER.info("Init: %s", self._did)
        else:
            self._device = None
            self._attr_available: bool = False
            _LOGGER.error("Init error: %s ", {type(controller).__name__})

    # ------------------------------
    # 第三步：必须实现的属性（HA 读取状态用）
    # ------------------------------
    # @property
    # def is_on(self) -> bool:
    #     """Get OnOff Status."""
    #     if self._device is None:
    #         return False
    #     return True
    #     # return self._device.light_().on_().get_value()

    # @property
    # def brightness(self) -> int | None:
    #     """Get Brightness."""
    #     if self._device is None:
    #         return None
    #     return 80
    #     # return self._device.light_().brightness_().get_value()

    # @property
    # def color_temp_kelvin(self) -> int | None:
    #     """Get Color Temperature."""
    #     if self._device is None:
    #         return None
    #     return 2700

    # # ------------------------------
    # # 修复点3：必须实现 color_mode 属性（HA 2026 强制要求）
    # # ------------------------------
    # @property
    # def color_mode(self) -> ColorMode | None:
    #     """Get Color Mode."""
    #     return self._color_mode

    # ------------------------------
    # 第四步：必须实现的控制方法（HA 操作灯时调用）
    # ------------------------------
    async def async_turn_on(self, **kwargs) -> None:
        """Set On."""
        _LOGGER.info("Turn On: %s", kwargs)

        # 1. 标记灯为开启
        self._attr_is_on = True

        # 2. 解析 RGB 颜色（如果用户设置了颜色）
        # if rgb := kwargs.get("rgb_color"):
        #     self._rgb_color = rgb
        #     self._color_mode = ColorMode.RGB  # 切换到 RGB 模式

        # 3. 解析色温（如果用户设置了色温）
        # if color_temp := kwargs.get("color_temp"):
        #     self._color_temp = color_temp
        #     self._color_mode = ColorMode.COLOR_TEMP  # 切换到色温模式

        # 4. 解析亮度（通用所有模式）
        if brightness := kwargs.get("brightness"):
            self._attr_brightness = brightness

        # ========================
        # 【你的核心业务逻辑】
        # 在这里写：发送指令到你的硬件/API/设备
        # 例：await self._device.turn_on(brightness, rgb, color_temp)
        # ========================

        # 通知 HA：状态已更新，刷新界面
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Set Off."""
        _LOGGER.info("Turn Off: %s", kwargs)

        self._attr_is_on = False

        # 通知 HA：状态已更新
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update Status."""
        self._attr_available = True
        self.async_write_ha_state()

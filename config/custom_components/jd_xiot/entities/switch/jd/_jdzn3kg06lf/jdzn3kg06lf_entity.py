"""Light Jdzn3kg06lf."""

import logging

from custom_components.jd_xiot.core.api import JingDongXiotApi
from custom_components.jd_xiot.core.typedef.joy_device_detail import JoyDeviceDetail
from custom_components.jd_xiot.entities.switch.jd_switch_mapping import (
    register_switch_entity,
)
from xiot_core.support.typedef.controller.device_controller import DeviceController
from xiot_core_device_controller.jd._switch._jdzn3kg06lf.jdzn3kg06lf import Jdzn3kg06lf

from homeassistant.components.switch import SwitchEntity

_LOGGER = logging.getLogger(__name__)

@register_switch_entity
class Jdzn3kg06lfEntity1(SwitchEntity):
    """Jdzn3kg06lf Entity(1)."""

    TYPE: str = Jdzn3kg06lf.TYPE

    def __init__(
        self,
        controller: DeviceController,
        api: JingDongXiotApi,
        detail: JoyDeviceDetail,
    ) -> None:
        """Init Switch Entity."""

        # 保存
        self._api: JingDongXiotApi = api
        self._detail: JoyDeviceDetail = detail
        self._device: Jdzn3kg06lf | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_light_{controller.did}_1"

        # 必须：实体名称
        self._attr_name: str = detail.get("additional", {}).get("name", detail["did"])

        # 实体可用
        self._attr_available: bool = True

        # 初始状态
        self._attr_is_on: bool = False

        if isinstance(controller, Jdzn3kg06lf):
            self._device: Jdzn3kg06lf = controller
            self._device.set_operator(
                api.set_property, api.invoke_action, detail["userDeviceId"]
            )
            _LOGGER.info("Init: %s", detail["did"])
        else:
            self._device = None
            self._attr_available: bool = False
            _LOGGER.error("Init error: %s ", {type(controller).__name__})

    async def async_turn_on(self, **kwargs) -> None:
        """Set On."""
        _LOGGER.info("Turn On: %s", kwargs)

        try:
            await self._device.switch6_().on_().set(True)
            self._attr_is_on = True
        except ValueError as e:
            _LOGGER.error("Turn On Error: %s", e)

        # 通知 HA：状态已更新，刷新界面
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Set Off."""
        _LOGGER.info("Turn Off: %s", kwargs)

        try:
            await self._device.switch6_().on_().set(False)
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

@register_switch_entity
class Jdzn3kg06lfEntity2(SwitchEntity):
    """Jdzn3kg06lf Entity(2)."""

    TYPE: str = Jdzn3kg06lf.TYPE

    def __init__(
        self,
        controller: DeviceController,
        api: JingDongXiotApi,
        detail: JoyDeviceDetail,
    ) -> None:
        """Init Switch Entity."""

        # 保存
        self._api: JingDongXiotApi = api
        self._detail: JoyDeviceDetail = detail
        self._device: Jdzn3kg06lf | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_light_{controller.did}_2"

        # 必须：实体名称
        self._attr_name: str = detail.get("additional", {}).get("name", detail["did"])

        # 实体可用
        self._attr_available: bool = True

        # 初始状态
        self._attr_is_on: bool = False

        if isinstance(controller, Jdzn3kg06lf):
            self._device: Jdzn3kg06lf = controller
            self._device.set_operator(
                api.set_property, api.invoke_action, detail["userDeviceId"]
            )
            _LOGGER.info("Init: %s", detail["did"])
        else:
            self._device = None
            self._attr_available: bool = False
            _LOGGER.error("Init error: %s ", {type(controller).__name__})

    async def async_turn_on(self, **kwargs) -> None:
        """Set On."""
        _LOGGER.info("Turn On: %s", kwargs)

        try:
            await self._device.switch7_().on_().set(True)
            self._attr_is_on = True
        except ValueError as e:
            _LOGGER.error("Turn On Error: %s", e)

        # 通知 HA：状态已更新，刷新界面
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Set Off."""
        _LOGGER.info("Turn Off: %s", kwargs)

        try:
            await self._device.switch7_().on_().set(False)
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

@register_switch_entity
class Jdzn3kg06lfEntity3(SwitchEntity):
    """Jdzn3kg06lf Entity(3)."""

    TYPE: str = Jdzn3kg06lf.TYPE

    def __init__(
        self,
        controller: DeviceController,
        api: JingDongXiotApi,
        detail: JoyDeviceDetail,
    ) -> None:
        """Init Switch Entity."""

        # 保存
        self._api: JingDongXiotApi = api
        self._detail: JoyDeviceDetail = detail
        self._device: Jdzn3kg06lf | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_light_{controller.did}_3"

        # 必须：实体名称
        self._attr_name: str = detail.get("additional", {}).get("name", detail["did"])

        # 实体可用
        self._attr_available: bool = True

        # 初始状态
        self._attr_is_on: bool = False

        if isinstance(controller, Jdzn3kg06lf):
            self._device: Jdzn3kg06lf = controller
            self._device.set_operator(
                api.set_property, api.invoke_action, detail["userDeviceId"]
            )
            _LOGGER.info("Init: %s", detail["did"])
        else:
            self._device = None
            self._attr_available: bool = False
            _LOGGER.error("Init error: %s ", {type(controller).__name__})

    async def async_turn_on(self, **kwargs) -> None:
        """Set On."""
        _LOGGER.info("Turn On: %s", kwargs)

        try:
            await self._device.switch8_().on_().set(True)
            self._attr_is_on = True
        except ValueError as e:
            _LOGGER.error("Turn On Error: %s", e)

        # 通知 HA：状态已更新，刷新界面
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Set Off."""
        _LOGGER.info("Turn Off: %s", kwargs)

        try:
            await self._device.switch8_().on_().set(False)
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

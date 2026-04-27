"""Light DeviceJdzn1kg01lf."""

import logging

from custom_components.jd_xiot.core.api import JingDongXiotApi
from custom_components.jd_xiot.core.typedef.joy_device_detail import JoyDeviceDetail
from custom_components.jd_xiot.entities.switch.jd_switch_mapping import (
    register_switch_entity,
)
from xiot_core.support.typedef.controller.device_controller import DeviceController
from xiot_core_device_controller.jd._switch._jdzn1kg01lf.device_jdzn1kg01lf import (
    DeviceJdzn1kg01lf,
)

from homeassistant.components.switch import SwitchEntity

_LOGGER = logging.getLogger(__name__)

@register_switch_entity
class DeviceJdzn1kg01lfEntity(SwitchEntity):
    """DeviceJdzn1kg01lf Entity."""

    TYPE: str = DeviceJdzn1kg01lf.TYPE

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
        self._device: DeviceJdzn1kg01lf | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_light_{controller.did}"

        # 必须：实体名称
        self._attr_name: str = detail.get("additional", {}).get("name", detail["did"])

        # 实体可用
        self._attr_available: bool = True

        # 初始状态
        self._attr_is_on: bool = False

        if isinstance(controller, DeviceJdzn1kg01lf):
            self._device: DeviceJdzn1kg01lf = controller
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
            await self._device.service_switch().property_on().set(True)
        except ValueError as e:
            _LOGGER.error("Turn On Error: %s", e)

        self._attr_is_on = True

        # 通知 HA：状态已更新，刷新界面
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Set Off."""
        _LOGGER.info("Turn Off: %s", kwargs)

        try:
            await self._device.service_switch().property_on().set(False)
        except ValueError as e:
            _LOGGER.error("Turn Off Error: %s", e)

        self._attr_is_on = False

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

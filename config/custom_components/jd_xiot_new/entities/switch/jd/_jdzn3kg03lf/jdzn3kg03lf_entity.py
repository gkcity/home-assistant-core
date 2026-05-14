"""Light DeviceJdzn3kg03lf."""

import logging

from custom_components.jd_xiot_new.api.const import DOMAIN
from custom_components.jd_xiot_new.api.jd_client import JingDongClient
from custom_components.jd_xiot_new.api.typedef.joy_device_detail import JoyDeviceDetail
from custom_components.jd_xiot_new.entities.switch.jd_switch_mapping import (
    register_switch_entity,
)
from xiot_core.support.typedef.controller.device_controller import DeviceController
from xiot_core_device_controller.jd._switch._jdzn3kg03lf.device_jdzn3kg03lf import (
    DeviceJdzn3kg03lf,
)

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.device_registry import DeviceInfo

_LOGGER = logging.getLogger(__name__)

@register_switch_entity
class DeviceJdzn3kg03lfEntity1(SwitchEntity):
    """DeviceJdzn3kg03lf Entity(1)."""

    TYPE: str = DeviceJdzn3kg03lf.TYPE

    def __init__(
        self,
        controller: DeviceController,
        client: JingDongClient,
        detail: JoyDeviceDetail,
    ) -> None:
        """Init Switch Entity."""

        # 保存
        self._client: JingDongClient = client
        self._detail: JoyDeviceDetail = detail
        self._device: DeviceJdzn3kg03lf | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_new_{controller.did}_1"

        # 必须：实体名称
        self._attr_name: str = detail.get("additional", {}).get("name", detail["did"])

        # 实体可用
        self._attr_available: bool = True

        # 初始状态
        self._attr_is_on: bool = False

        # 设备信息
        self._attr_device_info = DeviceInfo(
            identifiers = {(DOMAIN, detail["did"])},
            name = detail['additional']['name'],
            manufacturer = "京东小家",
            model = f"{detail["summary"].type.model}",
        )

        if isinstance(controller, DeviceJdzn3kg03lf):
            self._device: DeviceJdzn3kg03lf = controller
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

    async def async_turn_on(self, **kwargs) -> None:
        """Set On."""
        _LOGGER.info("Turn On: %s", kwargs)

        try:
            await self._device.service_switch6().property_on().set(True)
        except ValueError as e:
            _LOGGER.error("Turn On Error: %s", e)

        self._attr_is_on = True

        # 通知 HA：状态已更新，刷新界面
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Set Off."""
        _LOGGER.info("Turn Off: %s", kwargs)

        try:
            await self._device.service_switch6().property_on().set(False)
        except ValueError as e:
            _LOGGER.error("Turn Off Error: %s", e)

        self._attr_is_on = False

        # 通知 HA：状态已更新
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update Status."""
        _LOGGER.info("Update")

        try:
            onoff = await self._device.service_switch6().property_on().get()
            self._attr_is_on = bool(onoff)

            name = await self._device.service_switch6().property_name().get()
            if name is not None and name.strip() != "":
                self._attr_name = name

            self._attr_available = True
        except ValueError as e:
            _LOGGER.error("Update Error: %s", e)
            self._attr_available = False

        self.async_write_ha_state()

@register_switch_entity
class DeviceJdzn3kg03lfEntity2(SwitchEntity):
    """DeviceJdzn3kg03lf Entity(2)."""

    TYPE: str = DeviceJdzn3kg03lf.TYPE

    def __init__(
        self,
        controller: DeviceController,
        client: JingDongClient,
        detail: JoyDeviceDetail,
    ) -> None:
        """Init Switch Entity."""

        # 保存
        self._client: JingDongClient = client
        self._detail: JoyDeviceDetail = detail
        self._device: DeviceJdzn3kg03lf | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_new_{controller.did}_2"

        # 必须：实体名称
        self._attr_name: str = detail.get("additional", {}).get("name", detail["did"])

        # 实体可用
        self._attr_available: bool = True

        # 初始状态
        self._attr_is_on: bool = False

        # 设备信息
        self._attr_device_info = DeviceInfo(
            identifiers = {(DOMAIN, detail["did"])},
            name = detail['additional']['name'],
            manufacturer = "京东小家",
            model = f"{detail["summary"].type.model}",
        )

        if isinstance(controller, DeviceJdzn3kg03lf):
            self._device: DeviceJdzn3kg03lf = controller
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

    async def async_turn_on(self, **kwargs) -> None:
        """Set On."""
        _LOGGER.info("Turn On: %s", kwargs)

        try:
            await self._device.service_switch7().property_on().set(True)
        except ValueError as e:
            _LOGGER.error("Turn On Error: %s", e)

        self._attr_is_on = True

        # 通知 HA：状态已更新，刷新界面
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Set Off."""
        _LOGGER.info("Turn Off: %s", kwargs)

        try:
            await self._device.service_switch7().property_on().set(False)
        except ValueError as e:
            _LOGGER.error("Turn Off Error: %s", e)

        self._attr_is_on = False

        # 通知 HA：状态已更新
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update Status."""
        _LOGGER.info("Update")

        try:
            onoff = await self._device.service_switch7().property_on().get()
            self._attr_is_on = bool(onoff)

            name = await self._device.service_switch7().property_name().get()
            if name is not None and name.strip() != "":
                self._attr_name = name

            self._attr_available = True
        except ValueError as e:
            _LOGGER.error("Update Error: %s", e)
            self._attr_available = False

        self.async_write_ha_state()

@register_switch_entity
class DeviceJdzn3kg03lfEntity3(SwitchEntity):
    """DeviceJdzn3kg03lf Entity(3)."""

    TYPE: str = DeviceJdzn3kg03lf.TYPE

    def __init__(
        self,
        controller: DeviceController,
        client: JingDongClient,
        detail: JoyDeviceDetail,
    ) -> None:
        """Init Switch Entity."""

        # 保存
        self._client: JingDongClient = client
        self._detail: JoyDeviceDetail = detail
        self._device: DeviceJdzn3kg03lf | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_new_{controller.did}_3"

        # 必须：实体名称
        self._attr_name: str = detail.get("additional", {}).get("name", detail["did"])

        # 实体可用
        self._attr_available: bool = True

        # 初始状态
        self._attr_is_on: bool = False

        # 设备信息
        self._attr_device_info = DeviceInfo(
            identifiers = {(DOMAIN, detail["did"])},
            name = detail['additional']['name'],
            manufacturer = "京东小家",
            model = f"{detail["summary"].type.model}",
        )

        if isinstance(controller, DeviceJdzn3kg03lf):
            self._device: DeviceJdzn3kg03lf = controller
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

    async def async_turn_on(self, **kwargs) -> None:
        """Set On."""
        _LOGGER.info("Turn On: %s", kwargs)

        try:
            await self._device.service_switch8().property_on().set(True)
        except ValueError as e:
            _LOGGER.error("Turn On Error: %s", e)

        self._attr_is_on = True

        # 通知 HA：状态已更新，刷新界面
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Set Off."""
        _LOGGER.info("Turn Off: %s", kwargs)

        try:
            await self._device.service_switch8().property_on().set(False)
        except ValueError as e:
            _LOGGER.error("Turn Off Error: %s", e)

        self._attr_is_on = False

        # 通知 HA：状态已更新
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Update Status."""
        _LOGGER.info("Update")

        try:
            onoff = await self._device.service_switch8().property_on().get()
            self._attr_is_on = bool(onoff)

            name = await self._device.service_switch8().property_name().get()
            if name is not None and name.strip() != "":
                self._attr_name = name

            self._attr_available = True
        except ValueError as e:
            _LOGGER.error("Update Error: %s", e)
            self._attr_available = False

        self.async_write_ha_state()

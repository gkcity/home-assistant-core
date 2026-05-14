"""Cover DeviceJdzncl01dy."""

import logging
from typing import Any

from custom_components.jd_xiot_new.api.const import DOMAIN
from custom_components.jd_xiot_new.api.jd_client import JingDongClient
from custom_components.jd_xiot_new.api.typedef.joy_device_detail import JoyDeviceDetail
from custom_components.jd_xiot_new.entities.cover.jd_cover_mapping import (
    register_cover_entity,
)
from xiot_core.support.typedef.controller.device_controller import DeviceController
from xiot_core_device_controller.jd._curtain._jdzncl01dy.device_jdzncl01dy import (
    DeviceJdzncl01dy,
)

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.helpers.device_registry import DeviceInfo

_LOGGER = logging.getLogger(__name__)


@register_cover_entity
class DeviceJdzncl01dyEntity(CoverEntity):
    """DeviceJdzncl01dy Entity."""

    TYPE: str = DeviceJdzncl01dy.TYPE

    def __init__(
        self,
        controller: DeviceController,
        client: JingDongClient,
        detail: JoyDeviceDetail,
    ) -> None:
        """Init Cover Entity."""
        self._client: JingDongClient = client
        self._detail: JoyDeviceDetail = detail
        self._device: DeviceJdzncl01dy | None = None

        # 必须：声明实体唯一 ID（不能重复，用于 HA 识别设备）
        self._attr_unique_id: str = f"jd_xiot_new_{controller.did}"

        # 必须：实体名称
        self._attr_name: str = detail.get("additional", {}).get("name", detail["did"])

        # 实体可用
        self._attr_available: bool = True

        # HA 窗帘支持的功能
        # 支持：打开、关闭、暂停、百分比位置
        self._attr_supported_features = (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.STOP
            | CoverEntityFeature.SET_POSITION
        )

        # 初始状态：关闭
        self._attr_is_closed: bool = False
        self._attr_current_cover_position: int = 0  # 0=关 100=开

        # 设备信息
        self._attr_device_info = DeviceInfo(
            identifiers = {(DOMAIN, detail["did"])},
            name = detail['additional']['name'],
            manufacturer = "京东小家",
            model = f"{detail["summary"].type.model}",
        )

        # 绑定设备控制器
        if isinstance(controller, DeviceJdzncl01dy):
            self._device = controller
            self._device.set_operator(
                client.get_property,
                client.set_property,
                client.invoke_action,
                detail["userDeviceId"]
            )
            _LOGGER.info("初始化窗帘成功: %s", self._attr_unique_id)
        else:
            self._device = None
            self._attr_available = False
            _LOGGER.error("窗帘控制器类型不匹配: %s", type(controller).__name__)

    # ------------------------------------------------------
    # 核心：打开窗帘
    # ------------------------------------------------------
    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open."""
        _LOGGER.info("窗帘打开: %s", self._attr_unique_id)
        try:
            await self._device.service_curtain().action_open_curtain().invoke()
        except ValueError as e:
            _LOGGER.error("打开窗帘失败: %s", e)

        self._attr_current_cover_position = 100
        self._attr_is_closed = False
        self.async_write_ha_state()

    # ------------------------------------------------------
    # 核心：关闭窗帘
    # ------------------------------------------------------
    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close."""
        _LOGGER.info("窗帘关闭: %s", self._attr_unique_id)

        try:
            await self._device.service_curtain().action_close_curtain().invoke()
        except ValueError as e:
            _LOGGER.error("关闭窗帘失败: %s", e)

        self._attr_current_cover_position = 0
        self._attr_is_closed = True
        self.async_write_ha_state()

    # ------------------------------------------------------
    # 核心：暂停窗帘
    # ------------------------------------------------------
    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop."""
        _LOGGER.info("窗帘暂停: %s", self._attr_unique_id)
        try:
            await self._device.service_curtain().action_stop_curtain().invoke()
        except ValueError as e:
            _LOGGER.error("暂停窗帘失败: %s", e)
        self.async_write_ha_state()

    # ------------------------------------------------------
    # 核心：设置百分比位置（0~100）
    # ------------------------------------------------------
    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set Target Position."""
        position: int = kwargs.get(ATTR_POSITION, 0)
        _LOGGER.info("设置窗帘位置: %s -> %s", self._attr_unique_id, position)

        try:
            await self._device.service_curtain().property_target_position().set(position)
        except ValueError as e:
            _LOGGER.error("设置窗帘位置失败: %s", e)

        self._attr_current_cover_position = position
        self._attr_is_closed = position == 0
        self.async_write_ha_state()

    # ------------------------------------------------------
    # HA 自动刷新状态
    # ------------------------------------------------------
    async def async_update(self) -> None:
        """Update Status."""
        _LOGGER.info("Update")

        self._attr_available = True

        # try:
        #     current_position = await self._device.service_curtain().property_current_position().get()
        #     self._attr_current_cover_position = current_position or 0
        #     self._attr_is_closed = self._attr_current_cover_position == 0
        #     self._attr_available = True
        # except ValueError as e:
        #     _LOGGER.error("Update Error: %s", e)
        #     self._attr_available = False

        self.async_write_ha_state()

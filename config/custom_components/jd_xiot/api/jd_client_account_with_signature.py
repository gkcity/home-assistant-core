"""JingDong Client Account implementation."""

import logging

from xiot_core.spec.typedef.operation.action_operation import ActionOperation
from xiot_core.spec.typedef.operation.property_operation import PropertyOperation

from .jd_client import JingDongClient
from .typedef.joy_device_detail import JoyDeviceDetail
from .typedef.joy_house import JoyHouse

_LOGGER = logging.getLogger(__name__)

class JingdongClientAccountWithSignatureImpl(JingDongClient):
    """JingDong Client Account implementation."""

    async def async_get_houses(self) -> tuple[bool, list[JoyHouse]]:
        """Get Houses."""
        return True, []

    async def async_get_devices(self) -> list[JoyDeviceDetail]:
        """Get Devices."""
        return []

    async def async_get_devices_info(self, deviceIds: list[str]) -> list[JoyDeviceDetail]:
        """Get Device."""
        return []

    async def set_property(self, p: PropertyOperation) -> PropertyOperation:
        """Set Property."""
        return p

    async def get_property(self, p: PropertyOperation) -> PropertyOperation:
        """Get Property."""
        return p

    async def invoke_action(self, a: ActionOperation) -> ActionOperation:
        """Invoke Action."""
        return a

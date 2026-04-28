"""Switch mapping for DeviceController."""

import logging

from custom_components.jd_xiot.api.jd_client import JingDongClient
from custom_components.jd_xiot.api.typedef.joy_device_detail import JoyDeviceDetail
from xiot_core_device_controller.device_mapping import create_device_controller

from homeassistant.components.switch import SwitchEntity

_LOGGER = logging.getLogger(__name__)

_classes: dict[str, list[type[SwitchEntity]]] = {}

def register_switch_entity(cls):
    """Register Switch Entity.

    Args:
        cls: SwitchEntity

    Returns:
        SwitchEntity class
    """
    _LOGGER.info("Register: %s", cls.TYPE)
    _classes.setdefault(cls.TYPE, []).append(cls)
    return cls


def create_switch_entity(
    device_type: str, client: JingDongClient, detail: JoyDeviceDetail
) -> list[SwitchEntity]:
    """Create Switch Entity.

    Args:
        device_type: DeviceType
        api: API
        detail: JoyDeviceDetail

    Returns:
        Switch Entity or None
    """

    device = create_device_controller(device_type)
    if device is None:
        _LOGGER.info("Create Device Controller failed: %s", device_type)
        return []
    device.did = detail["did"]

    if device.type.name != "switch":
        _LOGGER.info("Ignore non-switch equipment: %s", device_type)
        return []

    _LOGGER.info("Create Switch Entity: %s (entities: %d)", device_type, len(_classes))

    classes = _classes.get(device_type)
    if classes is None:
        _LOGGER.info("Entity Class not found: %s", device_type)
        return []

    return [clazz(device, client, detail) for clazz in classes]

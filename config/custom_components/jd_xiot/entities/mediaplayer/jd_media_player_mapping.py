"""MediaPlayer mapping for DeviceController."""

import logging

from custom_components.jd_xiot.api.jd_client import JingDongClient
from custom_components.jd_xiot.api.typedef.joy_device_detail import JoyDeviceDetail
from xiot_core_device_controller.device_mapping import create_device_controller

from homeassistant.components.media_player import MediaPlayerEntity

_LOGGER = logging.getLogger(__name__)


_entities: dict[str, type[MediaPlayerEntity]] = {}


def register_media_player_entity(cls):
    """注册灯光实体类到实体注册表中.

    Args:
        cls: 待注册的实体类，需包含 TYPE 类属性

    Returns:
        传入的设备控制器类
    """
    _LOGGER.info("Register: %s", cls.TYPE)
    _entities[cls.TYPE] = cls
    return cls


def create_media_player(
    device_type: str, client: JingDongClient, detail: JoyDeviceDetail
) -> MediaPlayerEntity | None:
    """根据 TYPE 字符串创建灯光实例.

    Args:
        device_type: Device Type
        client: JingDongClient
        detail: Device Detail Info

    Returns:
        初始化后的灯光实例，若类型不存在则返回 None
    """

    device = create_device_controller(device_type)
    if device is None:
        _LOGGER.info("Create Device Controller failed: %s", device_type)
        return None
    device.did = detail["did"]

    clazz = _entities.get(device_type)
    if clazz is None:
        _LOGGER.info("Entity Class not found: %s", device_type)
        return None

    return clazz(device, client, detail)

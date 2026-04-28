"""JoyHouse for the JingDong XIoT integration."""

from typing import Any, TypedDict

from .joy_device import JoyDevice, joy_device_decode_array


class JoyRoom(TypedDict):
    """Represents a room containing devices."""

    id: int
    name: str
    devices: list[JoyDevice]


def joy_room_decode_array(json_array: list[dict[str, Any]]) -> list[JoyRoom]:
    """将京东IoT返回的JsonArray解码为JoyRoom列表.

    Args:
        json_array: 从接口获取的原始JSON数组(字典列表)

    Returns:
        类型安全的JoyRoom列表

    Raises:
        ValueError: 当JSON数据缺少必要字段或类型不匹配时抛出
    """
    joy_room_list: list[JoyRoom] = []

    for idx, item in enumerate(json_array):
        # 校验必要字段是否存在
        if "roomId" not in item or "name" not in item:
            raise ValueError(
                f"第{idx}个房屋数据缺少必要字段,必须包含roomId和name: {item}"
            )

        # 校验字段类型（id必须是int，name必须是str）
        try:
            room_id: int = int(item["roomId"])
            room_name: str = str(item["name"])
            devices: list[JoyDevice] = joy_device_decode_array(item["devices"])
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"第{idx}个房源数据字段类型错误: roomId必须为整数, name必须为字符串。错误详情: {e}"
            ) from e

        # 构造JoyRoom对象并添加到列表
        joy_room: JoyRoom = {"id": room_id, "name": room_name, "devices": devices}
        joy_room_list.append(joy_room)

    return joy_room_list


# 可选：添加一个容错版本（不抛出异常，跳过无效数据），适用于非核心场景
def joy_room_decode_array_safe(json_array: list[dict[str, Any]]) -> list[JoyRoom]:
    """容错版解码函数 - 跳过无效数据，不抛出异常（适用于非核心场景）.

    Args:
        json_array: 从接口获取的原始JSON数组(字典列表)

    Returns:
        过滤后的有效JoyRoom列表
    """
    joy_room_list: list[JoyRoom] = []

    for item in json_array:
        if not isinstance(item, dict):
            continue

        # 尝试提取并转换字段
        try:
            room_id: int = int(item.get("roomId", ""))
            room_name: str = str(item.get("name", ""))
            devices: list[JoyDevice] = joy_device_decode_array(item.get("devices", []))
        except (TypeError, ValueError):
            continue

        # 确保id和name不为空（可选校验）
        if room_id and room_name:
            joy_room: JoyRoom = {"id": room_id, "name": room_name, "devices": devices}
            joy_room_list.append(joy_room)

    return joy_room_list

"""JoyHouse for the JingDong XIoT integration."""

from typing import Any, TypedDict

from .joy_room import JoyRoom, joy_room_decode_array


class JoyHouse(TypedDict):
    """Represents a house containing rooms and devices."""

    id: int
    name: str
    rooms: list[JoyRoom]


def get_all_user_device_ids(house: JoyHouse) -> list[int]:
    """Extract all userDeviceId from a house recursively. Strong typing, safe, no exceptions."""

    user_device_ids: list[int] = []

    # 遍历所有房间
    for room in house["rooms"]:
        user_device_ids.extend(device["userDeviceId"] for device in room["devices"])

        # 遍历每个房间下的所有设备
        # for device in room["devices"]:
        #     # user_device_ids.append(device["userDeviceId"])

    return user_device_ids


def joy_house_decode_array(json_array: list[dict[str, Any]]) -> list[JoyHouse]:
    """将京东IoT返回的JsonArray解码为JoyHouse列表.

    Args:
        json_array: 从接口获取的原始JSON数组(字典列表)

    Returns:
        类型安全的JoyHouse列表

    Raises:
        ValueError: 当JSON数据缺少必要字段或类型不匹配时抛出
    """
    joy_house_list: list[JoyHouse] = []

    for idx, item in enumerate(json_array):
        # 校验必要字段是否存在
        if "houseId" not in item or "name" not in item:
            raise ValueError(
                f"第{idx}个房屋数据缺少必要字段,必须包含houseId和name: {item}"
            )

        # 校验字段类型（id必须是int，name必须是str）
        try:
            house_id: int = int(item["houseId"])
            house_name: str = str(item["name"])
            rooms: list[JoyRoom] = joy_room_decode_array(item["rooms"])
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"第{idx}个房源数据字段类型错误: houseId必须为整数, name必须为字符串。错误详情: {e}"
            ) from e

        # 构造JoyHouse对象并添加到列表
        joy_house: JoyHouse = {"id": house_id, "name": house_name, "rooms": rooms}
        joy_house_list.append(joy_house)

    return joy_house_list


# 可选：添加一个容错版本（不抛出异常，跳过无效数据），适用于非核心场景
def joy_house_decode_array_safe(json_array: list[dict[str, Any]]) -> list[JoyHouse]:
    """容错版解码函数 - 跳过无效数据，不抛出异常（适用于非核心场景）.

    Args:
        json_array: 从接口获取的原始JSON数组(字典列表)

    Returns:
        过滤后的有效JoyHouse列表
    """
    joy_house_list: list[JoyHouse] = []

    for item in json_array:
        if not isinstance(item, dict):
            continue

        # 尝试提取并转换字段
        try:
            house_id: int = int(item.get("houseId", ""))
            house_name: str = str(item.get("name", ""))
            rooms: list[JoyRoom] = joy_room_decode_array(item.get["rooms", []])
        except TypeError, ValueError:
            continue

        # 确保id和name不为空（可选校验）
        if house_id and house_name:
            joy_house: JoyHouse = {"id": house_id, "name": house_name, "rooms": rooms}
            joy_house_list.append(joy_house)

    return joy_house_list

"""JoyDevice TypedDict definition."""

from typing import Any, TypedDict


class JoyDevice(TypedDict):
    """Represents a device inside a room."""

    userDeviceId: int
    did: str


def joy_device_decode_array(json_array: list[dict[str, Any]]) -> list[JoyDevice]:
    """将京东IoT返回的JsonArray解码为JoyDevice列表.

    Args:
        json_array: 从接口获取的原始JSON数组(字典列表)

    Returns:
        类型安全的JoyDevice列表

    Raises:
        ValueError: 当JSON数据缺少必要字段或类型不匹配时抛出
    """
    joy_device_list: list[JoyDevice] = []

    for idx, item in enumerate(json_array):
        # 校验必要字段是否存在
        if "did" not in item or "userDeviceId" not in item:
            raise ValueError(
                f"第{idx}个房屋数据缺少必要字段,必须包含did和userDeviceId: {item}"
            )

        # 校验字段类型（userDeviceId必须是int，did必须是str）
        try:
            user_device_id = int(item["userDeviceId"])
            did = str(item["did"])
        except (TypeError, ValueError) as e:
            raise ValueError(
                f"第{idx}个房源数据字段类型错误: userDeviceId必须为整数, did必须为字符串。错误详情: {e}"
            ) from e

        # 构造JoyHouse对象并添加到列表
        joy_device: JoyDevice = {"userDeviceId": user_device_id, "did": did}
        joy_device_list.append(joy_device)

    return joy_device_list


# 可选：添加一个容错版本（不抛出异常，跳过无效数据），适用于非核心场景
def joy_device_decode_array_safe(json_array: list[dict[str, Any]]) -> list[JoyDevice]:
    """容错版解码函数 - 跳过无效数据，不抛出异常（适用于非核心场景）.

    Args:
        json_array: 从接口获取的原始JSON数组（字典列表）

    Returns:
        过滤后的有效JoyHouse列表
    """
    joy_device_list: list[JoyDevice] = []

    for item in json_array:
        if not isinstance(item, dict):
            continue

        # 尝试提取并转换字段
        try:
            user_device_id = int(item.get("userDeviceId", ""))
            did = str(item.get("did", ""))
        except (TypeError, ValueError):
            continue

        # 确保id和name不为空（可选校验）
        if user_device_id and did:
            joy_device: JoyDevice = {"userDeviceId": user_device_id, "did": did}
            joy_device_list.append(joy_device)

    return joy_device_list

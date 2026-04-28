"""JoyHouse for the JingDong XIoT integration."""

from typing import Any, TypedDict

from .summary import Summary, summary_decode


class JoyDeviceAdditional(TypedDict):
    """Additional metadata for a device."""

    productId: int
    modelId: int
    name: str
    userDeviceId: int


class JoyDeviceDetail(TypedDict):
    """Detailed device information."""

    userDeviceId: int
    did: str
    summary: Summary
    additional: JoyDeviceAdditional

def joy_device_additional_decode(data: dict[str, Any]) -> JoyDeviceAdditional:
    """Convert a dict to JoyDeviceAdditional. Strict type checking: raises KeyError if fields missing."""

    # 强制获取字段，不存在直接抛 KeyError(强类型风格)
    productId: int = data["productId"]
    modelId: int = data["modelId"]
    userDeviceId: int = data["userDeviceId"]
    name: str = data["name"]

    # 强制类型校验（确保不会把 int/None 混进去）
    if not isinstance(name, str):
        raise TypeError(f"name 必须是字符串，实际类型：{type(name).__name__}")

    if not isinstance(productId, int):
        raise TypeError(f"productId 必须是整型，实际类型：{type(productId).__name__}")

    if not isinstance(modelId, int):
        raise TypeError(f"modelId 必须是整型，实际类型：{type(modelId).__name__}")

    if not isinstance(userDeviceId, int):
        raise TypeError(f"userDeviceId 必须是整型，实际类型：{type(userDeviceId).__name__}")

    # 强类型返回
    return JoyDeviceAdditional(
        productId=productId, modelId=modelId, name=name, userDeviceId=userDeviceId
    )

#       "additional": {
#         "name": "",
#         "userDeviceId": 0,
#         "roomId": 0,
#         "productName": null,
#         "productIcon": null,
#         "updateTime": 1776657818
#       }
def joy_device_additional_decode_local(data: dict[str, Any]) -> JoyDeviceAdditional:
    """Convert a dict to JoyDeviceAdditional. Strict type checking: raises KeyError if fields missing."""

    # 强制获取字段，不存在直接抛 KeyError(强类型风格)
    productId: int = 0
    modelId: int = 0
    userDeviceId: int = data["userDeviceId"]
    name: str = data.get("name") or data.get("productName") or "?"

    # 强制类型校验（确保不会把 int/None 混进去）
    if not isinstance(name, str):
        raise TypeError(f"name 必须是字符串，实际类型：{type(name).__name__}")

    if not isinstance(productId, int):
        raise TypeError(f"productId 必须是整型，实际类型：{type(productId).__name__}")

    if not isinstance(modelId, int):
        raise TypeError(f"modelId 必须是整型，实际类型：{type(modelId).__name__}")

    if not isinstance(userDeviceId, int):
        raise TypeError(f"userDeviceId 必须是整型，实际类型：{type(userDeviceId).__name__}")

    # 强类型返回
    return JoyDeviceAdditional(
        productId=productId, modelId=modelId, name=name, userDeviceId=userDeviceId
    )

def joy_device_additional_decode_safe(
    data: dict[str, Any] | None,
) -> JoyDeviceAdditional | None:
    """Safely convert a dict to JoyDeviceAdditional, return None on failure. Suitable for unstable device data in HA integration."""

    if not isinstance(data, dict):
        return None

    try:
        productId = int(data["productId"])
        modelId = int(data["modelId"])
        userDeviceId = int(data["userDeviceId"])
        name = str(data["name"])
        return JoyDeviceAdditional(
            productId=productId, modelId=modelId, name=name, userDeviceId=userDeviceId
        )
    except (KeyError, TypeError, ValueError):
        return None

def joy_device_detail_decode_array_local(data: list[Any]) -> list[JoyDeviceDetail]:
    """Convert a list to JoyDeviceDetail Array. Strict type checking: raises KeyError if fields missing."""

    return [joy_device_detail_decode_local(item) for item in data]

#     {
#       "device": {
#         "did": "YXFYOBYPS7FMXO7L@14775695",
#         "summary": {...}
#       },
#       "additional": {...}
#     }
def joy_device_detail_decode_local(data: dict[str, Any]) -> JoyDeviceDetail:
    """Convert a dict to JoyDeviceDetail. Strict type checking: raises KeyError if fields missing."""

    # 强制获取字段，不存在直接抛 KeyError（强类型风格）

    did: str = data.get("device", {}).get("did")
    userDeviceId: int = 0
    summary: Summary = summary_decode(data.get("device", {}).get("summary"))
    additional: JoyDeviceAdditional = joy_device_additional_decode_local(data["additional"])

    # 强制类型校验（确保不会把 int/None 混进去）
    if not isinstance(did, str):
        raise TypeError(f"did 必须是字符串，实际类型：{type(did)}")

    if not isinstance(userDeviceId, int):
        raise TypeError(f"userDeviceId 必须是整型，实际类型：{type(userDeviceId).__name__}")

    # 强类型返回
    return JoyDeviceDetail(
        did=did, userDeviceId=userDeviceId, summary=summary, additional=additional
    )

def joy_device_detail_decode_array(data: list[Any]) -> list[JoyDeviceDetail]:
    """Convert a list to JoyDeviceDetail Array. Strict type checking: raises KeyError if fields missing."""

    return [joy_device_detail_decode(item) for item in data]

def joy_device_detail_decode(data: dict[str, Any]) -> JoyDeviceDetail:
    """Convert a dict to JoyDeviceDetail. Strict type checking: raises KeyError if fields missing."""

    # 强制获取字段，不存在直接抛 KeyError（强类型风格）
    did: str = data["did"]
    userDeviceId: int = data["userDeviceId"]
    summary: Summary = summary_decode(data["summary"])
    additional: JoyDeviceAdditional = joy_device_additional_decode(data["additional"])

    # 强制类型校验（确保不会把 int/None 混进去）
    if not isinstance(did, str):
        raise TypeError(f"did 必须是字符串，实际类型：{type(did).__name__}")

    if not isinstance(userDeviceId, int):
        raise TypeError(f"userDeviceId 必须是布尔值，实际类型：{type(userDeviceId).__name__}")

    # 强类型返回
    return JoyDeviceDetail(
        did=did, userDeviceId=userDeviceId, summary=summary, additional=additional
    )


def joy_device_detail_decode_safe(
    data: dict[str, Any] | None,
) -> JoyDeviceDetail | None:
    """Safely convert a dict to JoyDeviceDetail, return None on failure. Suitable for unstable device data in HA integration."""

    if not isinstance(data, dict):
        return None

    try:
        did = str(data["did"])
        userDeviceId = int(data["userDeviceId"])
        summary: Summary = summary_decode(data["summary"])
        additional: JoyDeviceAdditional = joy_device_additional_decode(
            data["additional"]
        )
        return JoyDeviceDetail(
            did=did, userDeviceId=userDeviceId, summary=summary, additional=additional
        )
    except (KeyError, TypeError, ValueError):
        return None

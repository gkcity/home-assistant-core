"""JoyHouse for the JingDong XIoT integration."""

from typing import Any, TypedDict

from xiot_core.spec.codec.summary.summary_codec import SummaryCodec

# from .summary import Summary, summary_decode
from xiot_core.spec.typedef.summary.summary import Summary


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
    product_id: int = data["productId"]
    model_id: int = data["modelId"]
    user_device_id: int = data["userDeviceId"]
    name: str = data["name"]

    # 强制类型校验（确保不会把 int/None 混进去）
    if not isinstance(name, str):
        raise TypeError(f"name 必须是字符串，实际类型：{type(name).__name__}")

    if not isinstance(product_id, int):
        raise TypeError(f"productId 必须是整型，实际类型：{type(product_id).__name__}")

    if not isinstance(model_id, int):
        raise TypeError(f"modelId 必须是整型，实际类型：{type(model_id).__name__}")

    if not isinstance(user_device_id, int):
        raise TypeError(f"userDeviceId 必须是整型，实际类型：{type(user_device_id).__name__}")

    # 强类型返回
    return JoyDeviceAdditional(
        productId=product_id, modelId=model_id, name=name, userDeviceId=user_device_id
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
    product_id: int = 0
    model_id: int = 0
    user_device_id: int = data["userDeviceId"]
    name: str = data.get("name") or data.get("productName") or "?"

    # 强制类型校验（确保不会把 int/None 混进去）
    if not isinstance(name, str):
        raise TypeError(f"name 必须是字符串，实际类型：{type(name).__name__}")

    if not isinstance(product_id, int):
        raise TypeError(f"productId 必须是整型，实际类型：{type(product_id).__name__}")

    if not isinstance(model_id, int):
        raise TypeError(f"modelId 必须是整型，实际类型：{type(model_id).__name__}")

    if not isinstance(user_device_id, int):
        raise TypeError(f"userDeviceId 必须是整型，实际类型：{type(user_device_id).__name__}")

    # 强类型返回
    return JoyDeviceAdditional(
        productId=product_id, modelId=model_id, name=name, userDeviceId=user_device_id
    )

def joy_device_additional_decode_safe(
    data: dict[str, Any] | None,
) -> JoyDeviceAdditional | None:
    """Safely convert a dict to JoyDeviceAdditional, return None on failure. Suitable for unstable device data in HA integration."""

    if not isinstance(data, dict):
        return None

    try:
        product_id = int(data["productId"])
        model_id = int(data["modelId"])
        user_device_id = int(data["userDeviceId"])
        name = str(data["name"])
        return JoyDeviceAdditional(
            productId=product_id, modelId=model_id, name=name, userDeviceId=user_device_id
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
    _device = data.get("device", {})
    _summary = _device.get("summary", {})

    did: str = data.get("device", {}).get("did")
    user_device_id: int = 0
    summary: Summary | None = SummaryCodec.decode_single(_summary)
    additional: JoyDeviceAdditional = joy_device_additional_decode_local(data["additional"])

    # 强制类型校验（确保不会把 int/None 混进去）
    if not isinstance(did, str):
        raise TypeError(f"did 必须是字符串，实际类型：{type(did)}")

    if not isinstance(user_device_id, int):
        raise TypeError(f"userDeviceId 必须是整型，实际类型：{type(user_device_id).__name__}")

    if summary is None:
        raise TypeError("summary is None")

    # 强类型返回
    return JoyDeviceDetail(
        did=did, userDeviceId=user_device_id, summary=summary, additional=additional
    )

def joy_device_detail_decode_array(data: list[Any]) -> list[JoyDeviceDetail]:
    """Convert a list to JoyDeviceDetail Array. Strict type checking: raises KeyError if fields missing."""

    return [joy_device_detail_decode(item) for item in data]

def joy_device_detail_decode(data: dict[str, Any]) -> JoyDeviceDetail:
    """Convert a dict to JoyDeviceDetail. Strict type checking: raises KeyError if fields missing."""

    # 强制获取字段，不存在直接抛 KeyError（强类型风格）
    _device = data.get("device", {})
    _summary = _device.get("summary", {})

    did: str = data["did"]
    user_device_id: int = data["userDeviceId"]
    summary: Summary | None = SummaryCodec.decode_single(_summary)
    additional: JoyDeviceAdditional = joy_device_additional_decode(data["additional"])

    # 强制类型校验（确保不会把 int/None 混进去）
    if not isinstance(did, str):
        raise TypeError(f"did 必须是字符串，实际类型：{type(did).__name__}")

    if not isinstance(user_device_id, int):
        raise TypeError(f"userDeviceId 必须是布尔值，实际类型：{type(user_device_id).__name__}")

    if summary is None:
        raise TypeError("summary is None")

    # 强类型返回
    return JoyDeviceDetail(
        did=did, userDeviceId=user_device_id, summary=summary, additional=additional
    )

def joy_device_detail_decode_safe(
    data: dict[str, Any] | None,
) -> JoyDeviceDetail | None:
    """Safely convert a dict to JoyDeviceDetail, return None on failure. Suitable for unstable device data in HA integration."""

    if not isinstance(data, dict):
        return None

    try:
        _device = data.get("device", {})
        _summary = _device.get("summary", {})

        did = str(data["did"])
        user_device_id = int(data["userDeviceId"])
        summary: Summary | None = SummaryCodec.decode_single(_summary)
        additional: JoyDeviceAdditional = joy_device_additional_decode(
            data["additional"]
        )

        if summary is None:
            return None

        return JoyDeviceDetail(
            did=did, userDeviceId=user_device_id, summary=summary, additional=additional
        )
    except (KeyError, TypeError, ValueError):
        return None

"""Summary for the JingDong XIoT integration."""



# class Summary(TypedDict):
#     """Device summary information."""
#
#     type: str
#     online: bool
#
#
# def summary_decode(data: dict[str, Any]) -> Summary:
#     """Convert a dict to Summary. Strict type checking: raises KeyError if fields missing."""
#
#     # 强制获取字段，不存在直接抛 KeyError（强类型风格）
#     deviceType: str = data["type"]
#     online: bool = data["online"]
#
#     # 强制类型校验（确保不会把 int/None 混进去）
#     if not isinstance(deviceType, str):
#         raise TypeError(f"type 必须是字符串，实际类型：{type(deviceType)}")
#
#     if not isinstance(online, bool):
#         raise TypeError(f"online 必须是布尔值，实际类型：{type(online)}")
#
#     # 强类型返回
#     return Summary(type=deviceType, online=online)
#
#
# def summary_decode_safe(data: dict[str, Any] | None) -> Summary | None:
#     """Safely convert a dict to Summary, return None on failure. Suitable for unstable device data in HA integration."""
#
#     if not isinstance(data, dict):
#         return None
#
#     try:
#         device_type = str(data["type"])
#         online = bool(data["online"])
#         return Summary(type=device_type, online=online)
#     except (KeyError, TypeError, ValueError):
#         return None

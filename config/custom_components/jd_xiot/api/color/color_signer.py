"""Type definitions and utilities for JingDong XIoT integration."""
import hashlib
import hmac


def bytes_to_hex(byte_data: bytes) -> str:
    """Bytes to Hex."""
    hex_str = ""
    for b in byte_data:
        # 处理负数（Java byte是有符号的，Python bytes是无符号的）
        digital = b if b >= 0 else b + 256
        if digital < 16:
            hex_str += "0"
        hex_str += hex(digital)[2:]  # 去掉0x前缀
    return hex_str

def hmac_sha256(message: str, key: str) -> str:
    """HMAC SHA256."""
    try:
        # 转换为UTF-8字节
        key_bytes = key.encode("utf-8")
        message_bytes = message.encode("utf-8")

        # 初始化HMAC-SHA256
        hmac_obj = hmac.new(key_bytes, message_bytes, hashlib.sha256)
        digest = hmac_obj.digest()

        # 转换为十六进制字符串
        return bytes_to_hex(digest)

    except (UnicodeEncodeError, TypeError, ValueError):
        return ""

def generate_signature(params: dict[str, str], secret_key: str) -> str:
    """Generate Signature."""
    # 移除sign参数（如果存在）
    params_copy = params.copy()
    params_copy.pop("sign", None)

    # 筛选参数：排除ep/ef/bef，且值非空
    param_name_list: list[str] = []
    for key, value in params_copy.items():
        # 跳过加密开关参数
        if key in ["ep", "ef", "bef"]:
            continue
        # 跳过空值（模拟StringUtils.isNotEmpty）
        if value and value.strip():
            param_name_list.append(key)

    # 按字典序排序
    param_name_list.sort()

    # 拼接参数值：第一个值直接拼，后续加&拼接
    builder = []
    first = True
    for param_name in param_name_list:
        value = params_copy[param_name]
        if first:
            builder.append(value)
            first = False
        else:
            builder.append(f"&{value}")

    # 生成最终待签名字符串
    sign_str = "".join(builder)

    # 计算HMACSHA256签名
    return hmac_sha256(sign_str, secret_key)


# 测试示例
# if __name__ == "__main__":
#     # 测试参数
#     test_params = {
#         "name": "test",
#         "age": "18",
#         "ep": "123",  # 会被排除
#         "bef": "",  # 会被排除
#         "sign": "old_sign",  # 会被移除
#         "empty_key": "",  # 空值会被排除
#         "address": "beijing"
#     }
#     test_secret = "my_secret_key"
#
#     # java: 0fbeacd50bdb7f07d13aea190215458bc8e06e90ec803da07697faa69a3fab4b
#
#     # 生成签名
#     sign = generate_signature(test_params, test_secret)
#     print("生成的签名：", sign)

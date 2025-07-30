import hashlib
import hmac
import typing
import json


SIGN_METHOD_MD5 = "md5"
SIGN_METHOD_HMAC = "hmac"
SIGN_METHOD_HMAC_SHA256 = "hmac-sha256"
CHARSET_UTF8 = "utf-8"


def sign_top_request(params: typing.Dict[str, typing.Any], secret: str, sign_method: str) -> str:
    """
    给TOP请求签名。
    :param params: 请求主体内容
    :param secret: 签名密钥
    :param sign_method: 签名方法，目前支持：空（老md5)、md5, hmac_md5, hmac-sha256 三种
    :return: 签名
    """
    # 第一步：检查参数是否已经排序
    keys = sorted(params.keys())

    # 第二步：把所有参数名和参数值串在一起
    query = ""
    if sign_method == SIGN_METHOD_MD5:
        query += secret

    for key in keys:
        value = params[key]
        if value is None:
            continue

        value_str = ""
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, separators=(',', ':'), ensure_ascii=False)
        else:
            value_str = str(value)

        # The original Java code checks for `!"null".equals(value.toString().replace("\"",""))`
        # and `StringUtils.isNotBlank(value.toString())`.
        # A simple check for not None should suffice for most python use cases,
        # but we will try to replicate it more closely.
        str_value_stripped = value_str.strip()
        if str_value_stripped and str_value_stripped != "null":
            query += f"{key}{value_str}"

    # 第三步：使用MD5/HMAC加密
    if sign_method == SIGN_METHOD_HMAC:
        bytes_to_sign = query.encode(CHARSET_UTF8)
        secret_bytes = secret.encode(CHARSET_UTF8)
        # Note: The java code uses "HmacMD5", which is not a standard algorithm name in python hmac.
        # It's likely using MD5 as the digest.
        signature = hmac.new(secret_bytes, bytes_to_sign, hashlib.md5).digest()
    elif sign_method == SIGN_METHOD_HMAC_SHA256:
        bytes_to_sign = query.encode(CHARSET_UTF8)
        secret_bytes = secret.encode(CHARSET_UTF8)
        signature = hmac.new(secret_bytes, bytes_to_sign, hashlib.sha256).digest()
    else:
        query += secret
        bytes_to_sign = query.encode(CHARSET_UTF8)
        signature = hashlib.md5(bytes_to_sign).digest()
    print(query,"签名字符")
    # 第四步：把二进制转化为大写的十六进制
    return signature.hex().upper() 
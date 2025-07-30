def binary_to_quaternary(binary: str):
    """
    将二进制转换为四进制
    :param binary: 二进制串
    :return: 返回二进制的四进制数据
    """
    quaternary = ""
    binary_length = len(binary)
    if binary_length % 2 != 0:
        binary = '0' * (2 - binary_length % 2) + binary
    for i in range(0, binary_length, 2):
        binary_pair = binary[i:i + 2]
        decimal_value = int(binary_pair, 2)
        quaternary_value = str(decimal_value)
        quaternary += quaternary_value

    return quaternary


def quaternary_to_binary(quaternary: str):
    """
    将四进制转换为二进制
    :param quaternary: 四进制串
    :return: 返回四进制的二进制数据
    """
    binary = ''
    for digit in quaternary:
        binary += bin(int(digit))[2:].zfill(2)
    return binary


def string_to_binary(string):
    """
    将字符串转换为二进制
    :param string: 字符串
    :return: 返回字符串的二进制数据
    """
    bytes_data = string.encode('utf-8')
    binary_data = ''.join(format(byte, '08b') for byte in bytes_data)
    return binary_data


def binary_to_string(binary: str):
    """
    将二进制转换为字符串
    :param binary: 二进制串
    :return: 返回二进制代表的字符串
    """
    bytes_data = [int(binary[i:i + 8], 2) for i in range(0, len(binary), 8)]
    string = bytes(bytes_data).decode('utf-8')
    return string


def split_pairwise(string: str):
    """
    将字符串两两分为一组并存入数组
    :param string: 被分割的字符串
    :return: 返回分割好的数组
    """
    result = []
    for i in range(0, len(string), 2):
        result.append(string[i:i + 2])
    return result


def split_double_pairwise(string: str):
    """
    将字符串每四个分为一组并存入数组
    :param string: 被分割的字符串
    :return: 返回分割好的数组
    """
    result = []
    for i in range(0, len(string), 4):
        result.append(string[i:i + 4])
    return result


def order_compression_and_decompression2(mode: bool, data: str, keys2: dict):
    """
    将加密内容二次压缩或解压
    :param keys2: 密钥对
    :param mode: True为加密，False为解密，bool类型
    :param data: 需要被压缩或解压的数据
    :return: 返回被压缩或解压的数据
    """
    if mode:
        for k, v in keys2.items():
            data = data.replace(k, v)
    else:
        for k, v in keys2.items():
            data = data.replace(v, k)
    return data


def order_compression_and_decompression(mode: bool, data: str, keys1: dict):
    """
    将加密内容压缩或解压
    :param keys1: 密钥对
    :param mode: True为加密，False为解密，bool类型
    :param data: 需要被压缩或解压的数据
    :return: 返回被压缩或解压的数据
    """
    if mode:
        for k, v in keys1.items():
            data = data.replace(k, v)
    else:
        for k, v in keys1.items():
            data = data.replace(v, k)
    return data



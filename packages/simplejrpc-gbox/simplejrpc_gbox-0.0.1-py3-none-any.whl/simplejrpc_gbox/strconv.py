import contextlib
import socket
import re


def camel_to_snake(camel_case):
    """Convert a string from camel case to snake case.

    Args:
        camel_case (str): The string in camel case.

    Returns:
        str: The string converted to snake case.

    """
    snake_case = ""
    prev_char = ""
    for char in camel_case:
        if char.isupper() and prev_char.islower():
            snake_case += "_"
        snake_case += char.lower()
        prev_char = char
    return snake_case


def snake_to_camel(snake_str: str):
    """ """
    components = snake_str.split("_")
    camel_str = "".join(x.title() for x in components)
    return camel_str


def params_data_deal(params):
    """
    参数处理
    使用application/x-www-form-urlencoded 传递如cgi.fix_pathinfo参数
    :param params:
    :return:
    """
    new_data = {}
    for k, v in params["data"].items():
        if "#_#" in k:
            k = k.replace("#_#", ".")
        new_data[k] = v
    params["data"] = new_data


def bool_to_int(b):
    """
    bool转int
    :param b:
    :return:
    """
    return 1 if b else 0


def check_str_is_num(s):
    """
    检查字符串是否是数字
    :param s:
    :return:
    """
    with contextlib.suppress(ValueError):
        float(s)
        return True
    with contextlib.suppress(TypeError, ValueError):
        import unicodedata

        unicodedata.numeric(s)
        return True
    return False


def get_file_prefix_name(filename: str):
    """ """
    filenames = filename.split(".")
    return filenames[0]


def get_real_len(string):
    """
    获取含中文的字符串字精确长度
    :param string<str>
    :return int
    """
    return len(string) + sum("\u2e80" <= s <= "\ufe4f" for s in string)


def get_ip(address):
    """
    获取IP范围
    :param address:
    :return:
    """
    arr = address.split("-")
    s_ips = arr[0].split(".")
    e_ips = arr[1].split(".")
    head_s_ip = f"{s_ips[0]}.{s_ips[1]}.{s_ips[2]}."
    region = int(e_ips[-1]) - int(s_ips[-1])
    return [head_s_ip + str(num + int(s_ips[-1])) for num in range(region + 1)]


def is_ipv6(ip):
    """
    判断是否为IPv6地址
    :param ip:
    :return:
    """
    # 验证基本格式
    if not re.match(r"^[\w:]+$", ip):
        return False

    # 验证IPv6地址
    try:
        socket.inet_pton(socket.AF_INET6, ip)
    except socket.error:
        return False
    return True


def xcut(contents, from_str, end_str):
    """ """
    message = contents.split(from_str)
    if len(message) < 2:
        return ""
    message = message[1].split(end_str)
    if message[0] == "":
        message[0] = ""
    return message[0]


def map_to_list(map_obj):
    """
    map转list
    :param map_obj:
    :return:
    """
    try:
        if type(map_obj) != list and type(map_obj) != str:
            map_obj = list(map_obj)
        return map_obj
    except:
        return []


def is_number(s):
    # DNS regular expression
    return bool(re.fullmatch(r"[-+]?\d+(\.\d+)?", s))


def validate_dns_string(dns_str: str):
    """ """
    dns_ls = dns_str.split(".")
    dns_isdigit = (is_number(x) for x in dns_ls)
    if all(dns_isdigit):
        """ """
        if len(dns_ls) != 4 or int(dns_ls[0]) <= 0:
            return False
        return all((int(x) <= 255 and int(x) >= 0 for x in dns_ls))
    else:
        return True

import subprocess
import socket
import os

from ._file import read_file


def get_public_ip():
    """获取公网ip"""
    try:
        command = ["curl", "ip.sb"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode().strip()
    except Exception:
        return None


def get_local_ip():
    """获取内网ip"""
    try:
        # 创建UDP套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接Google的公共DNS服务器
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except socket.error:
        return None


def get_hostname():
    """ """
    import socket

    return socket.gethostname()


def get_sys_swap():
    """ """
    try:
        res = subprocess.check_output("free -m|grep Swap", shell=True)
    except subprocess.CalledProcessError:
        return
    return res.decode()


def centos_is78():
    """
    判断是否为CentOS 7/8
    :return:
    """
    if os.path.exists("/etc/redhat-release"):
        version = read_file("/etc/redhat-release")
        if isinstance(version, str) and (
            version.find(" 7.") != -1 or version.find(" 8.") != -1
        ):
            return True
    return False

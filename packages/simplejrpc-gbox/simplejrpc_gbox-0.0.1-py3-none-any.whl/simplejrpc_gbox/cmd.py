import time
import subprocess
import tempfile
import pwd
import os
import traceback
import base64
import threading
import psutil


def exec_shell(cmd_string, timeout=None, shell=True, cwd=None, env=None, user=None):
    """
    @name 执行命令
    @param cmd_string 命令 [必传]
    @param timeout 超时时间
    @param shell 是否通过shell运行
    @param cwd 进入的目录
    @param env 环境变量
    @param user 执行用户名
    @return 命令执行结果
    """

    pre_exec_fn = None
    tmp_dir = "/dev/shm"
    if user:
        pre_exec_fn = get_pre_exec_fn(user)
        tmp_dir = "/tmp"
    try:
        rx = md5(cmd_string.encode("utf-8"))
        success_f = tempfile.SpooledTemporaryFile(
            max_size=4096,
            mode="wb+",
            suffix="_success",
            prefix=f"b_tex_{rx}",
            dir=tmp_dir,
        )
        error_f = tempfile.SpooledTemporaryFile(
            max_size=4096,
            mode="wb+",
            suffix="_error",
            prefix=f"b_tex_{rx}",
            dir=tmp_dir,
        )
        sub = subprocess.Popen(
            cmd_string,
            close_fds=True,
            shell=shell,
            bufsize=128,
            stdout=success_f,
            stderr=error_f,
            cwd=cwd,
            env=env,
            preexec_fn=pre_exec_fn,
        )
        if timeout:
            s = 0
            d = 0.01
            while sub.poll() is None:
                time.sleep(d)
                s += d
                if s >= timeout:
                    if not error_f.closed:
                        error_f.close()
                    if not success_f.closed:
                        success_f.close()
                    return "", "Timed out"
        else:
            sub.wait()

        error_f.seek(0)
        success_f.seek(0)
        a = success_f.read()
        e = error_f.read()
        if not error_f.closed:
            error_f.close()
        if not success_f.closed:
            success_f.close()
    except Exception:
        return "", get_error_info()
    try:
        # 编码修正
        if type(a) == bytes:
            a = a.decode("utf-8")
        if type(e) == bytes:
            e = e.decode("utf-8")
    except Exception:
        a = str(a)
        e = str(e)

    return a, e


def get_pre_exec_fn(run_user):
    """
    @name 获取指定执行用户预处理函数
    @param run_user<string> 运行用户
    @return 预处理函数
    """

    pid = pwd.getpwnam(run_user)
    uid = pid.pw_uid
    gid = pid.pw_gid

    def _exec_rn():
        os.setgid(gid)
        os.setuid(uid)

    return _exec_rn


def get_error_info():
    """ """

    return traceback.format_exc()


def md5(strings):
    """
    @name 生成MD5
    @param strings 要被处理的字符串
    @return string(32)
    """
    if type(strings) != bytes:
        strings = strings.encode()
    import hashlib

    m = hashlib.md5()
    m.update(strings)
    return m.hexdigest()


def async_run(cmd_string: str):
    """
    异步执行命令
    """
    exec_shell(f"nohup {cmd_string} &")


def check_command_exists(command):
    """
    执行which命令检查命令是否存在
    :param command:
    :return:
    """
    process = subprocess.Popen(
        ["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()

    return process.returncode == 0


def get_mode_and_user(path):
    """
    取文件或目录权限信息
    """
    import pwd

    if not os.path.exists(path):
        return None
    stat = os.stat(path)
    data = {"mode": str(oct(stat.st_mode)[-3:])}
    try:
        data["user"] = pwd.getpwuid(stat.st_uid).pw_name
    except Exception:
        data["user"] = str(stat.st_uid)
    return data


def check_sudo_permission():
    """ """
    try:
        subprocess.check_output('sudo -n echo "Sudo permission granted"', shell=True)
    except subprocess.CalledProcessError:
        return False
    return True


def check_service_status(service_name):
    """
    执行systemctl命令检查服务状态
    :param service_name:
    :return:
    """
    command = f"systemctl is-active {service_name}"
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()

    if process.returncode == 0 and output.decode().strip() == "active":
        # 服务已启动
        return True
    else:
        # 服务未启动
        return False


def check_yum_installed(package_name):
    """
    判断 yum 包是否已安装
    :param package_name:
    :return:
    """
    if package_name == "firewalld":
        command = f"yum list installed | grep {package_name}|grep -v filesystem"
    else:
        command = f"yum list installed | grep {package_name}"
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()

    if process.returncode == 0 and output.decode().strip().find(package_name) != -1:
        # 已安装
        return True
    else:
        # 未安装
        return False


def echo(msg: str):
    """
    打印消息
    """
    print(f"\n{msg}\n")


def is_process_exists_by_exe(bin_path):
    """
    根据执行文件路径查找进程是否存在
    """
    if isinstance(bin_path, str):
        bin_path = [bin_path]
    if not isinstance(bin_path, list):
        return False
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            _exe_bin = p.exe()
            for _e in bin_path:
                if _exe_bin.find(_e) != -1:
                    return True
        except:
            continue
    return False


def pid_exists(pid):
    """ """
    if os.path.exists("/proc/{}/exe".format(pid)):
        return True
    return False


def chmod_path(path, mode):
    """ """
    return exec_shell(f"chmod {mode} -R {path}")


def build_execute_command(command: str, **kwargs):
    """Note:
    This will deadlock when using stdout=PIPE or stderr=PIPE and the child process generates enough output to a pipe such that it blocks waiting for the OS pipe buffer to accept more data. Use Popen.communicate() when using pipes to avoid that.
    """

    def async_exec(exec_cmd: str):
        subprocess.Popen(
            exec_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
            **kwargs,
        )

    name = base64.b64encode(command.encode("utf-8")).decode("utf-8")
    threading.Thread(target=async_exec, args=(command,), name=name).start()

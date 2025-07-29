import os
import requests


def read_file(filename, mode="r") -> str:
    """
    读取文件内容
    @filename 文件名
    return string(bin) 若文件不存在，则返回False
    """
    import os

    if not os.path.exists(filename):
        return ""
    fp = None
    try:
        fp = open(filename, mode)
        f_body = fp.read()
    except Exception:
        try:
            fp = open(filename, mode, encoding="utf-8", errors="ignore")
            f_body = fp.read()
        except Exception:
            fp = open(filename, mode, encoding="GBK", errors="ignore")
            f_body = fp.read()
    finally:
        if fp and not fp.closed:
            fp.close()
    return f_body


def download_file(remote_file, local_file, force=False):
    """
    下载文件
    :param remote_file:
    :param local_file:
    :param force:
    :return:
    """
    if not force and os.path.exists(local_file):
        return True

    if not os.path.exists(os.path.dirname(local_file)):
        os.makedirs(os.path.dirname(local_file))

    try:

        r = requests.get(remote_file, stream=True)
        with open(local_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True
    except Exception:
        return False

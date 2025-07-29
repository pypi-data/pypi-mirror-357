import datetime
import time


def get_now_strftime(format="%Y-%m-%d %H:%M:%S"):
    """Get the current"""
    return datetime.datetime.now().strftime(format)


def format_date(format_str="%Y-%m-%d %H:%M:%S", times=None):
    """Get the current"""
    if not times:
        times = int(time.time())
    time_local = time.localtime(times)
    return time.strftime(format_str, time_local)

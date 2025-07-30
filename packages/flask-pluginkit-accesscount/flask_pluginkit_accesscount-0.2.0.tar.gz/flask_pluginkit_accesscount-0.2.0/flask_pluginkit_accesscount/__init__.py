# -*- coding: utf-8 -*-
"""
AccessCount
-----------

PV and IP plugins for statistical access.

:copyright: (c) 2025 by Hiroshi.tao.
:license: BSD 3-Clause License, see LICENSE for more details.
"""

from datetime import datetime, date, timedelta

from flask import current_app, request, g
from flask_pluginkit import RedisStorage
from prettytable import PrettyTable

__plugin_name__ = "AccessCount"
__description__ = "IP、PV、Endpoint Statistics"
__author__ = "Hiroshi.tao <me@tcw.im>"
__version__ = "0.2.0"
__license__ = "BSD 3-Clause"
__license_file__ = "LICENSE"
__readme_file__ = "README.md"
__url__ = "https://github.com/saintic/flask-pluginkit-accesscount"
__state__ = "enabled"

default_key_prefix: str = "pluginkit"


def get_time(fm="%Y-%m-%d %H:%M:%S"):
    """获取今天日期"""
    return datetime.now().strftime(fm)


def dayAgo(day: int):
    """多少天以前"""
    today = date.today()
    oneday = timedelta(days=day)
    return str(today - oneday)


def record_ip_pv(response):
    """记录ip、ip"""
    today = get_time("%Y%m%d")
    prefix = (
        current_app.config.get("PLUGINKIT_ACCESSCOUNT_KEY_PREFIX") or default_key_prefix
    )
    pvKey = f"{prefix}:AccessCount:pv:hash"
    epKey = f"{prefix}:AccessCount:endpoint:hash"
    conn_name = current_app.config.get("PLUGINKIT_ACCESSCOUNT_REDIS_NAME") or "redis"
    redis_url = current_app.config.get("PLUGINKIT_ACCESSCOUNT_REDIS_URL")
    redis_conn = getattr(g, conn_name, None)
    if not redis_url and not redis_conn:
        current_app.logger.error(
            "AccessCount plugin not found valid redis url or connection."
        )
        return
    storage = RedisStorage(redis_url=redis_url, redis_connection=redis_conn)
    pipe = storage._db.pipeline()
    pipe.hincrby(pvKey, today, 1)
    if request.endpoint:
        pipe.hincrby(epKey, "%s:%s" % (today, request.endpoint), 1)
    try:
        pipe.execute()
    except Exception as e:
        current_app.logger.error("AccessCount plugin write data failed", e)


def register():
    return dict(hep=dict(after_request=record_ip_pv))


def print_pv(
    day: int,
    redis_url: str = "",
    redis_conn=None,
    redis_key_prefix: str = default_key_prefix,
):
    """PV访问量查询"""

    def pv_value_filter(v):
        try:
            v = int(v)
        except (ValueError, TypeError):
            return 0
        else:
            return v

    day = int(day)
    if not redis_url and not redis_conn:
        raise ValueError("AccessCount plugin not found valid redis url or connection.")
    storage = RedisStorage(redis_url=redis_url, redis_connection=redis_conn)
    column = sorted([dayAgo(d) for d in range(0, day)])
    try:
        pipe = storage._db.pipeline()
        key = f"{redis_key_prefix}:AccessCount:pv:hash"
        for i in column:
            pipe.hget(key, i.replace("-", ""))
        row = pipe.execute()
        row.append(sum(map(pv_value_filter, row)) / day)
    except Exception as e:
        raise
    else:
        column.append("平均")
        table = PrettyTable(column)
        table.add_row(row)
        print(table)


def print_ep(
    day: int,
    redis_url: str = "",
    redis_conn=None,
    redis_key_prefix: str = default_key_prefix,
):
    """端点访问量查询"""
    # 根据日期查询端点每天访问量
    # 根据端点查询每天访问量
    day = int(day)
    if not redis_url and not redis_conn:
        raise ValueError("AccessCount plugin not found valid redis url or connection.")
    storage = RedisStorage(redis_url=redis_url, redis_connection=redis_conn)

    column = sorted([dayAgo(d) for d in range(0, day)])
    table = PrettyTable(column)
    key = f"{redis_key_prefix}:AccessCount:endpoint:hash"
    data = storage._db.hgetall(key)
    row = []
    for d in column:
        # 符合日期的所有键的列表，键包含endpoint
        keys = [k for k in data.keys() if k.startswith(d.replace("-", ""))]
        # 定义子表格显示行
        subtable = PrettyTable(["端点", "访问量"])
        todaydata = sorted(
            [(k.split(":")[-1], data[k]) for k in keys],
            key=lambda x: int(x[-1]),
            reverse=True,
        )
        for i in todaydata:
            subtable.add_row(i)
        row.append(subtable)
    table.add_row(row)
    print(table)

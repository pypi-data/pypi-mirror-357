# -*- coding: utf-8 -*-
"""
AccessCount
-----------

PV and IP plugins for statistical access.

:copyright: (c) 2025 by Hiroshi.tao.
:license: BSD 3-Clause License, see LICENSE for more details.
"""

from datetime import datetime
from flask import current_app, request, g
from flask_pluginkit import RedisStorage

__plugin_name__ = "AccessCount"
__description__ = "IP、PV、Endpoint Statistics"
__author__ = "Hiroshi.tao <me@tcw.im>"
__version__ = "0.1.0"
__license__ = "BSD 3-Clause"
#__license_file__ = "LICENSE"
__readme_file__ = "README.md"
__url__ = "https://github.com/saintic/flask-pluginkit-accesscount"
__state__ = "enabled"


def get_time(fm="%Y-%m-%d %H:%M:%S"):
    """获取今天日期"""
    return datetime.now().strftime(fm)


def record_ip_pv(response):
    """记录ip、ip"""
    today = get_time("%Y%m%d")
    prefix = current_app.config.get("PLUGINKIT_ACCESSCOUNT_KEY_PREFIX") or "pluginkit"
    pvKey = (
        current_app.config.get("PLUGINKIT_ACCESSCOUNT_PVKEY")
        or f"{prefix}:AccessCount:pv:hash"
    )
    epKey = (
        current_app.config.get("PLUGINKIT_ACCESSCOUNT_EPKEY")
        or f"{prefix}:AccessCount:endpoint:hash"
    )
    conn_name = current_app.config.get("PLUGINKIT_ACCESSCOUNT_REDIS_CONN_NAME") or "redis"
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


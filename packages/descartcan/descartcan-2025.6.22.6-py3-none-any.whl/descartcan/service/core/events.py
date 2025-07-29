# -*- coding:utf-8 -*-
"""
# Time       ：2023/12/8 18:23
# Author     ：Maxwell
# version    ：python 3.9
# Description：
"""

from typing import Callable
from fastapi import FastAPI
from descartcan.service.database.mysql import register_mysql
from descartcan.service.database.redis import sys_cache


def startup(app: FastAPI) -> Callable:

    async def app_start() -> None:
        await register_mysql(app)
        app.state.cache = await sys_cache()

    return app_start


def stopping(app: FastAPI) -> Callable:

    async def stop_app() -> None:
        cache = app.state.cache
        if cache:
            await cache.close()

    return stop_app

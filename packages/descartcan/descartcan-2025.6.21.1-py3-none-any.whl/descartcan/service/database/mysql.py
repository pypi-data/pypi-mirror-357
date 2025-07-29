# -*- coding:utf-8 -*-
"""
# Time       ：2023/12/8 18:23
# Author     ：Maxwell
# Description：
"""

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from descartcan.service.core import config


async def register_mysql(app: FastAPI):
    db_config = {
        "connections": {
            "base": {
                "engine": "tortoise.backends.mysql",
                "credentials": {
                    "host": config.MYSQL_HOST,
                    "user": config.MYSQL_USER,
                    "password": config.MYSQL_PASSWORD,
                    "port": config.MYSQL_PORT,
                    "database": config.MYSQL_DB,
                },
            }
        },
        "apps": {
            "base": {"models": config.MYSQL_TABLE_MODELS, "default_connection": "base"},
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai",
    }
    register_tortoise(
        app,
        config=db_config,
        generate_schemas=False,
        add_exception_handlers=False,
    )

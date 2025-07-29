# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/2/2 20:05
# Author     ：Maxwell
# Description：
"""
import pytz
import psutil
from fastapi import APIRouter
from descartcan.service.core.response import success
from descartcan.config import config
from datetime import datetime


monitor_router = APIRouter(prefix="")


@monitor_router.get(path="")
async def monitor():
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    process = psutil.Process()
    process_memory = process.memory_info().rss / (1024 * 1024)
    return success(
        {
            "app": {
                "version": config.APP_VERSION,
                "name": config.APP_NAME,
                "env": config.env,
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
            },
            "process": {
                "memory_mb": process_memory,
                "cpu_percent": process.cpu_percent(interval=0.1),
            },
            "timestamp": datetime.now(pytz.UTC).isoformat(),
        }
    )

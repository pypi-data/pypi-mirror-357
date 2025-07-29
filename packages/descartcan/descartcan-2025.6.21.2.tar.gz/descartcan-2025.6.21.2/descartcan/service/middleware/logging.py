# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2024/1/12 10:27
# Author     ：Maxwell
# Description：
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import traceback
from descartcan.utils import logger
from descartcan.utils.http.info import ClientInfoExtractor


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.monotonic()
        client_ip: Optional[str] = None
        path: Optional[str] = None

        try:
            client_ip = ClientInfoExtractor.client_ip(request=request)
            path = request.url.path[:200]
            response = await call_next(request)
            elapsed_ms = (time.monotonic() - start_time) * 1000
            logger.info("Req: ip=%s, elapsed_ms=%.2f, %s", client_ip,elapsed_ms, path)
            return response

        except Exception as e:
            logger.error(
                "Global error: ip=%s, path=%s, error=%s, traceback=%s",
                client_ip or "unknown",
                path or "unknown",
                str(e),
                traceback.format_exc()
            )
            return Response(content="Server error.", status_code=500)

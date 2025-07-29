# !/usr/bin/env python
# -*-coding:utf-8 -*-
"""
# Time       ：2024/1/17 11:38
# Author     ：Maxwell
# Description：
"""
import os
from dotenv import load_dotenv

load_dotenv()
env = os.getenv("ENV", "dev")
load_dotenv(f"./config/.env.{env}", override=True)

APP_DOCS = None
APP_RE_DOCS = None
APP_NAME = os.getenv("APP_NAME", default="DescartCan")
APP_VERSION = os.getenv("APP_VERSION", default="1.0.0")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", default="")
APP_DEBUG = env != "pro"
if APP_DEBUG:
    APP_DOCS = "/doc"
    APP_RE_DOCS = "/redoc"

APP_BASE_URI = os.getenv("APP_BASE_URI", default="")
APP_HOST = os.getenv("APP_HOST", default="127.0.0.1")
APP_PORT = os.getenv("APP_PORT", default="8008")


# Authorization
OAUTH2_REDIRECT_URL = os.getenv("OAUTH2_REDIRECT_URL")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_TABLE_MODELS = os.getenv("MYSQL_TABLE_MODELS", "").split(",")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "EN")
DEFAULT_LANGUAGE_IS_EN = DEFAULT_LANGUAGE == "EN"



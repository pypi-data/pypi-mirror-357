# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License.
Created on 2025/6/24 21:28
Email: yundi.xxii@outlook.com
Description:
---------------------------------------------
"""

from .store.database import (
    NAME,
    DB_PATH,
    CONFIG_PATH,
    get_settings,
    sql,
    put,
    has,
    tb_path,
    read_ck,
    read_mysql,
)

__version__ = "1.0.0b1"


__all__ = [
    "__version__",
    "NAME",
    "DB_PATH",
    "CONFIG_PATH",
    "get_settings",
    "sql",
    "put",
    "has",
    "tb_path",
    "read_ck",
    "read_mysql",
]


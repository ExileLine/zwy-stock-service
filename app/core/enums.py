# -*- coding: utf-8 -*-
# @Time    : 2026-03-26 17:52:34
# @Author  : yangyuexiong
# @File    : enums.py

from enum import Enum


class UserStatus(str, Enum):
    normal = "正常"
    disable = "禁用"
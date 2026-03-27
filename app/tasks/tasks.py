# -*- coding: utf-8 -*-
# @Time    : 2026-03-26 17:52:34
# @Author  : yangyuexiong
# @File    : tasks.py

from app.core.config import get_config


async def test_async_task(*args, **kwargs):
    import os
    os.environ["yyx"] = "okc"
    print(f"test_async_task: {os.getenv('yyx')}", args, kwargs)


def test_sync_task(*args, **kwargs):
    import os
    print(f"test_sync_task: {os.getenv('yyx')}", args, kwargs)
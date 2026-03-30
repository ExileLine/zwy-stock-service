# -*- coding: utf-8 -*-
# @Time    : 2026-03-26 17:52:34
# @Author  : yangyuexiong
# @File    : local_run.py

import uvicorn


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=7777, reload=True)
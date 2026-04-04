FROM python:3.12-slim-bookworm

LABEL maintainer="YangYueXiong"

# 设置非交互模式，避免 tzdata 等阻塞
ENV DEBIAN_FRONTEND=noninteractive

# 切换为阿里云 Debian bookworm 源 + 安装依赖
RUN set -eux; \
    ARCH=$(uname -m); \
    echo "deb http://mirrors.aliyun.com/debian bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list; \
    echo "deb http://mirrors.aliyun.com/debian bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    echo "deb http://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list; \
    apt-get clean && apt-get update -y && \
    apt-get install -y --no-install-recommends \
        ca-certificates build-essential gcc g++ libffi-dev libssl-dev util-linux && \
    rm -rf /var/lib/apt/lists/*

# 更新pip
RUN pip install --upgrade pip -i https://pypi.doubanio.com/simple

# 复制应用程序代码
WORKDIR /srv
RUN mkdir -p logs/service
COPY . /srv/zwy-stock-service

# 设置工作目录为
WORKDIR /srv/zwy-stock-service

# 安装uv
RUN pip install uv -i https://pypi.doubanio.com/simple

# 安装项目依赖包
RUN pip install -r requirements.txt -i https://pypi.doubanio.com/simple

# 设置环境变量（支持 docker-compose 传入，默认 development）
ARG FAST_API_ENV=development
ENV FAST_API_ENV=${FAST_API_ENV}
RUN echo "FAST_API_ENV is set to: $FAST_API_ENV"

# 时区
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 本地测试: 启动 FastAPI 应用(部署时删除--reload)
CMD uvicorn app.main:app --host 0.0.0.0 --port 5001

# 暴露 FastAPI 的默认端口
EXPOSE 5001


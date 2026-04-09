# zwy-stock-service

Author: yangyuexiong

### 项目环境配置

- 安装`python3.12`与`uv`
  ```shell 
  pip install uv
  ```

### 配置文件与使用

- 配置文件描述：[.env.example](.env.example)
- 本地开发环境配置文件：[.env.development](.env.development)
- 测试环境配置文件：[.env.test](.env.test)
- 生产环境配置文件：[.env.production](.env.production)

### 数据库初始化与迁移

- ORM 统一基于 SQLAlchemy 2.0
- 迁移工具统一使用 Alembic，模型注册入口在 `app/models/__init__.py`
- 生产环境建议先生成迁移 SQL 并经过审核后再执行

```shell
# 1) 生成迁移脚本（根据当前模型与数据库差异）
uv run alembic revision --autogenerate -m "feat: update table schema"

# 2) 执行到最新版本
uv run alembic upgrade head

# 3) 回滚一个版本（可选）
uv run alembic downgrade -1
```

### 启动

```shell
# 本地启动
python local_run.py

# 或
uv run local_run.py 

# 或(`uvicorn`前台调试模式)
uv run uvicorn app.main:app --host 0.0.0.0 --port 5002

# 或(`gunicorn`前台调试模式)
uv run gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:5002

# 或(`gunicorn`后台进程模式)
uv run gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app -b 0.0.0.0:5002 --access-logfile /srv/logs/zwy_stock/access.log --error-logfile /srv/logs/zwy_stock/error.log --log-level debug -D --timeout 300 --capture-output


```

### docker-compose部署

```shell
# 构建`Dockerfile`目录
cd /zwy-stock-service

# 构建`docker-compose`目录 
cd /zwy-stock-service/docker

# 本地
docker build -f Dockerfile.dev -t zwy-stock-service:dev .
docker-compose -f docker-compose-local.yml up -d

# 测试
docker build -t 'zwy-stock-service' .
docker-compose -f docker-compose-test.yml up -d

# 生产
docker build -t 'zwy-stock-service' .
docker-compose -f docker-compose.yml up -d

# 导出镜像 
docker save -o zwy-stock-service-x86.tar zwy-stock-service:latest
docker save -o zwy-stock-service-arm64.tar zwy-stock-service:latest
```

### 项目依赖(有更新则需要)

- `requirements.txt`用于部署使用，本地使用`uv`环境即可

```shell
# 如需安装新的库例如
uv add fastapi ...
```

```shell
# pyproject.toml 生成 requirements.txt
# 导出所有依赖
uv pip compile pyproject.toml -o requirements.txt
```
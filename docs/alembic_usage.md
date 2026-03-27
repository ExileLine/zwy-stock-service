# Alembic 使用说明

当前项目已接入 Alembic，并以库存模块为迁移管理范围：

- `stock_category`
- `stock_in_out_record`

当前基线版本：

- `20260327_1105`

## 常用命令

查看当前版本：

```bash
./.venv/bin/alembic current
```

查看历史版本：

```bash
./.venv/bin/alembic history
```

检查模型与数据库是否有差异：

```bash
./.venv/bin/alembic check
```

生成新迁移：

```bash
./.venv/bin/alembic revision --autogenerate -m "your message"
```

执行迁移：

```bash
./.venv/bin/alembic upgrade head
```

回滚一个版本：

```bash
./.venv/bin/alembic downgrade -1
```

## 当前配置说明

- Alembic 配置文件：`alembic.ini`
- 迁移环境：`alembic/env.py`
- 版本目录：`alembic/versions`
- 数据库连接：复用项目 `app.core.config.get_config()` 的开发环境配置
- 当前 `env.py` 仅纳入库存相关两张表，避免把未纳入本次范围的其他模型一起自动生成迁移

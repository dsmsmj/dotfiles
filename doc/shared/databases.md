# 本地数据库（Docker Compose 一键启动）

这份文档用于在本地快速启动常见依赖（Postgres + Redis + 可选 MySQL），适用于全栈开发的“开箱即用”环境。

对应 compose 文件：

- `doc/shared/compose/databases.compose.yml`

## 启动

在仓库根目录执行：

```bash
docker compose -f doc/shared/compose/databases.compose.yml up -d
```

查看状态：

```bash
docker compose -f doc/shared/compose/databases.compose.yml ps
```

查看日志：

```bash
docker compose -f doc/shared/compose/databases.compose.yml logs -f
```

停止并保留数据卷：

```bash
docker compose -f doc/shared/compose/databases.compose.yml down
```

停止并删除数据卷（会清空数据）：

```bash
docker compose -f doc/shared/compose/databases.compose.yml down -v
```

## 连接信息（默认）

### Postgres

- **Host**：`localhost`
- **Port**：`5432`
- **User**：`app`
- **Password**：`app`
- **Database**：`app`

示例连接串：

- `postgresql://app:app@localhost:5432/app`

### Redis

- **Host**：`localhost`
- **Port**：`6379`

### MySQL（可选）

该服务默认不开启（使用 compose profiles）。

启用 MySQL：

```bash
docker compose -f doc/shared/compose/databases.compose.yml --profile mysql up -d
```

连接信息：

- **Host**：`localhost`
- **Port**：`3306`
- **User**：`app`
- **Password**：`app`
- **Database**：`app`
- **Root password**：`root`

## 常见问题

### 1) 端口被占用

如果本机已有 Postgres/Redis/MySQL，可能占用 5432/6379/3306。解决方式：

- 关闭本机服务，或
- 修改 compose 文件的端口映射（例如把 `5432:5432` 改为 `15432:5432`）

### 2) 数据存哪里

数据存储在 Docker named volumes 中（`postgres_data` / `redis_data` / `mysql_data`）。`down` 不会删除数据，`down -v` 才会删除。


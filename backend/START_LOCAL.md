# 🚀 ReliHub 后端开发与部署指南

> **适用环境**: macOS 本地开发 / 测试环境部署
> **前提条件**: Python 3.9+, PostgreSQL 14+, Redis（可选）, Docker（可选）

---

## 📋 文档目录

1. [快速启动步骤](#快速启动步骤) - 本地开发环境快速启动
2. [Docker 部署](#docker-部署可选) - 使用 Docker 部署数据库
3. [测试环境配置](#测试环境配置) - 测试环境配置与运行
4. [验证部署](#验证部署) - 部署后验证
5. [常见问题](#常见问题) - FAQ 与故障排除
6. [部署验证清单](#部署验证清单) - 部署完成检查项

---

## 📋 快速启动步骤

### 步骤 1: 创建数据库和用户

```bash
# 连接到 PostgreSQL
psql -h localhost -U $(whoami) postgres

# 创建用户和数据库
CREATE USER postgres WITH SUPERUSER PASSWORD 'postgres';
CREATE DATABASE relihub OWNER postgres;
GRANT ALL PRIVILEGES ON DATABASE relihub TO postgres;

# 退出
\q
```

**或者使用一行命令**:
```bash
createuser -s postgres 2>/dev/null || true
createdb -U postgres relihub 2>/dev/null || true
```

### 步骤 2: 配置环境变量

```bash
cd backend

# 复制环境配置模板
cp .env.example .env

# 编辑 .env 文件，确保以下配置正确：
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/relihub
# REDIS_URL=redis://localhost:6379/0
```

### 步骤 3: 创建虚拟环境并安装依赖

```bash
cd backend

# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤 4: 执行数据库迁移

```bash
cd backend
source .venv/bin/activate

# 执行迁移
alembic upgrade head

# 验证迁移
alembic current
```

### 步骤 5: 启动应用

```bash
cd backend
source .venv/bin/activate

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**访问地址**:
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

---

## 🔧 使用启动脚本（推荐）

我们提供了自动化启动脚本：

```bash
cd backend
chmod +x deploy.sh
./deploy.sh
```

脚本会自动执行以下步骤：
1. ✅ 环境检查（Python、pip）
2. ✅ 虚拟环境检查/创建
3. ✅ 依赖安装
4. ✅ 环境配置检查（.env）
5. ✅ 数据库连接验证
6. ✅ 数据库迁移
7. ✅ 启动应用

**启动后访问地址**:
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

---

## 🚀 生产环境部署

### 生产环境检查清单

- [ ] Python 3.9+
- [ ] Docker 20.10+ (如使用容器部署)
- [ ] Docker Compose 2.0+ (如使用容器部署)
- [ ] PostgreSQL 客户端工具（可选）

### 生产环境部署步骤

1. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 配置生产环境参数
```

2. **生成 SECRET_KEY**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. **使用 Docker 部署**
```bash
docker-compose up -d db redis
docker-compose ps
```

4. **执行数据库迁移**
```bash
alembic upgrade head
```

5. **启动应用**
```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式（推荐）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🧪 测试环境配置

> ⚠️ **重要**: 所有测试必须使用 PostgreSQL 数据库，严禁使用 SQLite。

### 创建测试数据库

```bash
# 创建测试数据库
createdb -U postgres relihub_test

# 或者使用 psql
psql -U postgres -c "CREATE DATABASE relihub_test OWNER postgres;"
```

### 配置测试环境变量

在 `.env` 文件中添加测试数据库配置：

```bash
# 测试数据库连接 (必须使用 PostgreSQL)
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/relihub_test
```

### 运行测试

```bash
cd backend
source .venv/bin/activate

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_auth_service.py -v
```

### 测试数据库要求

| 要求项 | 说明 |
|--------|------|
| **数据库类型** | PostgreSQL 15+ (与生产环境保持一致) |
| **禁止使用** | SQLite、MySQL 等非PostgreSQL数据库 |
| **测试数据库** | `relihub_test` (独立于开发/生产数据库) |
| **隔离策略** | 每个测试用例使用事务回滚，确保数据隔离 |

---

## 🐳 Docker 部署（可选）

如果使用 Docker 部署 PostgreSQL 和 Redis，可以使用以下方式：

### 启动数据库和 Redis

```bash
# 使用 Docker Compose 启动
docker-compose up -d db redis

# 检查容器状态
docker-compose ps

# 查看日志（如有问题）
docker-compose logs db
docker-compose logs redis
```

**预期输出**:
```
NAME                STATUS
backend_db_1        Up
backend_redis_1     Up
```

### 验证 Docker 部署

```bash
# 连接数据库
psql -h localhost -U postgres -d relihub

# 查看表数量
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';

# 退出
\q
```

**预期结果**: 12+ 个表

---

## ✅ 验证部署

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

**预期响应**:
```json
{"status": "healthy"}
```

### 2. 检查数据库表

```bash
psql -h localhost -U postgres -d relihub -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
```

**预期结果**: 12+ 个表

### 3. 测试 API

```bash
# 获取资源列表
curl http://localhost:8000/api/v1/resources/
```

### 4. API 端点验证

```bash
# 测试 Swagger UI
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs
# 预期: 200

# 测试 OpenAPI 文档
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/openapi.json
# 预期: 200

# 测试用户注册 API
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"Test123456","verification_code":"888888"}'
# 预期: 返回包含 code 字段的 JSON 响应
```

---

## 🐛 常见问题

### 问题 1: 数据库连接失败

**错误**: `psql: error: connection to server ... failed: FATAL: role "postgres" does not exist`

**解决方案**:
```bash
# 创建 postgres 用户
createuser -s postgres

# 或者修改 .env 中的 DATABASE_URL 使用当前用户
# DATABASE_URL=postgresql://$(whoami)@localhost:5432/relihub
```

### 问题 2: 数据库不存在

**错误**: `database "relihub" does not exist`

**解决方案**:
```bash
createdb -U postgres relihub
```

### 问题 3: 端口已被占用

**错误**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或者使用其他端口
uvicorn app.main:app --reload --port 8001
```

### 问题 4: 依赖安装失败

**错误**: `Could not find a version that satisfies the requirement`

**解决方案**:
```bash
# 升级 pip
pip install --upgrade pip

# 清理缓存重新安装
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

---

## 📊 部署验证清单

完成部署后，请确认以下项目：

### 基础设施
- [ ] PostgreSQL 已启动
- [ ] 数据库 relihub 已创建
- [ ] 用户 postgres 已创建
- [ ] 数据库连接正常

### 应用服务
- [ ] 虚拟环境已激活
- [ ] 依赖已安装
- [ ] 数据库迁移已执行
- [ ] Uvicorn 服务器启动
- [ ] 端口 8000 可访问
- [ ] 健康检查通过
- [ ] API 文档可访问

### 功能验证
- [ ] 用户认证 API 可用
- [ ] 资源管理 API 可用
- [ ] AI 对话 API 可用
- [ ] 社区功能 API 可用
- [ ] 账本功能 API 可用
- [ ] 通知功能 API 可用

---

## 🎯 下一步

部署成功后：

1. **冒烟测试** - 测试核心功能
2. **Sprint C 开发准备** - 获取 API Key
3. **开始 Sprint C 开发** - LLM 集成

---

**部署成功！开始使用 ReliHub** 🚀

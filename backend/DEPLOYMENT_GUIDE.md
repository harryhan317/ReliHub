# 🚀 Sprint B 部署快速指南

> **版本**: Sprint B  
> **更新日期**: 2026-04-04  
> **部署目标**: 测试环境

---

## 📋 部署前检查清单

### 环境要求

- [ ] Python 3.9+
- [ ] Docker 20.10+
- [ ] Docker Compose 2.0+
- [ ] PostgreSQL 客户端工具（可选）

### 文件检查

- [ ] `backend/.env` - 环境配置文件
- [ ] `backend/requirements.txt` - Python 依赖
- [ ] `backend/docker-compose.yml` - Docker 配置
- [ ] `backend/alembic/` - 数据库迁移脚本

---

## 🎯 快速部署（推荐）

### 方法一：使用部署脚本

```bash
# 1. 进入后端目录
cd backend

# 2. 执行部署脚本
chmod +x deploy_sprint_b.sh
./deploy_sprint_b.sh
```

脚本会自动执行以下步骤：
1. ✅ 环境检查（Python、Docker、Docker Compose）
2. ✅ 环境配置检查（.env 文件）
3. ✅ 启动数据库和 Redis
4. ✅ 执行数据库迁移
5. ✅ 验证数据库
6. ✅ 启动应用

---

## 🔧 手动部署（详细步骤）

### 步骤 1: 环境准备

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（如未创建）
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 步骤 2: 配置环境变量

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑 .env 文件，配置以下关键变量：
# - SECRET_KEY: 生成随机密钥
# - DATABASE_URL: 数据库连接字符串
# - COS_SECRET_ID/COS_SECRET_KEY: 腾讯云 COS 凭证（可选）
```

**生成 SECRET_KEY**:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 步骤 3: 启动数据库和 Redis

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

### 步骤 4: 执行数据库迁移

```bash
# 激活虚拟环境
source .venv/bin/activate

# 执行迁移
alembic upgrade head

# 查看当前版本
alembic current
```

**预期输出**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> dcd94c32d506, add_ai_resource_community_ledger_notification_file
```

### 步骤 5: 验证数据库

```bash
# 连接数据库
psql -h localhost -U postgres -d relihub

# 查看表数量
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';

# 查看所有表
\dt

# 退出
\q
```

**预期结果**:
- 数据表数量：12+
- 包含：users, ai_sessions, resources, topics, ledger_entries, notifications, files 等

### 步骤 6: 启动应用

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**预期输出**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxx]
INFO:     Started server process [xxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## ✅ 部署验证

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

**预期响应**:
```json
{"status": "healthy"}
```

### 2. API 文档访问

浏览器访问：http://localhost:8000/docs

**检查项**:
- [ ] Swagger UI 正常加载
- [ ] 所有 API 端点显示正常
- [ ] 可以尝试执行 API 调用

### 3. 数据库连接验证

```bash
curl http://localhost:8000/api/v1/health/database
```

**预期响应**:
```json
{
  "status": "ok",
  "database": "connected",
  "tables": 12
}
```

### 4. 功能冒烟测试

```bash
# 用户注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "password": "Test123456",
    "sms_code": "888888"
  }'

# 获取资源列表
curl http://localhost:8000/api/v1/resources/
```

---

## 🐛 常见问题排查

### 问题 1: 数据库连接失败

**错误**: `could not connect to server`

**解决方案**:
```bash
# 检查 Docker 容器
docker-compose ps

# 重启数据库容器
docker-compose restart db

# 检查端口占用
lsof -i :5432

# 查看数据库日志
docker-compose logs db
```

### 问题 2: 端口已被占用

**错误**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或者修改端口
uvicorn app.main:app --port 8001
```

### 问题 3: 迁移失败

**错误**: `alembic.util.exc.CommandError`

**解决方案**:
```bash
# 检查迁移历史
alembic history

# 回滚到上一个版本
alembic downgrade -1

# 重新迁移
alembic upgrade head

# 如果仍然失败，重置数据库
docker-compose down -v
docker-compose up -d db
alembic upgrade head
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

# 检查 Python 版本
python3 --version  # 应为 3.9+
```

---

## 📊 部署验证清单

完成部署后，请确认以下项目：

### 基础设施
- [ ] Docker 容器运行正常
- [ ] PostgreSQL 可连接
- [ ] Redis 可连接
- [ ] 数据库迁移已执行

### 应用服务
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

## 🔐 安全注意事项

### 开发环境
- ✅ 可以使用测试密钥
- ✅ 可以启用 mock 模式
- ✅ 可以关闭 CORS 限制

### 生产环境
- ⚠️ 必须使用强 SECRET_KEY
- ⚠️ 必须配置真实数据库密码
- ⚠️ 必须启用 HTTPS
- ⚠️ 必须配置正确的 CORS 域名
- ⚠️ 必须关闭调试模式

---

## 📞 获取帮助

如遇到其他问题：

1. 查看应用日志：
   ```bash
   docker-compose logs -f
   ```

2. 查看数据库日志：
   ```bash
   docker-compose logs db
   ```

3. 查看 Alembic 迁移日志：
   ```bash
   alembic current -v
   ```

4. 联系开发团队

---

**部署成功后，请继续执行冒烟测试和 UAT 测试！** 🎉

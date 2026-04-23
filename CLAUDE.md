# ReliHub 开发指南

## 技术栈
- 前端: React 18 + Vite + TypeScript + Tailwind CSS + Zustand
- 后端: FastAPI + SQLAlchemy + Celery
- 数据库: PostgreSQL (pgvector) + Redis

## 目录结构
```
backend/app/
├── api/v1/          # API路由 (admin, ai, auth, community, ledger, notification, resources, search, users)
├── core/            # config, deps, exceptions, security
├── models/          # SQLAlchemy模型
├── schemas/         # Pydantic schemas
└── services/        # 业务逻辑

frontend/src/
├── components/      # UI组件
├── pages/           # 页面
├── services/        # API调用
└── store/           # Zustand状态
```

## 核心规范

### 数据库操作
- 计数更新必须用原子操作: `update(Resource).values(like_count=Resource.like_count + 1)`
- 并发操作必须用行级锁: `query.with_for_update()`

### 事务管理
```python
try:
    self.db.begin()
    # 操作
    self.db.commit()
except:
    self.db.rollback()
    raise
```

### 错误码
- `COM_4005`: 业务错误 | `COM_4006`: 交互错误 | `RES_4008`: 资源不存在 | `USER_4010`: 用户不存在

## 功能模块
1. **启动与游客模式**: 游客每日3次AI会话，会话存Redis(TTL=24h)
2. **登录注册**: 手机号+验证码/密码+微信登录，Argon2id密码哈希
3. **爱问(ReliBot)**: 流式SSE对话、多轮支持、附件上传、System Prompt围栏
4. **资源**: OSS上传、分类、点赞/收藏
5. **社区**: 话题、回复、点赞、举报
6. **我的**: 签到(每日10+早鸟5积分)、可可豆、信誉分
7. **搜索**: PostgreSQL全文搜索
8. **管理后台**: 用户、内容、LLM配置

## 测试
```bash
# 后端
cd backend && source .venv/bin/activate && python -m pytest --cov=app tests/

# 前端
cd frontend && npm run test:coverage
```
目标: 覆盖率≥80%

## 部署
```bash
# 后端
cd backend && docker-compose up -d && ./deploy.sh

# 前端
cd frontend && npm run dev
```

**端口**: 前端3000/5179 | 后端8000 | API文档8000/docs

## 安全
- JWT认证 (access 1h / refresh 7d)
- 密码Argon2id哈希
- 手机号盲索引保护
- 敏感词双轨检查

## 关键文件
- `backend/app/core/config.py`: 配置
- `backend/app/core/exceptions.py`: 错误码
- `backend/app/services/interaction_service.py`: 交互服务
- `frontend/src/store/authStore.ts`: 认证状态
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

## 兼容性检查流程

### 提交前强制检查
在每次提交最新代码改动前，必须执行全面的兼容性检查流程，确保所有前端组件（包括用户端界面和管理后台系统）与后端API接口规范及数据库结构实现完全对齐。

### 检查内容
1. **数据字段对齐**
   - 验证前端数据模型与后端数据库表结构字段名称、数据类型一致
   - 检查所有API请求/响应字段的命名规范和数据格式

2. **API接口规范**
   - 确认前端API调用方式与后端接口定义完全匹配
   - 验证HTTP方法、URL路径、请求参数、响应格式
   - 检查分页、排序、过滤等参数传递规范

3. **数据类型一致性**
   - 确保TypeScript接口定义与Python Pydantic Schema一致
   - 验证枚举值、布尔值、日期时间等特殊类型的处理

4. **错误处理机制**
   - 确认前端错误处理逻辑与后端错误码体系对齐
   - 验证异常情况的用户提示和重试机制

5. **配置项管理**
   - 检查系统配置项的白名单配置
   - 验证配置项的存储格式和解析逻辑

### 检查清单
- [ ] 前端TypeScript接口与后端Pydantic Schema对齐
- [ ] API端点路径和HTTP方法正确
- [ ] 请求参数和响应格式一致
- [ ] 数据库字段与前端数据模型匹配
- [ ] 错误码和处理逻辑对齐
- [ ] 配置项白名单包含所有必要的键
- [ ] 数据持久化格式正确解析

### 验证方法
1. **手动测试**：通过管理后台和用户端界面进行功能测试
2. **API测试**：使用Postman或curl验证API接口
3. **数据库检查**：直接查询数据库确认数据完整性
4. **日志分析**：检查审计日志和错误日志

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
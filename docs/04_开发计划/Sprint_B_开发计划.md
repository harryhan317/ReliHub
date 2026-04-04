# Sprint B 开发计划

> **文档版本**: V1.0  
> **创建日期**: 2026-04-04  
> **适用范围**: ReliHub MVP 阶段 (Phase 1)  
> **预计周期**: 6-8 周

---

## 一、Sprint B 概述

### 1.1 Sprint 定位
**Sprint B** 是 ReliHub MVP 的核心功能实现阶段，重点完成 **AI 爱问模块**、**资源模块**、**社区模块** 三大核心业务功能。

### 1.2 Sprint 目标
| 模块 | 完成度目标 | 核心交付物 |
|------|-----------|-----------|
| **爱问模块** | 100% | AI 对话、附件上传、历史会话管理 |
| **资源模块** | 100% | 资源上传、审核、预览、下载、分账 |
| **社区模块** | 100% | 话题发起、回复、采纳、悬赏 |
| **可可豆系统** | 100% | 记账流水、分账引擎、扩充包 |
| **通知系统** | 80% | 系统通知、互动通知（基础功能） |

---

## 二、Sprint B 工作分解结构（WBS）

### 阶段 1：数据库与模型层（Week 1）

#### 1.1 数据库表创建
**优先级**：🔴 **最高**

| 任务 | 对应文档 | 预计工时 | 依赖 |
|------|---------|---------|------|
| 创建 `ai_sessions` 表 | DB_ai 对话.md | 2h | - |
| 创建 `ai_messages` 表 | DB_ai 对话.md | 2h | ai_sessions |
| 创建 `file_meta` 表 | DB_文件元数据.md | 2h | - |
| 创建 `resources` 表 | DB_资源.md | 2h | file_meta |
| 创建 `resource_previews` 表 | DB_资源.md | 1h | resources |
| 创建 `topics` 表 | DB_社区.md | 2h | - |
| 创建 `posts` 表 | DB_社区.md | 2h | topics |
| 创建 `point_ledger` 表 | DB_可可豆.md | 2h | users |
| 创建 `asset_packages` 表 | DB_可可豆.md | 1h | - |
| 创建 `notifications` 表 | DB_通知.md | 2h | users |

**交付物**：
- Alembic migration 脚本
- SQLAlchemy ORM 模型文件
- 数据库验证脚本

---

#### 1.2 ORM 模型实现
**优先级**：🔴 **最高**

| 文件路径 | 模型类 | 预计工时 |
|---------|-------|---------|
| `backend/app/models/ai_session.py` | AISession | 3h |
| `backend/app/models/ai_message.py` | AIMessage | 3h |
| `backend/app/models/file_meta.py` | FileMeta | 3h |
| `backend/app/models/resource.py` | Resource, ResourcePreview | 4h |
| `backend/app/models/topic.py` | Topic | 3h |
| `backend/app/models/post.py` | Post | 3h |
| `backend/app/models/ledger.py` | PointLedger, AttemptedTransaction, AssetPackage | 4h |
| `backend/app/models/notification.py` | Notification | 3h |

**关键实现要点**：
- ✅ 所有字段类型与 DB 文档 100% 对齐
- ✅ 索引定义完整（特别是外键索引）
- ✅ Enum 类型正确映射
- ✅ 逻辑删除字段 `is_deleted` 统一实现
- ✅ 时间戳自动管理（`created_at`, `updated_at`）

---

### 阶段 2：Pydantic Schemas（Week 2）

#### 2.1 Request/Response Schemas
**优先级**：🔴 **最高**

| 文件路径 | 主要 Schema | 预计工时 |
|---------|------------|---------|
| `backend/app/schemas/ai.py` | 对话相关 Schema | 4h |
| `backend/app/schemas/resource.py` | 资源相关 Schema | 4h |
| `backend/app/schemas/community.py` | 社区相关 Schema | 4h |
| `backend/app/schemas/ledger.py` | 可可豆相关 Schema | 3h |
| `backend/app/schemas/notification.py` | 通知相关 Schema | 2h |

**关键实现要点**：
- ✅ 所有字段验证规则（长度、范围、正则）
- ✅ 嵌套 Schema 正确组织
- ✅ 响应 Schema 包含 `from_attributes = True`

---

### 阶段 3：核心业务服务层（Week 3-4）

#### 3.1 AI 爱问模块服务
**优先级**：🔴 **最高**

| 服务文件 | 核心功能 | 预计工时 | PRD 对齐 |
|---------|---------|---------|---------|
| `services/ai_service.py` | 对话管理、配额校验 | 8h | M1-F001, F006, F008 |
| `services/attachment_service.py` | 附件上传、OSS 集成 | 6h | M1-F007 |
| `services/quota_service.py` | 配额管理、限额校验 | 6h | 可可豆体系§4.1.2 |

**关键业务逻辑**：
```python
# 配额校验伪代码
def validate_ai_quota(user: User, action: str) -> bool:
    # 1. 检查每日新会话上限
    # 2. 检查每日问答总轮次
    # 3. 检查单会话轮次上限
    # 4. 检查 Token 余额
    # 5. 检查敏感词
    # 6. 返回 True/False + 具体原因
```

---

#### 3.2 资源模块服务
**优先级**：🔴 **最高**

| 服务文件 | 核心功能 | 预计工时 | PRD 对齐 |
|---------|---------|---------|---------|
| `services/resource_service.py` | 资源 CRUD、状态流转 | 10h | M2-F001~F010 |
| `services/resource_audit_service.py` | AI 预审、查重、敏感词 | 8h | M2-F009, M5-F001 |
| `services/download_service.py` | 下载鉴权、扣费、分账 | 10h | M2-F015, F020 |
| `services/preview_service.py` | 安全预览、水印 | 6h | M2-F013 |

**关键业务逻辑**：
```python
# 70/30 分账伪代码
def distribute_resource_revenue(downloader_id, resource_id):
    # 1. 查询资源定价 P
    # 2. 检查下载者余额（优先福利豆）
    # 3. 原子事务：
    #    - 扣除下载者 P 豆
    #    - 贡献者 + floor(P * 0.7)
    #    - 系统销毁 + floor(P * 0.3)
    #    - 记录 point_ledger 三条流水
    # 4. 生成下载 Token（5 分钟有效）
    # 5. 写入数字水印
```

---

#### 3.3 社区模块服务
**优先级**：🔴 **最高**

| 服务文件 | 核心功能 | 预计工时 | PRD 对齐 |
|---------|---------|---------|---------|
| `services/topic_service.py` | 话题 CRUD、悬赏管理 | 8h | M3-F001~F010 |
| `services/post_service.py` | 回复、采纳、点赞 | 6h | M3-F011~F020 |
| `services/bounty_service.py` | 悬赏锁定/释放/退款 | 6h | M3-F021~F026 |

**关键业务逻辑**：
```python
# 悬赏采纳 70/30 分账
def accept_bounty(topic_id, post_id):
    # 1. 查询悬赏金额 B
    # 2. 原子事务：
    #    - 回答者 + floor(B * 0.7)
    #    - 系统销毁 + floor(B * 0.3)
    #    - 更新 topic.bounty_status = RESOLVED
    #    - 更新 topic.accepted_post_id
```

---

#### 3.4 可可豆系统服务
**优先级**：🔴 **最高**

| 服务文件 | 核心功能 | 预计工时 | PRD 对齐 |
|---------|---------|---------|---------|
| `services/ledger_service.py` | 复式记账、流水记录 | 8h | DB_可可豆§1 |
| `services/bean_service.py` | 福利豆/资产豆管理 | 4h | PRD 可可豆体系§2.2 |

**关键设计**：
- ✅ 每一笔可可豆变动必须记录 `point_ledger`
- ✅ 消耗顺序：福利豆 → 资产豆
- ✅ 所有计算使用 `floor()` 向下取整
- ✅ 事务原子性保证

---

### 阶段 4：API 路由层（Week 5-6）

#### 4.1 AI 爱问模块 API
**优先级**：🔴 **最高**

| 路由文件 | 端点 | 预计工时 | API 文档对齐 |
|---------|------|---------|-------------|
| `api/v1/ai/router.py` | POST /sessions | 4h | API_爱问模块§2.1 |
| | GET /sessions | 2h | API_爱问模块§2.2 |
| | POST /sessions/{id}/messages | 6h | API_爱问模块§2.3 |
| | GET /sessions/{id}/messages | 2h | API_爱问模块§2.4 |
| | POST /attachments | 4h | API_爱问模块§2.5 |
| | DELETE /sessions/{id} | 2h | API_爱问模块§2.6 |

**SSE 流式输出实现**：
```python
@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, body: MessageRequest, user: User = Depends(get_current_user)):
    async def generate():
        async for chunk in ai_service.stream_response(session_id, body.content):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

---

#### 4.2 资源模块 API
**优先级**：🔴 **最高**

| 路由文件 | 端点 | 预计工时 | API 文档对齐 |
|---------|------|---------|-------------|
| `api/v1/resources/router.py` | GET / (列表) | 4h | API_资源模块§2.1 |
| | POST / (上传) | 6h | API_资源模块§2.2 |
| | GET /{id} (详情) | 2h | API_资源模块§2.3 |
| | POST /{id}/download | 6h | API_资源模块§2.4 |
| | GET /{id}/preview | 4h | API_资源模块§2.5 |
| | POST /{id}/like | 2h | API_资源模块§2.6 |

---

#### 4.3 社区模块 API
**优先级**：🔴 **最高**

| 路由文件 | 端点 | 预计工时 | API 文档对齐 |
|---------|------|---------|-------------|
| `api/v1/community/router.py` | GET /topics (列表) | 4h | API_社区模块§2.1 |
| | POST /topics (发起) | 6h | API_社区模块§2.2 |
| | GET /topics/{id} (详情) | 2h | API_社区模块§2.3 |
| | POST /topics/{id}/posts (回复) | 4h | API_社区模块§2.4 |
| | POST /topics/{id}/accept (采纳) | 4h | API_社区模块§2.5 |
| | POST /topics/{id}/like | 2h | API_社区模块§2.6 |

---

### 阶段 5：集成与测试（Week 7-8）

#### 5.1 端到端集成测试
**优先级**：🟡 **高**

| 测试场景 | 覆盖功能 | 预计工时 |
|---------|---------|---------|
| AI 对话完整流程 | 创建会话→多轮对话→保存历史 | 4h |
| 资源上传下载 | 上传→审核→预览→扣费下载→分账 | 6h |
| 社区悬赏 | 发起悬赏→回复→采纳→分账 | 4h |
| 可可豆流水 | 验证所有交易类型正确记账 | 4h |

---

#### 5.2 性能测试
**优先级**：🟡 **高**

| 测试项 | 性能指标 | 目标值 |
|-------|---------|--------|
| AI 首字响应 | TTFT | ≤1 秒 |
| SSE 流式输出 | 延迟 | ≤200ms/chunk |
| 资源下载 | 并发下载 | ≥20 用户同时 |
| 数据库查询 | 列表页响应 | ≤500ms |

---

## 三、关键技术决策

### 3.1 AI 对话 SSE 流式输出
**技术选型**：FastAPI `StreamingResponse` + Server-Sent Events

**理由**：
- ✅ 原生支持流式输出
- ✅ 前端 EventSource API 简单
- ✅ 比 WebSocket 更轻量

---

### 3.2 文件存储方案
**技术选型**：腾讯云 COS（MVP 阶段）

**理由**：
- ✅ 成本低（0.118 元/GB/月）
- ✅ 集成简单（官方 SDK）
- ✅ 支持水印、防盗链

---

### 3.3 分账事务处理
**技术选型**：PostgreSQL 事务 + 行级锁

**实现**：
```python
with db.begin_nested():  # SAVEPOINT
    # 1. 锁定用户行（SELECT FOR UPDATE）
    user = db.query(User).filter(User.id == user_id).with_for_update().first()
    
    # 2. 检查余额
    if user.gold_beans + user.bonus_beans < amount:
        raise BusinessException(ErrorCode.ECON_4001)
    
    # 3. 执行扣费和分账
    # ...
    
    # 4. 记录流水
    ledger = PointLedger(...)
    db.add(ledger)
```

---

### 3.4 Token 限流方案
**技术选型**：Redis + 滑动窗口计数器

**Key 设计**：
```
# 每日新会话计数
ai:daily_sessions:{user_id}:{date} -> count, TTL=24h

# 单会话轮次计数
ai:session_turns:{session_id} -> count, TTL=7d

# 每日 Token 消耗
ai:daily_tokens:{user_id}:{date} -> count, TTL=24h
```

---

## 四、风险与缓解措施

### 风险 1：AI API 成本失控
**概率**：🟡 中 | **影响**：🔴 高

**缓解措施**：
1. ✅ 严格执行配额管理（每日/每会话限制）
2. ✅ 敏感词过滤前置（减少无效调用）
3. ✅ 设置 Token 消耗上限告警
4. ✅ 实现请求限流（Redis 限流器）

---

### 风险 2：文件上传安全漏洞
**概率**：🟡 中 | **影响**：🔴 高

**缓解措施**：
1. ✅ ClamAV 病毒扫描（上传前）
2. ✅ 文件类型白名单校验
3. ✅ 文件大小限制（20MB）
4. ✅ OSS 私有读权限（防盗链 Token）

---

### 风险 3：分账逻辑精度误差
**概率**：🟢 低 | **影响**：🔴 高

**缓解措施**：
1. ✅ 统一使用 `floor()` 向下取整
2. ✅ 所有计算使用整数（避免浮点误差）
3. ✅ 每条流水记录 `balance_after` 快照
4. ✅ 每日对账脚本（审计 `point_ledger` 总和）

---

## 五、交付清单

### 5.1 代码交付
- [ ] 14 个 ORM 模型文件
- [ ] 25+ 个 Pydantic Schema
- [ ] 12 个 Service 服务文件
- [ ] 9 个 API Router 文件
- [ ] Alembic Migration 脚本
- [ ] 单元测试（覆盖率≥80%）
- [ ] 集成测试脚本

---

### 5.2 文档交付
- [ ] API 接口文档（Swagger/OpenAPI）
- [ ] 数据库 ER 图
- [ ] 部署文档（Docker Compose）
- [ ] 用户使用手册（MVP 版）

---

## 六、里程碑

| 里程碑 | 时间节点 | 交付物 | 验收标准 |
|-------|---------|--------|---------|
| **M1：数据库就绪** | Week 1 结束 | 所有表创建完成 | 能通过 Alembic 迁移 |
| **M2：服务层完成** | Week 4 结束 | 所有 Service 实现 | 单元测试通过 |
| **M3：API 完成** | Week 6 结束 | 所有端点可用 | Postman 测试通过 |
| **M4：集成测试** | Week 8 结束 | 端到端测试通过 | 性能指标达标 |

---

## 七、团队分工建议

| 角色 | 职责 | 建议人数 |
|------|------|---------|
| **后端开发** | 模型、服务、API | 2-3 人 |
| **前端开发** | React 界面、状态管理 | 2 人 |
| **测试工程师** | 测试用例、自动化 | 1 人 |
| **DevOps** | Docker、CI/CD、部署 | 1 人 |

---

## 八、下一步行动

### 立即开始（Week 1 Day 1）

1. **创建数据库 Migration**
   ```bash
   alembic revision --autogenerate -m "Add AI, Resource, Community tables"
   ```

2. **实现 ORM 模型**
   - 优先实现 `AISession`, `AIMessage`, `FileMeta`
   - 然后实现 `Resource`, `Topic`, `Post`
   - 最后实现 `PointLedger`, `Notification`

3. **编写单元测试**
   - 每个模型一个测试文件
   - 验证字段约束、索引、关系

---

**准备好了吗？让我们开始 Sprint B 的征程！** 🚀

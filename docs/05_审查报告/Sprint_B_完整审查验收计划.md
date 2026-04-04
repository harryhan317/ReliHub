# Sprint B 完整审查验收计划

> **文档版本**: V1.0  
> **创建日期**: 2026-04-04  
> **审查范围**: Sprint B 全周期工作成果（阶段 1-5）  
> **验收标准**: 与 PRD/技术设计文档 100% 对齐  
> **责任人**: 质量审查团队

---

## 一、审查概述

### 1.1 审查目标
全面验证 Trae 完成的 Sprint B 工作是否达到验收标准，包括：
1. **需求完整性** - 是否覆盖 PRD 中的所有需求
2. **设计一致性** - 是否遵循技术设计文档
3. **代码质量** - 是否符合编码规范与最佳实践
4. **功能完备性** - 是否具备全部业务逻辑
5. **性能指标** - 是否达到非功能需求
6. **安全合规性** - 是否通过安全审查

### 1.2 审查范围
| 阶段 | 交付物 | 优先级 |
|------|--------|--------|
| **阶段 1** | 数据库表 + ORM 模型 | 🔴 必须 |
| **阶段 2** | Pydantic Schemas | 🔴 必须 |
| **阶段 3** | Service 服务层 | 🔴 必须 |
| **阶段 4** | API 路由层 | 🔴 必须 |
| **阶段 5** | 集成测试 + 文档 | 🟡 重要 |

### 1.3 审查参与者
- **代码审查**: 2 名资深开发
- **设计审查**: 1 名架构师
- **测试审查**: 1 名 QA 工程师
- **安全审查**: 1 名安全专家（可选）

---

## 二、分层审查计划

### 阶段 1：数据库与 ORM 模型审查

#### 审查清单

##### 1.1 数据库表完整性
**审查项目**: 所有 12 个表是否创建完成

| 表名 | 关键字段数 | 索引数 | 状态 | 检查方法 |
|-----|---------|--------|------|---------|
| `ai_sessions` | 11 | 2 | ? | `\d ai_sessions` in psql |
| `ai_messages` | 10 | 2 | ? | `\d ai_messages` in psql |
| `file_meta` | 10 | 3 | ? | `\d file_meta` in psql |
| `file_usage` | 6 | 2 | ? | `\d file_usage` in psql |
| `resources` | 17 | 4 | ? | `\d resources` in psql |
| `resource_previews` | 5 | 1 | ? | `\d resource_previews` in psql |
| `topics` | 14 | 3 | ? | `\d topics` in psql |
| `posts` | 9 | 2 | ? | `\d posts` in psql |
| `point_ledger` | 11 | 5 | ? | `\d point_ledger` in psql |
| `attempted_transaction` | 5 | 2 | ? | `\d attempted_transaction` in psql |
| `asset_packages` | 5 | 0 | ? | `\d asset_packages` in psql |
| `user_purchased_assets` | 8 | 2 | ? | `\d user_purchased_assets` in psql |
| `notifications` | 12 | 3 | ? | `\d notifications` in psql |

**验收标准**:
- ✅ 所有 12 个表存在
- ✅ 表结构与 DB_*.md 文档 100% 对齐
- ✅ 所有字段类型正确
- ✅ 所有约束正确（PK, FK, NOT NULL, UNIQUE）

**测试命令**:
```bash
# 检查表是否存在
psql -U postgres -d reliHub -c "\dt"

# 检查特定表结构
psql -U postgres -d reliHub -c "\d ai_sessions"

# 检查索引
psql -U postgres -d reliHub -c "\di"
```

---

##### 1.2 ORM 模型文件完整性
**审查项目**: 8 个 ORM 模型文件是否正确实现

```python
# 检查清单
models/
├── ai_session.py        # ✅ 必须包含: AISession 类, 11 个字段, 2 个索引
├── ai_message.py        # ✅ 必须包含: AIMessage 类, 10 个字段, 2 个索引
├── file_meta.py         # ✅ 必须包含: FileMeta 类, 10 个字段, 3 个索引
├── resources.py         # ✅ 必须包含: Resource, ResourcePreview 类
├── topic.py             # ✅ 必须包含: Topic 类, 14 个字段, 3 个索引
├── ledger.py            # ✅ 必须包含: PointLedger, AttemptedTransaction, AssetPackage 类
├── notification.py      # ✅ 必须包含: Notification 类, 12 个字段, 3 个索引
└── __init__.py          # ✅ 必须包含: 所有类的正确导入
```

**验收标准**:
- ✅ 所有 8 个文件存在
- ✅ 每个文件包含对应的 SQLAlchemy 模型类
- ✅ 所有字段都有正确的数据类型注解
- ✅ 所有主键都是 UUID (String(36))
- ✅ 所有时间戳字段使用 `DateTime(timezone=True)`
- ✅ 所有 Enum 类型都正确定义
- ✅ 所有索引都正确定义（包括复合索引）

**详细检查点**:

###### AISession 模型
```python
# 应包含字段
id: UUID (PK)
user_id: UUID (可空, 索引)
title: String(100, 可空)
model_type: String(50, 默认='general')
total_tokens: Integer(默认=0)
total_turns: Integer(默认=0)
max_turns: Integer(默认=50)
max_tokens: Integer(默认=50000)
is_deleted: Boolean(默认=False)
created_at: DateTime (索引)
updated_at: DateTime

# 必须包含索引
idx_user_created: (user_id, created_at)
idx_sessions_user_id
```

###### AIMessage 模型
```python
# 应包含字段
id: UUID (PK)
session_id: UUID (索引)
role: String(20) - ['user', 'assistant']
content: Text
token_count: Integer(默认=0)
has_attachment: Boolean(默认=False)
attachment_ids: String(500, 可空)
feedback_type: String(20, 可空) - ['helpful', 'unhelpful', 'bug', 'improvement']
is_deleted: Boolean(默认=False)
created_at: DateTime
```

###### FileMeta 模型
```python
# 应包含字段
file_uuid: UUID (PK)
file_hash: String(64, 唯一, 索引)
oss_path: String(1024, 必填)
file_name: String(255)
file_size: Integer
mime_type: String(100)
ref_counts: Integer(默认=1)
status: Enum[FileStatus] (6 个值)
lifecycle_status: Enum[LifecycleStatus] (3 个值)
uploader_uid: UUID (索引)

# Enum 值验证
FileStatus: NORMAL, SCANNING, ISOLATED, SUSPICIOUS, BLOCKED, DELETED
LifecycleStatus: ACTIVE, SOFT_DELETED, PERMANENTLY_DELETED
```

###### Resource 模型
```python
# 应包含字段（共 17 个）
id: UUID (PK)
uploader_id: UUID (索引)
title: String(255, 索引)
description: Text(可空)
category_id: Integer
tags: String(500, 可空) [JSON 格式]
price: Integer(默认=5)
file_uuid: UUID (FK)
view_count: Integer(默认=0)
download_count: Integer(默认=0)
like_count: Integer(默认=0)
dislike_count: Integer(默认=0)
heat_score: Float(索引, 默认=0.0)
is_seed: Boolean(默认=False)
status: Enum[ResourceStatus] (6 个值, 索引)
anonymized_user_hash: String(64, 索引, 可空)
is_deleted: Boolean(默认=False)
created_at: DateTime (索引)
updated_at: DateTime

# Enum 值验证
ResourceStatus: SCANNING, PENDING_REVIEW, APPROVED, REJECTED, APPEALING, BLOCKED
```

###### Topic 模型
```python
# 应包含字段（共 14 个）
id: UUID (PK)
author_id: UUID (索引)
title: String(255)
content: Text
category_id: Integer
bounty_amount: Integer(默认=0)
bounty_status: Enum[BountyStatus] (4 个值)
accepted_post_id: UUID(可空)
status: Enum[TopicStatus] (3 个值)
is_deleted: Boolean(默认=False)
view_count: Integer(默认=0)
post_count: Integer(默认=0)
heat_score: Float(索引, 默认=0.0)
anonymized_user_hash: String(64, 索引, 可空)
created_at: DateTime (索引)

# Enum 值验证
BountyStatus: NONE, ACTIVE, RESOLVED, REFUNDED
TopicStatus: NORMAL, BLOCKED, PENDING
```

###### PointLedger 模型
```python
# 应包含字段（共 11 个）
id: UUID (PK)
transaction_uuid: UUID (索引)
user_id: UUID (索引)
amount: Integer
point_type: Enum[PointType] (2 个值)
dist_ratio: Float(可空)
order_type: Enum[OrderType] (18 个值, 索引)
balance_after: Integer
related_id: UUID(索引, 可空)
description: String(255, 可空)
created_at: DateTime (索引)

# Enum 值验证
PointType: GOLD_BEAN, BONUS_BEAN
OrderType: 18 个值（DOWNLOAD, DOWNLOAD_REVENUE, DESTRUCTION, BOUNTY_AMOUNT_LOCKED, 
          BOUNTY_AMOUNT_RELEASED, BOUNTY_DISTRIBUTION, FEEDBACK_REWARD 等）
```

###### Notification 模型
```python
# 应包含字段（共 12 个）
id: UUID (PK)
receiver_id: UUID (索引)
sender_id: UUID(可空)
type: Enum[NotificationType] (5 个值, 索引)
priority: Enum[NotificationPriority] (2 个值)
is_broadcast_exemption: Boolean(默认=False)
title: String(100, 可空)
content: Text
link_url: String(500, 可空)
is_read: Boolean(默认=False)
read_at: DateTime(可空)
created_at: DateTime (索引)

# Enum 值验证
NotificationType: SYSTEM, INTERACTION, AUDIT, REWARD, BROADCAST
NotificationPriority: NORMAL, HIGH
```

**测试脚本**:
```python
# 验证模型导入
from app.models import (
    AISession, AIMessage, FileMeta, FileUsage,
    Resource, ResourcePreview,
    Topic, Post,
    PointLedger, AttemptedTransaction, AssetPackage,
    UserPurchasedAssets,
    Notification
)

# 验证字段存在
assert hasattr(AISession, 'id')
assert hasattr(AISession, 'user_id')
# ... 逐一检查所有字段

# 验证 Enum 类型
from app.models import FileStatus, ResourceStatus, BountyStatus
assert len(FileStatus) == 6
assert len(ResourceStatus) == 6
assert len(BountyStatus) == 4
```

---

#### 1.3 Migration 脚本审查
**审查项目**: Alembic Migration 脚本的正确性

**检查清单**:
- ✅ Migration 文件存在: `alembic/versions/dcd94c32d506_add_ai_resource_community_ledger_.py`
- ✅ Migration 脚本能够正确执行
- ✅ 所有表创建命令正确
- ✅ 所有索引创建命令正确
- ✅ 所有外键关系正确
- ✅ 脚本包含 `upgrade()` 和 `downgrade()` 函数

**测试命令**:
```bash
# 执行迁移
cd backend
alembic upgrade head

# 验证表创建
psql -U postgres -d reliHub -c "\dt"

# 回滚测试
alembic downgrade -1

# 再次执行
alembic upgrade head
```

**验收标准**:
- ✅ Migration 脚本能完整执行
- ✅ 所有表成功创建
- ✅ 所有索引成功创建
- ✅ 回滚功能正常

---

#### 1.4 关键设计决策验证
**审查项目**: 数据库设计中的关键决策是否合理

| 决策项 | 方案 | 验证点 | 状态 |
|--------|------|--------|------|
| **主键策略** | UUID (String(36)) | 所有表主键一致 | ? |
| **软删除** | `is_deleted` 字段 | 核心业务表都有 | ? |
| **时间戳** | `created_at`, `updated_at` | 所有表都有 | ? |
| **状态枚举** | PostgreSQL ENUM | 避免字符串 | ? |
| **复合索引** | `(user_id, created_at)` | 优化查询性能 | ? |
| **外键约束** | 正确的 ON DELETE 策略 | 检查级联删除 | ? |

---

### 阶段 2：Pydantic Schemas 审查

#### 审查清单

##### 2.1 Schema 文件完整性
**审查项目**: 5 个 Schema 文件是否完整实现

```python
schemas/
├── ai.py                # 对话相关 Schema
├── resource.py          # 资源相关 Schema
├── community.py         # 社区相关 Schema
├── ledger.py            # 可可豆相关 Schema
├── notification.py      # 通知相关 Schema
└── common.py            # 通用 Schema
```

**验收标准**:
- ✅ 所有 5 个文件存在
- ✅ 每个文件包含完整的 Request/Response Schema
- ✅ 所有字段都有正确的类型注解
- ✅ 所有字段都有必要的验证器
- ✅ 所有 Response Schema 包含 `model_config = ConfigDict(from_attributes=True)`

---

##### 2.2 AI 对话 Schema (`ai.py`)

**必须包含的 Schema**:
```python
# Request Schema
class CreateSessionRequest:
    model_type: str = Field(default="general", description="对话模型类型")

class MessageRequest:
    content: str = Field(min_length=1, max_length=4000, description="消息内容")
    has_attachment: bool = Field(default=False)
    attachment_ids: Optional[List[str]] = Field(default=None)

# Response Schema
class AISessionResponse:
    id: str
    user_id: Optional[str]
    title: Optional[str]
    model_type: str
    total_tokens: int
    total_turns: int
    max_turns: int
    created_at: datetime
    updated_at: datetime

class AIMessageResponse:
    id: str
    session_id: str
    role: str
    content: str
    token_count: int
    has_attachment: bool
    attachment_ids: Optional[str]
    feedback_type: Optional[str]
    created_at: datetime

class ChatStreamResponse:
    # SSE 流式输出格式
    chunk: str
    token_count: int
    finished: bool
```

**验收标准**:
- ✅ 所有字段都有 `Field()` 描述
- ✅ 所有枚举字段都使用 Enum 类型
- ✅ 所有时间戳字段使用 `datetime` 类型
- ✅ 所有可空字段使用 `Optional[T]`
- ✅ 所有请求 Schema 都有字段验证

---

##### 2.3 资源 Schema (`resource.py`)

**必须包含的 Schema**:
```python
# Request Schema
class CreateResourceRequest:
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=10000)
    category_id: int
    tags: Optional[List[str]] = Field(default=None)
    price: int = Field(ge=5, le=10000, default=5)
    file_uuid: str

class UpdateResourceRequest:
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None

class ResourceDownloadRequest:
    resource_id: str

# Response Schema
class ResourceResponse:
    id: str
    uploader_id: str
    title: str
    description: Optional[str]
    category_id: int
    tags: Optional[List[str]]
    price: int
    file_uuid: str
    view_count: int
    download_count: int
    like_count: int
    dislike_count: int
    heat_score: float
    is_seed: bool
    status: str
    created_at: datetime
    updated_at: datetime

class ResourcePreviewResponse:
    id: str
    resource_id: str
    preview_url: str
    page_number: Optional[int]

class DownloadTokenResponse:
    download_token: str
    expires_at: datetime
    file_url: str
```

**验收标准**:
- ✅ 字段验证范围正确（特别是 `price` 范围）
- ✅ Tags 使用 List[str] 类型
- ✅ 状态字段使用枚举类型
- ✅ 分页信息完整（Response 中包含 `total`, `page`, `page_size`）

---

##### 2.4 社区 Schema (`community.py`)

**必须包含的 Schema**:
```python
# Request Schema
class CreateTopicRequest:
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=10, max_length=50000)
    category_id: int
    bounty_amount: int = Field(ge=0, le=100000, default=0)

class CreatePostRequest:
    content: str = Field(min_length=1, max_length=50000)
    parent_id: Optional[str] = None

class AcceptPostRequest:
    post_id: str

# Response Schema
class TopicResponse:
    id: str
    author_id: str
    title: str
    content: str
    category_id: int
    bounty_amount: int
    bounty_status: str
    accepted_post_id: Optional[str]
    status: str
    view_count: int
    post_count: int
    heat_score: float
    created_at: datetime

class PostResponse:
    id: str
    topic_id: str
    author_id: str
    content: str
    parent_id: Optional[str]
    is_accepted: bool
    like_count: int
    created_at: datetime

class BountyDistributionResponse:
    answerer_id: str
    amount: int
    reason: str
    transaction_id: str
```

**验收标准**:
- ✅ 悬赏金额验证范围正确
- ✅ 采纳操作返回分账信息
- ✅ 状态字段使用枚举

---

##### 2.5 可可豆 Schema (`ledger.py`)

**必须包含的 Schema**:
```python
# Request Schema
class QueryLedgerRequest:
    start_date: date = Field(description="起始日期")
    end_date: date = Field(description="结束日期")
    order_type: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=1000)

# Response Schema
class PointLedgerResponse:
    id: str
    transaction_uuid: str
    user_id: str
    amount: int
    point_type: str  # GOLD_BEAN, BONUS_BEAN
    dist_ratio: Optional[float]
    order_type: str
    balance_after: int
    related_id: Optional[str]
    description: Optional[str]
    created_at: datetime

class PointBalanceResponse:
    user_id: str
    gold_beans: int
    bonus_beans: int
    total_beans: int
    last_updated: datetime

class LedgerStatisticsResponse:
    total_income: int
    total_expense: int
    net_change: int
    period: str
```

**验收标准**:
- ✅ 所有字段都对应 `point_ledger` 表
- ✅ 余额快照字段正确
- ✅ 统计接口包含完整信息

---

##### 2.6 通知 Schema (`notification.py`)

**必须包含的 Schema**:
```python
# Request Schema
class MarkAsReadRequest:
    notification_id: str

class BatchMarkAsReadRequest:
    notification_ids: List[str]

# Response Schema
class NotificationResponse:
    id: str
    receiver_id: str
    sender_id: Optional[str]
    type: str
    priority: str
    title: Optional[str]
    content: str
    link_url: Optional[str]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

class NotificationListResponse:
    total: int
    unread_count: int
    items: List[NotificationResponse]
```

**验收标准**:
- ✅ 通知类型字段使用枚举
- ✅ 优先级字段使用枚举
- ✅ 包含未读计数

---

#### 2.7 通用 Schema (`common.py`)

**必须包含的 Schema**:
```python
# 分页 Schema
class PaginatedResponse(Generic[T]):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[T]

# 错误 Schema
class ErrorResponse:
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]]

# 成功响应
class SuccessResponse(Generic[T]):
    code: int
    message: str
    data: T
```

---

#### 2.8 Schema 验证审查

| 验证项 | 检查内容 | 状态 |
|--------|---------|------|
| **字段类型** | 所有字段都有正确的 Python 类型 | ? |
| **验证器** | 所有字符串/数字字段都有范围限制 | ? |
| **可空字段** | 所有可空字段使用 `Optional[T]` | ? |
| **描述信息** | 所有字段都有 `description` | ? |
| **默认值** | 默认值都有合理的设置 | ? |
| **枚举类型** | 状态字段都使用 Enum 类型 | ? |
| **响应模型** | 所有 Response 都包含 `model_config` | ? |

---

### 阶段 3：Service 服务层审查

#### 审查清单

##### 3.1 Service 文件完整性
**审查项目**: 8 个 Service 文件是否完整实现

```python
services/
├── ai_service.py              # AI 对话管理
├── resource_service.py         # 资源 CRUD + 分账
├── community_service.py        # 话题/回复管理
├── ledger_service.py           # 复式记账
├── notification_service.py     # 通知管理
├── file_service.py             # 文件存储
└── auth_service.py             # 认证服务（可能已实现）
```

**验收标准**:
- ✅ 所有 Service 文件存在
- ✅ 每个 Service 包含对应的核心业务逻辑
- ✅ 所有数据库操作都在 Service 中实现
- ✅ 所有事务处理都正确实现

---

##### 3.2 AI 服务 (`ai_service.py`)

**必须实现的功能**:

```python
class AIService:
    # 会话管理
    async def create_session(user_id: str, model_type: str = "general") -> AISession
    async def get_session(session_id: str, user_id: Optional[str]) -> AISession
    async def list_sessions(user_id: str, page: int, page_size: int) -> List[AISession]
    async def delete_session(session_id: str, user_id: str) -> bool
    
    # 消息管理
    async def send_message(session_id: str, user_id: str, content: str, 
                          attachments: List[str]) -> AIMessage
    async def get_messages(session_id: str, limit: int = 50) -> List[AIMessage]
    
    # 关键：配额校验
    async def validate_ai_quota(user_id: str) -> Tuple[bool, str]
    # 检查项：
    # 1. 每日新会话数 ≤ 配额上限
    # 2. 每日总轮数 ≤ 配额上限
    # 3. 单会话轮数 ≤ 50
    # 4. Token 余额充足
    # 5. 敏感词过滤
    
    # 关键：流式输出
    async def stream_response(session_id: str, user_id: str, 
                            content: str) -> AsyncGenerator[str, None]
    # 实现 SSE 流式传输
    # 返回 Server-Sent Events 格式
    
    # Token 计数
    async def count_tokens(text: str) -> int
    
    # 反馈记录
    async def save_feedback(message_id: str, feedback_type: str) -> bool
```

**关键业务逻辑验证**:
```python
# 配额校验逻辑验证
def validate_ai_quota():
    # 1. 从 Redis 获取每日会话计数
    daily_sessions = redis.get(f"ai:daily_sessions:{user_id}:{today}")
    if daily_sessions >= USER_DAILY_SESSION_LIMIT:
        return False, "超过每日新会话上限"
    
    # 2. 从 Redis 获取每日轮数计数
    daily_turns = redis.get(f"ai:daily_turns:{user_id}:{today}")
    if daily_turns >= USER_DAILY_TURN_LIMIT:
        return False, "超过每日问答轮数"
    
    # 3. 检查单会话轮数
    session_turns = len(db.query(AIMessage).filter(...))
    if session_turns >= MAX_TURNS_PER_SESSION:
        return False, "超过单会话轮数上限"
    
    # 4. 检查 Token 余额
    user = db.query(User).get(user_id)
    if user.gold_beans < TOKEN_COST_PER_MESSAGE:
        return False, "可可豆余额不足"
    
    # 5. 敏感词检查
    if contains_sensitive_words(content):
        return False, "包含敏感词"
    
    return True, "配额充足"

# 流式输出逻辑验证
async def stream_response():
    # 1. 验证配额
    if not validate_ai_quota():
        yield json.dumps({"error": "配额不足"})
        return
    
    # 2. 调用 AI API（流式）
    async with ai_client.stream_chat(...) as stream:
        message_id = generate_uuid()
        buffer = []
        token_count = 0
        
        async for chunk in stream:
            # 3. 实时发送 SSE 数据
            yield f"data: {json.dumps({'chunk': chunk, 'token_count': token_count})}\n\n"
            buffer.append(chunk)
            token_count += count_tokens(chunk)
        
        # 4. 保存完整消息到数据库
        full_content = "".join(buffer)
        save_message(session_id, "assistant", full_content, token_count)
        
        # 5. 扣除可可豆
        deduct_beans(user_id, token_count * COST_PER_TOKEN)
        
        # 6. 更新会话计数
        session.total_tokens += token_count
        session.total_turns += 1
```

**测试用例**:
- [ ] 创建新会话成功
- [ ] 获取已有会话成功
- [ ] 发送消息成功
- [ ] 超过每日新会话上限返回错误
- [ ] 超过每日轮数上限返回错误
- [ ] 可可豆余额不足返回错误
- [ ] 包含敏感词返回错误
- [ ] 流式输出正确返回 SSE 格式
- [ ] 流式输出完成后消息正确保存
- [ ] 流式输出完成后可可豆正确扣除
- [ ] 删除会话成功

---

##### 3.3 资源服务 (`resource_service.py`)

**必须实现的功能**:

```python
class ResourceService:
    # CRUD 操作
    async def create_resource(uploader_id: str, data: CreateResourceRequest, 
                            file_uuid: str) -> Resource
    async def get_resource(resource_id: str) -> Resource
    async def list_resources(filters: Dict, page: int, page_size: int) -> List[Resource]
    async def update_resource(resource_id: str, uploader_id: str, 
                            data: UpdateResourceRequest) -> Resource
    async def delete_resource(resource_id: str, uploader_id: str) -> bool
    
    # 关键：下载鉴权与分账
    async def create_download_token(resource_id: str, downloader_id: str) -> str
    # 逻辑：
    # 1. 检查资源是否存在且已审核通过
    # 2. 检查下载者是否有资金（优先福利豆）
    # 3. 原子事务：
    #    a. 扣除下载者 P 豆
    #    b. 贡献者 + floor(P * 0.7)
    #    c. 系统销毁 + floor(P * 0.3)
    #    d. 记录三条 point_ledger 流水
    # 4. 生成下载 Token（5 分钟有效）
    # 5. 增加下载计数
    
    async def verify_download_token(token: str) -> Tuple[bool, str]
    
    # 预览功能
    async def get_preview(resource_id: str) -> List[ResourcePreviewResponse]
    
    # 热度计算
    async def update_heat_score(resource_id: str) -> float
    # heat_score = view_count * 0.3 + download_count * 0.5 + like_count * 0.2
    
    # 操作计数
    async def increment_view_count(resource_id: str) -> int
    async def increment_like_count(resource_id: str) -> int
    async def increment_dislike_count(resource_id: str) -> int
```

**关键业务逻辑验证**:

```python
# 70/30 分账逻辑验证
async def create_download_token():
    # 1. 查询资源
    resource = db.query(Resource).get(resource_id)
    if not resource:
        raise ResourceNotFound()
    if resource.status != ResourceStatus.APPROVED:
        raise ResourceNotApproved()
    
    # 2. 检查下载者余额
    downloader = db.query(User).get(downloader_id)
    available_beans = downloader.bonus_beans + downloader.gold_beans
    if available_beans < resource.price:
        raise InsufficientBeans()
    
    # 3. 原子事务处理
    with db.begin_nested():
        # 3a. 扣除下载者的豆
        # 优先消耗福利豆，再消耗资产豆
        bonus_deduct = min(downloader.bonus_beans, resource.price)
        gold_deduct = resource.price - bonus_deduct
        
        downloader.bonus_beans -= bonus_deduct
        downloader.gold_beans -= gold_deduct
        
        # 3b. 贡献者获得 70%
        contributor_amount = math.floor(resource.price * 0.7)
        contributor = db.query(User).get(resource.uploader_id)
        contributor.gold_beans += contributor_amount
        
        # 3c. 系统销毁 30%
        destroy_amount = math.floor(resource.price * 0.3)
        # 记录销毁交易（不转给任何用户）
        
        # 3d. 记录三条流水
        ledger_1 = PointLedger(
            user_id=downloader_id,
            amount=-resource.price,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.DOWNLOAD,
            balance_after=downloader.gold_beans,
            related_id=resource_id
        )
        ledger_2 = PointLedger(
            user_id=resource.uploader_id,
            amount=contributor_amount,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.DOWNLOAD_REVENUE,
            balance_after=contributor.gold_beans,
            related_id=resource_id
        )
        ledger_3 = PointLedger(
            user_id=None,  # 系统账户
            amount=-destroy_amount,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.DESTRUCTION,
            balance_after=0,
            related_id=resource_id
        )
        
        db.add_all([ledger_1, ledger_2, ledger_3])
        db.flush()
    
    # 4. 生成下载 Token
    token = generate_download_token(resource_id, downloader_id, expires_in=5*60)
    
    # 5. 更新下载计数
    resource.download_count += 1
    
    # 6. 更新热度分数
    resource.heat_score = calculate_heat_score(resource)
    
    db.commit()
    return token
```

**测试用例**:
- [ ] 上传资源成功
- [ ] 获取资源详情成功
- [ ] 资源列表分页正确
- [ ] 下载者余额不足返回错误
- [ ] 资源未审核返回错误
- [ ] 70/30 分账计算正确
- [ ] 三条流水记录正确
- [ ] 下载 Token 5 分钟后过期
- [ ] 热度分数计算正确
- [ ] 查看计数递增正确
- [ ] 点赞计数递增正确

---

##### 3.4 社区服务 (`community_service.py`)

**必须实现的功能**:

```python
class CommunityService:
    # 话题管理
    async def create_topic(author_id: str, data: CreateTopicRequest) -> Topic
    async def get_topic(topic_id: str) -> Topic
    async def list_topics(filters: Dict, page: int, page_size: int) -> List[Topic]
    async def delete_topic(topic_id: str, author_id: str) -> bool
    
    # 关键：悬赏管理
    async def set_bounty(topic_id: str, author_id: str, amount: int) -> bool
    # 逻辑：
    # 1. 检查作者余额
    # 2. 原子事务锁定悬赏金额：
    #    a. 扣除作者 amount 豆
    #    b. 记录 BOUNTY_AMOUNT_LOCKED 流水
    #    c. 更新 topic.bounty_status = ACTIVE
    
    async def accept_post(topic_id: str, author_id: str, post_id: str) -> Dict
    # 逻辑：
    # 1. 验证 post 确实属于该 topic
    # 2. 验证 topic 有悬赏
    # 3. 原子事务分账：
    #    a. 回答者 + floor(bounty_amount * 0.7)
    #    b. 系统销毁 + floor(bounty_amount * 0.3)
    #    c. 记录两条流水
    #    d. 更新 topic.accepted_post_id
    #    e. 更新 topic.bounty_status = RESOLVED
    
    async def refund_bounty(topic_id: str, author_id: str) -> bool
    # 逻辑：
    # 1. 只能在未采纳时退款
    # 2. 原子事务：
    #    a. 作者 + bounty_amount
    #    b. 记录 BOUNTY_AMOUNT_RELEASED 流水
    #    c. 更新 topic.bounty_status = REFUNDED
    
    # 回复管理
    async def create_post(topic_id: str, author_id: str, 
                         data: CreatePostRequest) -> Post
    async def get_post(post_id: str) -> Post
    async def list_posts(topic_id: str, page: int, page_size: int) -> List[Post]
    async def delete_post(post_id: str, author_id: str) -> bool
    
    # 互动功能
    async def like_post(post_id: str, user_id: str) -> bool
    async def unlike_post(post_id: str, user_id: str) -> bool
```

**关键业务逻辑验证**:

```python
# 悬赏采纳 70/30 分账
async def accept_post():
    # 1. 获取 topic 和 post
    topic = db.query(Topic).get(topic_id)
    post = db.query(Post).get(post_id)
    
    if post.topic_id != topic_id:
        raise PostNotInTopic()
    
    if topic.bounty_status != BountyStatus.ACTIVE:
        raise BountyNotActive()
    
    # 2. 原子事务
    with db.begin_nested():
        bounty_amount = topic.bounty_amount
        
        # 2a. 回答者获得 70%
        answerer_amount = math.floor(bounty_amount * 0.7)
        answerer = db.query(User).get(post.author_id)
        answerer.gold_beans += answerer_amount
        
        # 2b. 系统销毁 30%
        destroy_amount = math.floor(bounty_amount * 0.3)
        
        # 2c. 记录流水
        ledger_1 = PointLedger(
            user_id=post.author_id,
            amount=answerer_amount,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.BOUNTY_DISTRIBUTION,
            balance_after=answerer.gold_beans,
            related_id=topic_id
        )
        ledger_2 = PointLedger(
            user_id=None,
            amount=-destroy_amount,
            point_type=PointType.GOLD_BEAN,
            order_type=OrderType.DESTRUCTION,
            balance_after=0,
            related_id=topic_id
        )
        
        # 2d. 更新状态
        post.is_accepted = True
        topic.accepted_post_id = post_id
        topic.bounty_status = BountyStatus.RESOLVED
        
        db.add_all([ledger_1, ledger_2])
        db.flush()
    
    db.commit()
    return {
        "answerer_id": post.author_id,
        "amount": answerer_amount,
        "transaction_id": ledger_1.transaction_uuid
    }
```

**测试用例**:
- [ ] 创建话题成功
- [ ] 获取话题详情成功
- [ ] 话题列表分页正确
- [ ] 设置悬赏成功
- [ ] 悬赏余额不足返回错误
- [ ] 采纳回复成功
- [ ] 70/30 分账计算正确
- [ ] 两条流水记录正确
- [ ] 采纳后 topic.bounty_status = RESOLVED
- [ ] 退款逻辑正确
- [ ] 回复操作成功
- [ ] 点赞操作成功

---

##### 3.5 可可豆服务 (`ledger_service.py`)

**必须实现的功能**:

```python
class LedgerService:
    # 记账操作
    async def record_transaction(user_id: str, amount: int, point_type: PointType,
                                order_type: OrderType, related_id: Optional[str],
                                description: Optional[str]) -> PointLedger
    
    # 余额查询
    async def get_balance(user_id: str) -> Dict[str, int]
    # 返回: {"gold_beans": int, "bonus_beans": int, "total": int}
    
    # 流水查询
    async def query_ledger(user_id: str, start_date: date, end_date: date,
                          order_type: Optional[str] = None,
                          limit: int = 50) -> List[PointLedger]
    
    # 统计报告
    async def get_statistics(user_id: str, period: str = "today") -> Dict
    # period: "today", "week", "month"
    # 返回: {
    #   "total_income": int,
    #   "total_expense": int,
    #   "net_change": int,
    #   "breakdown_by_type": Dict[str, int]
    # }
    
    # 对账验证
    async def verify_ledger(user_id: str) -> Tuple[bool, str]
    # 逻辑：
    # 1. 求和 point_ledger 表中该用户的所有 balance_after
    # 2. 与 users 表中的 gold_beans + bonus_beans 对比
    # 3. 如不一致，返回错误信息
```

**关键业务逻辑验证**:

```python
# 复式记账规则验证
# 每一笔操作必须对应一条或多条流水
# 并且必须满足平衡方程：sum(amount) = 0

# 示例 1：下载资源（3 条流水）
# 下载者扣费: -P, gold_beans
# 贡献者收入: +floor(P*0.7), gold_beans
# 系统销毁: -floor(P*0.3), (销毁账户)
# 验证: -P + floor(P*0.7) + (-floor(P*0.3)) = -P + floor(P*0.7) - floor(P*0.3)

# 示例 2：采纳悬赏（2 条流水）
# 回答者收入: +floor(B*0.7), gold_beans
# 系统销毁: -floor(B*0.3), (销毁账户)
# 验证: floor(B*0.7) - floor(B*0.3) = B（若两个余数相加 = 1）
```

**对账脚本**:
```python
async def daily_reconciliation():
    """每日对账脚本"""
    # 1. 遍历所有用户
    users = db.query(User).all()
    
    for user in users:
        # 2. 获取 point_ledger 中的最后一条记录
        last_ledger = db.query(PointLedger) \
            .filter(PointLedger.user_id == user.id) \
            .order_by(PointLedger.created_at.desc()) \
            .first()
        
        # 3. 比对 balance_after 与实际余额
        expected_balance = last_ledger.balance_after if last_ledger else 0
        actual_balance = user.gold_beans + user.bonus_beans
        
        if expected_balance != actual_balance:
            # 记录不一致
            logger.error(f"User {user.id} ledger mismatch: "
                        f"expected {expected_balance}, got {actual_balance}")
            # 发送告警
            send_alert(f"Ledger inconsistency for user {user.id}")
```

**测试用例**:
- [ ] 记录单条交易成功
- [ ] 记录多条交易成功
- [ ] 余额查询正确
- [ ] 流水查询按时间排序正确
- [ ] 统计报告数据正确
- [ ] 对账验证通过
- [ ] 复式记账平衡验证通过

---

##### 3.6 通知服务 (`notification_service.py`)

**必须实现的功能**:

```python
class NotificationService:
    # 发送通知
    async def send_notification(receiver_id: str, notification_type: NotificationType,
                              title: str, content: str, link_url: Optional[str] = None,
                              priority: NotificationPriority = NotificationPriority.NORMAL,
                              sender_id: Optional[str] = None) -> Notification
    
    # 批量发送通知
    async def send_batch_notification(receiver_ids: List[str], 
                                    notification_type: NotificationType,
                                    title: str, content: str,
                                    is_broadcast_exemption: bool = False) -> int
    
    # 查询通知
    async def list_notifications(user_id: str, page: int, page_size: int,
                               unread_only: bool = False) -> List[Notification]
    
    # 标记已读
    async def mark_as_read(notification_id: str) -> bool
    async def batch_mark_as_read(notification_ids: List[str]) -> int
    
    # 删除通知
    async def delete_notification(notification_id: str) -> bool
    
    # 统计
    async def get_unread_count(user_id: str) -> int
```

**测试用例**:
- [ ] 发送通知成功
- [ ] 批量发送通知成功
- [ ] 查询通知列表成功
- [ ] 标记已读成功
- [ ] 未读计数正确
- [ ] 通知类型正确

---

##### 3.7 文件服务 (`file_service.py`)

**必须实现的功能**:

```python
class FileService:
    # 文件上传
    async def upload_file(file: UploadFile, uploader_id: str) -> FileMeta
    # 逻辑：
    # 1. 计算文件 hash (SHA256)
    # 2. 检查是否已上传过（hash 去重）
    # 3. 上传到 COS
    # 4. 创建 file_meta 记录
    # 5. 返回 file_uuid
    
    async def get_file_meta(file_uuid: str) -> FileMeta
    
    # 文件删除
    async def delete_file(file_uuid: str, requester_id: str) -> bool
    
    # 文件类型检查
    async def validate_file_type(file: UploadFile) -> Tuple[bool, str]
    # 允许的文件类型：pdf, doc, docx, xls, xlsx, ppt, pptx, jpg, png, zip
    
    # 病毒扫描（调用 ClamAV）
    async def scan_file(file_path: str) -> Tuple[bool, Optional[str]]
    # 返回: (是否安全, 威胁描述)
    
    # 文件下载
    async def generate_download_url(file_uuid: str, expires_in: int = 3600) -> str
```

**测试用例**:
- [ ] 上传文件成功
- [ ] 文件 hash 去重正确
- [ ] 文件类型验证正确
- [ ] 不允许的文件类型被拒绝
- [ ] 文件大小限制（20MB）
- [ ] 病毒扫描功能正常
- [ ] 下载 URL 生成正确
- [ ] 下载 URL 过期时间正确

---

#### 3.8 Service 层通用检查

| 检查项 | 标准 | 状态 |
|--------|------|------|
| **事务处理** | 所有多步操作都使用事务 | ? |
| **错误处理** | 所有操作都有异常捕获 | ? |
| **日志记录** | 关键操作都有日志 | ? |
| **参数验证** | 输入参数都有校验 | ? |
| **权限检查** | 操作都检查用户权限 | ? |
| **性能优化** | 查询都有索引优化 | ? |
| **线程安全** | 并发操作都有锁机制 | ? |

---

### 阶段 4：API 路由层审查

#### 审查清单

##### 4.1 API 文件完整性
**审查项目**: 所有 API 路由文件是否完整实现

```python
api/v1/
├── ai/
│   └── router.py           # AI 对话路由
├── resources/
│   └── router.py           # 资源模块路由
├── community/
│   └── router.py           # 社区模块路由
├── ledger/
│   └── router.py           # 可可豆路由
├── notification/
│   └── router.py           # 通知路由
└── __init__.py             # 路由注册
```

**验收标准**:
- ✅ 所有路由文件存在
- ✅ 所有路由都注册到主应用
- ✅ 所有路由都有认证保护
- ✅ 所有路由都有错误处理

---

##### 4.2 AI 对话 API (`api/v1/ai/router.py`)

**必须实现的端点**:

```python
# 1. 创建新会话
@router.post("/sessions", response_model=AISessionResponse)
async def create_session(
    body: CreateSessionRequest,
    current_user: User = Depends(get_current_user)
) -> AISessionResponse

# 验收标准:
# - ✅ 返回 201 Created
# - ✅ 返回创建的 session 完整信息
# - ✅ 要求认证

# 2. 获取会话列表
@router.get("/sessions", response_model=PaginatedResponse[AISessionResponse])
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
) -> PaginatedResponse[AISessionResponse]

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 分页信息正确
# - ✅ 只返回当前用户的会话
# - ✅ 按 created_at DESC 排序

# 3. 获取会话详情
@router.get("/sessions/{session_id}", response_model=AISessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> AISessionResponse

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 会话存在且属于当前用户
# - ✅ 返回 404 Not Found 若不存在

# 4. 发送消息（流式 SSE）
@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    body: MessageRequest,
    current_user: User = Depends(get_current_user)
) -> StreamingResponse

# 验收标准:
# - ✅ 返回 Server-Sent Events 流
# - ✅ Content-Type: text/event-stream
# - ✅ 流式传输 AI 响应
# - ✅ 完成后保存消息到数据库
# - ✅ 完成后更新用户可可豆余额
# - ✅ 配额不足返回 400 Bad Request

# 5. 获取消息历史
@router.get("/sessions/{session_id}/messages", 
           response_model=PaginatedResponse[AIMessageResponse])
async def get_messages(
    session_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
) -> PaginatedResponse[AIMessageResponse]

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 分页信息正确
# - ✅ 消息按 created_at ASC 排序
# - ✅ 只返回属于该会话的消息

# 6. 上传附件
@router.post("/attachments", response_model=Dict)
async def upload_attachment(
    file: UploadFile,
    current_user: User = Depends(get_current_user)
) -> Dict

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 返回 file_uuid
# - ✅ 文件类型验证
# - ✅ 文件大小限制（20MB）
# - ✅ 病毒扫描通过

# 7. 删除会话
@router.delete("/sessions/{session_id}", response_model=Dict)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 逻辑删除（is_deleted = True）
# - ✅ 只允许会话拥有者删除
```

**关键实现验证**:

```python
# SSE 流式输出实现
@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, body: MessageRequest, 
                      current_user: User = Depends(get_current_user)):
    async def generate():
        try:
            # 1. 验证配额
            is_valid, reason = await ai_service.validate_ai_quota(current_user.id)
            if not is_valid:
                yield f"data: {json.dumps({'error': reason, 'code': 'QUOTA_LIMIT'})}\n\n"
                return
            
            # 2. 实时流式输出
            token_count = 0
            async for chunk in await ai_service.stream_response(
                session_id, current_user.id, body.content
            ):
                token_count += count_tokens(chunk)
                yield f"data: {json.dumps({'chunk': chunk, 'token_count': token_count})}\n\n"
                await asyncio.sleep(0.01)  # 模拟流式延迟
            
            yield f"data: {json.dumps({'finished': True, 'total_tokens': token_count})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**测试用例**:
- [ ] POST /sessions - 创建会话
- [ ] GET /sessions - 列表会话
- [ ] GET /sessions/{id} - 获取会话详情
- [ ] POST /sessions/{id}/messages - 发送消息（SSE）
- [ ] GET /sessions/{id}/messages - 获取历史消息
- [ ] POST /attachments - 上传附件
- [ ] DELETE /sessions/{id} - 删除会话
- [ ] 未认证访问返回 401
- [ ] 访问其他用户的会话返回 403

---

##### 4.3 资源模块 API (`api/v1/resources/router.py`)

**必须实现的端点**:

```python
# 1. 资源列表（支持搜索、过滤、排序）
@router.get("/", response_model=PaginatedResponse[ResourceResponse])
async def list_resources(
    category_id: Optional[int] = Query(None),
    sort_by: str = Query("created_at", enum=["created_at", "heat_score", "download_count"]),
    order: str = Query("desc", enum=["asc", "desc"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> PaginatedResponse[ResourceResponse]

# 验收标准:
# - ✅ 只返回 APPROVED 的资源
# - ✅ 支持按 category 过滤
# - ✅ 支持按热度/下载数排序
# - ✅ 分页信息正确
# - ✅ 查看时增加 view_count

# 2. 上传资源
@router.post("/", response_model=ResourceResponse, status_code=201)
async def create_resource(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: int = Form(...),
    price: int = Form(5, ge=5, le=10000),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> ResourceResponse

# 验收标准:
# - ✅ 返回 201 Created
# - ✅ 文件上传成功
# - ✅ 资源状态初始为 SCANNING
# - ✅ 触发 AI 预审 (异步 Celery 任务)

# 3. 获取资源详情
@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> ResourceResponse

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 增加 view_count
# - ✅ 返回 404 Not Found 若不存在

# 4. 下载资源（生成下载 Token）
@router.post("/{resource_id}/download", response_model=DownloadTokenResponse)
async def create_download_token(
    resource_id: str,
    current_user: User = Depends(get_current_user)
) -> DownloadTokenResponse

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 返回 download_token (5 分钟有效)
# - ✅ 返回文件下载 URL
# - ✅ 执行 70/30 分账
# - ✅ 可可豆不足返回 400

# 5. 资源预览
@router.get("/{resource_id}/preview", response_model=List[ResourcePreviewResponse])
async def get_preview(
    resource_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> List[ResourcePreviewResponse]

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 返回所有预览 URL（带水印）

# 6. 点赞资源
@router.post("/{resource_id}/like", response_model=Dict)
async def like_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ like_count 递增
# - ✅ 返回新的 like_count

# 7. 取消点赞
@router.delete("/{resource_id}/like", response_model=Dict)
async def unlike_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict

# 8. 更新资源（仅限上传者）
@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    body: UpdateResourceRequest,
    current_user: User = Depends(get_current_user)
) -> ResourceResponse

# 验收标准:
# - ✅ 只允许上传者修改
# - ✅ 状态为 APPROVED 才能修改
# - ✅ 返回 403 若无权限

# 9. 删除资源（仅限上传者）
@router.delete("/{resource_id}", response_model=Dict)
async def delete_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict

# 验收标准:
# - ✅ 逻辑删除（is_deleted = True）
# - ✅ 只允许上传者删除
```

**测试用例**:
- [ ] GET / - 获取资源列表
- [ ] GET /?category_id=1 - 按分类过滤
- [ ] GET /?sort_by=heat_score&order=desc - 按热度排序
- [ ] POST / - 上传资源
- [ ] GET /{id} - 获取资源详情
- [ ] POST /{id}/download - 生成下载 Token
- [ ] GET /{id}/preview - 获取预览
- [ ] POST /{id}/like - 点赞
- [ ] DELETE /{id}/like - 取消点赞
- [ ] PUT /{id} - 更新资源
- [ ] DELETE /{id} - 删除资源
- [ ] 可可豆不足返回 400
- [ ] 访问其他用户的资源返回 403

---

##### 4.4 社区模块 API (`api/v1/community/router.py`)

**必须实现的端点**:

```python
# 1. 话题列表
@router.get("/topics", response_model=PaginatedResponse[TopicResponse])
async def list_topics(
    category_id: Optional[int] = Query(None),
    sort_by: str = Query("created_at", enum=["created_at", "heat_score"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> PaginatedResponse[TopicResponse]

# 2. 创建话题
@router.post("/topics", response_model=TopicResponse, status_code=201)
async def create_topic(
    body: CreateTopicRequest,
    current_user: User = Depends(get_current_user)
) -> TopicResponse

# 验收标准:
# - ✅ 返回 201 Created
# - ✅ 若指定悬赏金额，则锁定该金额
# - ✅ 检查用户余额

# 3. 获取话题详情
@router.get("/topics/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> TopicResponse

# 4. 发布回复
@router.post("/topics/{topic_id}/posts", response_model=PostResponse, status_code=201)
async def create_post(
    topic_id: str,
    body: CreatePostRequest,
    current_user: User = Depends(get_current_user)
) -> PostResponse

# 验收标准:
# - ✅ 返回 201 Created
# - ✅ post_count 递增
# - ✅ parent_id 支持楼层回复

# 5. 获取回复列表
@router.get("/topics/{topic_id}/posts", response_model=PaginatedResponse[PostResponse])
async def list_posts(
    topic_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> PaginatedResponse[PostResponse]

# 6. 采纳回复（仅限话题作者，触发分账）
@router.post("/topics/{topic_id}/accept", response_model=BountyDistributionResponse)
async def accept_post(
    topic_id: str,
    body: AcceptPostRequest,
    current_user: User = Depends(get_current_user)
) -> BountyDistributionResponse

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 只允许话题作者操作
# - ✅ 只有有悬赏的话题才能采纳
# - ✅ 执行 70/30 分账
# - ✅ 返回分账信息 (answerer_id, amount, transaction_id)

# 7. 删除话题（仅限作者）
@router.delete("/topics/{topic_id}", response_model=Dict)
async def delete_topic(
    topic_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict

# 8. 点赞回复
@router.post("/posts/{post_id}/like", response_model=Dict)
async def like_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict

# 9. 取消点赞
@router.delete("/posts/{post_id}/like", response_model=Dict)
async def unlike_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict
```

**测试用例**:
- [ ] GET /topics - 获取话题列表
- [ ] POST /topics - 创建话题
- [ ] GET /topics/{id} - 获取话题详情
- [ ] POST /topics/{id}/posts - 发布回复
- [ ] GET /topics/{id}/posts - 获取回复列表
- [ ] POST /topics/{id}/accept - 采纳回复
- [ ] DELETE /topics/{id} - 删除话题
- [ ] POST /posts/{id}/like - 点赞回复
- [ ] DELETE /posts/{id}/like - 取消点赞
- [ ] 采纳时分账正确执行
- [ ] 只有作者能采纳返回 403
- [ ] 余额不足返回 400

---

##### 4.5 可可豆 API (`api/v1/ledger/router.py`)

**必须实现的端点**:

```python
# 1. 查询余额
@router.get("/balance", response_model=PointBalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user)
) -> PointBalanceResponse

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 返回 gold_beans, bonus_beans, total

# 2. 查询流水
@router.post("/query", response_model=PaginatedResponse[PointLedgerResponse])
async def query_ledger(
    body: QueryLedgerRequest,
    current_user: User = Depends(get_current_user)
) -> PaginatedResponse[PointLedgerResponse]

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 按 created_at DESC 排序
# - ✅ 支持按 order_type 过滤

# 3. 获取统计
@router.get("/statistics", response_model=LedgerStatisticsResponse)
async def get_statistics(
    period: str = Query("today", enum=["today", "week", "month"]),
    current_user: User = Depends(get_current_user)
) -> LedgerStatisticsResponse

# 验收标准:
# - ✅ 返回 200 OK
# - ✅ 计算收入、支出、净变化
# - ✅ 按类型分类统计
```

**测试用例**:
- [ ] GET /balance - 查询余额
- [ ] POST /query - 查询流水
- [ ] GET /statistics?period=today - 今日统计
- [ ] GET /statistics?period=week - 周统计
- [ ] GET /statistics?period=month - 月统计

---

##### 4.6 通知 API (`api/v1/notification/router.py`)

**必须实现的端点**:

```python
# 1. 获取通知列表
@router.get("/", response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    unread_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
) -> PaginatedResponse[NotificationResponse]

# 2. 标记已读
@router.post("/{notification_id}/read", response_model=Dict)
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict

# 3. 批量标记已读
@router.post("/batch/read", response_model=Dict)
async def batch_mark_as_read(
    body: BatchMarkAsReadRequest,
    current_user: User = Depends(get_current_user)
) -> Dict

# 4. 获取未读计数
@router.get("/unread-count", response_model=Dict)
async def get_unread_count(
    current_user: User = Depends(get_current_user)
) -> Dict
```

**测试用例**:
- [ ] GET / - 获取通知列表
- [ ] GET /?unread_only=true - 只获取未读
- [ ] POST /{id}/read - 标记已读
- [ ] POST /batch/read - 批量标记已读
- [ ] GET /unread-count - 获取未读计数

---

#### 4.7 API 层通用检查

| 检查项 | 标准 | 状态 |
|--------|------|------|
| **认证** | 所有受保护端点都需要 Token 认证 | ? |
| **授权** | 所有操作都检查用户权限 | ? |
| **错误处理** | 所有错误都返回标准错误格式 | ? |
| **速率限制** | 关键操作都有速率限制 | ? |
| **日志记录** | 所有操作都有日志 | ? |
| **CORS** | CORS 配置正确 | ? |
| **文档** | Swagger 文档完整 | ? |

---

### 阶段 5：集成测试与文档审查

#### 审查清单

##### 5.1 集成测试覆盖率

| 测试场景 | 覆盖端点 | 预期结果 | 状态 |
|---------|---------|---------|------|
| **AI 对话完整流程** | POST /sessions → POST /messages → GET /messages | 消息保存、可可豆扣除、返回流式数据 | ? |
| **资源上传下载** | POST /resources → POST /download → GET /preview | 文件上传成功、分账正确、下载 Token 有效 | ? |
| **社区悬赏** | POST /topics (含悬赏) → POST /posts → POST /accept | 悬赏锁定、采纳后分账、流水记录 | ? |
| **可可豆流水** | 执行多个操作 → GET /ledger/query | 所有交易都被正确记录 | ? |
| **权限验证** | 访问其他用户资源 | 返回 403 Forbidden | ? |
| **配额限制** | 超限操作 | 返回 400 Bad Request | ? |

---

##### 5.2 性能测试

| 测试项 | 目标值 | 测试方法 | 状态 |
|--------|--------|---------|------|
| **AI 首字响应** | ≤ 1 秒 | 发送消息，记录首个 chunk 返回时间 | ? |
| **SSE 流式延迟** | ≤ 200ms/chunk | 发送消息，记录每个 chunk 间隔 | ? |
| **资源列表响应** | ≤ 500ms | GET /resources，20 个结果 | ? |
| **并发下载** | ≥ 20 用户 | 模拟 20 并发下载请求 | ? |
| **数据库查询** | ≤ 100ms | 单表查询响应时间 | ? |

---

##### 5.3 文档完整性

| 文档类型 | 文件名 | 检查项 | 状态 |
|---------|--------|--------|------|
| **API 文档** | Swagger/OpenAPI | 所有端点都有文档 | ? |
| **ER 图** | architecture_er.png | 所有表关系正确 | ? |
| **部署文档** | DEPLOYMENT.md | Docker Compose 配置完整 | ? |
| **使用手册** | USER_GUIDE.md | 功能说明完整 | ? |
| **数据库脚本** | init_schema.sql | 所有表创建脚本 | ? |

---

## 三、审查执行计划

### 时间表
| 阶段 | 审查项 | 负责人 | 预计时间 | 开始日期 | 结束日期 |
|------|--------|--------|---------|---------|---------|
| **1** | 数据库 + ORM | 后端审查 | 2 天 | 2026-04-05 | 2026-04-06 |
| **2** | Schemas | 后端审查 | 1 天 | 2026-04-07 | 2026-04-07 |
| **3** | Service 服务 | 后端审查 + 架构师 | 3 天 | 2026-04-08 | 2026-04-10 |
| **4** | API 路由 | 后端审查 | 2 天 | 2026-04-11 | 2026-04-12 |
| **5** | 集成测试 | QA 工程师 | 3 天 | 2026-04-13 | 2026-04-15 |
| **6** | 文档审查 | 架构师 | 1 天 | 2026-04-16 | 2026-04-16 |
| **总计** | 全面审查 | | **12 天** | 2026-04-05 | 2026-04-16 |

### 审查会议

| 会议 | 时间 | 参与者 | 议题 |
|------|------|--------|------|
| **启动会** | 2026-04-05 09:00 | 全审查小组 | 讲解审查标准、分工、风险识别 |
| **中期同步** | 2026-04-10 15:00 | 全审查小组 | 进度检查、问题反馈、风险升级 |
| **最终评审** | 2026-04-17 10:00 | 全审查小组 + PM | 审查结论、通过/不通过决议、签名 |

---

## 四、审查通过/不通过标准

### 🟢 **通过** 的标准
满足以下所有条件：

1. **需求覆盖率** ≥ 95%
   - 所有 PRD 中标注为 MVP 的功能都已实现
   - 所有 P0 级别需求都已完成

2. **代码质量**
   - ✅ 所有代码都符合编码规范
   - ✅ 没有高风险的 Bug
   - ✅ 注释完整清晰

3. **测试覆盖率** ≥ 80%
   - ✅ 所有核心功能都有单元测试
   - ✅ 所有集成点都有集成测试
   - ✅ 所有关键路径都有端到端测试

4. **性能指标**
   - ✅ 所有响应时间都在目标值内
   - ✅ 数据库查询都有索引优化
   - ✅ 没有明显的 N+1 查询问题

5. **安全合规**
   - ✅ 所有输入都进行了验证
   - ✅ 所有输出都进行了转义
   - ✅ 所有敏感数据都加密存储

6. **文档完整**
   - ✅ API 文档完整
   - ✅ 架构文档完整
   - ✅ 部署文档完整

---

### 🔴 **不通过** 的标准
出现以下任一条件：

1. **需求缺失** > 5%
   - 有多个 PRD 需求未实现

2. **关键 Bug**
   - 分账计算错误
   - 数据一致性问题
   - 认证授权漏洞

3. **测试覆盖率** < 60%
   - 关键路径缺乏测试

4. **性能不达标**
   - 关键接口响应时间 > 2 秒
   - 数据库查询性能恶劣

5. **安全漏洞**
   - 有明显的安全隐患（SQL 注入、认证绕过等）

6. **文档缺失** > 20%
   - 重要文档缺失或不完整

---

## 五、发现问题处理流程

### 问题分类

**🔴 严重 (P0)**
- 需要立即修复，阻止发布
- 例：分账逻辑错误、认证漏洞、数据丢失

**🟡 中等 (P1)**
- 需要在发布前修复
- 例：性能问题、样式问题、功能缺陷

**🟢 轻微 (P2)**
- 可以在下一个版本修复
- 例：文档不完整、日志缺失、边界情况处理

### 问题跟踪

1. **记录** - 使用 GitHub Issues 记录问题
2. **评审** - 开发者评估修复工作量
3. **修复** - 开发者修复问题
4. **验证** - 审查员验证修复
5. **关闭** - 确认问题已解决

---

## 六、审查报告模板

### 审查报告结构

```markdown
# Sprint B 审查报告 - [阶段]

## 审查概览
- 审查对象：[具体内容]
- 审查周期：[开始日期] - [结束日期]
- 审查人员：[名单]
- 最终结论：[通过 / 需要改进 / 不通过]

## 审查结果汇总
| 审查维度 | 检查项数 | 通过数 | 通过率 | 结论 |
|---------|---------|--------|--------|------|
| ... | ... | ... | ... | ... |

## 主要发现
### 通过的项目
- ✅ [项目]

### 需要改进的项目
- ⚠️ [问题]: [详细描述]
- ⚠️ ...

### 不通过的项目
- ❌ [问题]: [详细描述]
- ❌ ...

## 建议与改进
1. [建议 1]
2. [建议 2]

## 审查结论
[最终结论文字]

## 签名
- 审查人 A：___________  日期：_________
- 审查人 B：___________  日期：_________
- 项目经理：__________  日期：_________
```

---

## 七、验收清单（最终）

### ✅ 所有交付物确认

#### 代码交付
- [ ] 14 个 ORM 模型文件 - 完整且正确
- [ ] 25+ 个 Pydantic Schema - 完整且验证规则完善
- [ ] 8 个 Service 服务文件 - 实现了所有业务逻辑
- [ ] 6 个 API Router 文件 - 所有端点都可用
- [ ] Alembic Migration 脚本 - 能正确执行
- [ ] 单元测试（覆盖率 ≥ 80%）
- [ ] 集成测试脚本
- [ ] E2E 测试脚本

#### 文档交付
- [ ] API 接口文档（Swagger/OpenAPI）
- [ ] 数据库 ER 图
- [ ] 部署文档（Docker Compose）
- [ ] 用户使用手册（MVP 版）
- [ ] 架构设计文档
- [ ] 运维文档

#### 配置交付
- [ ] Docker Compose 配置完整
- [ ] 环境变量配置文档
- [ ] 数据库初始化脚本

---

## 八、签字审核

| 角色 | 姓名 | 签字 | 日期 | 备注 |
|------|------|------|------|------|
| 代码审查 1 | | | | |
| 代码审查 2 | | | | |
| 架构师 | | | | |
| QA 工程师 | | | | |
| 项目经理 | | | | |

---

**文档历史**
| 版本 | 日期 | 作者 | 描述 |
|------|------|------|------|
| V1.0 | 2026-04-04 | AI Assistant | 初始版本 |


# Sprint B API 使用文档

> **版本**: v1.0  
> **更新日期**: 2026-04-04  
> **基础路径**: `/api/v1`

---

## 目录

1. [AI 对话模块](#ai-对话模块)
2. [资源管理模块](#资源管理模块)
3. [社区管理模块](#社区管理模块)
4. [可可豆经济模块](#可可豆经济模块)
5. [通知管理模块](#通知管理模块)
6. [文件管理模块](#文件管理模块)

---

## AI 对话模块

### 创建会话
```http
POST /api/v1/ai/sessions
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "我的 AI 对话",
  "model_type": "general"
}
```

**响应**:
```json
{
  "id": "uuid",
  "user_id": "user-uuid",
  "title": "我的 AI 对话",
  "model_type": "general",
  "total_tokens": 0,
  "total_turns": 0,
  "created_at": "2026-04-04T12:00:00Z",
  "updated_at": "2026-04-04T12:00:00Z"
}
```

### 获取会话列表
```http
GET /api/v1/ai/sessions?page=1&page_size=20
Authorization: Bearer {token}
```

### 发送消息
```http
POST /api/v1/ai/sessions/{session_id}/messages
Content-Type: application/json
Authorization: Bearer {token}

{
  "content": "你好，请帮我解释一下 Python 的装饰器",
  "attachment_ids": ["file-uuid-1", "file-uuid-2"]
}
```

### 获取消息历史
```http
GET /api/v1/ai/sessions/{session_id}/messages?page=1&page_size=50
Authorization: Bearer {token}
```

### 添加反馈
```http
POST /api/v1/ai/messages/{message_id}/feedback
Content-Type: application/json
Authorization: Bearer {token}

{
  "feedback_type": "like"
}
```

### 删除会话
```http
DELETE /api/v1/ai/sessions/{session_id}
Authorization: Bearer {token}
```

---

## 资源管理模块

### 创建资源
```http
POST /api/v1/resources
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "Python 高级编程技巧",
  "description": "分享一些 Python 高级编程技巧",
  "category_id": 1,
  "tags": ["python", "programming"],
  "price": 10,
  "file_uuid": "file-uuid"
}
```

**响应**:
```json
{
  "id": "resource-uuid",
  "uploader_id": "user-uuid",
  "title": "Python 高级编程技巧",
  "description": "分享一些 Python 高级编程技巧",
  "category_id": 1,
  "tags": "python,programming",
  "price": 10,
  "file_uuid": "file-uuid",
  "view_count": 0,
  "download_count": 0,
  "like_count": 0,
  "dislike_count": 0,
  "heat_score": 0.0,
  "is_seed": false,
  "status": "SCANNING",
  "created_at": "2026-04-04T12:00:00Z",
  "updated_at": "2026-04-04T12:00:00Z"
}
```

### 获取资源列表
```http
GET /api/v1/resources?category_id=1&search=python&sort_by=heat_score&page=1&page_size=20
```

**查询参数**:
- `category_id`: 分类 ID（可选）
- `search`: 搜索关键词（可选）
- `sort_by`: 排序字段（可选）
  - `heat_score`（默认）
  - `created_at`
  - `view_count`
  - `download_count`
  - `price`
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20，最大 100）

### 获取资源详情
```http
GET /api/v1/resources/{resource_id}
```

### 更新资源
```http
PUT /api/v1/resources/{resource_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "更新后的标题",
  "price": 15
}
```

### 删除资源
```http
DELETE /api/v1/resources/{resource_id}
Authorization: Bearer {token}
```

### 下载资源
```http
POST /api/v1/resources/{resource_id}/download
Authorization: Bearer {token}
```

**流程**:
1. 检查用户可可豆余额
2. 扣除相应 beans
3. 记录交易流水
4. 返回下载链接

### 增加浏览计数
```http
POST /api/v1/resources/{resource_id}/view
```

---

## 社区管理模块

### 创建话题
```http
POST /api/v1/community/topics
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "如何学习 Python？",
  "content": "我是一名编程新手，想学习 Python，请问应该从哪里开始？",
  "category_id": 1,
  "bounty_amount": 50
}
```

**响应**:
```json
{
  "id": "topic-uuid",
  "author_id": "user-uuid",
  "title": "如何学习 Python？",
  "content": "我是一名编程新手...",
  "category_id": 1,
  "bounty_amount": 50,
  "bounty_status": "ACTIVE",
  "view_count": 0,
  "post_count": 0,
  "heat_score": 0.0,
  "created_at": "2026-04-04T12:00:00Z"
}
```

### 获取话题列表
```http
GET /api/v1/community/topics?category_id=1&search=python&sort_by=heat_score&page=1&page_size=20
```

### 获取话题详情
```http
GET /api/v1/community/topics/{topic_id}
```

**说明**: 每次访问会自动增加浏览计数

### 更新话题
```http
PUT /api/v1/community/topics/{topic_id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "title": "更新后的标题",
  "content": "更新后的内容"
}
```

### 删除话题
```http
DELETE /api/v1/community/topics/{topic_id}
Authorization: Bearer {token}
```

### 创建回复
```http
POST /api/v1/community/topics/{topic_id}/posts
Content-Type: application/json
Authorization: Bearer {token}

{
  "content": "这是一个很好的问题！我建议从 Python 基础语法开始...",
  "parent_id": null
}
```

**说明**: 
- `parent_id` 用于回复特定评论（楼中楼）
- `parent_id` 为 null 表示直接回复主题

### 获取回复列表
```http
GET /api/v1/community/topics/{topic_id}/posts?page=1&page_size=20
```

### 采纳回答
```http
POST /api/v1/community/posts/{post_id}/accept
Authorization: Bearer {token}
```

**说明**: 仅话题作者可以采纳回答

**效果**:
- 标记该回复为已采纳
- 更新话题的 `bounty_status` 为 `RESOLVED`
- 将悬赏可可豆奖励给回答者

### 删除回复
```http
DELETE /api/v1/community/posts/{post_id}
Authorization: Bearer {token}
```

### 点赞回复
```http
POST /api/v1/community/posts/{post_id}/like
Authorization: Bearer {token}
```

---

## 可可豆经济模块

### 获取余额
```http
GET /api/v1/ledger/balance
Authorization: Bearer {token}
```

**响应**:
```json
{
  "user_id": "user-uuid",
  "gold_beans": 100,
  "bonus_beans": 50,
  "total_beans": 150,
  "last_updated": "2026-04-04T12:00:00Z"
}
```

### 获取交易历史
```http
GET /api/v1/ledger/history?page=1&page_size=20
Authorization: Bearer {token}
```

**响应**:
```json
{
  "ledgers": [
    {
      "id": "ledger-uuid",
      "transaction_uuid": "txn-uuid",
      "user_id": "user-uuid",
      "amount": 10,
      "point_type": "GOLD_BEAN",
      "order_type": "DOWNLOAD_REVENUE",
      "balance_after": 100,
      "related_id": "resource-uuid",
      "description": "资源下载收入",
      "created_at": "2026-04-04T12:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

### 充值可可豆
```http
POST /api/v1/ledger/recharge
Content-Type: application/json
Authorization: Bearer {token}

{
  "amount": 100,
  "payment_method": "wechat"
}
```

**说明**: 
- `amount`: 充值金额（CNY），范围 10-10000
- `payment_method`: 支付方式（`wechat` 或 `alipay`）

**响应**:
```json
{
  "message": "Payment order created",
  "amount": 100,
  "payment_method": "wechat",
  "order_id": "order-uuid"
}
```

### 获取资产套餐列表
```http
GET /api/v1/ledger/packages
```

**响应**:
```json
[
  {
    "id": "package-uuid",
    "name": "基础套餐",
    "price_beans": 100,
    "quota_mb": 1000,
    "discount_rate": 0.8,
    "created_at": "2026-04-04T12:00:00Z"
  }
]
```

### 购买资产套餐
```http
POST /api/v1/ledger/packages/purchase
Content-Type: application/json
Authorization: Bearer {token}

{
  "package_id": "package-uuid"
}
```

### 获取已购资产
```http
GET /api/v1/ledger/assets
Authorization: Bearer {token}
```

**响应**:
```json
[
  {
    "id": "asset-uuid",
    "user_id": "user-uuid",
    "package_id": "package-uuid",
    "remaining_mb": 800,
    "used_mb": 200,
    "expires_at": "2026-05-04T12:00:00Z",
    "is_active": true,
    "created_at": "2026-04-04T12:00:00Z"
  }
]
```

### 获取剩余额度
```http
GET /api/v1/ledger/assets/quota
Authorization: Bearer {token}
```

**响应**:
```json
{
  "user_id": "user-uuid",
  "total_remaining_mb": 800
}
```

---

## 通知管理模块

### 获取通知列表
```http
GET /api/v1/notifications?notification_type=SYSTEM&unread_only=false&page=1&page_size=20
Authorization: Bearer {token}
```

**查询参数**:
- `notification_type`: 通知类型（可选）
  - `SYSTEM` - 系统通知
  - `INTERACTION` - 互动通知
  - `AUDIT` - 审核通知
  - `REWARD` - 奖励通知
  - `BROADCAST` - 广播通知
- `unread_only`: 仅未读（可选，默认 false）
- `page`: 页码
- `page_size`: 每页数量

**响应**:
```json
{
  "notifications": [
    {
      "id": "notification-uuid",
      "type": "SYSTEM",
      "priority": "NORMAL",
      "title": "欢迎使用 ReliHub",
      "content": "欢迎加入 ReliHub 社区！",
      "is_read": false,
      "created_at": "2026-04-04T12:00:00Z"
    }
  ],
  "total": 10,
  "unread_count": 5,
  "page": 1,
  "page_size": 20
}
```

### 获取通知详情
```http
GET /api/v1/notifications/{notification_id}
Authorization: Bearer {token}
```

### 标记为已读
```http
POST /api/v1/notifications/mark-as-read
Content-Type: application/json
Authorization: Bearer {token}

{
  "notification_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

### 全部标记为已读
```http
POST /api/v1/notifications/mark-all-as-read
Authorization: Bearer {token}
```

### 获取统计信息
```http
GET /api/v1/notifications/stats
Authorization: Bearer {token}
```

**响应**:
```json
{
  "total_count": 50,
  "unread_count": 10,
  "read_count": 40,
  "by_type": {
    "SYSTEM": 20,
    "INTERACTION": 15,
    "AUDIT": 5,
    "REWARD": 8,
    "BROADCAST": 2
  }
}
```

### 删除通知
```http
DELETE /api/v1/notifications/{notification_id}
Authorization: Bearer {token}
```

---

## 文件管理模块

### 上传文件
```http
POST /api/v1/files/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: (binary)
```

**响应**:
```json
{
  "file_uuid": "file-uuid",
  "file_hash": "sha256-hash",
  "oss_path": "/uploads/file-uuid/filename.pdf",
  "file_name": "filename.pdf",
  "file_size": 1048576,
  "mime_type": "application/pdf"
}
```

**说明**:
- 自动进行文件去重（基于 SHA-256 哈希）
- 如果文件已存在，返回已有文件信息
- 文件状态初始为 `SCANNING`（待扫描）

### 获取文件信息
```http
GET /api/v1/files/{file_uuid}
Authorization: Bearer {token}
```

**权限**: 仅文件所有者或有访问权限的用户可访问

### 获取下载链接
```http
GET /api/v1/files/{file_uuid}/download
Authorization: Bearer {token}
```

**响应**:
```json
{
  "download_url": "/uploads/file-uuid/filename.pdf?download=true",
  "file_name": "filename.pdf"
}
```

### 获取我的文件
```http
GET /api/v1/files/user/my-files?page=1&page_size=20
Authorization: Bearer {token}
```

### 删除文件
```http
DELETE /api/v1/files/{file_uuid}
Authorization: Bearer {token}
```

**说明**: 软删除，将 `lifecycle_status` 设置为 `SOFT_DELETED`

### 记录文件使用
```http
POST /api/v1/files/{file_uuid}/usage?target_id=resource-uuid&target_type=RESOURCE
Authorization: Bearer {token}
```

**说明**:
- `target_type`: `CONVERSATION`, `RESOURCE`, `TOPIC`
- 创建文件使用记录
- 增加文件引用计数

### 获取文件使用记录
```http
GET /api/v1/files/{file_uuid}/usages
Authorization: Bearer {token}
```

**响应**:
```json
{
  "file_uuid": "file-uuid",
  "usages": [
    {
      "id": "usage-uuid",
      "target_id": "resource-uuid",
      "target_type": "RESOURCE",
      "user_id": "user-uuid",
      "created_at": "2026-04-04T12:00:00Z"
    }
  ]
}
```

---

## 错误响应

所有 API 错误统一返回格式：

```json
{
  "detail": "错误描述信息"
}
```

**常见错误码**:
- `400`: 请求参数错误
- `401`: 未授权（需要登录）
- `403`: 禁止访问（权限不足）
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 认证说明

所有需要登录的接口都要求在请求头中携带 JWT Token：

```
Authorization: Bearer {your_jwt_token}
```

Token 通过 `/api/v1/auth/login` 接口获取。

---

## 分页说明

所有列表接口都支持分页，统一使用以下参数：

- `page`: 页码，从 1 开始，默认 1
- `page_size`: 每页数量，默认 20，最大 100

响应中统一包含：
- `total`: 总记录数
- `page`: 当前页码
- `page_size`: 每页数量

---

## 枚举值说明

### ResourceStatus（资源状态）
- `SCANNING`: 待扫描
- `PENDING_REVIEW`: 待审核
- `APPROVED`: 已通过
- `REJECTED`: 已拒绝
- `APPEALING`: 申诉中
- `BLOCKED`: 已封禁

### BountyStatus（悬赏状态）
- `NONE`: 无悬赏
- `ACTIVE`: 悬赏中
- `RESOLVED`: 已解决
- `REFUNDED`: 已退款

### TopicStatus（话题状态）
- `NORMAL`: 正常
- `BLOCKED`: 已封禁
- `PENDING`: 待审核

### PointType（可可豆类型）
- `GOLD_BEAN`: 金豆（可提现）
- `BONUS_BEAN`: 奖励豆（不可提现）

### NotificationType（通知类型）
- `SYSTEM`: 系统通知
- `INTERACTION`: 互动通知
- `AUDIT`: 审核通知
- `REWARD`: 奖励通知
- `BROADCAST`: 广播通知

### NotificationPriority（通知优先级）
- `NORMAL`: 普通
- `HIGH`: 高优先级

### FileStatus（文件状态）
- `NORMAL`: 正常
- `SCANNING`: 扫描中
- `ISOLATED`: 已隔离
- `SUSPICIOUS`: 可疑
- `BLOCKED`: 已封禁
- `DELETED`: 已删除

### LifecycleStatus（生命周期状态）
- `ACTIVE`: 活跃
- `SOFT_DELETED`: 软删除
- `PERMANENTLY_DELETED`: 永久删除

### TargetType（目标类型）
- `CONVERSATION`: 对话
- `RESOURCE`: 资源
- `TOPIC`: 话题

---

**文档结束**

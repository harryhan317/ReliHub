# API 接口 - Sprint C 新增模块

**版本**: v1.0  
**更新日期**: 2026-04-08  
**Sprint 周期**: Sprint C (2026-04-09 ~ 2026-05-07)

---

## 1. 概述

本文档记录 Sprint C 迭代周期中新增的所有 API 端点，包括：
- AI 对话模块增强（LLM 多提供商支持）
- 支付模块（微信支付集成）
- LLM 提供商管理（管理后台）

---

## 2. AI 对话模块增强

### 2.1 获取 LLM 提供商列表

**接口名称**: 获取可用的 LLM 提供商列表  
**功能描述**: 返回系统中已启用的 LLM 提供商列表，用户可选择不同的提供商进行对话

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/ai/providers` |
| **认证要求** | 可选（支持游客访问） |
| **权限要求** | 无 |

#### 请求参数

无需请求参数

#### 请求示例

```http
GET /api/v1/ai/providers HTTP/1.1
Host: api.relihub.com
Authorization: Bearer {token}  # 可选
```

#### 响应示例

**成功响应 (200 OK)**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "deepseek",
    "display_name": "DeepSeek",
    "cost_per_1k_tokens": 0.001
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "openai",
    "display_name": "OpenAI",
    "cost_per_1k_tokens": 0.002
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "claude",
    "display_name": "Claude",
    "cost_per_1k_tokens": 0.003
  }
]
```

**无可用提供商 (200 OK)**:
```json
[]
```

#### 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | string | 提供商唯一标识 (UUID) |
| name | string | 提供商内部名称 (用于API调用) |
| display_name | string | 提供商显示名称 (用于前端展示) |
| cost_per_1k_tokens | float | 每 1000 tokens 的费用 (CNY) |

---

### 2.2 发送消息 (增强版)

**接口名称**: 发送消息到 AI 会话  
**功能描述**: 向指定会话发送消息，支持流式响应、多提供商选择、自定义模型参数

| 属性 | 值 |
|------|-----|
| **请求方法** | POST |
| **URL路径** | `/api/v1/ai/sessions/{session_id}/messages` |
| **认证要求** | 可选（支持游客访问） |
| **权限要求** | 无 |

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 会话 ID |

#### 请求体参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| content | string | 是 | - | 消息内容，长度 1-2000 字符 |
| attachment_ids | array[string] | 否 | null | 附件文件 UUID 列表 |
| stream | boolean | 否 | true | 是否使用流式响应 |
| provider_name | string | 否 | null | LLM 提供商名称 (deepseek/openai/claude) |
| model | string | 否 | null | 模型名称 |
| temperature | float | 否 | 0.7 | 温度参数，范围 0.0-2.0 |
| max_tokens | integer | 否 | 2000 | 最大输出 tokens，范围 1-32000 |

#### 请求示例

**普通请求 (非流式)**:
```http
POST /api/v1/ai/sessions/550e8400-e29b-41d4-a716-446655440000/messages HTTP/1.1
Host: api.relihub.com
Content-Type: application/json
Authorization: Bearer {token}

{
  "content": "请解释什么是可靠性工程？",
  "stream": false,
  "provider_name": "deepseek",
  "model": "deepseek-chat",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**流式请求**:
```http
POST /api/v1/ai/sessions/550e8400-e29b-41d4-a716-446655440000/messages HTTP/1.1
Host: api.relihub.com
Content-Type: application/json
Authorization: Bearer {token}

{
  "content": "请解释什么是可靠性工程？",
  "stream": true,
  "provider_name": "deepseek",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**带附件请求**:
```http
POST /api/v1/ai/sessions/550e8400-e29b-41d4-a716-446655440000/messages HTTP/1.1
Host: api.relihub.com
Content-Type: application/json
Authorization: Bearer {token}

{
  "content": "请分析这份报告",
  "attachment_ids": [
    "file-uuid-1",
    "file-uuid-2"
  ],
  "stream": true,
  "provider_name": "openai",
  "model": "gpt-4-vision-preview"
}
```

#### 响应示例

**非流式响应 (200 OK)**:
```json
{
  "id": "msg-550e8400-e29b-41d4-a716-446655440000",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "assistant",
  "content": "可靠性工程是一门工程学科，专注于确保系统和组件在规定条件下和规定时间内执行所需功能的能力...",
  "token_count": 256,
  "has_attachment": false,
  "attachment_ids": null,
  "feedback_type": null,
  "created_at": "2026-04-08T10:30:00Z"
}
```

**流式响应 (SSE)**:
```
data: {"content": "可靠性", "finish_reason": null}

data: {"content": "工程", "finish_reason": null}

data: {"content": "是一门", "finish_reason": null}

data: {"content": "工程学科...", "finish_reason": "stop"}

data: [DONE]
```

**错误响应 (429 Too Many Requests)**:
```json
{
  "detail": "Rate limit exceeded"
}
```

**错误响应 (404 Not Found)**:
```json
{
  "detail": "Session not found"
}
```

---

### 2.3 添加消息反馈

**接口名称**: 为 AI 消息添加反馈  
**功能描述**: 用户对 AI 回复进行点赞或点踩反馈

| 属性 | 值 |
|------|-----|
| **请求方法** | POST |
| **URL路径** | `/api/v1/ai/sessions/{session_id}/feedback` |
| **认证要求** | 可选 |
| **权限要求** | 无 |

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 会话 ID |

#### 查询参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| message_id | string | 是 | 消息 ID |

#### 请求体参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| feedback_type | string | 是 | 反馈类型，可选值: "like", "dislike" |

#### 请求示例

```http
POST /api/v1/ai/sessions/550e8400-e29b-41d4-a716-446655440000/feedback?message_id=msg-123 HTTP/1.1
Host: api.relihub.com
Content-Type: application/json
Authorization: Bearer {token}

{
  "feedback_type": "like"
}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "message": "Feedback recorded"
}
```

**错误响应 (404 Not Found)**:
```json
{
  "detail": "Message not found"
}
```

---

## 3. 支付模块

### 3.1 创建支付订单

**接口名称**: 创建支付订单  
**功能描述**: 创建一个新的支付订单，用于充值可可豆

| 属性 | 值 |
|------|-----|
| **请求方法** | POST |
| **URL路径** | `/api/v1/payment/orders` |
| **认证要求** | 必需 |
| **权限要求** | 登录用户 |

#### 请求体参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| amount | float | 是 | - | 支付金额 (CNY)，必须大于 0 |
| subject | string | 是 | - | 订单标题，长度 1-255 字符 |
| body | string | 否 | null | 订单描述，最大 1000 字符 |
| payment_method | string | 否 | "wechat" | 支付方式: wechat/alipay/bank_transfer |
| callback_url | string | 否 | null | 回调 URL，最大 500 字符 |

#### 请求示例

```http
POST /api/v1/payment/orders HTTP/1.1
Host: api.relihub.com
Content-Type: application/json
Authorization: Bearer {token}

{
  "amount": 100.00,
  "subject": "可可豆充值 - 100个",
  "body": "充值100个可可豆",
  "payment_method": "wechat"
}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "id": "order-550e8400-e29b-41d4-a716-446655440000",
  "order_no": "PAY20260408103000001",
  "user_id": "user-550e8400-e29b-41d4-a716-446655440000",
  "amount": 100.00,
  "currency": "CNY",
  "payment_method": "wechat",
  "payment_status": "pending",
  "subject": "可可豆充值 - 100个",
  "body": "充值100个可可豆",
  "transaction_id": null,
  "paid_at": null,
  "created_at": "2026-04-08T10:30:00Z",
  "updated_at": "2026-04-08T10:30:00Z"
}
```

**错误响应 (400 Bad Request)**:
```json
{
  "detail": "Amount must be positive"
}
```

---

### 3.2 获取支付订单列表

**接口名称**: 获取用户支付订单列表  
**功能描述**: 分页查询当前用户的支付订单

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/payment/orders` |
| **认证要求** | 必需 |
| **权限要求** | 登录用户 |

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| status | string | 否 | null | 订单状态过滤: pending/success/failed/refunded/cancelled |
| page | integer | 否 | 1 | 页码，最小值 1 |
| page_size | integer | 否 | 20 | 每页数量，范围 1-100 |

#### 请求示例

```http
GET /api/v1/payment/orders?status=success&page=1&page_size=20 HTTP/1.1
Host: api.relihub.com
Authorization: Bearer {token}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "orders": [
    {
      "id": "order-550e8400-e29b-41d4-a716-446655440000",
      "order_no": "PAY20260408103000001",
      "user_id": "user-550e8400-e29b-41d4-a716-446655440000",
      "amount": 100.00,
      "currency": "CNY",
      "payment_method": "wechat",
      "payment_status": "success",
      "subject": "可可豆充值 - 100个",
      "body": "充值100个可可豆",
      "transaction_id": "wx-trans-123456",
      "paid_at": "2026-04-08T10:35:00Z",
      "created_at": "2026-04-08T10:30:00Z",
      "updated_at": "2026-04-08T10:35:00Z"
    }
  ],
  "total": 1
}
```

---

### 3.3 获取支付订单详情

**接口名称**: 获取支付订单详情  
**功能描述**: 根据订单 ID 获取订单详细信息

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/payment/orders/{order_id}` |
| **认证要求** | 必需 |
| **权限要求** | 登录用户 (仅能查看自己的订单) |

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | string | 是 | 订单 ID |

#### 请求示例

```http
GET /api/v1/payment/orders/order-550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: api.relihub.com
Authorization: Bearer {token}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "id": "order-550e8400-e29b-41d4-a716-446655440000",
  "order_no": "PAY20260408103000001",
  "user_id": "user-550e8400-e29b-41d4-a716-446655440000",
  "amount": 100.00,
  "currency": "CNY",
  "payment_method": "wechat",
  "payment_status": "pending",
  "subject": "可可豆充值 - 100个",
  "body": "充值100个可可豆",
  "transaction_id": null,
  "paid_at": null,
  "created_at": "2026-04-08T10:30:00Z",
  "updated_at": "2026-04-08T10:30:00Z"
}
```

**错误响应 (404 Not Found)**:
```json
{
  "detail": "Order not found"
}
```

---

### 3.4 创建微信 JSAPI 支付

**接口名称**: 创建微信 JSAPI 支付  
**功能描述**: 创建微信 JSAPI 支付订单，返回支付参数供前端调起支付

| 属性 | 值 |
|------|-----|
| **请求方法** | POST |
| **URL路径** | `/api/v1/payment/wechat/jsapi` |
| **认证要求** | 必需 |
| **权限要求** | 登录用户 (需绑定微信) |

#### 请求体参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | string | 否 | 已有订单 ID，如提供则使用该订单 |
| amount | float | 否 | 支付金额 (CNY)，order_id 为空时必填 |
| subject | string | 否 | 订单标题，order_id 为空时必填 |
| body | string | 否 | 订单描述 |

#### 请求示例

```http
POST /api/v1/payment/wechat/jsapi HTTP/1.1
Host: api.relihub.com
Content-Type: application/json
Authorization: Bearer {token}

{
  "amount": 100.00,
  "subject": "可可豆充值 - 100个",
  "body": "充值100个可可豆"
}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "order_id": "order-550e8400-e29b-41d4-a716-446655440000",
  "order_no": "PAY20260408103000001",
  "prepay_id": "wx_prepay_id_123456",
  "appId": "wx1234567890abcdef",
  "timeStamp": "1712567400",
  "nonceStr": "abc123def456",
  "package": "prepay_id=wx_prepay_id_123456",
  "signType": "RSA",
  "paySign": "sign_string_here"
}
```

**错误响应 (400 Bad Request)**:
```json
{
  "detail": "WeChat JSAPI payment failed: invalid openid"
}
```

---

### 3.5 创建微信 Native 支付 (扫码支付)

**接口名称**: 创建微信 Native 支付  
**功能描述**: 创建微信扫码支付订单，返回二维码链接

| 属性 | 值 |
|------|-----|
| **请求方法** | POST |
| **URL路径** | `/api/v1/payment/wechat/native` |
| **认证要求** | 必需 |
| **权限要求** | 登录用户 |

#### 请求体参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | string | 否 | 已有订单 ID，如提供则使用该订单 |
| amount | float | 否 | 支付金额 (CNY)，order_id 为空时必填 |
| subject | string | 否 | 订单标题，order_id 为空时必填 |
| body | string | 否 | 订单描述 |

#### 请求示例

```http
POST /api/v1/payment/wechat/native HTTP/1.1
Host: api.relihub.com
Content-Type: application/json
Authorization: Bearer {token}

{
  "amount": 100.00,
  "subject": "可可豆充值 - 100个",
  "body": "充值100个可可豆"
}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "order_id": "order-550e8400-e29b-41d4-a716-446655440000",
  "order_no": "PAY20260408103000001",
  "prepay_id": "wx_prepay_id_123456",
  "code_url": "weixin://wxpay/bizpayurl?pr=abc123"
}
```

---

### 3.6 微信支付回调

**接口名称**: 微信支付结果通知回调  
**功能描述**: 接收微信支付平台的支付结果通知

| 属性 | 值 |
|------|-----|
| **请求方法** | POST |
| **URL路径** | `/api/v1/payment/wechat/notify` |
| **认证要求** | 无 (微信服务器调用) |
| **权限要求** | 无 |

#### 请求示例

由微信服务器发送，格式为加密的 JSON 数据。

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "code": "SUCCESS",
  "message": "Payment processed successfully"
}
```

**失败响应 (200 OK)**:
```json
{
  "code": "FAIL",
  "message": "Signature verification failed"
}
```

---

### 3.7 获取用户余额

**接口名称**: 获取用户余额  
**功能描述**: 查询当前用户的账户余额信息

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/payment/balance` |
| **认证要求** | 必需 |
| **权限要求** | 登录用户 |

#### 请求示例

```http
GET /api/v1/payment/balance HTTP/1.1
Host: api.relihub.com
Authorization: Bearer {token}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "id": "balance-550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-550e8400-e29b-41d4-a716-446655440000",
  "balance": 500.00,
  "frozen_balance": 0.00,
  "total_recharged": 1000.00,
  "total_consumed": 500.00,
  "total_refunded": 0.00,
  "created_at": "2026-04-01T00:00:00Z",
  "updated_at": "2026-04-08T10:30:00Z"
}
```

---

### 3.8 获取余额交易记录

**接口名称**: 获取余额交易记录  
**功能描述**: 分页查询当前用户的余额变动记录

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/payment/balance/transactions` |
| **认证要求** | 必需 |
| **权限要求** | 登录用户 |

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，最小值 1 |
| page_size | integer | 否 | 50 | 每页数量，范围 1-100 |

#### 请求示例

```http
GET /api/v1/payment/balance/transactions?page=1&page_size=50 HTTP/1.1
Host: api.relihub.com
Authorization: Bearer {token}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
[
  {
    "id": "trans-550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user-550e8400-e29b-41d4-a716-446655440000",
    "transaction_type": "recharge",
    "amount": 100.00,
    "balance_after": 500.00,
    "description": "微信充值",
    "remark": "订单号: PAY20260408103000001",
    "created_at": "2026-04-08T10:35:00Z"
  },
  {
    "id": "trans-550e8400-e29b-41d4-a716-446655440001",
    "user_id": "user-550e8400-e29b-41d4-a716-446655440000",
    "transaction_type": "consume",
    "amount": -10.00,
    "balance_after": 400.00,
    "description": "AI对话消费",
    "remark": "会话ID: session-123",
    "created_at": "2026-04-08T11:00:00Z"
  }
]
```

---

### 3.9 测试充值接口

**接口名称**: 测试充值 (仅测试环境)  
**功能描述**: 直接为用户充值余额，仅用于测试环境

| 属性 | 值 |
|------|-----|
| **请求方法** | POST |
| **URL路径** | `/api/v1/payment/balance/recharge` |
| **认证要求** | 必需 |
| **权限要求** | 登录用户 |

#### 查询参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| amount | float | 是 | 充值金额 (CNY)，必须大于 0 |

#### 请求示例

```http
POST /api/v1/payment/balance/recharge?amount=100.00 HTTP/1.1
Host: api.relihub.com
Authorization: Bearer {token}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "message": "Recharge successful",
  "order_no": "PAY20260408103000001",
  "amount": 100.00
}
```

**错误响应 (400 Bad Request)**:
```json
{
  "detail": "Amount must be positive"
}
```

---

## 4. LLM 提供商管理 (管理后台)

### 4.1 获取 LLM 提供商列表

**接口名称**: 获取 LLM 提供商列表 (管理后台)  
**功能描述**: 管理员查看所有 LLM 提供商配置

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/admin/llm-providers` |
| **认证要求** | 必需 |
| **权限要求** | 管理员 |

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| enabled | boolean | 否 | null | 按启用状态过滤 |

#### 请求示例

```http
GET /api/v1/admin/llm-providers?enabled=true HTTP/1.1
Host: api.relihub.com
Authorization: Bearer {admin_token}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "total": 3,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "deepseek",
      "display_name": "DeepSeek",
      "api_base_url": "https://api.deepseek.com/v1",
      "api_key_env": "DEEPSEEK_API_KEY",
      "cost_per_1k_tokens": 0.001,
      "rate_limit_per_minute": 60,
      "enabled": true,
      "created_at": "2026-04-01T00:00:00Z",
      "updated_at": "2026-04-08T10:30:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "openai",
      "display_name": "OpenAI",
      "api_base_url": "https://api.openai.com/v1",
      "api_key_env": "OPENAI_API_KEY",
      "cost_per_1k_tokens": 0.002,
      "rate_limit_per_minute": 60,
      "enabled": true,
      "created_at": "2026-04-01T00:00:00Z",
      "updated_at": "2026-04-08T10:30:00Z"
    }
  ]
}
```

---

### 4.2 获取 LLM 提供商详情

**接口名称**: 获取 LLM 提供商详情  
**功能描述**: 根据 ID 获取提供商详细配置

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/admin/llm-providers/{provider_id}` |
| **认证要求** | 必需 |
| **权限要求** | 管理员 |

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| provider_id | string | 是 | 提供商 ID |

#### 请求示例

```http
GET /api/v1/admin/llm-providers/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: api.relihub.com
Authorization: Bearer {admin_token}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "deepseek",
  "display_name": "DeepSeek",
  "api_base_url": "https://api.deepseek.com/v1",
  "api_key_env": "DEEPSEEK_API_KEY",
  "cost_per_1k_tokens": 0.001,
  "rate_limit_per_minute": 60,
  "enabled": true,
  "created_at": "2026-04-01T00:00:00Z",
  "updated_at": "2026-04-08T10:30:00Z"
}
```

**错误响应 (404 Not Found)**:
```json
{
  "detail": "LLM Provider 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

---

### 4.3 创建 LLM 提供商

**接口名称**: 创建 LLM 提供商  
**功能描述**: 添加新的 LLM 提供商配置

| 属性 | 值 |
|------|-----|
| **请求方法** | POST |
| **URL路径** | `/api/v1/admin/llm-providers` |
| **认证要求** | 必需 |
| **权限要求** | 管理员 |

#### 请求体参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| name | string | 是 | - | 唯一标识符，长度 1-50，如 'deepseek' |
| display_name | string | 是 | - | 显示名称，长度 1-100，如 'DeepSeek' |
| api_base_url | string | 是 | - | API 基础 URL |
| api_key_env | string | 是 | - | API 密钥环境变量名 |
| cost_per_1k_tokens | float | 是 | - | 每 1000 tokens 费用，必须大于 0 |
| rate_limit_per_minute | integer | 否 | 60 | 每分钟请求限制，最小值 1 |

#### 请求示例

```http
POST /api/v1/admin/llm-providers HTTP/1.1
Host: api.relihub.com
Content-Type: application/json
Authorization: Bearer {admin_token}

{
  "name": "claude",
  "display_name": "Claude",
  "api_base_url": "https://api.anthropic.com/v1",
  "api_key_env": "ANTHROPIC_API_KEY",
  "cost_per_1k_tokens": 0.003,
  "rate_limit_per_minute": 60
}
```

#### 响应示例

**成功响应 (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "name": "claude",
  "display_name": "Claude",
  "api_base_url": "https://api.anthropic.com/v1",
  "api_key_env": "ANTHROPIC_API_KEY",
  "cost_per_1k_tokens": 0.003,
  "rate_limit_per_minute": 60,
  "enabled": true,
  "created_at": "2026-04-08T10:30:00Z",
  "updated_at": "2026-04-08T10:30:00Z"
}
```

**错误响应 (400 Bad Request)**:
```json
{
  "detail": "LLM Provider 'claude' already exists"
}
```

---

### 4.4 更新 LLM 提供商

**接口名称**: 更新 LLM 提供商  
**功能描述**: 修改现有 LLM 提供商配置

| 属性 | 值 |
|------|-----|
| **请求方法** | PUT |
| **URL路径** | `/api/v1/admin/llm-providers/{provider_id}` |
| **认证要求** | 必需 |
| **权限要求** | 管理员 |

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| provider_id | string | 是 | 提供商 ID |

#### 请求体参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| display_name | string | 否 | 显示名称 |
| api_base_url | string | 否 | API 基础 URL |
| api_key_env | string | 否 | API 密钥环境变量名 |
| cost_per_1k_tokens | float | 否 | 每 1000 tokens 费用 |
| rate_limit_per_minute | integer | 否 | 每分钟请求限制 |
| enabled | boolean | 否 | 是否启用 |

#### 请求示例

```http
PUT /api/v1/admin/llm-providers/550e8400-e29b-41d4-a716-446655440002 HTTP/1.1
Host: api.relihub.com
Content-Type: application/json
Authorization: Bearer {admin_token}

{
  "display_name": "Claude 3.5",
  "cost_per_1k_tokens": 0.004,
  "rate_limit_per_minute": 100
}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "name": "claude",
  "display_name": "Claude 3.5",
  "api_base_url": "https://api.anthropic.com/v1",
  "api_key_env": "ANTHROPIC_API_KEY",
  "cost_per_1k_tokens": 0.004,
  "rate_limit_per_minute": 100,
  "enabled": true,
  "created_at": "2026-04-08T10:30:00Z",
  "updated_at": "2026-04-08T11:00:00Z"
}
```

---

### 4.5 删除 LLM 提供商

**接口名称**: 删除 LLM 提供商  
**功能描述**: 删除指定的 LLM 提供商配置

| 属性 | 值 |
|------|-----|
| **请求方法** | DELETE |
| **URL路径** | `/api/v1/admin/llm-providers/{provider_id}` |
| **认证要求** | 必需 |
| **权限要求** | 管理员 |

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| provider_id | string | 是 | 提供商 ID |

#### 请求示例

```http
DELETE /api/v1/admin/llm-providers/550e8400-e29b-41d4-a716-446655440002 HTTP/1.1
Host: api.relihub.com
Authorization: Bearer {admin_token}
```

#### 响应示例

**成功响应 (204 No Content)**:
无响应体

**错误响应 (404 Not Found)**:
```json
{
  "detail": "LLM Provider 550e8400-e29b-41d4-a716-446655440002 not found"
}
```

---

### 4.6 切换 LLM 提供商状态

**接口名称**: 切换 LLM 提供商启用状态  
**功能描述**: 快速启用或禁用 LLM 提供商

| 属性 | 值 |
|------|-----|
| **请求方法** | POST |
| **URL路径** | `/api/v1/admin/llm-providers/{provider_id}/toggle` |
| **认证要求** | 必需 |
| **权限要求** | 管理员 |

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| provider_id | string | 是 | 提供商 ID |

#### 请求示例

```http
POST /api/v1/admin/llm-providers/550e8400-e29b-41d4-a716-446655440000/toggle HTTP/1.1
Host: api.relihub.com
Authorization: Bearer {admin_token}
```

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "deepseek",
  "display_name": "DeepSeek",
  "api_base_url": "https://api.deepseek.com/v1",
  "api_key_env": "DEEPSEEK_API_KEY",
  "cost_per_1k_tokens": 0.001,
  "rate_limit_per_minute": 60,
  "enabled": false,
  "created_at": "2026-04-01T00:00:00Z",
  "updated_at": "2026-04-08T11:00:00Z"
}
```

---

## 5. 数据模型

### 5.1 PaymentStatus 枚举

| 值 | 说明 |
|-----|------|
| pending | 待支付 |
| success | 支付成功 |
| failed | 支付失败 |
| refunded | 已退款 |
| cancelled | 已取消 |

### 5.2 PaymentMethod 枚举

| 值 | 说明 |
|-----|------|
| wechat | 微信支付 |
| alipay | 支付宝 |
| bank_transfer | 银行转账 |

### 5.3 MessageRole 枚举

| 值 | 说明 |
|-----|------|
| user | 用户消息 |
| assistant | AI 助手消息 |
| system | 系统消息 |

---

## 6. 错误码

| HTTP 状态码 | 错误说明 |
|-------------|----------|
| 400 | 请求参数错误 |
| 401 | 未授权，需要登录 |
| 403 | 权限不足或配额超限 |
| 404 | 资源不存在 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |

---

## 7. 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-04-08 | v1.0 | 初始版本，包含 Sprint C 所有新增 API |

---

- [x] 对齐代码实现：端点路径已与 `app/api/v1/` 目录下路由文件同步
- [x] 对齐数据模型：Schema 定义已与 `app/schemas/` 目录下文件同步
- [x] 覆盖 Sprint C 功能：LLM 多提供商、支付模块、管理后台

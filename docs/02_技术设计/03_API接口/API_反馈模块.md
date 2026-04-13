# API 接口 - 意见反馈模块 (API_反馈模块)

**文档版本**: V2.0（全面对齐 PRD_MVP_意见反馈 V1.5）  
**最后更新**: 2026-04-09  
**参考 PRD**: [PRD_MVP_意见反馈.md](../../../01_产品需求/03_MVP_PRD/PRD_MVP_意见反馈.md)

---

## 1. 模块概述

提供用户提交建议、故障反馈及查看反馈进度的接口。支持图片附件上传、上下文关联、管理员抢单处理、满意度评价及回复结单通知。

**当前实现状态**: ✅ 已实现 (管理后台 + 用户端)

### 1.1 关键业务约束（源自 PRD §2.1/§3.1）

| 约束项 | 规则 |
|--------|------|
| 反馈内容长度 | 10 ~ **1000** 字符（PRD §3.1 原文） |
| 附件图片数量 | 最多 3 张；单文件 ≤ 5MB |
| 支持格式 | `png, jpg, jpeg, gif, bmp, webp, tif, tiff` |
| 用户日限额 | 同一 UID 每日最多提交 **5 条**（零点重置） |
| 管理后台分页 | **50 条/页**（PRD §4.1 原文） |
| 用户端分页 | 20 条/页 |
| SLA 结单目标 | **48 小时**内从 PENDING → RESOLVED/REJECTED |

### 1.2 工单状态机

```
                   ┌──────────────────────────────┐
                   │  超级管理员可强制释放/转办    │
                   └──────────────┬───────────────┘
                                  │
PENDING ──[抢单]──▶ PROCESSING ──[确认解决]──▶ RESOLVED
                              └──[驳回]──────▶ REJECTED
```

| 状态 | 代码 | 说明 | 允许后续操作 |
|------|------|------|-------------|
| 待处理 | `PENDING` | 进入公共领用池，等待管理员抢单 | 抢单 |
| 处理中 | `PROCESSING` | 已绑定处理人，锁定为独占处理 | 解决/驳回 |
| 已解决 | `RESOLVED` | 管理员提交解决结论，**回复内容必填** | 满意度评价（7天内） |
| 已驳回 | `REJECTED` | 恶意/重复/超范围，**驳回原因必填** | — |

> **⚠️ 注意**: 状态流转**严禁逆向**。超级管理员可通过独立 API 将"孤儿工单"（长期无响应的 PROCESSING 工单）强制重置为 PENDING 或直接转办。

---

## 2. 用户端接口

### 2.1 提交反馈

- **Endpoint**: `POST /api/v1/feedback`
- **状态**: ✅ 已实现
- **权限**: 需登录（游客访问返回 401）
- **限流**: 5 次/天/UID，超出返回 `FEEDBACK_4291`

**请求参数 (FeedbackCreateRequest)**:

| 字段 | 类型 | 必选 | 约束 | 说明 |
|------|------|------|------|------|
| `type` | string | 是 | `BUG/SUGGESTION/CONTENT/OTHER` | 反馈类型 |
| `content` | string | 是 | **10~1000 字符** | 反馈正文（`content_body`） |
| `images` | array[string] | 否 | 最多 3 张 URL；单文件 ≤ 5MB | 附件图片（需预先上传至文件服务） |
| `contact` | string | 否 | 最多 100 字符 | 联系方式（`contact_info`，存储时加密） |
| `reference_id` | string (UUID) | 否 | — | 关联内容 ID（资源 ID/话题 ID/会话 ID） |
| `reference_type` | string | 否 | `RESOURCE/TOPIC/SESSION` | 关联类型，`reference_id` 存在时必填 |

**请求示例**:

```json
{
  "type": "BUG",
  "content": "在上传文件时出现网络错误，文件没有上传成功但扣除了积分，请排查原因",
  "images": ["https://cdn.relihub.com/feedback/error1.png"],
  "contact": "wechat: user123",
  "reference_id": "550e8400-e29b-41d4-a716-446655440001",
  "reference_type": "RESOURCE"
}
```

**响应 (201 Created)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ticket_id": "FB20260409000001",
  "type": "BUG",
  "content": "在上传文件时出现网络错误...",
  "status": "PENDING",
  "created_at": "2026-04-09T12:00:00Z"
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 反馈内部 ID（UUID） |
| `ticket_id` | string | **工单业务单号**，格式 `FB + YYYYMMDD + 6位流水`，如 `FB20260409000001` |
| `type` | string | 反馈类型 |
| `content` | string | 反馈内容（截断展示，原文已加密存储） |
| `status` | string | 初始状态为 `PENDING` |
| `created_at` | string | 提交时间 ISO 8601 |

---

### 2.2 获取我的反馈列表

- **Endpoint**: `GET /api/v1/feedback/my`
- **状态**: ✅ 已实现
- **权限**: 需登录

**请求参数**:

| 参数名 | 类型 | 必选 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码（≥ 1） |
| `page_size` | int | 否 | 20 | 每页数量（1~50） |
| `status` | string | 否 | — | 按状态筛选：`PENDING/PROCESSING/RESOLVED/REJECTED` |

**响应 (200 OK)**:

```json
{
  "feedbacks": [
    {
      "id": "uuid",
      "ticket_id": "FB20260409000001",
      "type": "BUG",
      "content": "在上传文件时出现网络错误...",
      "status": "RESOLVED",
      "has_reply": true,
      "created_at": "2026-04-09T12:00:00Z",
      "resolved_at": "2026-04-09T18:30:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `ticket_id` | string | 工单业务单号 |
| `has_reply` | bool | 是否已有管理员回复（用于前端展示未读标记） |
| `resolved_at` | string | 结单时间（RESOLVED/REJECTED 时有值） |

---

### 2.3 获取反馈详情

- **Endpoint**: `GET /api/v1/feedback/{id}`
- **状态**: ✅ 已实现
- **权限**: 需登录（仅本人可查看）

**路径参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `id` | string | 反馈 ID（UUID） |

**响应 (200 OK)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ticket_id": "FB20260409000001",
  "type": "BUG",
  "content": "在上传文件时出现网络错误，文件没有上传成功但扣除了积分，请排查原因",
  "images": ["https://cdn.relihub.com/feedback/error1.png"],
  "contact": "wechat: user123",
  "reference_id": "550e8400-e29b-41d4-a716-446655440001",
  "reference_type": "RESOURCE",
  "status": "RESOLVED",
  "reply": {
    "content": "感谢您的反馈。我们已定位该问题并将在 v1.1.1 版本修复，积分已原路退回。",
    "replied_at": "2026-04-09T18:30:00Z"
  },
  "evaluation": null,
  "can_evaluate": true,
  "evaluate_deadline": "2026-04-16T18:30:00Z",
  "created_at": "2026-04-09T12:00:00Z",
  "resolved_at": "2026-04-09T18:30:00Z"
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `reply` | object\|null | 管理员回复（RESOLVED/REJECTED 时有值） |
| `reply.content` | string | 回复/驳回内容 |
| `reply.replied_at` | string | 回复时间 |
| `evaluation` | object\|null | 满意度评价（已评价时有值） |
| `can_evaluate` | bool | 是否在 7 天评价窗口内且状态为 RESOLVED |
| `evaluate_deadline` | string\|null | 评价截止时间（结单后 7 个自然日） |
| `resolved_at` | string\|null | 结单时间 |

---

### 2.4 提交满意度评价

- **Endpoint**: `POST /api/v1/feedback/{id}/evaluate`
- **状态**: ✅ 已实现（SUP-F051）
- **权限**: 需登录（仅本人，仅 RESOLVED 状态）
- **时间限制**: 结单后 **7 个自然日**内有效

**路径参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `id` | string | 反馈 ID（UUID） |

**请求参数 (FeedbackEvaluationRequest)**:

| 字段 | 类型 | 必选 | 约束 | 说明 |
|------|------|------|------|------|
| `score` | int | 是 | `1` 或 `2` | 满意度：`1` = 满意；`2` = 不满意 |
| `comment` | string | 否 | ≤ 100 字符 | 评价文字说明 |

**请求示例**:

```json
{
  "score": 1,
  "comment": "响应及时，问题得到了很好的解决，感谢！"
}
```

**响应 (200 OK)**:

```json
{
  "message": "评价提交成功",
  "evaluation_score": 1,
  "evaluation_at": "2026-04-10T09:00:00Z"
}
```

**错误情形**:

| HTTP 状态 | 错误码 | 原因 |
|-----------|--------|------|
| 400 | `FEEDBACK_4005` | 已评价过（不可重复） |
| 403 | `FEEDBACK_4032` | 反馈非 RESOLVED 状态，不可评价 |
| 410 | `FEEDBACK_4100` | 超过 7 天评价窗口，评价入口已关闭 |

---

## 3. 管理后台接口

### 3.1 获取反馈列表（Admin）

- **Endpoint**: `GET /admin/feedbacks`
- **状态**: ✅ 已实现
- **权限**: `SUPER_ADMIN, OPERATOR, AUDITOR`

**请求参数**:

| 参数名 | 类型 | 必选 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码 |
| `page_size` | int | 否 | **50** | 每页数量（PRD §4.1，最大 100） |
| `status` | string | 否 | — | 状态筛选：`PENDING/PROCESSING/RESOLVED/REJECTED` |
| `type` | string | 否 | — | 类型筛选：`BUG/SUGGESTION/CONTENT/OTHER` |
| `sla_overdue` | bool | 否 | — | `true` = 仅显示超过 48h 未结单的工单（SLA 超时预警） |
| `handler_id` | string | 否 | — | 按处理人 UUID 筛选 |
| `search` | string | 否 | — | 全文搜索（匹配 ticket_id 或内容摘要） |

**响应 (200 OK)**:

```json
{
  "feedbacks": [
    {
      "id": "uuid",
      "ticket_id": "FB20260409000001",
      "user_id": "user-uuid",
      "type": "BUG",
      "content": "在上传文件时出现网络错误...",
      "reference_id": "resource-uuid",
      "reference_type": "RESOURCE",
      "status": "PENDING",
      "handler_id": null,
      "handler_name": null,
      "sla_overdue": false,
      "hours_since_created": 3.5,
      "has_attachment": true,
      "attachment_safe": true,
      "created_at": "2026-04-09T12:00:00Z",
      "updated_at": "2026-04-09T12:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 50
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `ticket_id` | string | 工单业务单号（用于列表展示、搜索） |
| `reference_id` | string\|null | 关联内容 ID |
| `reference_type` | string\|null | 关联类型：`RESOURCE/TOPIC/SESSION` |
| `handler_id` | string\|null | 处理人 UUID（PROCESSING 状态时有值） |
| `handler_name` | string\|null | 处理人昵称（脱敏显示） |
| `sla_overdue` | bool | 是否已超过 48h SLA 未结单（超时高亮预警标志位） |
| `hours_since_created` | float | 距创建已过小时数（前端据此渲染进度条） |
| `has_attachment` | bool | 是否包含附件图片 |
| `attachment_safe` | bool | 附件安全检测是否已通过（`false` 时拦截"确认解决"操作） |

---

### 3.2 获取反馈详情（Admin）

- **Endpoint**: `GET /admin/feedbacks/{feedback_id}`
- **状态**: ✅ 已实现
- **权限**: `SUPER_ADMIN, OPERATOR, AUDITOR`

**路径参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `feedback_id` | string | 反馈 ID（UUID）或 `ticket_id`（如 `FB20260409000001`）均可 |

**响应 (200 OK)**:

```json
{
  "id": "uuid",
  "ticket_id": "FB20260409000001",
  "user_id": "user-uuid",
  "user_nickname": "张三",
  "type": "BUG",
  "content": "在上传文件时出现网络错误...",
  "images": ["https://cdn.relihub.com/feedback/error1.png"],
  "contact_info": "wec****123",
  "reference_id": "resource-uuid",
  "reference_type": "RESOURCE",
  "reference_title": "可靠性设计指南.pdf",
  "status": "PROCESSING",
  "handler_id": "admin-uuid",
  "handler_name": "管理员A",
  "internal_notes": "已联系研发定位，预计明天修复",
  "reply_content": null,
  "sla_overdue": false,
  "hours_since_created": 3.5,
  "has_attachment": true,
  "attachment_safe": true,
  "evaluation_score": null,
  "evaluation_body": null,
  "evaluation_at": null,
  "created_at": "2026-04-09T12:00:00Z",
  "resolved_at": null
}
```

**PII 脱敏规则**:

| 角色 | `contact_info` 展示 |
|------|-------------------|
| `OPERATOR` / `AUDITOR` | 脱敏显示，如 `wec****123`、`138****5678` |
| `SUPER_ADMIN` | **明文原文**（用于紧急线下联系） |

---

### 3.3 抢单（管理员领用工单）

- **Endpoint**: `POST /admin/feedbacks/{feedback_id}/claim`
- **状态**: ✅ 已实现（SUP-F049）
- **权限**: `SUPER_ADMIN, OPERATOR`
- **约束**: 仅 `PENDING` 状态工单可被领用；一旦领用成功，其他管理员不可再操作（锁定机制）

**路径参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `feedback_id` | string | 反馈 ID |

**请求体**: 无（操作人由 JWT Token 获取）

**响应 (200 OK)**:

```json
{
  "id": "uuid",
  "ticket_id": "FB20260409000001",
  "status": "PROCESSING",
  "handler_id": "admin-uuid",
  "handler_name": "管理员A",
  "updated_at": "2026-04-09T13:00:00Z"
}
```

**错误情形**:

| HTTP 状态 | 错误码 | 原因 |
|-----------|--------|------|
| 409 | `FEEDBACK_4090` | 工单已被其他管理员领用（`status != PENDING`） |
| 404 | `ADMIN_4007` | 反馈不存在 |

---

### 3.4 回复反馈（确认解决）

- **Endpoint**: `POST /admin/feedbacks/{feedback_id}/reply`
- **状态**: ✅ 已实现
- **权限**: `SUPER_ADMIN, OPERATOR`（且必须是当前 `handler_id` 或 `SUPER_ADMIN`）
- **约束**: 仅 `PROCESSING` 状态可调用；`attachment_safe = false` 时拦截
- **副作用**: 工单状态 → `RESOLVED`；触发站内通知下发（同步伴随，失败不阻塞结单）

**路径参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `feedback_id` | string | 反馈 ID |

**请求参数 (FeedbackReplyRequest)**:

| 字段 | 类型 | 必选 | 约束 | 说明 |
|------|------|------|------|------|
| `reply` | string | 是 | **1~2000 字符** | 对外回复内容（推送至用户） |
| `internal_notes` | string | 否 | ≤ 500 字符 | 内部备注（用户不可见） |

**请求示例**:

```json
{
  "reply": "感谢您的反馈。我们已定位该问题并将在 v1.1.1 版本修复，积分已原路退回，请稍后查看。",
  "internal_notes": "Bug 编号 #2341，研发在 commit abc123 中已修复"
}
```

**响应 (200 OK)**:

```json
{
  "id": "uuid",
  "ticket_id": "FB20260409000001",
  "status": "RESOLVED",
  "reply_content": "感谢您的反馈。我们已定位该问题...",
  "handler_name": "管理员A",
  "resolved_at": "2026-04-09T18:30:00Z"
}
```

**通知下发规则**（对齐 PRD §4.2）:

> 发送站内通知，模板：  
> `【反馈处理结果】您的反馈（单号：{ticket_id}）已有处理结果。管理员回复：{reply_content_preview}。点击查看详情。`  
> `reply_content_preview` 截取前 50 字符。

---

### 3.5 驳回工单

- **Endpoint**: `POST /admin/feedbacks/{feedback_id}/reject`
- **状态**: ✅ 已实现
- **权限**: `SUPER_ADMIN, OPERATOR`（且必须是当前 `handler_id` 或 `SUPER_ADMIN`）
- **约束**: 仅 `PROCESSING` 状态可调用；驳回原因（`reason`）**必填**
- **副作用**: 工单状态 → `REJECTED`；触发站内通知下发

**请求参数 (FeedbackRejectRequest)**:

| 字段 | 类型 | 必选 | 约束 | 说明 |
|------|------|------|------|------|
| `reason` | string | **是** | 1~500 字符 | 驳回原因（对外展示给用户） |
| `internal_notes` | string | 否 | ≤ 500 字符 | 内部备注 |

**请求示例**:

```json
{
  "reason": "您的反馈内容与系统功能无关，属于重复投诉，请查阅帮助中心文档后再行反馈。",
  "internal_notes": "同一用户本月第 3 次重复提交"
}
```

**响应 (200 OK)**:

```json
{
  "id": "uuid",
  "ticket_id": "FB20260409000001",
  "status": "REJECTED",
  "reply_content": "您的反馈内容与系统功能无关...",
  "resolved_at": "2026-04-09T18:30:00Z"
}
```

---

### 3.6 强制释放/转办工单（超级管理员）

- **Endpoint**: `POST /admin/feedbacks/{feedback_id}/transfer`
- **状态**: ✅ 已实现
- **权限**: `SUPER_ADMIN` 独占
- **使用场景**: 处理"孤儿工单"——`PROCESSING` 状态但处理人长期无响应

**请求参数 (FeedbackTransferRequest)**:

| 字段 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `action` | string | 是 | `RELEASE`（重置为 PENDING）或 `REASSIGN`（直接转办） |
| `new_handler_id` | string (UUID) | 否 | `action = REASSIGN` 时必填，目标管理员 UUID |
| `reason` | string | 否 | 操作原因（写入审计日志） |

**请求示例（转办）**:

```json
{
  "action": "REASSIGN",
  "new_handler_id": "admin-uuid-b",
  "reason": "原处理人 A 已离职，转办给管理员 B"
}
```

**响应 (200 OK)**:

```json
{
  "id": "uuid",
  "ticket_id": "FB20260409000001",
  "status": "PROCESSING",
  "handler_id": "admin-uuid-b",
  "handler_name": "管理员B",
  "updated_at": "2026-04-09T20:00:00Z"
}
```

---

## 4. 业务规则

### 4.1 反馈类型枚举

| 类型 | 代码 | PRD 原文 |
|------|------|---------|
| 功能异常 | `BUG` | 对应 PRD "功能异常" |
| 体验建议 | `SUGGESTION` | 对应 PRD "体验建议" |
| 内容纠错 | `CONTENT` | 对应 PRD "内容纠错" |
| 其他 | `OTHER` | 对应 PRD "其他" |

### 4.2 reference_type 枚举

| 值 | 关联内容 | 使用场景 |
|----|---------|---------|
| `RESOURCE` | 资源详情页 | 用户在资源页发起内容纠错 |
| `TOPIC` | 社区话题页 | 用户在话题页举报内容 |
| `SESSION` | AI 对话会话 | 用户对 AI 回答反馈 |

### 4.3 满意度评价规则

| 规则 | 说明 |
|------|------|
| 触发条件 | 工单状态变为 `RESOLVED` |
| 评价窗口 | 结单后 **7 个自然日** |
| 逾期处理 | 超期未评价自动关闭评价入口，**不落 evaluation_body**，`evaluation_score` 结案值视为无评价 |
| 评分枚举 | `1` = 满意；`2` = 不满意 |
| 文字说明 | 可选，上限 100 字符 |
| 重复评价 | 不可重复（返回 `FEEDBACK_4005`） |

### 4.4 SLA 超时预警规则

| 触发 | 条件 |
|------|------|
| 高亮预警 | 工单从首次进入 PENDING 状态起，超过 **48 小时** 未进入 RESOLVED/REJECTED |
| 管理后台展示 | `sla_overdue = true` 时触发列表高亮置顶 + 🔴 标记 |
| 查询过滤 | `GET /admin/feedbacks?sla_overdue=true` 可单独查询所有逾期工单 |

### 4.5 限流规则

| 操作 | 限制 | 说明 |
|------|------|------|
| 提交反馈 | **5 次/天/UID** | 零点重置，超出返回 `FEEDBACK_4291` |
| 查看反馈 | 无限制 | 需登录 |

### 4.6 附件安全联动规则（对齐 PRD §五-2）

| 附件状态 | 管理后台行为 |
|---------|------------|
| `SCANNING` | 工单详情显示"附件安全检测中"，**拦截** "确认解决"和"驳回"操作 |
| `ISOLATED` | 工单详情显示"附件已隔离"，**拦截** 操作，提示管理员人工研判 |
| `CLEAN` | 正常操作 |

---

## 5. 错误码映射

| 错误码 | HTTP 状态 | 业务含义 | 前端处理建议 |
|--------|-----------|---------|------------|
| `FEEDBACK_4001` | 400 | 内容过短（< 10 字符） | 提示"反馈内容至少 10 个字符" |
| `FEEDBACK_4002` | 400 | 内容过长（> 1000 字符） | 提示"反馈内容不超过 1000 字符" |
| `FEEDBACK_4003` | 400 | 无效的反馈类型 | 检查 `type` 枚举值 |
| `FEEDBACK_4004` | 400 | `reference_type` 缺失（`reference_id` 存在时） | 前端同步传入 `reference_type` |
| `FEEDBACK_4005` | 400 | 已评价过（不可重复评价） | 提示"您已评价过该反馈" |
| `FEEDBACK_4011` | 401 | 未登录 | 跳转登录页面 |
| `FEEDBACK_4031` | 403 | 无权限查看他人反馈 | 提示"仅能查看自己的反馈" |
| `FEEDBACK_4032` | 403 | 工单非 RESOLVED 状态，不可评价 | 禁用评价按钮 |
| `FEEDBACK_4033` | 403 | 非当前处理人，不可操作 | 提示"该工单已由其他管理员处理" |
| `FEEDBACK_4041` | 404 | 反馈不存在 | 刷新列表 |
| `FEEDBACK_4090` | 409 | 工单已被抢单（并发冲突） | 提示"该工单已被其他管理员领取" |
| `FEEDBACK_4100` | 410 | 评价窗口已关闭（超 7 天） | 隐藏评价入口 |
| `FEEDBACK_4291` | 429 | 今日提交上限（5 次） | 提示"今日提交次数已用完，请明天再试" |
| `FEEDBACK_5001` | 500 | 服务器异常 | 提示"服务异常，请稍后重试" |

---

## 6. 前端集成指南

### 6.1 反馈提交表单（TypeScript 类型）

```typescript
interface FeedbackFormData {
  type: 'BUG' | 'SUGGESTION' | 'CONTENT' | 'OTHER';
  content: string;          // 10~1000 字符
  images?: string[];        // 预上传后的 URL，最多 3 个
  contact?: string;         // 选填，最多 100 字符
  reference_id?: string;    // 上下文关联 ID（从路由参数注入）
  reference_type?: 'RESOURCE' | 'TOPIC' | 'SESSION';
}

// 表单验证规则
const validationRules = {
  content: { minLength: 10, maxLength: 1000, required: true },
  type: { required: true, options: ['BUG', 'SUGGESTION', 'CONTENT', 'OTHER'] },
  images: { maxCount: 3, maxSizeMb: 5 }
};
```

### 6.2 工单状态展示

| 状态 | 显示文本 | 颜色 | 图标 |
|------|---------|------|------|
| `PENDING` | 待处理 | `#FF9500` 橙 | ⏳ |
| `PROCESSING` | 处理中 | `#3B82F6` 蓝 | 🔄 |
| `RESOLVED` | 已解决 | `#10B981` 绿 | ✅ |
| `REJECTED` | 已驳回 | `#6B7280` 灰 | 🚫 |

### 6.3 满意度评价入口逻辑

```typescript
// 显示评价按钮的条件
const showEvaluateButton = 
  feedback.status === 'RESOLVED' &&
  feedback.can_evaluate === true &&
  feedback.evaluation === null;

// 评价窗口倒计时
const daysRemaining = Math.ceil(
  (new Date(feedback.evaluate_deadline) - new Date()) / (1000 * 60 * 60 * 24)
);
```

### 6.4 提交成功处理

1. 显示成功 Toast：`"反馈提交成功（单号：{ticket_id}），感谢您的参与！"`
2. 清空表单内容
3. 跳转至反馈列表页
4. 更新列表显示新反馈

### 6.5 限流和附件安全处理

```typescript
// 监听 429（限流）
if (response.status === 429) {
  Toast.show("今日提交次数已用完，请明天再试");
  disableSubmitButton();
}

// 管理端：附件安全检测中时禁用操作按钮
if (!feedback.attachment_safe) {
  disableResolveAndRejectButtons();
  showWarningBanner("附件安全检测中，处理操作暂时不可用");
}
```

---

## 7. 接口汇总表

| 接口 | 方法 | 路径 | 权限 | 状态 |
|------|------|------|------|------|
| 提交反馈 | POST | `/api/v1/feedback` | 登录用户 | ✅ |
| 我的反馈列表 | GET | `/api/v1/feedback/my` | 登录用户 | ✅ |
| 反馈详情 | GET | `/api/v1/feedback/{id}` | 登录用户（本人） | ✅ |
| 满意度评价 | POST | `/api/v1/feedback/{id}/evaluate` | 登录用户（本人） | ✅ |
| 管理后台列表 | GET | `/admin/feedbacks` | SUPER_ADMIN/OPERATOR/AUDITOR | ✅ |
| 管理后台详情 | GET | `/admin/feedbacks/{id}` | SUPER_ADMIN/OPERATOR/AUDITOR | ✅ |
| 抢单（领用） | POST | `/admin/feedbacks/{id}/claim` | SUPER_ADMIN/OPERATOR | ✅ |
| 回复（结案解决） | POST | `/admin/feedbacks/{id}/reply` | SUPER_ADMIN/OPERATOR | ✅ |
| 驳回 | POST | `/admin/feedbacks/{id}/reject` | SUPER_ADMIN/OPERATOR | ✅ |
| 强制转办 | POST | `/admin/feedbacks/{id}/transfer` | SUPER_ADMIN | ✅ |

---

## 8. 实施检查清单

| 功能 | 状态 | 备注 |
|------|------|------|
| 用户提交反馈 API | ✅ 已实现 | `POST /api/v1/feedback` |
| 工单业务单号生成 | ✅ 已实现 | 格式 `FB + YYYYMMDD + 6位流水` |
| 上下文关联字段 | ✅ 已实现 | `reference_id` + `reference_type` |
| 我的反馈列表 API | ✅ 已实现 | `GET /api/v1/feedback/my` |
| 反馈详情 API | ✅ 已实现 | `GET /api/v1/feedback/{id}` |
| 满意度评价 API | ✅ 已实现 | `POST /api/v1/feedback/{id}/evaluate` |
| 管理后台反馈列表 | ✅ 已实现 | 50条/页，支持 SLA 超时过滤 |
| 管理后台反馈详情 | ✅ 已实现 | 含 PII 脱敏逻辑 |
| 管理员抢单 API | ✅ 已实现 | `POST /admin/feedbacks/{id}/claim` |
| 管理后台回复反馈 | ✅ 已实现 | `POST /admin/feedbacks/{id}/reply` |
| 驳回工单 API | ✅ 已实现 | `POST /admin/feedbacks/{id}/reject` |
| 强制转办 API | ✅ 已实现 | `SUPER_ADMIN` 专用 |
| SLA 超时预警字段 | ✅ 已实现 | `sla_overdue` 字段 + 过滤参数 |
| 限流逻辑 | ✅ 已实现 | 每日 5 次限制 |
| PII 脱敏 | ✅ 已实现 | `contact_info` 按角色脱敏 |
| 可可豆奖励 | ⬜ Phase 2 | SUP-F057，MVP 阶段暂不实现 |

---

## 9. 依赖关系

### 前端依赖
- 文件上传模块（上传图片，获取 URL 后填入 `images`）
- 用户登录状态
- Toast / Banner 提示组件
- 路由参数注入（`reference_id`、`reference_type`）

### 后端依赖
- 用户服务（获取用户信息、角色验证）
- 文件服务（图片 URL 生成、安全检测状态查询）
- 通知服务（结单后触发站内消息）
- Redis 限流服务（日限额计数）

---

## 10. 修改历史

| 版本 | 日期 | 修改内容 |
|------|------|---------|
| V1.0 | 2026-04-08 | 初版，基础用户端和管理端接口 |
| V2.0 | 2026-04-09 | 全面对齐 PRD V1.5：修正内容字长（500→1000）、分页（20→50）、补充 ticket_id/reference_id/REJECTED 状态/抢单 API/满意度评价 API/SLA 超时/PII 脱敏/强制转办 API/附件安全联动 |

---

- [x] 对齐 PRD_MVP_意见反馈 §2.1/§3.1/§4.1/§4.2/§5.0。
- [x] 支持管理员抢单（领用池模式）。
- [x] 补充满意度评价 API（SUP-F051）。
- [x] 补充驳回工单和强制转办 API。
- [x] 补充 SLA 超时预警机制。
- [x] 补充 PII 脱敏规则（contact_info 按角色展示）。
- [x] 补充上下文关联字段（reference_id/reference_type）。
- [x] 更新实施检查清单（10 项已实现，1 项 Phase 2）。

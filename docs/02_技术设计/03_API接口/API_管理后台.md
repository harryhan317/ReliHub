# API 接口 - 管理后台 (API_管理后台)

## 1. 用户管理

### 1.1 用户列表查询
- **Endpoint**: `GET /admin/users`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **参数**:
  - `status` (可选): 用户状态筛选 (ACTIVE, DISABLED, LOCKED, HIBERNATED)
  - `search` (可选): 按昵称或手机号搜索
  - `page` (可选): 页码，默认 1
  - `page_size` (可选): 每页数量，默认 20，最大 100
- **响应**: `UserListResponse`

### 1.2 用户详情查询
- **Endpoint**: `GET /admin/users/{user_id}`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **响应**: `UserResponse`

### 1.3 用户封禁
- **Endpoint**: `POST /admin/users/{user_id}/ban`
- **方法**: POST
- **权限**: SUPER_ADMIN, OPERATOR
- **请求体**:
  ```json
  {
    "reason": "违规原因",
    "duration_days": null
  }
  ```
- **响应**: `UserResponse`

### 1.4 用户解封
- **Endpoint**: `POST /admin/users/{user_id}/unban`
- **方法**: POST
- **权限**: SUPER_ADMIN, OPERATOR
- **响应**: `UserResponse`

### 1.5 用户锁定
- **Endpoint**: `POST /admin/users/{user_id}/lock`
- **方法**: POST
- **权限**: SUPER_ADMIN, OPERATOR
- **请求体**:
  ```json
  {
    "reason": "锁定原因"
  }
  ```
- **响应**: `UserResponse`

### 1.6 用户解锁
- **Endpoint**: `POST /admin/users/{user_id}/unlock`
- **方法**: POST
- **权限**: SUPER_ADMIN, OPERATOR
- **响应**: `UserResponse`

---

## 2. 内容审核

### 2.1 待审核资源列表
- **Endpoint**: `GET /admin/resources/pending`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **参数**:
  - `page` (可选): 页码，默认 1
  - `page_size` (可选): 每页数量，默认 20，最大 100
- **响应**: `ResourceListResponse`

### 2.2 批准资源
- **Endpoint**: `POST /admin/resources/{resource_id}/approve`
- **方法**: POST
- **权限**: SUPER_ADMIN, OPERATOR
- **请求体**:
  ```json
  {
    "reason": "审核通过原因（可选）"
  }
  ```
- **响应**: `ResourceResponse`

### 2.3 拒绝资源
- **Endpoint**: `POST /admin/resources/{resource_id}/reject`
- **方法**: POST
- **权限**: SUPER_ADMIN, OPERATOR
- **请求体**:
  ```json
  {
    "reason": "拒绝原因"
  }
  ```
- **响应**: `ResourceResponse`

### 2.4 封禁资源
- **Endpoint**: `POST /admin/resources/{resource_id}/block`
- **方法**: POST
- **权限**: SUPER_ADMIN, OPERATOR
- **请求体**:
  ```json
  {
    "reason": "封禁原因"
  }
  ```
- **响应**: `ResourceResponse`

### 2.5 话题列表
- **Endpoint**: `GET /admin/topics`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **参数**:
  - `status` (可选): 话题状态筛选
  - `page` (可选): 页码，默认 1
  - `page_size` (可选): 每页数量，默认 20，最大 100
- **响应**: `TopicListResponse`

### 2.6 封禁话题
- **Endpoint**: `POST /admin/topics/{topic_id}/block`
- **方法**: POST
- **权限**: SUPER_ADMIN, OPERATOR
- **请求体**:
  ```json
  {
    "reason": "封禁原因"
  }
  ```
- **响应**: `TopicResponse`

---

## 3. 审计日志

### 3.1 审计日志列表
- **Endpoint**: `GET /admin/audit-logs`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **参数**:
  - `admin_id` (可选): 按管理员 ID 筛选
  - `action` (可选): 按操作类型筛选 (BAN_USER, APPROVE_RESOURCE, etc.)
  - `page` (可选): 页码，默认 1
  - `page_size` (可选): 每页数量，默认 20，最大 100
- **响应**: `AuditLogListResponse`

### 3.2 审计日志详情
- **Endpoint**: `GET /admin/audit-logs/{log_id}`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **响应**: `AuditLogResponse`

---

## 4. 系统配置

### 4.1 系统配置列表
- **Endpoint**: `GET /admin/system-configs`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **响应**: `SystemConfigListResponse`

### 4.2 更新系统配置
- **Endpoint**: `PATCH /admin/system-configs`
- **方法**: PATCH
- **权限**: SUPER_ADMIN
- **请求体**:
  ```json
  {
    "config_key": "配置键名",
    "config_value": "配置值",
    "description": "配置描述（可选）"
  }
  ```
- **响应**: `SystemConfigResponse`

---

## 5. 意见反馈处理

### 5.1 反馈列表
- **Endpoint**: `GET /admin/feedbacks`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **参数**:
  - `status` (可选): 反馈状态筛选 (PENDING, RESOLVED, CLOSED)
  - `page` (可选): 页码，默认 1
  - `page_size` (可选): 每页数量，默认 20，最大 100
- **响应**: `FeedbackListResponse`

### 5.2 反馈详情
- **Endpoint**: `GET /admin/feedbacks/{feedback_id}`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **响应**: `FeedbackResponse`

### 5.3 回复反馈
- **Endpoint**: `POST /admin/feedbacks/{feedback_id}/reply`
- **方法**: POST
- **权限**: SUPER_ADMIN, OPERATOR
- **请求体**:
  ```json
  {
    "reply": "回复内容"
  }
  ```
- **核心逻辑**: 工单状态同步置为 `RESOLVED`，绑定处理人 ID，触发给用户的下行消息通知。
- **响应**: `FeedbackResponse`

---

## 6. 扩容包管理

### 6.1 扩容包列表
- **Endpoint**: `GET /admin/asset-packages`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **响应**: `AssetPackageListResponse`

### 6.2 更新扩容包
- **Endpoint**: `PATCH /admin/asset-packages/{package_id}`
- **方法**: PATCH
- **权限**: SUPER_ADMIN
- **请求体**:
  ```json
  {
    "price_beans": 100,
    "discount_rate": 0.80
  }
  ```
- **参数约束**:
  - `price_beans`: 有效范围 1~100000（特惠包默认 80；畅享包默认 350）
  - `discount_rate`: 折扣率 0.0~1.0（特惠包默认 0.85；畅享包默认 0.70）
- **约束**: 价格修改后不影响已售出套餐，只对新购用户生效；历史订单不做追溯。
- **响应**: `AssetPackageResponse`

---

## 7. 仪表盘统计

### 7.1 获取统计数据
- **Endpoint**: `GET /admin/dashboard/stats`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR
- **响应**: `DashboardStatsResponse`
- **返回字段**:
  - `total_users`: 总用户数
  - `active_users`: 活跃用户数
  - `total_resources`: 总资源数
  - `pending_resources`: 待审核资源数
  - `total_topics`: 总话题数
  - `total_posts`: 总帖子数
  - `total_feedbacks`: 总反馈数
  - `pending_feedbacks`: 待处理反馈数

---

## 8. LLM Provider 管理

### 8.1 创建 LLM Provider
- **Endpoint**: `POST /admin/llm-providers`
- **方法**: POST
- **权限**: SUPER_ADMIN
- **请求体**:
  ```json
  {
    "name": "deepseek",
    "display_name": "DeepSeek",
    "api_base_url": "https://api.deepseek.com",
    "api_key_env": "DEEPSEEK_API_KEY",
    "cost_per_1k_tokens": 0.001,
    "rate_limit_per_minute": 60
  }
  ```
- **响应**: `LLMProviderResponse`

### 8.2 LLM Provider 列表
- **Endpoint**: `GET /admin/llm-providers`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR

### 8.3 获取 LLM Provider
- **Endpoint**: `GET /admin/llm-providers/{provider_id}`
- **方法**: GET
- **权限**: SUPER_ADMIN, OPERATOR, AUDITOR

### 8.4 更新 LLM Provider
- **Endpoint**: `PUT /admin/llm-providers/{provider_id}`
- **方法**: PUT
- **权限**: SUPER_ADMIN

### 8.5 删除 LLM Provider
- **Endpoint**: `DELETE /admin/llm-providers/{provider_id}`
- **方法**: DELETE
- **权限**: SUPER_ADMIN

### 8.6 测试 LLM Provider 连接
- **Endpoint**: `POST /admin/llm-providers/{provider_id}/test`
- **方法**: POST
- **权限**: SUPER_ADMIN

---

## 9. 权限控制与审计要求

### 9.1 RBAC 角色定义

| 角色 | 权限范围 |
|------|---------|
| SUPER_ADMIN | 所有操作，包括系统配置、扩容包管理、LLM Provider 管理 |
| OPERATOR | 用户管理、内容审核、反馈处理 |
| AUDITOR | 只读权限，仅查看审计日志和统计数据 |

### 9.2 审计日志 Hash Chaining

每次写操作强制触发 `admin_audit_logs` 的 Hash Chaining 写入逻辑：
1. 查询上一条日志的 `log_hash`
2. 计算当前日志的哈希值（包含 `prev_log_hash`）
3. 写入审计日志表

### 9.3 IP 子网隔离（Admin Subnet Binding）

在 **API Gateway 层**（Nginx/Envoy）执行 `admin_subnet` 检查：
- 请求头携带 `X-Forwarded-For` 或由网关透传的真实 IP
- 经 `ipaddress` 模块匹配 CIDR 子网列表
- 非匹配请求直接返回 403，不再路由至后端服务

---

## 10. 错误码

| 错误码 | 描述 | HTTP 状态码 |
|--------|------|------------|
| ADMIN_4001 | 管理员账号已被禁用 | 403 |
| ADMIN_4002 | 权限不足 | 403 |
| ADMIN_4003 | 管理员不存在 | 404 |
| ADMIN_4004 | 用户不存在 | 404 |
| ADMIN_4005 | 资源不存在 | 404 |
| ADMIN_4006 | 话题不存在 | 404 |
| ADMIN_4007 | 反馈不存在 | 404 |
| ADMIN_4008 | 配置项不存在 | 404 |
| ADMIN_4009 | 扩容包不存在 | 404 |

---
- [x] 对齐 PRD §5.0 管理后台核心功能。
- [x] 安全策略：所有路径受 `admin_subnet` 检查。
- [x] 实现状态：22 个 API 端点已全部实现并通过测试。

# API 接口 - 管理后台 (API_管理后台)

## 1. 管理员审计 (Internal Only)
- **Endpoint**: `GET /admin/v1/audit-logs`
- **参数**: `admin_id`, `action_type`, `time_range`

## 2. 内容审核
- **资源审核**: `PATCH /admin/v1/resources/{id}/status` (APPROVED/BLOCKED)
- **用户封禁**: `PATCH /admin/v1/users/{id}/status` (LOCKED/BANNED)

## 3. 权限控制与审计要求
- **RBAC**: 所有接口添加 `RoleChecker(role=["SUPER_ADMIN"])` 依赖保护。
- **审计**: 每次写操作强制触发 `admin_audit_logs` 的 Hash Chaining 写入逻辑。
- **IP 子网隔离（Admin Subnet Binding）**: 在 **API Gateway 层**（Nginx/Envoy）执行 `admin_subnet` 检查，请求头携带 `X-Forwarded-For` 或由网关透传的真实 IP，经 `ipaddress` 模块匹配 CIDR 子网列表。非匹配请求直接返回 403，不再路由至后端服务。

## 4. 全局参数配置
- **Endpoint**: `PATCH /admin/v1/system-configs`
- **参数**: `config_key`, `config_value`

## 5. 意见反馈处理
- **回复反馈**: `POST /admin/v1/feedbacks/{id}/reply`
  - 核心逻辑：工单状态同步置为 `RESOLVED`，绑定处理人ID，触发给用户的下行消息通知。

## 6. 扩容包管理
- **查询套餐列表**: `GET /admin/v1/asset-packages`
- **更新套餐价格/折扣率**: `PATCH /admin/v1/asset-packages/{id}`
  - `price_beans`: 特惠包有效范围 1~10000（默认 80）；畅享包有效范围 1~100000（默认 350）
  - `discount_rate`: 折扣率（特惠包默认 0.85；畅享包默认 0.70）
- **约束**: 价格修改后不影响已售出套餐，只对新购用户生效；历史订单不做追溯。

---
- [x] 对齐 PRD §5.0 管理后台核心功能。
- [x] 安全策略：所有路径受 `admin_subnet` 检查。

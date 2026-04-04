# 数据库设计 - 审计与管理员 (DB_管理员)

## 1. `admin_users` 表

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | UUID | 管理员 ID | PK |
| `username` | String | 登录名 | Unique |
| `password_hash` | String | 加密后的密码 | - |
| `role` | Enum | SUPER_ADMIN / OPERATOR / AUDITOR | - |
| `allowed_subnet` | JSONB | 对齐 users.admin_subnet | - |
| `last_login_at` | Timestamp | - | - |
| `is_active` | Boolean | 是否启用 | Default: True |

## 2. `admin_audit_logs` 表 (操作审计)

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | UUID | 记录 ID | PK |
| `admin_id` | UUID | 执行人 | FK -> admin_users.id |
| `action` | String | 动作 (如 DELETE_RESOURCE, BAN_USER) | Index |
| `target_type` | String | 目标对象类型 (users / resources / topics) | - |
| `target_id` | UUID | 目标对象 ID | - |
| `before_data` | JSONB | 变更前数据快照 | - |
| `after_data` | JSONB | 变更后数据快照 | - |
| `ip_address` | String | 操作人 IP | - |
| `prev_log_hash` | String | 上一条日志的哈希值 (Hash Chaining) | Not Null |
| `log_hash` | String | 本条日志的哈希值 | Not Null, Unique |
| `created_at` | Timestamp | 操作时间 | Index |

---
- [x] 对齐 PRD §5.5 管理后台安全：操作留痕与审计。
- [x] RBAC 权限角色支持。

# 数据库设计 - 通知系统 (DB_通知)

## 1. `notifications` 表

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | UUID | 通知 ID | PK |
| `receiver_id` | UUID | 接收者 | FK -> users.id, Index |
| `sender_id` | UUID | 发送者 (用户或系统) | FK -> users.id |
| `type` | Enum | SYSTEM / INTERACTION / AUDIT / REWARD / BROADCAST | Index |
| `priority` | Enum | NORMAL / HIGH | Default: NORMAL |
| `is_broadcast_exemption` | Boolean | 是否豁免 DND 免打扰 (广播类默认为 True) | Default: False |
| `title` | String | 简短标题 | - |
| `content` | Text | 详细内容 (支持模板变量) | - |
| `link_url` | String | 点击跳转地址 (如 /resources/xxx) | - |
| `is_read` | Boolean | 是否已读 | Default: False |
| `read_at` | Timestamp | 阅读时间 | - |
| `created_at` | Timestamp | 发送时间 | Index |

## 2. `notification_templates` 表 (可选)
- 存储各类预设通知的文案模板。

---
- [x] 对齐 PRD §5.0 通知系统：四类通知 (系统/互动/审核/奖励)。
- [x] 持久化与已读回执支持。

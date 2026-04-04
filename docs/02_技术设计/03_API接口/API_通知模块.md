# API 接口 - 通知模块 (API_通知模块)

## 1. 通知中心
### 1.1 分类通知列表
- **Endpoint**: `GET /api/v1/notifications`
- **参数**: `type` (SYSTEM/INTERACTION/AUDIT), `is_read` (可选)

### 1.2 标记已读
- **Endpoint**: `PATCH /api/v1/notifications/{id}/read`
- **全部标记已读**: `POST /api/v1/notifications/read-all`

### 1.3 获取未读计数
- **Endpoint**: `GET /api/v1/notifications/unread-count`

---
- [x] 对齐 PRD §5.0 通知实时性要求。
- [x] 对应 `DB_通知.md` 数据结构。

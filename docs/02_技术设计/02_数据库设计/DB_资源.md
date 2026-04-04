# 数据库设计 - 资源模块 (DB_资源)

## 1. `resources` 表 (资源主表)

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | UUID | 资源 ID | PK |
| `uploader_id` | UUID | 上传者 | FK -> users.id, Index |
| `title` | String | 资源标题 (≤100字) | Not Null, Index |
| `description` | Text | 资源描述 | - |
| `category_id` | Integer | 分类 ID | FK -> categories.id |
| `tags` | JSONB | 标签列表 (如 ["可靠性", "HALT"]) | - |
| `price` | Integer | 定价 (可可豆数) | Default: 5, Range: 5 - 100,000 |
| `file_uuid` | UUID | 关联文件元数据 | FK -> file_meta.file_uuid |
| `view_count` | Integer | 浏览量 | Default: 0 |
| `download_count` | Integer | 下载量 | Default: 0 |
| `like_count` | Integer | 点赞量 | Default: 0 |
| `dislike_count` | Integer | 点踩量 | Default: 0 |
| `heat_score` | Float | 热度分 (由异步任务计算) | Index |
| `is_seed` | Boolean | 是否为基础资源 (管理员标记，权益额度内免费) | Default: False |
| `status` | Enum | SCANNING / PENDING_REVIEW / APPROVED / REJECTED / APPEALING / BLOCKED | Default: 'SCANNING' |
| `anonymized_user_hash` | VARCHAR(64) | 匿名化关联哈希。由 HMAC-SHA256(original_user_id, salt) 生成，仅在用户注销时写入，用于关联同一匿名实体的资产。 | Index |
| `is_deleted` | Boolean | 逻辑删除 | Default: False |
| `created_at` | Timestamp | 上传时间 | Index |
| `updated_at` | Timestamp | 更新时间 | - |

## 2. `resource_previews` 表 (预览图/片段)
- 存储资源的预览图地址或 PDF 前 N 页的路径。

## 3. `resource_collections` 表 (收藏夹记录)
- `user_id`, `resource_id`, `created_at`。

---
- [x] 对齐 PRD §3.1 资源上传：支持分类、标签、定价。
- [x] 对齐 PRD §4.2 搜索热度：`heat_score` 字段准备。
- [x] 对齐 PRD 人工审核流转：扩充 `status` 以支持 `PENDING_REVIEW / REJECTED / APPEALING`。

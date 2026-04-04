# 数据库设计 - 社区模块 (DB_社区)

## 1. `topics` 表 (话题主表)

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | UUID | 话题 ID | PK |
| `author_id` | UUID | 发布者 | FK -> users.id, Index |
| `title` | String | 标题 | Not Null |
| `content` | Text | 正文 (支持 Markdown) | - |
| `category_id` | Integer | 板块 ID | - |
| `bounty_amount` | Integer | 悬赏可可豆数 | Default: 0 |
| `bounty_status` | Enum | NONE / ACTIVE / RESOLVED / REFUNDED | Default: 'NONE' |
| `accepted_post_id` | UUID | 采纳的回复 ID | FK -> posts.id |
| `status` | Enum | NORMAL / BLOCKED / PENDING | Default: 'NORMAL' |
| `view_count` | Integer | 浏览数 | - |
| `post_count` | Integer | 回复数 | - |
| `heat_score` | Float | 话题热度 | Index |
| `is_deleted` | Boolean | 逻辑删除 | Default: False |
| `anonymized_user_hash` | VARCHAR(64) | **匿名化关联哈希**。由 `HMAC-SHA256(original_user_id, salt)` 生成，仅在用户注销时写入，用于关联同一匿名实体的话题。 | Index |
| `created_at` | Timestamp | 发布时间 | Index |

## 2. `posts` 表 (回复/跟帖表)

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | UUID | 回复 ID | PK |
| `topic_id` | UUID | 所属话题 | FK -> topics.id, Index |
| `author_id` | UUID | 回复人 | FK -> users.id |
| `content` | Text | 回复内容 | - |
| `parent_id` | UUID | 父回复 ID (支持二级评论) | FK -> posts.id |
| `is_accepted` | Boolean | 是否被采纳 | Default: False |
| `anonymized_user_hash` | VARCHAR(64) | **匿名化关联哈希**。由 `HMAC-SHA256(original_user_id, salt)` 生成，仅在用户注销时写入，用于关联同一匿名实体的回复。 | Index |
| `like_count` | Integer | 点赞数 | - |
| `created_at` | Timestamp | 回复时间 | - |

---
- [x] 对齐 PRD §3.2 社区功能：悬赏、采纳、二级回复。
- [x] 对齐 PRD §5.5.3 自动退费：`bounty_status` 状态链路支持。

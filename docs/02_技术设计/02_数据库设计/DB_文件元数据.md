# 数据库设计 - 文件元数据 (DB_files)
 
 ## 1. `file_meta` 表
 
 | 字段名 | 类型 | 说明 | 约束 |
 |-------|------|------|-----|
 | `file_uuid` | UUID | 业务唯一标识 | PK |
 | `file_hash` | String | 全量 MD5 值 (用于秒传) | Unique, Index |
 | `oss_path` | String | 物理存储路径 | Not Null |
 | `file_name` | String | 原始文件名 | - |
 | `file_size` | Long | 文件大小 (Bytes) | - |
 | `mime_type` | String | MIME 类型 | - |
 | `ref_counts` | Integer | 全局引用计数 | Default: 1 |
 | `status` | Enum | NORMAL / SCANNING / ISOLATED / SUSPICIOUS / BLOCKED / DELETED | Index |
 | `lifecycle_status` | Enum | ACTIVE / SOFT_DELETED / PERMANENTLY_DELETED | Index |
 | `uploader_uid` | UUID | 首位上传者 ID | FK -> users.id |
 | `created_at` | Timestamp | 创建时间 | - |
 | `updated_at` | Timestamp | 更新时间 | - |
 
 ## 2. `file_usage` 表 (引用关系表)
 
 | 字段名 | 类型 | 说明 | 约束 |
 |-------|------|------|-----|
 | `id` | UUID | ID | PK |
 | `file_uuid` | UUID | 文件 ID | FK -> file_meta.file_uuid |
 | `target_id` | UUID | 引用目标 (Conversation/Resource/Topic) | Index |
 | `target_type` | Enum | CONVERSATION / RESOURCE / TOPIC | - |
 | `user_id` | UUID | 当前引用用户 | - |
 | `created_at` | Timestamp | 引用时间 | - |
 
 ---
 
 ## 核心逻辑设计 (Self-Audit)
 
 ### **双状态映射准则** (对齐文件规范 §9.0)
 - 当 `lifecycle_status` 为 `SOFT_DELETED` 或 `PERMANENTLY_DELETED` 时，`status` 必须强制同步为 `DELETED`。
 - 当 `lifecycle_status` 为 `ACTIVE` 时，`status` 才允许在 `NORMAL / SCANNING / ISOLATED / SUSPICIOUS / BLOCKED` 之间流转。
 
 ### **重复上传查重与封禁逻辑** (对齐管理后台 PRD §5.4.3 & 资源模块 PRD)
 - **API 层预校验（入口硬拦截）**：资源上传 API 在执行业务逻辑前，必须先查询 Redis `dup_upload_count:{uploader_uid}`。若值 ≥ 3，直接返回 `403 Forbidden`，响应体 `{"code": 403, "msg": "检测到重复上传行为，账号已临时限制上传7天"}`，不再进入文件处理流程。
 - **查重触发**: 资源上传时，AI 提取 Embedding 并执行 `cosine_similarity` 检索，相似度 > 80% 标记 `SUSPICIOUS_DUPLICATE`。
 - **计数机制**: 在 Redis 中以 `uploader_uid` 为 Key 维护计数器 `dup_upload_count`，TTL = 7 天，每次命中 `SUSPICIOUS_DUPLICATE` 时原子 +1。
 - **封禁触发**: 当 `dup_upload_count ≥ 3` 时，自动将用户 `status` 置为 `受限/禁用`，并发送站内通知。封禁时长 7 天（可配置），期间用户无法发起资源上传。
 - **解封**: 封禁到期后 Redis Key 自动过期，系统自动恢复上传权限（仅解封，不清除信誉分扣罚记录）。

 ### **秒传与粉碎逻辑**
 - **秒传**: 上传命中 Hash 时，仅在 `file_usage` 增加记录并对 `file_meta.ref_counts` 执行原子 +1。
 - **物理粉碎**: `lifecycle_status` 设为 `PERMANENTLY_DELETED`，触发审计。Worker 检测到 `ref_counts` 归零才执行 OSS 物理删除。

 ### **引用计数扣减触发机制** (文件生命周期联动)
 - **触发场景**: 当 `file_usage` 记录被删除时（用户删除对话/资源/话题），应用层在删除事务中同步执行 `file_meta.ref_counts - 1`（原子操作）。
 - **实现方式**: 在 Service 层 `FileUsageService.delete()` 方法中，删除 `file_usage` 记录后立即执行 `UPDATE file_meta SET ref_counts = ref_counts - 1 WHERE file_uuid = ?`，并以 `ref_counts = 0` 为触发条件发送 Celery 任务 `celery_tasks.physical_file_delete` 执行 OSS 物理删除。
 - **安全约束**: `ref_counts` 最低值为 0，不允许出现负数（数据库层 CHECK 约束 `ref_counts >= 0`）。

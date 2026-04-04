# 数据库设计 - AI 对话与配置 (DB_ai对话)
 
 ## 1. `ai_sessions` 表 (会话主表)
 
 | 字段名 | 类型 | 说明 | 约束 |
 |-------|------|------|-----|
 | `id` | UUID | 会话 ID | PK |
 | `user_id` | UUID | 所属用户 | FK -> users.id, Index |
 | `title` | String | 会话标题 | Default: '新会话' |
 | `system_prompt_version` | String | 采用的 Prompt 版本 (创建时快照，不可更改) | Linking to config |
 | `is_guest` | Boolean | 是否为游客对话 | - |
 | `round_count` | Integer | 当前轮次计数 (用于限额校验) | Default: 0 |
 | `total_file_size_mb` | Float | 本会话附件总大小 | Default: 0.0 |
 | `total_tokens` | Integer | 累计消耗 Token (用于成本统计) | Default: 0 |
 | `is_deleted` | Boolean | 逻辑删除 | Default: False |
 | `risk_level` | Enum | NORMAL / SUSPICIOUS / BLOCKED | 用于 AI 风控拦截 |
 | `created_at` | Timestamp | 创建时间 | Index |
 | `updated_at` | Timestamp | 最后活动时间 | Index |
 
 ## 2. `ai_messages` 表 (消息明细)
 
 | 字段名 | 类型 | 说明 | 约束 |
 |-------|------|------|-----|
 | `id` | UUID | 消息 ID | PK |
 | `session_id` | UUID | 所属会话 | FK -> ai_sessions.id, Index |
 | `role` | Enum | system / user / assistant | - |
 | `content` | Text | 消息正文 | - |
 | `attachment_ids` | JSONB | 关联的附件 UUID 列表 | - |
 | `metadata` | JSONB | 模型名称、耗时、Token 计算等 | - |
 | `created_at` | Timestamp | 发送时间 | - |
 
 ## 3. `ai_config` 表 (系统 Prompt 管理)
 
 | 字段名 | 类型 | 说明 | 约束 |
 |-------|------|------|-----|
 | `version` | String | 版本号 (如 v1.1.0) | PK |
 | `previous_version` | String | 前一版本号 (用于回滚追溯) | - |
 | `prompt_content` | Text | System Prompt 正文 | - |
 | `is_active` | Boolean | 是否当前生效 | Index |
 | `rollout_percentage` | Integer | 灰度比例 (0-100) | Default: 100 |
 | `effective_from` | Timestamp | 计划生效时间 | - |
 | `author` | String | 修订人 | - |
 | `created_at` | Timestamp | 创建记录时间 | - |
 
 ---
 
 ## 核心逻辑设计 (Self-Audit)
 
 ### **游客模式限额控制** (对齐 PRD §1.2.1)
 - 游客访问时，基于请求 IP 或 Device Fingerprint 在 Redis 中维护一个 `guest_session_counter`。
 - 每日 0 点自动过期重置。
 - 持久化：虽然是游客，但 `ai_sessions` 依然存入 DB (`is_guest=true`)，以便退出前引导注册。
 
 ### **AI 风控分级处理 (对齐社区/资源 PRD)**
 - **NORMAL**: 正常展示。
 - **SUSPICIOUS**: 命中可疑语义，允许提交但在前端展示“审核中”，落库 M5 审核队列。
 - **BLOCKED**: 命中黑名单，直接阻断提交。
 
 - [x] 对齐 §4.1.4 身份定义：通过 `ai_config` 统一 ReliBot 角色。
 - [x] 对齐 §3.4.2 历史保存：`ai_sessions` 使用 `updated_at` 排序支持列表查询。
 - [x] **版本管理优化**：补齐了 `previous_version` 与 `rollout_percentage` 灰度字段，支持安全回撤。

# 数据库设计 - 表结构汇总
 
 ## 1. 核心设计原则
 - **主键**: 统一使用 `UUID`，确保分布式环境下的唯一性与安全性（如盲索引支持）。不推荐自增自增 ID。
 - **软删除**: 使用 `is_deleted` (Boolean) 或 `deleted_at` (Timestamp) 处理逻辑删除。
 - **时间戳**: 所有表必须包含 `created_at` 和 `updated_at`。
 - **命名规范**: 采用 `snake_case` (如 `user_id`, `session_title`)。
 
 ## 2. 核心实体表 (MVP 概览)
 
 ### 2.1 用户与权限 (Users & Auth)
 - `users`: 存储用户核心信息（昵称、头像、等级、信誉分、可可豆余额）。
 - `admin_users`: 存储管理员账号、角色与权限位。
 
 ### 2.2 AI 对话 (AI Conversations)
 - `ai_sessions`: 对话会话表（会话标题、模型类型、System Prompt 版本）。
 - `ai_messages`: 对话消息明细（Role: user/assistant/system, Content, Token 消耗）。
 
 ### 2.3 资源与文件 (Resources & Files)
 - `resources`: 资源主表（标题、分类、标签、定价、审核状态）。
 - `file_meta`: 文件记录表 (对象存储 Key、MIME、大小、指纹 Hash)。
 
 ### 2.4 社区与互动 (Community)
 - `topics`: 话题主表。
 - `posts`: 话题下帖子或回复。
 
 ### 2.5 可可豆与资产 (Economy)
 - `point_ledger`: 可可豆流转日志 (对齐 DB_可可豆.md)。
 - `asset_orders`: 扩充包购买订单记录。
 
 ### 2.6 系统与合规 (System)
 - `audit_logs`: 管理员操作审计日志（操作人、操作动作、变更前后值）。
 - `feedbacks`: 用户意见反馈工单表。
 
 ---
 
 ## 3. 变更管理 (Migrations)
- **工具**: 采用 **Alembic** 执行增量表结构变动。
- **流程**: 
  1. 修改模块 TDD 对应的 DB 文件。
  2. 执行 `alembic revision --autogenerate`。
  3. 执行 `alembic upgrade head` 并同步至镜像库。
 
 ## 4. 实体关系图 (ER Diagram)
 
 ```mermaid
 erDiagram
     USERS ||--o{ POINT_LEDGER : "has"
     USERS ||--o{ REPUTATION_LOGS : "earns"
     USERS ||--o{ AI_SESSIONS : "starts"
     USERS ||--o{ ASSET_ORDERS : "purchases"
     AI_SESSIONS ||--o{ AI_MESSAGES : "contains"
     AI_CONFIG ||--o{ AI_SESSIONS : "powers"
     FILES ||--o{ ASSET_ORDERS : "referenced_by"
 ```

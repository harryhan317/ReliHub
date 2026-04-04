# 数据库设计 - 用户相关表 (DB_users)
 
 ## 1. `users` 表 (核心表)

 | 字段名 | 类型 | 说明 | 约束 |
 |-------|------|------|-----|
 | `id` | UUID | 用户唯一 ID | PK |
 | `wechat_openid` | String | 微信 OpenID | Unique, Index |
 | `phone` | String | 手机号（AES-256-CBC 加密存储） | — |
 | `phone_blind_index` | String | 手机号盲索引（HMAC-SHA256(phone, key) 取前 16 字节 hex，用于唯一约束与登录查询） | Unique, Index |
 | `nickname` | String | 昵称 | Not Null |
 | `avatar_url` | String | 头像地址 | - |
 | `rank` | Enum | 用户等级及信誉分范围: 新兵(0-99)/菜鸟(100-299)/入门(300-599)/熟手(600-999)/老炮(1000-1999)/达人(2000-4999)/专家(≥5000) | Default: '新兵' |
 | `reputation_points` | Integer | 信誉分（完成注册初始化50分） | Default: 50 |
 | `is_reward_triggered` | Boolean | 首次有效动作奖励触发标记 (用于邀请奖励/拉新判定) | Default: False |
 | `reputation_status` | Enum | 信誉状态 (NORMAL / BUFFER) | Default: 'NORMAL' |
 | `invite_code` | String | 自己的邀请码 | Unique, Index |
 | `referrer_id` | UUID | 邀请人 ID (由谁邀请)。若为 NULL 标识正常注册；非 NULL 时关联邀请人的 user_id。 | FK -> users.id |
 | `gold_beans` | Integer | 资产豆余额 (可取现) | Default: 0 |
 | `bonus_beans` | Integer | 福利豆余额 (不可取现) | Default: 0 |
 | `admin_subnet` | JSONB | 允许登录的子网掩码列表 (支持多段，如 ["192.168.1.0/24", "10.0.0.0/8"])，MVP 阶段默认 ["0.0.0.0/0"] 表示不限制 | Default: '["0.0.0.0/0"]' |
 | `notification_config` | JSONB | 通知与免打扰配置 (含 dnd_mode) | Default: '{}' |
 | `daily_token_usage` | Integer | 今日已消耗 Token (每日 0 点重置) | Default: 0 |
 | `total_ai_storage_mb` | Float | 累计已使用的会话附件容量 | Default: 0.0 |
 | `is_expert` | Boolean | 是否是专家 | Default: False |
 | `status` | Enum | 状态 (ACTIVE:活跃 / HIBERNATED:休眠 / LOCKED:资产冻结 / DISABLED:全限封禁) | Default: 'ACTIVE' |
 | `created_at` | Timestamp | 注册时间 | - |
 | `last_login_at` | Timestamp | 最后登录时间 | - |
 
 ## 2. `reputation_logs` 表 (信誉分流水)
 
 | 字段名 | 类型 | 说明 | 约束 |
 |-------|------|------|-----|
 | `id` | UUID | 流水 ID | PK |
 | `user_id` | UUID | 关联用户 | FK -> users.id, Index |
 | `change_value` | Integer | 变动值 (可正可负) | - |
 | `action_type` | Enum | SIGN_IN / CONTENT_TOPIC / CONTENT_POST / CONTENT_ADOPTED / ELITE_TOPIC / INVITE / VIOLATION / BUFFER_WARNING / DEMOTION / HIBERNATION_PENALTY | Index |
 | `reason` | String | 变动原因描述 | - |
 | `related_id` | UUID | 关联业务 ID | - |
 | `created_at` | Timestamp | 时间 | Index |
 
 ## 3. `expert_profiles` 表 (专家详细信息)
 
 | 字段名 | 类型 | 说明 | 约束 |
 |-------|------|------|-----|
 | `id` | UUID | 主键 | PK |
 | `user_id` | UUID | 关联用户 | FK -> users.id, Unique |
 | `real_name` | String | 真实姓名 | Not Null |
 | `professional_domain` | String | 专业领域 | - |
 | `bio` | String | 个人简介（≤500字） | - |
 | `consulting_config` | JSONB | 咨询服务配置 | - |
 | `audit_status` | Enum | PENDING / APPROVED / REJECTED / FROZEN | Default: 'PENDING' |
 | `submitted_at` | Timestamp | 申请提交时间 | - |
 | `reviewed_at` | Timestamp | 审核时间 | - |
 | `reviewed_by` | UUID | 审核管理员 ID | - |
 
 ---
 
 ## 对齐校验 (Self-Audit)
 - [x] 对应 PRD §3.7 注册送 30 可可豆：通过 `point_ledger` 初始化触发。
 - [x] 对应 PRD §4.4.3 休眠账号：`status` 字段支持 'HIBERNATED' 标记。
 - [x] **邀请人逻辑**：`referrer_id` 为空标识无邀请，不触发 `INVITE_REWARD`。

 ### **信誉分降级缓冲逻辑** (对齐 PRD §4.1 & 管理后台 §5.7)
 - **等级体系**：用户等级由信誉分决定，信誉分范围下限 × 缓冲系数（默认 0.8）决定降级触发阈值。
 - **降级阈值公式**：`demotion_threshold = floor(rank_min * buffer_coefficient)`（默认 buffer_coefficient = 0.8）。
 - **降级阶段**：
   1. **缓冲期预警**：信誉分跌破当前等级范围下限时，系统发出缓冲期预警通知（`reputation_logs.action_type = BUFFER_WARNING`）。
   2. **降级触发**：信誉分继续下跌至 `demotion_threshold` 时，立即执行降级，`rank` 字段下调一级，`reputation_logs.action_type = DEMOTION`。
 - **新兵保级**：新兵等级（信誉分 0~49）无降级阈值，降无可降。
 - **升级逻辑**：仅由系统根据信誉分自动判断，不存在人工降级后手动升级通道。

 ### **邀请奖励触发边界** (对齐管理后台 PRD §5.4.6)
 - `referrer_id` 非 NULL 时，通过 `reputation_logs.action_type = INVITE` 记录邀请人奖励。
 - 有效操作包括：首次AI问答会话（无需审核）、首次资源上传（审核通过）、首次社区话题发布（审核通过）。

 ### **信誉分恢复机制** (对齐 PRD §5.2.2)
 - **每日签到奖励**：用户每日首次签到，固定获得信誉分 +1（`reputation_logs.action_type = SIGN_IN`，`change_value = +1`），由 `DB_可可豆.md` 的签到奖励入账逻辑驱动写入。
 - **连续签到奖励**：用户连续签到 7 天，第 7 天额外奖励信誉分 +1（`action_type = SIGN_IN`，`change_value = +1`），同时重置连续签到计数器。
 - **内容采纳奖励**：社区话题/回复被管理员或发起人采纳为最佳答案时，奖励信誉分 +30（`action_type = CONTENT_ADOPTED`，`change_value = +30`），由采纳动作触发写入。
 - **话题发起奖励**：社区发起话题（通过审核），奖励信誉分 +10（`action_type = CONTENT_TOPIC`，`change_value = +10`），由话题发布成功触发写入。
 - **回复奖励**：社区回复话题（通过敏感词过滤），奖励信誉分 +5（`action_type = CONTENT_POST`，`change_value = +5`），每日上限 10 次（由 Redis Key `post_reward:{user_id}:{date}` TTL 控制）。
 - **精华话题奖励**：M5 管理员标记话题为"精华"时，额外奖励信誉分 +10（`action_type = ELITE_TOPIC`，`change_value = +10`），由管理员标记动作触发写入。
 - **精华资源奖励**：M5 管理员标记资源为"精华"时，额外奖励信誉分 +20（`action_type = ELITE_RESOURCE`，`change_value = +20`，分值范围 5-30 可配置），由管理员标记动作触发写入。
 - **连续签到计数器**：Redis Key `streak:{user_id}`，每次签到成功 +1，连续中断时重置为 0。
 - **信誉分范围约束**：信誉分不可为负（硬底线为 0），但不设固定最高上限（如 `专家` 等级需信誉分 ≥5000，且可长期累积成长）。
 - **休眠账号保护**：账号连续 6 个月未登录，标记为 `HIBERNATED`（由后台定时任务 `UserStatusResetTask` 执行）。连续 **2 年** 未登录且无余额资产，则触发 `AccountCleanupTask` 执行逻辑注销（设置 `is_deleted = true`，并对用户信息脱敏）。

### **数据安全与 PII 保护** (对齐 PRD §7.1)
- **加密存储**: `phone`, `email` 等敏感字段在数据库中采用 AES-256-CBC 加密存储。
- **Blind Index 索引方案**: 为解决加密字段无法直接建立唯一索引的问题，采用 HMAC-SHA256 生成盲索引（`phone_blind_index = HMAC-SHA256(phone, key)[:8]`，取前 8 字节 hex），用于唯一约束与登录查询。密钥（key）独立存储于 KMS，不得与数据库同实例。
- **脱敏显示**: 前端接口返回时，对敏感信息执行脱敏处理（如手机号 `138****0000`）。
- **哈希保护**: `password_hash` 使用 Argon2id 算法，并采用随机盐值。
- **地理位置隐私**: `last_login_ip` 仅用于异地登录检测，系统仅记录地理归属地快照，不保留原始 IP 的长期可回溯明细。

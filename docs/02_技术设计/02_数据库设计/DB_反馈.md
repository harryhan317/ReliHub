# 数据库设计 - 意见反馈模块 (DB_反馈)

## 1. `feedbacks` 表 (意见反馈工单表)

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | UUID | **技术主键**。后端关联、详情查询唯一标识。 | PK |
| `business_id` | VARCHAR(32) | **业务单号**。格式：`FB + YYYYMMDD + 6位流水`，用于展示与追溯。 | Unique, Index |
| `user_id` | UUID | 提交人唯一标识。 | FK -> users.id, Index |
| `type` | TINYINT | 类型枚举：1:功能异常, 2:体验建议, 3:内容纠错, 4:其他。 | - |
| `reference_id` | UUID | 关联的内容 ID (资源/话题/会话)。 | Index |
| `reference_type` | TINYINT | 关联业务类型：1:资源, 2:话题, 3:会话。 | - |
| `content_body` | TEXT | 反馈意见正文 (10~1000 字符)。 | - |
| `contact_info` | VARCHAR(255) | 选填联系方式 (手机/邮箱)。**查询需支持脱敏逻辑**。 | - |
| `attachments_urls` | JSONB | 附件图片 URL 数组 (单张文件 <= 5MB，最多 3 张)。 | - |
| `status` | Enum | 状态机：`PENDING`, `PROCESSING`, `RESOLVED`, `REJECTED`。 | Index, Default: PENDING |
| `handler_id` | UUID | 处理该工单的管理员 ID。 | FK -> users.id |
| `reply_content` | TEXT | 管理员回复内容 (结单必填)。 | - |
| `anonymized_user_hash` | VARCHAR(64) | **匿名化关联哈希**。由 `HMAC-SHA256(original_user_id, salt)` 生成，仅在用户注销时写入，用于关联同一匿名实体的历史反馈。 | Index |
| `evaluation_score` | TINYINT | 用户满意度评分：1:满意, 2:不满意。 | - |
| `evaluation_body` | VARCHAR(100) | 提交满意度时的评价文案。 | - |
| `evaluation_at` | TIMESTAMP | 用户评价操作时间。 | - |
| `created_at` | TIMESTAMP | 工单提交时间。 | Index, Default: NOW() |
| `resolved_at` | TIMESTAMP | 结单关单时间。 | - |

---

## 2. 深度审计一致性约束 (对齐 PRD §5.0)

### 2.1 注销与数据存留
- **匿名化逻辑**：若用户执行注销（主动或被动），触发以下操作：
    - `user_id` 物理重置为 `00000000-0000-0000-0000-000000000000` (匿名账户标识)。
    - **生成并写入 `anonymized_user_hash`**：确保管理员能识别该注销实体的反馈聚集性。
    - `contact_info` 字段**物理清除**（明文置 NULL）。
    - 反馈记录、评价及处理报告**永久存留**，用于系统审计。

### 2.2 状态机锁定
- 一旦 `status` 进入 `PROCESSING`，系统需记录 `handler_id`，防止其他管理员操作。
- 状态从 `PENDING` 到 `RESOLVED/REJECTED` 的流转周期入库监测，由运营报表导出判断 48h SLA。

---
- [x] 对齐 PRD §5.0 意见反馈核心需求。
- [x] 支持双 ID（UUID PK + FB 业务码）。
- [x] 符合全量数据匿名预警规则。

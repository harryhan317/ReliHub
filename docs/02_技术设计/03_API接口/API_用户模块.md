# API 接口 - 用户模块

## 1. 模块概述
处理用户注册、登录、签到、专家申请等核心用户生命周期接口。

## 2. 接口列表

### 2.1 用户签到
- **Endpoint**: `POST /api/v1/user/checkin`
- **认证**: JWT Bearer Token
- **请求参数**: 无
- **响应**:
  ```json
  {
    "code": 0,
    "data": {
      "beans_awarded": 2,
      "point_type": "BONUS_BEAN",
      "order_type": "SIGN_IN",
      "signin_days": 3,
      "reputation_awarded": 1,
      "is_reward_triggered": false,
      "msg": "签到成功"
    }
  }
  ```
- **业务规则**:
  - 每日首次签到有效（Redis Key: `sign_in:{user_id}:{date}`，TTL = 48h）。
  - 每日首次签到奖励 2 福利豆 + 1 信誉分。
  - 连续签到 7 天，第 7 天**额外**奖励信誉分 +1（即当日共 +2 信誉分）。

### 2.2 获取签到状态
- **Endpoint**: `GET /api/v1/user/checkin/status`
- **认证**: JWT Bearer Token
- **响应**:
  ```json
  {
    "code": 0,
    "data": {
      "signed_today": true,
      "signin_streak": 3,
      "last_signin_date": "2026-03-29"
    }
  }
  ```

### 2.3 专家申请
- **Endpoint**: `POST /api/v1/user/expert/apply`
- **认证**: JWT Bearer Token
- **请求参数**:
  - `real_name`: 真实姓名
  - `professional_domain`: 专业领域（字符串）
  - `bio`: 个人简介（500字以内）
  - `consulting_config`: 咨询服务配置（JSON，可选）
- **响应**:
  ```json
  { "code": 0, "msg": "申请已提交，请等待管理员审核" }
  ```
- **业务规则**:
  - 用户 `is_expert = false` 且 **信誉分 ≥ 5000** 时方可提交申请 (对齐 PRD_可可豆与信誉分体系 §4.1.2)。
  - 申请提交后写入 `expert_profiles` 表，`audit_status = PENDING`。
  - 不自动变更 `users.is_expert` 状态，待审核通过后由管理员操作。

### 2.4 查询专家申请状态
- **Endpoint**: `GET /api/v1/user/expert/application`
- **认证**: JWT Bearer Token
- **响应**:
  ```json
  {
    "code": 0,
    "data": {
      "audit_status": "PENDING",
      "submitted_at": "2026-03-29T10:00:00Z"
    }
  }
  ```

### 2.5 信誉分记录查询
- **Endpoint**: `GET /api/v1/user/reputation/logs`
- **认证**: JWT Bearer Token
- **参数**: `page`, `page_size`
- **响应**:
  ```json
  {
    "code": 0,
    "data": {
      "total": 25,
      "logs": [
        {
          "action_type": "SIGN_IN",
          "change_value": 1,
          "reason": "每日首次签到奖励信誉分",
          "created_at": "2026-03-29T08:00:00Z"
        },
        {
          "action_type": "BUFFER_WARNING",
          "change_value": 0,
          "reason": "信誉分进入缓冲期预警",
          "created_at": "2026-03-20T00:00:00Z"
        }
      ]
    }
  }
  ```
- **参数**: `page`, `page_size`
- **响应**: 同上文信誉分记录响应结构。

### 2.6 获取个人资料 (Profile)
- **Endpoint**: `GET /api/v1/user/profile`
- **认证**: JWT Bearer Token
- **响应**:
  ```json
  {
    "code": 0,
    "data": {
      "id": "uuid",
      "nickname": "Reli爱好者",
      "avatar_url": "url",
      "rank": "菜鸟",
      "reputation_points": 125,
      "gold_beans": 10,
      "bonus_beans": 40,
      "is_expert": false,
      "is_reward_triggered": false,
      "ai_quota": {
        "sessions_remaining": 5,
        "tokens_remaining": 15000
      }
    }
  }
  ```
- **逻辑**: 返回用户核心资产与权益标记位快照，`is_reward_triggered` 用于前端引导。

### 2.7 账号注销 (Deactivate)
- **Endpoint**: `POST /api/v1/user/deactivate`
- **认证**: JWT Bearer Token
- **响应**:
  ```json
  { "code": 0, "msg": "账号注销申请已成功受理" }
  ```
- **业务规则**:
  - 软删除标记：将 `users.is_deleted` 置为 `true`。
  - 数据物理脱敏：`phone_blind_index` 等 PII 数据进行物理清除/清零重置。
  - 匿名化隔离：更新历史反馈等产生的游离数据，`user_id` 重置为匿名 UUID 且注入 `anonymized_user_hash`。
  - 前置校验：用户当前需无正在进行、挂起状态中的悬赏订单。

---

## 3. 专家申请状态机（审核链路）

| 状态 | 触发者 | 后续动作 |
|------|--------|---------|
| `PENDING` | 用户提交申请 | 进入管理员审核队列 |
| `APPROVED` | 管理员审核通过 | 将 `users.is_expert` 置为 `True`，`expert_profiles.audit_status` 同步更新 |
| `REJECTED` | 管理员审核拒绝 | `expert_profiles.audit_status` 置为 `REJECTED`，用户可重新提交 |
| `FROZEN` | 管理员操作 | 将 `users.is_expert` 临时置否，**但系统必须继续采信底层信誉分映射的达人/常客等基础身份与对应配额（如发帖、下载等）**，仅冻结专家专属标识与功能，保留 `expert_profiles` 记录以供申诉 |

- **管理员审核 API**（内部接口，不对用户暴露）：
  - `PATCH /admin/v1/expert/application/{user_id}`，参数：`action` = APPROVED / REJECTED / FROZEN。
  - 审核操作须写入 `admin_audit_logs` 表。

---

## 4. 信誉分恢复机制（对齐 PRD §5.2.2）

| 恢复动作 | 触发条件 | 恢复值 | 记录方式 |
|---------|---------|--------|---------|
| 每日签到奖励 | 用户每日首次签到 | 信誉分 +1 | `reputation_logs.action_type = SIGN_IN`, `change_value = +1` |
| 连续签到奖励 | 连续签到达到 7 天 | 额外信誉分 +1 | `reputation_logs.action_type = SIGN_IN`, `change_value = +1` |
| 违规扣分机制 | 违反社区规范扣除信誉分 | 幅度由 `VIOLATION` 枚举动态控制 (如 -20, -30, -50 等) | 扣分动作通过管理后台发起 |
| 休眠账号处理 | 账号 6 个月未登录 | 每月扣 5 分 | 状态变更为 `HIBERNATED`，由后台定时任务 `UserStatusResetTask` 驱动 |
| 被动注销逻辑 | 账号 2 年未登录 (且无余额) | 逻辑删除 (`is_deleted`) | 对齐 PRD §4.3.2，账号脱敏并物理删除文件 |

- **连续签到计数器**: Redis Key `streak:{user_id}`，连续中断时重置为 0。
- **信誉分范围**: 最低为 0（不可为负数），无最高上限。

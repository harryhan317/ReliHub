# 数据库设计 - 可可豆与经济系统 (DB_可可豆)
 
 ## 1. `point_ledger` 表 (复式记账流水)
 
 | 字段名 | 类型 | 说明 | 约束 |
 |-------|------|------|-----|
 | `id` | UUID | 交易记录 ID | PK |
 | `transaction_uuid` | UUID | 事务唯一标识 (聚合同一笔交易的多条记录，如下载扣费+分成+销毁) | Index |
 | `user_id` | UUID | 变动主体 | FK -> users.id |
 | `amount` | Integer | 变动额度 (支出为负，收入为正) | - |
 | `point_type` | Enum | GOLD_BEAN (资产豆) / BONUS_BEAN (福利豆) | Not Null |
 | `dist_ratio` | Float | 分配比例 (0.7 / 0.3 / 0.15 等，用于审计对账) | - |
 | `order_type` | Enum | 交易类型 (DOWNLOAD/DOWNLOAD_REVENUE/RECHARGE/SYSTEM_GIFT/SHARE_REWARD/DESTRUCTION/EARLYBIRD_REWARD/SIGN_IN/INVITE_REWARD/CONTENT_TOPIC/CONTENT_POST/CATEGORY_FIRST_POST_REWARD/CONTENT_ADOPTED/BOUNTY_LOCK/BOUNTY_RELEASE/BOUNTY_REFUND/FEEDBACK_AWARD) | Index |
 | `balance_after` | Integer | 变动后余额 (对账快照) | Not Null |
 | `related_id` | UUID | 关联业务 ID (资源 ID / 话题 ID / 订单 ID) | Index |
 | `description` | String | 交易描述 | - |
 | `created_at` | Timestamp | 交易时间 | Index |
 
 ### **order_type 语义说明 (对齐 PRD §2.1.2 / §2.2.2)**
 - **DOWNLOAD**: 资源下载产生的扣费。扣除下载者可可豆（优先扣除福利豆）。**对于用户消耗下载权益导致的“基础资源 0 元下载”场景，系统必须在此表生成一条 `amount = 0` 的凭证流水（用于防刷限流校验与后期额度核销审计）。**
 - **RECHARGE**: 用户通过充值获得的资产豆（`GOLD_BEAN`），`amount` 为正数。
 - **SYSTEM_GIFT**: 系统向用户发放的初始福利豆（如注册奖励 30 福利豆，`point_type = BONUS_BEAN`），`amount` 为正数。
 - **SHARE_REWARD**: 用户通过分享内容被有效点击后获得的奖励（**[!]** Phase 2 实现，MVP 阶段不生效）。
 - **DESTRUCTION**: 通缩账户记录。记录 70/30 分账中由系统自动销毁的 30% 部分（或折扣让利后的销毁量）。
 - **EARLYBIRD_REWARD**: 前 200 名注册用户的一次性 20 **福利豆**奖励（`point_type = BONUS_BEAN`）。注意：此项奖励与 `SYSTEM_GIFT`（基础注册送 30 豆）同步独立记账，前 200 名共得 50 福利豆。
 - **SIGN_IN**: 用户每日首次签到奖励，固定发放 2 福利豆（同步写入 `reputation_logs`，`action_type = SIGN_IN`，`change_value = +1`）。
 - **INVITE_REWARD**: 邀请者与被邀请者双向获得的各 10 福利豆奖励（被邀请人须完成有效操作）。
 - **CONTENT_TOPIC**: 用户在社区发起话题（通过敏感词过滤）后，获得 10 福利豆；同一用户在同一分类下**首次**发起话题，额外奖励 10 福利豆（`point_type = BONUS_BEAN`）。
 - **CONTENT_POST**: 用户在社区回复话题（通过敏感词过滤）后，获得 5 福利豆（`point_type = BONUS_BEAN`）。
 - **CATEGORY_FIRST_POST_REWARD**: 全平台首发奖励。当用户在空分类下首次发布资源或话题成功后，额外奖励 30 福利豆（对齐 PRD_MVP_资源模块 §2.1.6）。
 - **CONTENT_ADOPTED**: 本交易类型**仅用于信誉分记录**，不涉及可可豆发放。采纳奖励通过 **BOUNTY_RELEASE** 类型发放悬赏金（悬赏金按 70/30 分账，回答者得 70%，平台销毁 30%）。
 - **BOUNTY_LOCK**: 话题悬赏**锁定**阶段。发起者设置悬赏 B 可可豆，系统从发起者账户扣除 B 豆并标记为冻结（`point_type` 跟随原豆池类型），`dist_ratio` 不适用。
 - **BOUNTY_RELEASE**: 话题悬赏**采纳结算**阶段。采纳回答后，悬赏金按 70/30 分账：回答者获得 `floor(B × 0.7)` 豆（`order_type = BOUNTY_RELEASE`，`user_id` = 回答者），平台销毁 `floor(B × 0.3)` 豆（`order_type = DESTRUCTION`，`user_id = SYSTEM_BURN`），与资源下载分账规则一致。
 - **BOUNTY_REFUND**: 话题悬赏**超时退款**阶段。悬赏发布 30 天内未被采纳，系统自动退款至发起者账户（`point_type` 跟随原豆池类型），`order_type = BOUNTY_REFUND`；**退款金额 = 原悬赏金额（全额定数，平台不收取任何服务费）**，此阶段**不涉及 DESTRUCTION 操作**。
 - **FEEDBACK_AWARD**: 管理员采纳用户反馈并标记"已解决"后，系统自动发放的 20 福利豆奖励（**[!]** Phase 2 实现，MVP 阶段不生效）。
 
 ### **消耗优先级与原子性 (对齐 PRD §2.2)**
- **消耗顺序**: 系统在执行扣费时，必须**优先扣除 `BONUS_BEAN` (福利豆)**，福利豆不足的部分再由 `GOLD_BEAN` (资产豆) 补足。
- **原子性**: 整个计算与扣费过程必须包裹在同一个数据库事务中，防止并发导致的超额消耗。
 **交易示例 (以 100 豆资源为例)：**
 1. **全额支付 (100%)**:
    - 下载者: -100
    - 贡献者: +70 (70%)
    - 系统销毁 (虚拟账户): +30 (30%)
 2. **特惠包 (85% 折扣)**:
    - 下载者: -85
    - 贡献者: +70 (维持 70% 原价收益)
    - 系统销毁: +15 (平台让利 15%)
 3. **畅享包 (70% 折扣)**:
    - 下载者: -70
    - 贡献者: +70 (维持 70% 原价收益)
    - 系统销毁: 0 (平台让利 30%)
 
 > **[!] 关键原则**：系统必须绝对保障资源贡献者的收益（按原定价 70%），折扣由平台减免服务费承担。
 
 ## 2. `attempted_transaction` 表 (防刷死信记录)
 本表用于隔离失败的资金流水操作（如 `ECON_4001` 等拦截记录），确保防挂机阻断审计隔离。
 
 | 字段名 | 类型 | 说明 |
 |-------|------|------|
 | `id` | UUID | 拦截记录 ID |
 | `user_id` | UUID | 发起方 ID |
 | `order_type` | Enum | 尝试触发的账变流水类型 |
 | `amount` | Integer | 尝试扣费的数值 (涉金必落库) |
 | `reason` | String | 阻断原因字串快照 (例如：余额不足以覆盖锁定金额) |
 | `created_at` | Timestamp | 被拦截时间 |

 ## 3. `asset_packages` 表 (扩充包定义)
 | 字段名 | 类型 | 说明 |
 | `id` | UUID | 套餐 ID |
 | `name` | String | 特惠包/畅享包 |
 | `price_beans` | Integer | 价格 (默认值: 特惠包 80 / 畅享包 350，范围: 特惠包 1~10000 / 畅享包 1~100000) |
 | `quota_mb` | Integer | 额度容量，单位为 MB（MVP 阶段仅支持 MB，未来 Phase 2 扩展时可考虑支持 GB 单位混用，届时需增加 `quota_unit` 枚举字段） |
 | `discount_rate` | Float | 折扣 (如 0.85) |
 
 ## 3. `user_purchased_assets` 表 (用户已购资产)
 - 记录用户当前剩余的扩充包额度与有效期。
 
 ---
 
 ## 4. 结算精度与取整规则 (对齐审计报 A-02)
 为平衡平台通缩与对账一致性，系统内所有层级的比例分配、折扣计算、分成计算均严格执行 **`floor()` (向下取整)**。
 - **计算顺序**: `amount = floor(base_price * ratio)`。
 - **示例**: 100 豆分成 70/30 -> 贡献者获得 $floor(100 \times 0.7) = 70$，平台销毁 $floor(100 \times 0.3) = 30$。
 - **示例 (折扣)**: 100 豆 8.5 折 -> 下载者支付 $floor(100 \times 0.85) = 85$。
 
 ## 关键逻辑设计 (Self-Audit)
 
 ### **70/30 分成计算逻辑** (对齐 PRD §3.5.3)
 1. 资源定价 $P$，用户点击下载。
 2. 扣除下载者 $P$ 个可可豆 (`point_ledger` record 1: amount = $-P$)。
 3. 给贡献者增加 $P \times 0.7$ 个可可豆 (`point_ledger` record 2: amount = $+0.7P$)。
 4. 产生销毁记录 $P \times 0.3$ 个可可豆 (`point_ledger` record 3: amount = $+0.3P$, `user_id` = SYSTEM_BURN)。
 5. 系统看板统计 `SYSTEM_BURN` 账户总额即为通缩量。
 
 ### **早鸟奖励入账逻辑** (对齐 §3.2.2)
 1. 点击注册完成。
 2. 首先生效基础奖励：插入 `point_ledger`：`amount` = 30, `point_type` = BONUS_BEAN, `order_type` = SYSTEM_GIFT。
 3. 检测 Redis 若早鸟计数器 < 200，则**叠加额外入账**：插入 `point_ledger`：`amount` = 20, `point_type` = BONUS_BEAN, `order_type` = EARLYBIRD_REWARD。
 4. 两条（或一条）流水包裹在同一事务中提交。

 ### **签到奖励入账逻辑** (对齐 PRD §3.7 签到)
 1. 用户每日首次签到，插入 `point_ledger`：`amount` = 2, `point_type` = BONUS_BEAN, `order_type` = SIGN_IN。
 2. 同时写入 `reputation_logs`：`action_type` = SIGN_IN，`change_value` = +1，`reason` = "每日签到奖励"。
 3. 签到奖励不涉及分账，无 `transaction_uuid` 关联记录。
 4. 每日签到计数器独立维护（Redis Key: `sign_in:{user_id}:{date}`，TTL = 48h，**且归零日切严格对齐北京时间 `Asia/Shanghai`**）。
 5. **连续7天额外奖励**：当用户连续签到达到7天时，额外写入 `reputation_logs`：`action_type` = SIGN_IN，`change_value` = +1，`reason` = "连续签到7天额外奖励"。同时重置连续签到计数器。
 
 ### **邀请奖励入账逻辑** (对齐 PRD §3.7 邀请好友)
 1. **有效操作定义（固定三种，不可配置）**：被邀请人完成以下任一行为即判定为"完成有效操作"：
    - 首次成功上传一份资源（状态转为已通过审核）。
    - 首次成功发起一次 AI 问答对话（**仅限注册用户，严格剔除游客会话**）。
    - 首次成功发起一个社区话题（状态转为已发布）。
 2. **入账时序与幂等校验**：
    - **原子事务**：检测被邀请人的 `users.is_reward_triggered` 是否为 `False`。若为 `False`，则在同一事务内：
      - 将 `users.is_reward_triggered` 置为 `True`。
      - 插入两条 `point_ledger` 记录：
        - 邀请人：`amount` = 10, `point_type` = BONUS_BEAN, `order_type` = INVITE_REWARD, `related_id` = 被邀请人 user_id。
        - 被邀请人：`amount` = 10, `point_type` = BONUS_BEAN, `order_type` = INVITE_REWARD, `related_id` = 邀请人 user_id。
      - 同步增加邀请人和被邀请人的 `reputation_points` 各 10 分（写入 `reputation_logs`）。
 3. 若被邀请人 `is_reward_triggered` 已为 `True`，则不再触发，系统通过死信记录拦截。
 
 - [x] 对齐 V2.2 通缩模型：通过系统虚拟账户实现。
 - [x] 对齐特惠包折扣逻辑：后端计算 amount 时应用 `user_purchased_assets` 中的折扣率。
 - [x] 对齐可可豆与信誉分体系：区分资产豆(可取现)与福利豆(不可取现)。
 - [x] 对齐邀请奖励：INVITE_REWARD 入账 + reputation_logs 联动。

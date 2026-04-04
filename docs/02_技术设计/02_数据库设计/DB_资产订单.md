# 数据库设计 - 资产订单 (DB_资产订单)

## 1. `coffee_bean_orders` 表 (充值/交易订单)

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | UUID | 订单 ID | PK |
| `user_id` | UUID | 下单用户 | FK -> users.id, Index |
| `amount_cny` | Decimal | 支付人民币金额 | - |
| `beans_obtained` | Integer | 获得的可可豆数 | - |
| `order_status` | Enum | PENDING / PAID / CANCELLED / REFUNDED | Index |
| `payment_method` | Enum | WECHAT / ALIPAY / SYSTEM | - |
| `third_party_id` | String | 第三方支付流水号 | Unique |
| `created_at` | Timestamp | 下单时间 | - |
| `paid_at` | Timestamp | 支付成功时间 | - |

## 2. `quota_orders` 表 (扩充额度订单)

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | UUID | 记录 ID | PK |
| `user_id` | UUID | 购买者 | FK -> users.id |
| `package_id` | UUID | 关联扩充包 | FK -> asset_packages.id |
| `beans_cost` | Integer | 消耗的可可豆数 | - |
| `quota_mb` | Integer | 增加的额度容量 | - |
| `expire_at` | Timestamp | 过期时间 | Index |
| `created_at` | Timestamp | 购买时间 | - |

## 3. `user_download_entitlements` 表 (下载权益追踪)
| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | UUID | 记录 ID | PK |
| `user_id` | UUID | 用户 | FK -> users.id |
| `resource_id` | UUID | 关联资源 | FK -> resources.id |
| `retries_left` | Integer | 剩余免费重下载次数 | Default: 2 |
| `expire_at` | Timestamp | 1 年有效期截止时间 | Index |
| `last_download_at` | Timestamp | 上次执行时间 | - |
- [x] 对应 `DB_可可豆.md` 的 asset_packages 引用。

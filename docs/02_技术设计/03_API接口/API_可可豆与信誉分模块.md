# API 接口 - 可可豆与信誉分 (API_可可豆模块)

## 1. 资产查询
- **Endpoint**: `GET /api/v1/beans/balance`
- **返回**: `gold_beans`, `bonus_beans`, `reputation_points`, `rank`。

## 2. 交易记录 (对齐 DB_可可豆.md)
- **Endpoint**: `GET /api/v1/beans/ledger`
- **参数**: `type` (GOLD/BONUS)

## 3. 购买扩充额度
- **Endpoint**: `POST /api/v1/beans/purchase-quota`
- **参数**: `package_id`

---
- [x] 对齐 PRD §3.1/3.2 经济系统交互。
- [x] 数据来源：`point_ledger` 与 `reputation_logs`。
- [x] 术语对齐：全量使用“可可豆”与“信誉分”。

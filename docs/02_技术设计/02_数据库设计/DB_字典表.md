# 数据库设计 - 字典与配置表 (DB_字典表)

## 1. `categories` 表 (业务分类)

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|-----|
| `id` | Integer | ID | PK |
| `parent_id` | Integer | 父分类 | - |
| `name` | String | 名称 (如 "环境试验", "可靠性设计") | Not Null |
| `type` | Enum | RESOURCE / COMMUNITY | Index |
| `order_index` | Integer | 排序权重 | - |

- **索引约束**: 必须对 `(name, type)` 建立 **UNIQUE INDEX**，确保同一类型下不允许重名分类，但允许不同类型（如 RESOURCE 和 COMMUNITY）拥有同名分类。

## 2. `system_configs` 表 (动态配置)

| 字段名 | 类型 | 说明 | 配置值示例 |
|-------|------|------|-----------|
| `id` | UUID | 主键 | PK |
| `config_key` | String | 配置唯一标识 | `RES_DUP_THRESHOLD` |
| `config_value` | String | 配置内容 | `0.8` |
| `description` | String | 参数说明 | 资源重复判定相似度阈值 |
| `created_at` | Timestamp | 创建时间 | - |
| `updated_at` | Timestamp | 更新时间 | - |

### **核心全局参数预置**
- **RES_DUP_THRESHOLD**: 资源重复判定相似度阈值 (0.8, 范围 0.5-0.99)。
- **APP_MIN_VERSION**: App 最低兼容版本 (强制更新，1.0.0)。
- **APP_LATEST_VERSION**: App 最新版本 (提示更新，1.0.5)。
- **TOKEN_DAILY_LIMIT**: 全局每日 Token 消耗熔断值 (1000000 K)。

---
- [x] 对齐 PRD 灵活性要求：全类型分类支持。
- [x] 全站业务参数动态调节设计。

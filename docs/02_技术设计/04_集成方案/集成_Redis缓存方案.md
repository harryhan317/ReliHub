# 集成方案 - Redis 缓存方案 (集成_Redis缓存方案)

## 1. Key 命名规范
- **格式**: `relihub:{module}:{type}:{id}`。
- 示例: `relihub:user:token:xxxx`, `relihub:resource:heat:123`。

## 2. 典型场景
- **分布式锁**: 可可豆扣减与秒杀。
- **计数器**: 每日签到、浏览量去重、短信发送限频、重复上传拦截。
- **缓存**: 系统配置表 (TTL=24h)、用户信息快照 (TTL=2h)。

## 3. 持久化与一致性
- 核心数据（如余额）严禁仅存在 Redis 中。
- 采用 Cache-Aside 模式：查询未命中 -> 查 DB -> 写入 Redis。

---
- [x] 对齐 PRD 非功能需求：低延迟响应。
- [x] 集成查重限频拦截器。

# 集成方案 - AI(LLM) 接入方案 (集成_AI接入方案)

## 1. 模型选择与优先级
- **主模型**: DeepSeek-V3 (性价比高，代码理解强)。
- **备选模型**: GPT-4o (稳定性高，逻辑缜密)。
- **灰度切换**: 通过 `ai_config.rollout_percentage` 实现流量平滑迁移。

## 2. 核心架构
- **后端适配器**: 实现统一的 `LLMServce` 抽象类，封装不同厂商的 SDK。
- **流式响应**: 基于 SSE (Server-Sent Events) 协议，确保前端低延迟。
- **重试机制**: 
  - 发生 `RateLimit` 或 `ConnectionError` 时，自动重试 3 次。
  - 3 次失败后，自动降级切换至备选模型。

## 3. Prompt 版本控制
- 使用 `ai_config` 表存储 Prompt 版本。
- 对齐 PRD §1.2.1：历史会话必须沿用创建时的 System Prompt 快照。

## 4. Token 额度执行与计数 (对齐 PRD §4.1.2)
- **计数器**: 使用 Redis `INCRBY` 原子操作统计各维度 Token：
  - `user:token:daily:{user_id}:{date}`: 每日总额。
  - `user:token:session:{user_id}:{session_id}`: 单对话限额。
- **执行逻辑**: 
  - 每次 LLM 响应返回 `usage` 后，后台异步累加。
  - 下次请求前校验 Redis 值，若超限返回 `403 Quota Exceeded`。
- **重置**: 每日 0 点自动过期。
- [x] 高可用设计：自动降级与重试机制。

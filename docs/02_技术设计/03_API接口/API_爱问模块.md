# API 接口 - 爱问模块 (AI Assistant)
 
 ## 1. 模块概述
 处理用户与 ReliBot 的所有交互，支持流式输出 (SSE) 协议。
 
 ## 2. 接口列表
 
 ### 2.1 创建会话
 - **Endpoint**: `POST /api/v1/ai/sessions`
 - **说明**: 初始化一个新的 AI 对话。
 
 ### 2.2 发送消息 (流式)
 - **Endpoint**: `POST /api/v1/ai/chat/sse`
 - **协议**: SSE (Server-Sent Events)
 - **参数**:
   - `session_id`: 会话 ID
   - `content`: 文本内容
   - `attachments`: 附件列表 (UUIDs)
 - **响应**: 持续推送流式 JSON，控制消息包含当前会话进度（轮次）：
  ```json
  { 
    "delta": "xxx", 
    "role": "assistant", 
    "round_count": 5,
    "quota_limit": 10
  }
  ```
- **参数说明**: `round_count` 为当前会话已消耗轮次，`quota_limit` 为当前用户的单会话轮次上限 (1 轮次 = 1 QA)。**为减少冗余流量，`round_count` 与 `quota_limit` 仅在 SSE 建立连接后的首个 `metadata` 数据包以及会话结束包中下发。**
 
 ### 2.3 获取历史会话
 - **Endpoint**: `GET /api/v1/ai/sessions`
 - **参数**: `page`, `page_size`, `keyword`
 
 ### 2.4 会话重命名/删除
 - **Endpoint**: `PATCH/DELETE /api/v1/ai/sessions/{id}`
 
 ---
 
 ## 3. 业务规则映射与限额校验 (对齐 §4.1.2)
 
 ### 3.1 等级限额校验矩阵 (权威数据源: PRD_可可豆与信誉分体系)
 | 等级 | 每日会话 | 单会话轮次 | 每日总轮次 | 输出/总 Token (单次) | 每日/累计 Token | 会话保存 (个/MB) |
 |------|---------|-----------|-----------|--------------------|-----------------|-----------------|
 | 游客 | 3       | 10        | 15        | 1K / 2K            | 5K / 500K       | 3 / -           |
 | 新兵 | 5       | 10        | 30        | 2K / 10K           | 15K / 1M        | 20 / 100MB      |
 | 菜鸟 | 5       | 15        | 40        | 2K / 12K           | 20K / 2M        | 30 / 300MB      |
 | 入门 | 8       | 15        | 50        | 4K / 16K           | 30K / 3M        | 50 / 500MB      |
 | 熟手 | 10      | 15        | 80        | 4K / 16K           | 50K / 5M        | 60 / 600MB      |
 | 老炮 | 12      | 20        | 100       | 4K / 24K           | 80K / 8M        | 80 / 800MB      |
 | 达人 | 15      | 20        | 120       | 8K / 32K           | 100K / 10M      | 100 / 1000MB    |
 | 专家 | 20      | 20        | 150       | 8K / 32K           | 120K / 12M      | 100 / 1000MB    |
 
 - **校验流程**:
   1. Middleware 拦截请求。
   2. 查询 `users.daily_token_usage` 及 `ai_sessions` 计数器。
   3. 匹配 `rank` 对应阈值，超限返回 `403 Quota Exceeded`。

### 3.2 游客附件权限校验
- **游客限制规则**：游客默认每日可发起 3 个新会话。**[!] 技术实现分层**：为了应对高并发下的配额检查压强，**系统采用“Redis 实时热路径拦截，DB 离线冷路径存根”的单真源策略**。
  - **实时热路径**：用户发起提问时，API Gateway 优先在 Redis Quota Counter 进行分布式拦截，耗时 < 1ms。
  - **离线冷路径**：会话结束后由后台任务同步至 `point_ledger` 或 `ai_sessions` 表作为离线存根审计。
  - `POST /api/v1/ai/chat/sse` 接口需在校验等级限额前，先校验 `attachments` 参数
  - 若用户 `rank = 'GUEST'` 且 `attachments` 非空，返回 `403 Forbidden` 并提示"请先注册后上传附件"
  - 游客发送纯文本消息不受影响（附件校验独立于消息内容校验）

### 3.3 DND 免打扰状态
 - **来源**: 读取 `users.notification_config` (JSONB) 中的 `dnd_mode` 标记。
 - **生效**: 若 DND=True，则仅在 App 内显示红点，不触发外部 Push。

# 📋 Sprint C 技术方案设计

**创建日期**: 2026-04-04  
**项目**: ReliHub MVP  
**Sprint 周期**: 2026-04-09 ~ 2026-05-07 (4 周)

---

## 🎯 Sprint C 目标

### 核心目标
1. ✅ 实现 LLM API 集成，使 AI 对话功能可用
2. ✅ 实现支付网关集成，完成商业闭环
3. ✅ 实现敏感词过滤，满足合规要求
4. ⚠️  性能优化（可选，视时间而定）

### 成功标准
- AI 对话可调用真实 LLM 模型
- 用户可充值可可豆
- 下载资源时自动扣费
- 敏感内容自动过滤
- 所有功能通过测试验收

---

## 📊 Sprint C 任务分解

### 任务 1: LLM API 集成 (2 周)

#### 📝 需求分析

**业务场景**:
1. 用户发起 AI 对话请求
2. 系统调用 LLM API 生成回复
3. 按 Token 数量扣除可可豆
4. 支持流式响应（打字机效果）

**功能需求**:
- 支持多个 LLM 提供商（OpenAI/Claude/Moonshot）
- 支持流式响应（SSE）
- Token 计费
- 速率限制
- 错误处理和重试

#### 🏗️ 技术设计

**架构设计**:
```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP (SSE)
       ▼
┌─────────────────────────────┐
│  API Router (ai/router.py)  │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│   AI Service (ai_service.py)│
│  ┌───────────────────────┐  │
│  │  LLM Provider Factory │  │
│  └───────────┬───────────┘  │
│              │              │
│  ┌───────────▼───────────┐  │
│  │  LLM Provider Interface│  │
│  └───────────┬───────────┘  │
│              │              │
│  ┌───────────▼───────────┐  │
│  │  OpenAI Provider      │  │
│  │  Claude Provider      │  │
│  │  Moonshot Provider    │  │
│  └───────────┬───────────┘  │
└──────────────┼──────────────┘
               │
               ▼
        ┌──────────────┐
        │  LLM API     │
        │  (External)  │
        └──────────────┘
```

**数据库设计**:

新增表：`llm_providers`
```sql
CREATE TABLE llm_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,  -- 'openai', 'claude', 'moonshot'
    display_name VARCHAR(100) NOT NULL,
    api_base_url VARCHAR(255) NOT NULL,
    api_key_env VARCHAR(100) NOT NULL,  -- 环境变量名
    enabled BOOLEAN DEFAULT true,
    rate_limit_per_minute INTEGER DEFAULT 60,
    cost_per_1k_tokens DECIMAL(10, 6) NOT NULL,  -- 每 1k token 成本
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_llm_providers_enabled ON llm_providers(enabled);
```

修改表：`ai_sessions`
```sql
ALTER TABLE ai_sessions ADD COLUMN provider_id UUID REFERENCES llm_providers(id);
ALTER TABLE ai_sessions ADD COLUMN total_tokens INTEGER DEFAULT 0;
ALTER TABLE ai_sessions ADD COLUMN total_cost DECIMAL(10, 6) DEFAULT 0;
```

修改表：`ai_messages`
```sql
ALTER TABLE ai_messages ADD COLUMN tokens INTEGER DEFAULT 0;
ALTER TABLE ai_messages ADD COLUMN cost DECIMAL(10, 6) DEFAULT 0;
```

**代码结构**:

```
backend/app/services/
├── ai_service.py (修改)
├── llm_provider/
│   ├── __init__.py
│   ├── base.py (抽象基类)
│   ├── openai_provider.py
│   ├── claude_provider.py
│   └── moonshot_provider.py
```

**核心代码实现**:

1. `backend/app/services/llm_provider/base.py`
```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any

class LLMProvider(ABC):
    """LLM 提供商抽象基类"""
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        聊天补全接口
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "hello"}]
            model: 模型名称
            temperature: 温度
            max_tokens: 最大 token 数
            stream: 是否流式输出
            
        Yields:
            {"content": str, "finish_reason": str|None, "usage": dict}
        """
        pass
    
    @abstractmethod
    async def count_tokens(self, messages: list[dict]) -> int:
        """计算 token 数量"""
        pass
```

2. `backend/app/services/llm_provider/openai_provider.py`
```python
import httpx
from .base import LLMProvider
from typing import AsyncGenerator, Dict, Any

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60.0
        )
    
    async def chat_completion(
        self,
        messages: list[dict],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """OpenAI 聊天补全"""
        url = "/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    
                    import json
                    chunk = json.loads(data)
                    
                    # 提取内容
                    if chunk["choices"]:
                        delta = chunk["choices"][0]["delta"]
                        content = delta.get("content", "")
                        finish_reason = chunk["choices"][0].get("finish_reason")
                        usage = chunk.get("usage")
                        
                        yield {
                            "content": content,
                            "finish_reason": finish_reason,
                            "usage": usage
                        }
    
    async def count_tokens(self, messages: list[dict]) -> int:
        """使用 tiktoken 计算 token 数"""
        import tiktoken
        encoder = tiktoken.get_encoding("cl100k_base")
        
        num_tokens = 0
        for message in messages:
            num_tokens += 3  # role + content + name
            for key, value in message.items():
                num_tokens += len(encoder.encode(str(value)))
        
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens
```

3. `backend/app/services/ai_service.py` (修改)
```python
from .llm_provider.base import LLMProvider
from .llm_provider.openai_provider import OpenAIProvider
from .llm_provider.claude_provider import ClaudeProvider
from .llm_provider.moonshot_provider import MoonshotProvider

class AIService:
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self._load_providers()
    
    def _load_providers(self):
        """加载 LLM 提供商"""
        settings = get_settings()
        
        # OpenAI
        if settings.OPENAI_API_KEY:
            self.providers["openai"] = OpenAIProvider(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
        
        # Claude
        if settings.ANTHROPIC_API_KEY:
            self.providers["claude"] = ClaudeProvider(
                api_key=settings.ANTHROPIC_API_KEY
            )
        
        # Moonshot
        if settings.MOONSHOT_API_KEY:
            self.providers["moonshot"] = MoonshotProvider(
                api_key=settings.MOONSHOT_API_KEY
            )
    
    async def create_message(
        self,
        session_id: UUID,
        user_id: UUID,
        content: str,
        provider_name: str = "openai",
        model: str = None
    ) -> AIMessage:
        """创建 AI 消息"""
        # 1. 获取会话
        session = await self.get_session(session_id)
        
        # 2. 获取提供商
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"不支持的 LLM 提供商：{provider_name}")
        
        # 3. 构建消息历史
        messages = await self._build_message_history(session)
        messages.append({"role": "user", "content": content})
        
        # 4. 调用 LLM API
        ai_response = ""
        total_tokens = 0
        
        async for chunk in provider.chat_completion(
            messages=messages,
            model=model or self._get_default_model(provider_name),
            stream=True
        ):
            if chunk["content"]:
                ai_response += chunk["content"]
            if chunk["usage"]:
                total_tokens = chunk["usage"]["total_tokens"]
        
        # 5. 计算费用
        cost = self._calculate_cost(total_tokens, provider_name)
        
        # 6. 扣除可可豆
        await self._deduct_points(user_id, cost)
        
        # 7. 保存消息
        user_message = await self._save_user_message(session_id, content)
        ai_message = await self._save_ai_message(
            session_id, 
            ai_response,
            tokens=total_tokens,
            cost=cost
        )
        
        # 8. 更新会话统计
        await self._update_session_stats(session_id, total_tokens, cost)
        
        return ai_message
```

#### 📦 依赖安装

```bash
# requirements.txt
httpx>=0.24.0  # HTTP 客户端
tiktoken>=0.5.0  # OpenAI token 计算
```

#### ✅ 验收标准

- [ ] 支持 OpenAI API 调用
- [ ] 支持 Claude API 调用
- [ ] 支持 Moonshot API 调用
- [ ] 流式响应工作正常
- [ ] Token 计费准确
- [ ] 错误处理完整
- [ ] 速率限制生效
- [ ] 单元测试覆盖

---

### 任务 2: 支付网关集成 (1 周)

#### 📝 需求分析

**业务场景**:
1. 用户选择充值金额
2. 创建支付订单
3. 跳转到支付页面
4. 用户完成支付
5. 接收异步回调
6. 更新订单状态
7. 增加用户可可豆余额

**支付方式**:
- 微信支付（主要）
- 支付宝（备选）
- Stripe（备选，国际支付）

#### 🏗️ 技术设计

**架构设计**:
```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  Payment Router         │
│  /api/v1/payment/*      │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Payment Service        │
│  ┌───────────────────┐  │
│  │ Payment Factory   │  │
│  └─────────┬─────────┘  │
│            │            │
│  ┌─────────▼─────────┐  │
│  │ Wechat Payment    │  │
│  │ Alipay Payment    │  │
│  │ Stripe Payment    │  │
│  └─────────┬─────────┘  │
└────────────┼────────────┘
             │
             ▼
    ┌────────────────┐
    │ Payment Gateway│
    │ (External)     │
    └────────────────┘
```

**数据库设计**:

新增表：`payment_orders`
```sql
CREATE TYPE payment_status AS ENUM (
    'pending',      -- 待支付
    'paid',         -- 已支付
    'failed',       -- 支付失败
    'refunded',     -- 已退款
    'cancelled'     -- 已取消
);

CREATE TYPE payment_method AS ENUM (
    'wechat',
    'alipay',
    'stripe'
);

CREATE TABLE payment_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_no VARCHAR(64) NOT NULL UNIQUE,  -- 订单号
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- 金额信息
    amount DECIMAL(10, 2) NOT NULL,  -- 充值金额（元）
    points INTEGER NOT NULL,         -- 获得的可可豆
    exchange_rate INTEGER NOT NULL,  -- 汇率（1 元 = ? 可可豆）
    
    -- 支付信息
    payment_method payment_method NOT NULL,
    payment_status payment_status DEFAULT 'pending',
    transaction_id VARCHAR(128),     -- 第三方支付流水号
    
    -- 微信支付信息
    wechat_prepay_id VARCHAR(128),
    wechat_code_url TEXT,
    
    -- 回调信息
    callback_data JSONB,
    callback_time TIMESTAMP,
    
    -- 时间信息
    expires_at TIMESTAMP NOT NULL,   -- 过期时间
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payment_orders_user ON payment_orders(user_id);
CREATE INDEX idx_payment_orders_status ON payment_orders(payment_status);
CREATE INDEX idx_payment_orders_order_no ON payment_orders(order_no);
```

新增表：`payment_transactions`
```sql
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES payment_orders(id),
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- 交易信息
    transaction_type VARCHAR(50) NOT NULL,  -- 'charge', 'refund'
    amount DECIMAL(10, 2) NOT NULL,
    points INTEGER NOT NULL,
    
    -- 第三方信息
    provider_transaction_id VARCHAR(128),
    provider_response JSONB,
    
    -- 审计信息
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payment_transactions_order ON payment_transactions(order_id);
CREATE INDEX idx_payment_transactions_user ON payment_transactions(user_id);
```

**代码结构**:

```
backend/app/
├── models/
│   └── payment.py (新建)
├── schemas/
│   └── payment.py (新建)
├── services/
│   ├── payment_service.py (新建)
│   └── payment_provider/
│       ├── __init__.py
│       ├── base.py
│       ├── wechat_provider.py
│       ├── alipay_provider.py
│       └── stripe_provider.py
└── api/v1/payment/
    ├── __init__.py
    └── router.py (新建)
```

**核心 API 设计**:

```python
# POST /api/v1/payment/orders
# 创建支付订单
{
    "payment_method": "wechat",
    "amount": 98.00,
    "points": 9800  # 1 元 = 100 可可豆
}

# Response
{
    "order_no": "PO202604040001",
    "payment_method": "wechat",
    "amount": 98.00,
    "points": 9800,
    "wechat_code_url": "https://...",  # 扫码支付 URL
    "expires_at": "2026-04-04T15:30:00Z"
}

# GET /api/v1/payment/orders/{order_no}/status
# 查询订单状态
{
    "order_no": "PO202604040001",
    "status": "paid",
    "paid_at": "2026-04-04T15:25:00Z",
    "points": 9800
}

# POST /api/v1/payment/webhooks/wechat
# 微信支付异步回调
{
    "transaction_id": "...",
    "out_trade_no": "PO202604040001",
    "total_fee": 9800,  # 分
    "status": "SUCCESS"
}
```

#### ✅ 验收标准

- [ ] 创建支付订单
- [ ] 微信支付集成
- [ ] 异步回调处理
- [ ] 订单状态查询
- [ ] 充值成功增加余额
- [ ] 交易记录审计
- [ ] 退款流程（可选）
- [ ] 单元测试覆盖

---

### 任务 3: 敏感词过滤 (3-5 天)

#### 📝 需求分析

**业务场景**:
1. 用户发布内容（AI 对话、资源、社区帖子）
2. 系统自动过滤敏感词
3. 根据策略处理（替换/拒绝/审核）

**过滤策略**:
- 替换：用 *** 替换敏感词
- 拒绝：直接拒绝发布
- 审核：先发布，后审核

#### 🏗️ 技术设计

**算法选择**: AC 自动机（Aho-Corasick）

**性能要求**:
- 单次过滤 < 50ms
- 支持 10 万 + 词库
- 支持动态更新

**代码结构**:

```
backend/app/services/
└── content_filter/
    ├── __init__.py
    ├── ac_automaton.py (AC 自动机实现)
    ├── sensitive_words.py (敏感词服务)
    └── content_filter.py (内容过滤服务)
```

**核心代码**:

```python
# backend/app/services/content_filter/ac_automaton.py
from collections import defaultdict
from typing import Dict, List, Set

class ACAutomaton:
    """AC 自动机实现"""
    
    def __init__(self):
        self.trie = defaultdict(dict)
        self.fail = {}
        self.output = defaultdict(set)
    
    def add_word(self, word: str):
        """添加敏感词"""
        node = self.trie
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]
        node['end'] = True
        self.output[id(node)].add(word)
    
    def build(self):
        """构建失败指针"""
        queue = []
        # 第一层
        for char, node in self.trie.items():
            self.fail[id(node)] = self.trie
            queue.append(node)
        
        # BFS 构建
        while queue:
            current = queue.pop(0)
            for char, node in current.items():
                if char == 'end':
                    continue
                
                fail_node = self.fail[id(current)]
                while fail_node and char not in fail_node:
                    fail_node = self.fail.get(id(fail_node))
                
                self.fail[id(node)] = fail_node[char] if fail_node and char in fail_node else self.trie
                self.output[id(node)].update(self.output[id(self.fail[id(node)])])
                queue.append(node)
    
    def find_all(self, text: str) -> List[Dict]:
        """查找所有敏感词"""
        result = []
        node = self.trie
        
        for i, char in enumerate(text):
            while node and char not in node:
                node = self.fail.get(id(node))
            
            if node:
                node = node[char]
            
            if node and id(node) in self.output:
                for word in self.output[id(node)]:
                    result.append({
                        "word": word,
                        "start": i - len(word) + 1,
                        "end": i + 1
                    })
        
        return result
    
    def replace(self, text: str, replacement: str = "***") -> str:
        """替换敏感词"""
        matches = self.find_all(text)
        matches.sort(key=lambda x: x["start"], reverse=True)
        
        result = list(text)
        for match in matches:
            result[match["start"]:match["end"]] = replacement
        
        return "".join(result)
```

**使用示例**:

```python
# backend/app/services/content_filter/content_filter.py
from .ac_automaton import ACAutomaton

class ContentFilter:
    def __init__(self):
        self.automaton = ACAutomaton()
        self._load_sensitive_words()
    
    def _load_sensitive_words(self):
        """加载敏感词库"""
        # 从文件或数据库加载
        words = ["敏感词 1", "敏感词 2", ...]
        for word in words:
            self.automaton.add_word(word)
        self.automaton.build()
    
    def filter(self, content: str, strategy: str = "replace") -> Dict:
        """
        过滤内容
        
        Args:
            content: 待过滤内容
            strategy: 'replace' | 'reject' | 'review'
            
        Returns:
            {
                "passed": bool,
                "content": str,
                "matches": List[Dict],
                "reason": str
            }
        """
        matches = self.automaton.find_all(content)
        
        if not matches:
            return {"passed": True, "content": content, "matches": []}
        
        if strategy == "replace":
            filtered = self.automaton.replace(content)
            return {
                "passed": True,
                "content": filtered,
                "matches": matches,
                "reason": "已替换敏感词"
            }
        elif strategy == "reject":
            return {
                "passed": False,
                "content": content,
                "matches": matches,
                "reason": "包含敏感词"
            }
        elif strategy == "review":
            return {
                "passed": True,
                "content": content,
                "matches": matches,
                "reason": "需要人工审核"
            }
```

#### ✅ 验收标准

- [ ] AC 自动机实现正确
- [ ] 敏感词库完整
- [ ] 过滤精准度 > 95%
- [ ] 性能 < 50ms
- [ ] 支持动态更新
- [ ] 集成到 AI 对话
- [ ] 集成到资源发布
- [ ] 集成到社区发帖

---

## 📅 Sprint C 时间规划

### 第 1 周 (04-09 ~ 04-15)
- [ ] Sprint C 启动会
- [ ] LLM API 集成 - OpenAI
- [ ] LLM API 集成 - Claude
- [ ] 敏感词过滤 - AC 自动机

### 第 2 周 (04-16 ~ 04-22)
- [ ] LLM API 集成 - Moonshot
- [ ] LLM API 集成 - 流式响应
- [ ] LLM API 集成 - Token 计费
- [ ] 敏感词过滤 - 集成到业务

### 第 3 周 (04-23 ~ 04-29)
- [ ] 支付网关 - 微信支付
- [ ] 支付网关 - 订单管理
- [ ] 支付网关 - 异步回调
- [ ] 支付网关 - 充值流程

### 第 4 周 (04-30 ~ 05-07)
- [ ] 支付网关 - 退款流程（可选）
- [ ] 性能优化（可选）
- [ ] 集成测试
- [ ] Sprint C 验收

---

## 📊 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| LLM API 成本高 | 中 | 高 | 设置速率限制，监控用量 |
| 支付资质问题 | 高 | 高 | 提前准备商户账户 |
| 敏感词库不完整 | 中 | 中 | 使用开源词库 + 人工维护 |
| 性能不达标 | 低 | 中 | 提前压测，优化算法 |

---

## 📝 下一步行动

1. **立即行动** (今天):
   - [ ] 获取 LLM API Key（OpenAI/Claude/Moonshot）
   - [ ] 申请支付商户账户
   - [ ] 收集敏感词库

2. **本周完成**:
   - [ ] 完成技术设计评审
   - [ ] 搭建开发环境
   - [ ] 创建 Sprint C 分支

3. **下周开始**:
   - [ ] Sprint C 开发启动
   - [ ] 每日站会同步进度
   - [ ] 每周演示成果

---

**Sprint C 技术方案设计完成！准备开始开发** 🚀

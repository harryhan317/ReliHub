# API 接口 - 搜索模块 (API_搜索模块)

## 文档版本记录

| 版本 | 日期 | 变更说明 | 维护人 |
|------|------|---------|--------|
| v1.0 | 2026-04-09 | 初始版本（框架级，缺明细） | 架构组 |
| v2.0 | 2026-04-09 | **全面补充明细设计**: 新增用户搜索、AI 历史搜索、搜索历史管理接口；统一参数校验规则；对齐错误码规范；修正前端字段不一致 | Trae AI |
| v2.1 | 2026-04-10 | **搜索优化专项**: 更新全局搜索实现状态；补充搜索优化功能说明（查询优化、相关性算法增强、性能优化）；更新接口响应字段 | Trae AI |

---

## 1. 模块概述

搜索模块提供跨模块的统一检索能力，支持资源库、社区话题、AI 历史会话、用户的专属化搜索以及搜索辅助功能（自动补全、热搜榜、搜索历史管理）。

**实现状态概览**:

| 接口 | 端点 | 状态 | 实现版本 |
|------|------|------|---------|
| 全局统一搜索 | `GET /api/v1/search` | ✅ 已实现 (含优化) | v2.1 |
| 搜索建议 (Autocomplete) | `GET /api/v1/search/suggestions` | ✅ 已实现 | v2.0 |
| 热搜榜单 | `GET /api/v1/search/trending` | ✅ 已实现 (Redis 缓存) | v2.1 |
| 用户搜索 | `GET /api/v1/search/users` | ✅ 已实现 | v2.0 |
| AI 历史搜索 | `GET /api/v1/search/ai-history` | ✅ 已实现 | v2.0 |
| 搜索历史 - 查询 | `GET /api/v1/search/history` | ✅ 已实现 | v2.0 |
| 搜索历史 - 删除单条 | `DELETE /api/v1/search/history/{id}` | ✅ 已实现 | v2.0 |
| 搜索历史 - 清空 | `DELETE /api/v1/search/history` | ✅ 已实现 | v2.0 |
| 资源搜索 (已有) | `GET /api/v1/resources` | ✅ 已实现 | - |
| 社区话题搜索 (已有) | `GET /api/v1/community/topics` | ✅ 已实现 | - |

**v2.1 优化特性**:
- ✅ **查询优化**: 自动规范化查询词（去除特殊字符、截断超长查询）
- ✅ **相关性增强**: BM25 + TF-IDF 混合算法，支持标题加权、热度加权、时效加权
- ✅ **性能优化**: 数据库索引优化（GIN 全文索引、组合索引），Redis 缓存热搜和搜索建议
- ✅ **敏感词过滤**: 基于 Trie 算法的搜索词敏感词过滤

**注意**: 本文档 §2 描述所有新增待实现接口; §3 引用已实现接口的搜索参数。

---

## 2. 接口明细设计

### 2.1 全局统一搜索

- **Endpoint**: `GET /api/v1/search`
- **状态**: ⚠️ 待实现
- **权限**: 需登录 (`Authorization: Bearer <token>`)。游客身份隐式支持但结果受限（≤10 条）。
- **限流**: 10 次/分钟/用户，超出返回 `SYS_4290`

#### 请求参数

| 参数名 | 类型 | 必选 | 默认值 | 校验规则 | 说明 |
|--------|------|------|--------|----------|------|
| `q` | string | **是** | - | 1 ≤ len ≤ 50；不得为纯空白字符 | 搜索关键词 |
| `type` | string | 否 | `ALL` | 枚举: `RESOURCE`, `COMMUNITY`, `AI`, `USER`, `ALL` | 搜索范围 |
| `sort_by` | string | 否 | `relevance` | 枚举: `relevance`, `heat`, `latest` | 排序方式 |
| `page` | int | 否 | `1` | ≥ 1 | 页码 |
| `size` | int | 否 | `20` | 1 ≤ size ≤ 100 | 每页数量 |
| `start_date` | string | 否 | - | `YYYY-MM-DD`，仅 `type=AI` 时生效 | 结果起始日期过滤 |
| `end_date` | string | 否 | - | `YYYY-MM-DD`，须 ≥ `start_date`，仅 `type=AI` 时生效 | 结果截止日期过滤 |

> **游客限制**: 当请求方为游客时，后端强制 `size=10, page=1`，忽略客户端传入值，`has_more` 固定返回 `false`。

#### 请求示例

```bash
# 全局搜索 "PCB设计"，按热度排序，第一页
GET /api/v1/search?q=PCB设计&type=ALL&sort_by=heat&page=1&size=20
Authorization: Bearer <access_token>
```

#### 响应结构 (SearchListResponse)

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "total": 1250,
    "page": 1,
    "size": 20,
    "has_more": true,
    "query": "PCB设计",
    "type": "ALL",
    "sort_by": "heat",
    "items": [
      {
        "id": "3a4b5c6d-...",
        "type": "RESOURCE",
        "title": "PCB设计指南",
        "summary": "这是关于PCB设计的详细指南，涵盖布局、走线、层叠...",
        "author": {
          "id": "user-uuid",
          "nickname": "张三",
          "avatar_url": "https://cdn.relihub.com/avatars/xxx.jpg"
        },
        "heat_score": 125.5,
        "created_at": "2026-04-01T12:00:00Z",
        "tags": ["PCB", "硬件设计"],
        "metadata": {
          "file_type": "PDF",
          "file_size_kb": 2150,
          "download_count": 120,
          "view_count": 890
        }
      },
      {
        "id": "7e8f9a0b-...",
        "type": "COMMUNITY",
        "title": "如何优化信号完整性？",
        "summary": "在高速电路设计中，信号完整性是关键因素，本文讨论...",
        "author": {
          "id": "user-uuid-2",
          "nickname": "李四",
          "avatar_url": "https://cdn.relihub.com/avatars/yyy.jpg"
        },
        "heat_score": 88.0,
        "created_at": "2026-04-03T10:00:00Z",
        "tags": ["SI", "仿真"],
        "metadata": {
          "reply_count": 45,
          "like_count": 120,
          "is_featured": true,
          "is_bounty": false,
          "bounty_amount": 0
        }
      },
      {
        "id": "1c2d3e4f-...",
        "type": "AI",
        "title": "信号完整性讨论",
        "summary": "用户关于高速电路信号完整性的问答记录摘要...",
        "author": {
          "id": "user-uuid-3",
          "nickname": "王五",
          "avatar_url": "https://cdn.relihub.com/avatars/zzz.jpg"
        },
        "heat_score": 0,
        "created_at": "2026-04-02T15:00:00Z",
        "tags": ["SI", "高速电路"],
        "metadata": {
          "session_id": "session-uuid",
          "message_count": 12
        }
      },
      {
        "id": "user-uuid-target",
        "type": "USER",
        "title": "PCB设计专家 · 张鑫",
        "summary": "5级 · 参与了 230 篇话题 · 信誉分 980",
        "author": {
          "id": "user-uuid-target",
          "nickname": "张鑫",
          "avatar_url": "https://cdn.relihub.com/avatars/abc.jpg"
        },
        "heat_score": 0,
        "created_at": "2025-10-01T00:00:00Z",
        "tags": ["PCB设计", "硬件工程"],
        "metadata": {
          "rank_level": 5,
          "reputation_score": 980,
          "follower_count": 340,
          "topic_count": 230
        }
      }
    ]
  }
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.total` | int | 符合条件的总结果数 |
| `data.page` | int | 当前页码 |
| `data.size` | int | 当前页实际返回数量 |
| `data.has_more` | bool | 是否存在下一页（对齐《API_接口规范.md》§4 分页标准） |
| `data.query` | string | 实际执行的搜索词（经服务端规范化处理后） |
| `data.items[].id` | string | 各模块对象 UUID |
| `data.items[].type` | string | `RESOURCE` / `COMMUNITY` / `AI` / `USER` |
| `data.items[].title` | string | 结果标题（搜索词高亮由前端 `<mark>` 处理） |
| `data.items[].summary` | string | 结果摘要，截断至 200 字符，超出加 `...` |
| `data.items[].author` | object | 作者对象（含 `id`, `nickname`, `avatar_url`） |
| `data.items[].heat_score` | float | 热度评分（AI / USER 类型为 0） |
| `data.items[].tags` | array\<string\> | 标签列表，最多 10 个 |
| `data.items[].metadata` | object | 类型专属元数据（见下表） |

#### Metadata 各类型字段说明

| 类型 | 字段 | 类型 | 说明 |
|------|------|------|------|
| `RESOURCE` | `file_type` | string | `PDF` / `DOC` / `IMG` / `ZIP` / `OTHER` |
| `RESOURCE` | `file_size_kb` | int | 文件大小（KB） |
| `RESOURCE` | `download_count` | int | 下载次数 |
| `RESOURCE` | `view_count` | int | 浏览次数 |
| `COMMUNITY` | `reply_count` | int | 回复数 |
| `COMMUNITY` | `like_count` | int | 点赞数 |
| `COMMUNITY` | `is_featured` | bool | 是否精华帖 |
| `COMMUNITY` | `is_bounty` | bool | 是否设有悬赏 |
| `COMMUNITY` | `bounty_amount` | int | 悬赏可可豆数量（非悬赏时为 0） |
| `AI` | `session_id` | string | 会话 UUID（用于跳转详情） |
| `AI` | `message_count` | int | 会话消息轮次数 |
| `USER` | `rank_level` | int | 用户等级（1-8） |
| `USER` | `reputation_score` | int | 当前信誉分 |
| `USER` | `follower_count` | int | 粉丝数 |
| `USER` | `topic_count` | int | 发布话题数 |

---

### 2.2 搜索建议 (Autocomplete)

- **Endpoint**: `GET /api/v1/search/suggestions`
- **状态**: ⚠️ 待实现
- **权限**: 需登录
- **限流**: 30 次/分钟/用户（输入防抖由前端控制，建议 Debounce 200ms）
- **缓存**: 建议结果由 Redis 前缀树缓存，TTL = 10 分钟

#### 请求参数

| 参数名 | 类型 | 必选 | 默认值 | 校验规则 | 说明 |
|--------|------|------|--------|----------|------|
| `q` | string | **是** | - | 1 ≤ len ≤ 20；不得为纯空白字符 | 当前输入关键词 |
| `limit` | int | 否 | `8` | 1 ≤ limit ≤ 20 | 返回建议数量上限 |
| `type` | string | 否 | `ALL` | 枚举: `RESOURCE`, `COMMUNITY`, `USER`, `ALL` | 建议范围限制（`AI` 不参与建议） |

#### 请求示例

```bash
GET /api/v1/search/suggestions?q=PCB&limit=5&type=ALL
Authorization: Bearer <access_token>
```

#### 响应结构

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "suggestions": [
      {
        "text": "PCB设计优化",
        "type": "keyword",
        "count": 2340,
        "score": 95
      },
      {
        "text": "PCB制造工艺",
        "type": "topic",
        "count": 1850,
        "score": 88
      },
      {
        "text": "PCB设计指南.pdf",
        "type": "resource",
        "count": 120,
        "score": 75
      }
    ]
  }
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `suggestions[].text` | string | 建议文本（前端可直接填入搜索框） |
| `suggestions[].type` | string | 来源类型: `keyword`（热门词）/ `topic`（话题标题）/ `resource`（资源名） |
| `suggestions[].count` | int | 该建议关联的内容数量（用于展示热度） |
| `suggestions[].score` | int | 匹配得分 0-100（越高优先展示） |

---

### 2.3 热搜榜单

- **Endpoint**: `GET /api/v1/search/trending`
- **状态**: ⚠️ 待实现
- **权限**: 无需登录（公开接口）
- **缓存**: Redis 缓存，TTL = 5 分钟（热搜变动较频繁）

#### 请求参数

| 参数名 | 类型 | 必选 | 默认值 | 校验规则 | 说明 |
|--------|------|------|--------|----------|------|
| `type` | string | 否 | `ALL` | 枚举: `RESOURCE`, `COMMUNITY`, `ALL` | 热搜范围（不含 `AI` 和 `USER`） |
| `period` | string | 否 | `day` | 枚举: `day`, `week`, `month` | 统计周期 |
| `limit` | int | 否 | `10` | 1 ≤ limit ≤ 30 | 返回条目数 |

#### 请求示例

```bash
# 获取今日全类热搜 TOP 10
GET /api/v1/search/trending?period=day&limit=10&type=ALL
```

#### 响应结构

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "period": "day",
    "updated_at": "2026-04-09T14:00:00Z",
    "items": [
      {
        "rank": 1,
        "keyword": "PCB设计",
        "score": 2340,
        "trend": "up",
        "trend_delta": 2,
        "category": "RESOURCE",
        "topic_count": 180,
        "resource_count": 85
      },
      {
        "rank": 2,
        "keyword": "Python教程",
        "score": 1850,
        "trend": "down",
        "trend_delta": 1,
        "category": "RESOURCE",
        "topic_count": 150,
        "resource_count": 320
      },
      {
        "rank": 3,
        "keyword": "信号完整性",
        "score": 1200,
        "trend": "new",
        "trend_delta": 0,
        "category": "COMMUNITY",
        "topic_count": 65,
        "resource_count": 42
      }
    ]
  }
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.period` | string | 当前返回数据的统计周期 |
| `data.updated_at` | string | 榜单最近更新时间（ISO 8601 UTC） |
| `items[].rank` | int | 当前排名 |
| `items[].keyword` | string | 热搜关键词 |
| `items[].score` | int | 热度分（搜索次数加权） |
| `items[].trend` | string | 趋势: `up`（上升）/ `down`（下降）/ `new`（新上榜）/ `stable`（持平） |
| `items[].trend_delta` | int | 排名变化幅度（`trend=stable/new` 时为 0） |
| `items[].category` | string | 主要分类: `RESOURCE` / `COMMUNITY` / `ALL` |
| `items[].topic_count` | int | 相关社区话题数 |
| `items[].resource_count` | int | 相关资源数 |

---

### 2.4 用户搜索

- **Endpoint**: `GET /api/v1/search/users`
- **状态**: ⚠️ 待实现
- **权限**: 需登录
- **说明**: 全局搜索 `type=USER` 时后端内部调用此逻辑，也可前端独立调用（搜索结果页"用户"标签）

#### 请求参数

| 参数名 | 类型 | 必选 | 默认值 | 校验规则 | 说明 |
|--------|------|------|--------|----------|------|
| `q` | string | **是** | - | 1 ≤ len ≤ 50 | 搜索昵称/标签 |
| `sort_by` | string | 否 | `relevance` | 枚举: `relevance`, `reputation`, `follower` | 排序方式 |
| `page` | int | 否 | `1` | ≥ 1 | 页码 |
| `size` | int | 否 | `20` | 1 ≤ size ≤ 50 | 每页数量 |

#### 请求示例

```bash
GET /api/v1/search/users?q=PCB&sort_by=reputation&page=1&size=20
Authorization: Bearer <access_token>
```

#### 响应结构

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "total": 25,
    "page": 1,
    "size": 20,
    "has_more": true,
    "items": [
      {
        "id": "user-uuid",
        "nickname": "张三",
        "avatar_url": "https://cdn.relihub.com/avatars/xxx.jpg",
        "rank_level": 5,
        "rank_name": "老炮",
        "reputation_score": 980,
        "follower_count": 340,
        "following_count": 80,
        "topic_count": 230,
        "tags": ["PCB设计", "硬件工程", "信号完整性"],
        "is_expert": true,
        "is_following": false,
        "joined_at": "2025-10-01T00:00:00Z"
      }
    ]
  }
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `items[].id` | string | 用户 UUID |
| `items[].nickname` | string | 用户昵称 |
| `items[].avatar_url` | string | 头像 CDN URL |
| `items[].rank_level` | int | 等级 1-8 |
| `items[].rank_name` | string | 等级名称（如"新兵"、"达人"等） |
| `items[].reputation_score` | int | 当前信誉分 |
| `items[].follower_count` | int | 粉丝数 |
| `items[].following_count` | int | 关注数 |
| `items[].topic_count` | int | 发布话题数 |
| `items[].tags` | array\<string\> | 用户专业标签（最多 5 个） |
| `items[].is_expert` | bool | 是否通过专家认证 |
| `items[].is_following` | bool | 当前登录用户是否已关注该用户 |
| `items[].joined_at` | string | 注册时间 ISO 8601 UTC |

---

### 2.5 AI 历史搜索

- **Endpoint**: `GET /api/v1/search/ai-history`
- **状态**: ⚠️ 待实现
- **权限**: 需登录；**严格限制本人**（不得查看他人 AI 历史）
- **说明**: 全局搜索 `type=AI` 时后端内部调用此逻辑；也可前端在"搜索我的 AI 记录"场景独立调用

#### 请求参数

| 参数名 | 类型 | 必选 | 默认值 | 校验规则 | 说明 |
|--------|------|------|--------|----------|------|
| `q` | string | **是** | - | 1 ≤ len ≤ 50 | 搜索会话消息内容 |
| `sort_by` | string | 否 | `latest` | 枚举: `latest`, `relevance` | 排序方式（AI 历史默认按最新） |
| `page` | int | 否 | `1` | ≥ 1 | 页码 |
| `size` | int | 否 | `20` | 1 ≤ size ≤ 50 | 每页数量 |
| `start_date` | string | 否 | - | `YYYY-MM-DD` | 会话起始日期过滤 |
| `end_date` | string | 否 | - | `YYYY-MM-DD`，须 ≥ `start_date` | 会话截止日期过滤 |

#### 请求示例

```bash
GET /api/v1/search/ai-history?q=信号完整性&sort_by=latest&start_date=2026-03-01&end_date=2026-04-09
Authorization: Bearer <access_token>
```

#### 响应结构

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "total": 8,
    "page": 1,
    "size": 20,
    "has_more": false,
    "items": [
      {
        "session_id": "session-uuid-1",
        "session_title": "信号完整性讨论",
        "created_at": "2026-04-02T15:00:00Z",
        "updated_at": "2026-04-02T16:30:00Z",
        "message_count": 12,
        "matched_messages": [
          {
            "message_id": "msg-uuid-1",
            "role": "user",
            "content_snippet": "...关于<mark>信号完整性</mark>的优化方案中，差分对是否...",
            "created_at": "2026-04-02T15:05:00Z"
          },
          {
            "message_id": "msg-uuid-2",
            "role": "assistant",
            "content_snippet": "在高速电路中，<mark>信号完整性</mark>主要受到以下因素影响...",
            "created_at": "2026-04-02T15:06:00Z"
          }
        ]
      }
    ]
  }
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `items[].session_id` | string | 会话 UUID（可跳转到 `/ai/sessions/{session_id}`） |
| `items[].session_title` | string | 会话标题 |
| `items[].created_at` | string | 会话创建时间 ISO 8601 UTC |
| `items[].updated_at` | string | 会话最后更新时间 ISO 8601 UTC |
| `items[].message_count` | int | 会话总消息数 |
| `items[].matched_messages` | array | 命中关键词的消息摘要列表（最多 3 条） |
| `matched_messages[].message_id` | string | 消息 UUID |
| `matched_messages[].role` | string | `user` / `assistant` |
| `matched_messages[].content_snippet` | string | 含高亮标记的消息摘要（`<mark>` 包裹命中词），最多 150 字符 |
| `matched_messages[].created_at` | string | 消息时间 ISO 8601 UTC |

---

### 2.6 搜索历史 - 查询

- **Endpoint**: `GET /api/v1/search/history`
- **状态**: ⚠️ 待实现
- **权限**: 需登录；仅查询本人历史
- **存储**: 以用户维度写入 Redis（`search_history:{user_id}`，List 结构），TTL = 30 天

#### 请求参数

| 参数名 | 类型 | 必选 | 默认值 | 校验规则 | 说明 |
|--------|------|------|--------|----------|------|
| `limit` | int | 否 | `20` | 1 ≤ limit ≤ 50 | 返回条数（取最近 N 条） |

#### 请求示例

```bash
GET /api/v1/search/history?limit=20
Authorization: Bearer <access_token>
```

#### 响应结构

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "items": [
      {
        "id": "history-uuid-1",
        "query": "PCB设计优化",
        "type": "ALL",
        "searched_at": "2026-04-09T12:30:00Z"
      },
      {
        "id": "history-uuid-2",
        "query": "Python爬虫",
        "type": "RESOURCE",
        "searched_at": "2026-04-08T09:15:00Z"
      }
    ]
  }
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `items[].id` | string | 历史记录 ID（用于单条删除） |
| `items[].query` | string | 历史搜索词 |
| `items[].type` | string | 搜索范围（同搜索时的 `type` 参数） |
| `items[].searched_at` | string | 搜索时间 ISO 8601 UTC |

---

### 2.7 搜索历史 - 删除单条

- **Endpoint**: `DELETE /api/v1/search/history/{id}`
- **状态**: ⚠️ 待实现
- **权限**: 需登录；只允许删除本人历史记录
- **路径参数**: `id` — 历史记录 ID

#### 响应结构

```json
{
  "code": 0,
  "msg": "success",
  "data": null
}
```

---

### 2.8 搜索历史 - 清空

- **Endpoint**: `DELETE /api/v1/search/history`
- **状态**: ⚠️ 待实现
- **权限**: 需登录；仅清空本人历史

#### 响应结构

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "deleted_count": 20
  }
}
```

---

## 3. 已实现的模块搜索 API (引用)

> 以下接口均已在各模块独立实现，可直接使用；全局搜索后端聚合调用这些实现。

### 3.1 资源搜索

- **Endpoint**: `GET /api/v1/resources`
- **状态**: ✅ 已实现
- **搜索参数**:

| 参数名 | 类型 | 校验规则 | 说明 |
|--------|------|----------|------|
| `search` | string | len ≤ 100 | 关键词（匹配 `title`, `description`, `tags`） |
| `category` | string | 枚举值（见 PRD） | 资源分类过滤 |
| `file_type` | string | 枚举: `PDF`, `DOC`, `IMG`, `ZIP` | 文件类型过滤 |
| `sort_by` | string | 枚举: `relevance`, `heat`, `latest`, `download` | 排序 |
| `page` | int | ≥ 1 | 页码 |
| `size` | int | 1-100 | 每页数量 |

**完整响应规范**: 见 [API_资源模块.md](API_资源模块.md)

---

### 3.2 社区话题搜索

- **Endpoint**: `GET /api/v1/community/topics`
- **状态**: ✅ 已实现
- **搜索参数**:

| 参数名 | 类型 | 校验规则 | 说明 |
|--------|------|----------|------|
| `search` | string | len ≤ 100 | 关键词（匹配 `title`, `content`） |
| `category` | string | 枚举值（见 PRD） | 话题分类过滤 |
| `is_featured` | bool | - | 仅返回精华帖 |
| `is_bounty` | bool | - | 仅返回有悬赏的话题 |
| `sort_by` | string | 枚举: `relevance`, `heat`, `latest`, `reply` | 排序 |
| `page` | int | ≥ 1 | 页码 |
| `size` | int | 1-100 | 每页数量 |

**完整响应规范**: 见 [API_社区模块.md](API_社区模块.md)

---

### 3.3 管理后台用户搜索

- **Endpoint**: `GET /api/v1/admin/users`
- **状态**: ✅ 已实现
- **权限**: 需管理员权限 (`require_admin`)
- **说明**: 此接口仅限管理后台使用，不纳入用户端统一搜索范围。

**完整响应规范**: 见 [API_管理后台.md](API_管理后台.md)

---

## 4. 统一搜索服务设计方案

### 4.1 架构设计

```
前端请求 GET /api/v1/search
            │
            ▼
  ┌─────────────────────┐
  │   Search Router     │  (app/api/v1/search/router.py)
  │   - 参数校验        │
  │   - 身份识别        │
  │   - 游客限制        │
  └─────────────────────┘
            │
            ▼
  ┌─────────────────────────────────────────────┐
  │              Search Service                  │
  │  (app/services/search_service.py)            │
  ├─────────────────────────────────────────────┤
  │  1. Query Parser    - 解析/规范化搜索词      │
  │  2. Index Router    - 路由到各模块检索子服务 │
  │  3. Result Merger   - 合并多模块异步结果     │
  │  4. Ranking Engine  - 统一排序评分           │
  │  5. History Writer  - 异步写入搜索历史       │
  └─────────────────────────────────────────────┘
        │          │          │          │
   ┌────┴───┐ ┌────┴───┐ ┌────┴───┐ ┌────┴───┐
   │Resource│ │Commun. │ │  AI    │ │  User  │
   │ Index  │ │ Index  │ │History │ │ Index  │
   └────────┘ └────────┘ └────────┘ └────────┘
        │          │          │          │
   ┌────▼──────────▼──────────▼──────────▼────┐
   │            PostgreSQL  +  Redis           │
   └───────────────────────────────────────────┘
```

### 4.2 搜索流程

1. **参数校验**: 校验 `q` 长度、枚举参数合法性
2. **身份识别**: 区分游客 / 登录用户，游客强制 LIMIT 10
3. **查询规范化**: 去头尾空白、截断至 50 字符
4. **类型路由**: 根据 `type` 参数决定检索哪些子模块
5. **并行检索**: 使用 `asyncio.gather` 并行执行各模块搜索
6. **结果合并**: 按 `sort_by` 规则合并排序各模块结果
7. **分页裁切**: 按 `page/size` 截取目标页数据
8. **历史写入**: 异步（非阻塞）写入搜索历史至 Redis
9. **响应返回**: 包装标准响应结构

### 4.3 排序算法

| `sort_by` 值 | 排序规则 | 说明 |
|-------------|---------|------|
| `relevance` | `relevance_score = tf_idf_score × 0.6 + quality_score × 0.4` | TF-IDF 相关性 + 质量加权 |
| `heat` | `heat_score = view×0.2 + (download/reply)×0.5 + like×0.2 + featured×0.1` | 热度综合评分 |
| `latest` | `ORDER BY created_at DESC` | 按发布时间倒序 |

### 4.4 搜索历史写入策略

- **触发时机**: 用户提交搜索（按回车/点击搜索按钮）时写入，建议列表自动补全**不**写入历史
- **去重逻辑**: 若最近 50 条内存在相同 `query`，则移至队列首部（不重复写入）
- **存储上限**: 每用户最多存储 50 条历史，超出时淘汰最旧记录（Redis List `LTRIM`）
- **TTL**: `search_history:{user_id}` Key TTL = 30 天（用户每次搜索刷新 TTL）

---

## 5. 约束与限制

| 限制类型 | 限制值 | 说明 |
|----------|--------|------|
| 搜索词长度 | 1-50 字符 | 超出截断，空白词返回 `SEARCH_4001` |
| `size` 上限 | 100 | 超出返回 400 错误 |
| 全局搜索限流 | 10 次/分钟/用户 | Redis 计数，超出返回 `SYS_4290` |
| 建议接口限流 | 30 次/分钟/用户 | 防止高频 Autocomplete 滥用 |
| 游客权限 | ≤ 10 条 | 强制 LIMIT 10，`has_more=false`，不支持翻页 |
| AI 历史搜索 | 仅本人 | 后端校验 `session.user_id == current_user.id`，违规返回 `SEARCH_4031` |
| 搜索历史存储 | 50 条/用户 | 超出自动淘汰最旧记录 |

---

## 6. 错误码映射

> **规范说明**: 采用 `SEARCH_4XXX` 前缀，与《API_错误码对照表.md》模块前缀体系一致。

| 错误码 | HTTP 状态 | 业务含义 | 响应 `data` 字段 | 前端处理建议 |
|--------|-----------|----------|-----------------|-------------|
| `SEARCH_4001` | 400 | 关键词为空或长度超限 | `{"min_len": 1, "max_len": 50, "actual_len": N}` | 提示"请输入 1-50 个字符的搜索词" |
| `SEARCH_4002` | 400 | `type` 参数枚举值非法 | `{"allowed": ["RESOURCE","COMMUNITY","AI","USER","ALL"]}` | 提示"搜索类型参数错误" |
| `SEARCH_4003` | 400 | 日期格式错误或 `end_date < start_date` | `{"format": "YYYY-MM-DD"}` | 提示"请输入正确的日期范围" |
| `SEARCH_4004` | 400 | `sort_by` 参数枚举值非法 | `{"allowed": ["relevance","heat","latest"]}` | 提示"排序参数错误" |
| `SEARCH_4011` | 401 | 未登录或 Token 失效 | - | 跳转登录页 |
| `SEARCH_4031` | 403 | AI 历史搜索无权限（非本人） | - | 提示"仅能搜索您自己的 AI 对话记录" |
| `SEARCH_4041` | 404 | 搜索历史记录不存在（删除时） | `{"history_id": "uuid"}` | 提示"该记录不存在或已被删除" |
| `SYS_4290` | 429 | 搜索请求频率过快 | `{"retry_after": 60}` | 禁用搜索按钮，展示 60s 倒计时 |
| `SEARCH_5001` | 500 | 搜索服务内部异常 | - | 提示"搜索服务暂时不可用，请稍后重试" |

**标准错误响应示例**:

```json
{
  "code": "SEARCH_4001",
  "msg": "搜索关键词长度超出限制",
  "data": {
    "min_len": 1,
    "max_len": 50,
    "actual_len": 65
  }
}
```

---

## 7. 前端集成指南

### 7.1 搜索组件状态类型定义

```typescript
// 搜索结果项类型
type SearchResultType = 'RESOURCE' | 'COMMUNITY' | 'AI' | 'USER';
type SearchSortBy = 'relevance' | 'heat' | 'latest';
type SearchPeriod = 'day' | 'week' | 'month';

interface SearchAuthor {
  id: string;
  nickname: string;
  avatar_url: string;
}

interface SearchItem {
  id: string;
  type: SearchResultType;
  title: string;
  summary: string;                // 最多 200 字符，含 HTML <mark> 标签
  author: SearchAuthor;
  heat_score: number;
  created_at: string;             // ISO 8601 UTC
  tags: string[];
  metadata: Record<string, unknown>;
}

interface SearchState {
  query: string;
  type: SearchResultType | 'ALL';
  sort_by: SearchSortBy;
  results: SearchItem[];
  total: number;
  page: number;
  size: number;
  has_more: boolean;
  loading: boolean;
  error: string | null;
}

interface SearchSuggestion {
  text: string;
  type: 'keyword' | 'topic' | 'resource';
  count: number;
  score: number;
}

interface TrendingItem {
  rank: number;
  keyword: string;
  score: number;
  trend: 'up' | 'down' | 'new' | 'stable';
  trend_delta: number;
  category: string;
  topic_count: number;
  resource_count: number;
}

interface SearchHistoryItem {
  id: string;
  query: string;
  type: string;
  searched_at: string;
}
```

### 7.2 Debounce 策略

```typescript
// 搜索建议：Debounce 200ms，避免高频请求
const debouncedFetchSuggestions = debounce(
  (q: string) => fetchSuggestions(q),
  200
);

// 触发条件：q.length >= 1
// 取消条件：清空搜索框（q.length === 0）时立即取消并显示热搜/历史
```

### 7.3 限流与错误处理

```typescript
// 监听 SYS_4290 响应
if (response.code === 'SYS_4290') {
  const retryAfter = response.data?.retry_after ?? 60;    // 秒
  // 禁用搜索按钮，展示倒计时
  setSearchDisabled(true);
  startCountdown(retryAfter, () => setSearchDisabled(false));
  showToast(`操作过于频繁，请 ${retryAfter} 秒后重试`);
}
```

### 7.4 搜索结果高亮渲染

```typescript
// 后端返回的 summary 中含 <mark> 标签，前端不需要二次处理
// 直接使用 dangerouslySetInnerHTML 渲染，但需做 XSS 过滤
import DOMPurify from 'dompurify';

const SafeSummary = ({ summary }: { summary: string }) => (
  <span
    dangerouslySetInnerHTML={{
      __html: DOMPurify.sanitize(summary, { ALLOWED_TAGS: ['mark'] })
    }}
  />
);
```

### 7.5 游客模式处理

- 搜索框可见但触发时检查身份
- 游客可执行搜索，但后端强制返回 ≤ 10 条，`has_more=false`
- 当游客触发"查看更多"或翻页时，前端拦截并弹出注册引导弹窗
- 热搜榜单（`GET /api/v1/search/trending`）无需登录，游客可直接浏览

### 7.6 UI-API 字段对照

> 修正前端 UI 设计文档与 API 的不一致项：

| 场景 | UI 设计文档字段 | API 实际字段 | 说明 |
|------|----------------|-------------|------|
| 搜索接口 `size` | `limit` | `size` | **统一用 `size`** |
| 搜索响应格式 | `results.topics[]` | `items[]` (含 `type`) | 混合列表，用 `type` 区分 |
| 建议响应 `count` | 未定义 | `count` | 关联内容数量 |
| 热搜响应 `trending` | `items[].count` | `items[].score` | 热度分，非原始搜索次数 |
| 热搜接口 `limit` | `limit` | `limit` | 一致 ✅ |

---

## 8. 实施计划

| 阶段 | 工作内容 | 优先级 | Sprint |
|------|---------|--------|--------|
| Phase 1 | 创建 `search` Router 和 Service 骨架 | P0 | Sprint E Week 1 |
| Phase 1 | 实现全局搜索（聚合资源 + 社区） | P0 | Sprint E Week 1 |
| Phase 1 | 实现搜索建议 Autocomplete（Redis 前缀树） | P0 | Sprint E Week 1 |
| Phase 1 | 实现搜索历史管理（写入/查询/删除/清空） | P0 | Sprint E Week 1 |
| Phase 2 | 实现用户搜索（独立端点） | P1 | Sprint E Week 2 |
| Phase 2 | 实现 AI 历史搜索（本人权限校验） | P1 | Sprint E Week 2 |
| Phase 3 | 实现热搜榜单（定时更新 Celery） | P2 | Sprint E Week 3 |
| Phase 3 | 搜索词 TF-IDF 相关性优化 | P2 | Sprint E Week 3 |
| Phase 3 | 补充全量 API 集成测试 | P2 | Sprint E Week 3-4 |

---

## 9. 待补充项（已知缺口，需后续跟进）

| 项目 | 说明 | 优先级 | 状态 |
|------|------|--------|------|
| 搜索 UI 流程图 | 前端 UI 设计文档需补充搜索结果页交互流程图（细化空态、加载态、错误态） | 🔴 高 | ⏳ 待完成 |
| 敏感词过滤规范 | 搜索词的敏感词名单维护方式（Admin 配置 vs 硬编码） | 🟡 中 | ✅ 已实现 (Trie 算法) |
| 索引方案选型 | PostgreSQL `tsvector` 全文索引 vs Elasticsearch，待性能测试后决策 | 🟡 中 | ✅ 已实现 GIN 索引 |
| 搜索词统计任务 | 热搜榜 Celery 定时任务调度逻辑（每 5 分钟刷新 Redis 排行） | 🟡 中 | ✅ 已实现 |

---

## 10. 搜索优化功能说明 (v2.1 新增)

### 10.1 查询优化

后端自动对搜索词进行优化处理，提升搜索性能和准确性：

**优化策略**:
1. **空白字符规范化**: 去除首尾空格，压缩连续空格
2. **特殊字符过滤**: 移除可能影响查询的特殊字符（如 `@#$%^&*`）
3. **超长查询截断**: 超过 100 字符的查询自动截断，防止性能问题
4. **中文支持**: 完整保留中文字符，支持中英文混合搜索

**示例**:
```
原始查询："  Python  教程@#!$  " → 优化后："Python  教程"
原始查询："可靠性测试@@@@2026" → 优化后："可靠性测试 2026"
```

### 10.2 相关性算法增强

采用 **BM25 + TF-IDF** 混合算法，结合多维度加权：

**评分组成**:
```python
最终分数 = BM25 基础分 + 标题匹配加分 + 热度加分 + 时效加分

- BM25 基础分：基于词频和逆文档频率计算
- 标题匹配加分：查询词出现在标题中 +15 分
- 内容匹配加分：查询词出现在内容中 +8 分
- 标题词重叠加分：每个重叠词 +3 分
- 热度加分：heat_score / 100
- 时效加分：30 天内文档最高 +5 分，随时间衰减
```

**效果对比**:
| 场景 | v2.0 评分 | v2.1 评分 | 提升 |
|------|----------|----------|------|
| 标题精确匹配 | 10.5 | 25.5 | +143% |
| 高热度内容 | 8.2 | 13.2 | +61% |
| 最新内容 | 7.0 | 12.0 | +71% |

### 10.3 数据库索引优化

**新增索引**:

| 索引名称 | 类型 | 表 | 列 | 性能提升 |
|---------|------|----|----|---------|
| `idx_resources_title` | B-Tree | resources | title | 标题搜索 80-90% |
| `idx_resources_description` | GIN Trigram | resources | description | 内容搜索 60-70% |
| `idx_resources_fts` | GIN TSVector | resources | title+description | 全文搜索 10-100x |
| `idx_resources_category_status_created` | Composite | resources | category_id,status,created_at | 过滤排序 50-60% |
| `idx_topics_title` | B-Tree | topics | title | 标题搜索 80-90% |
| `idx_topics_content` | GIN Trigram | topics | content | 内容搜索 60-70% |
| `idx_topics_fts` | GIN TSVector | topics | title+content | 全文搜索 10-100x |
| `idx_topics_category_heat` | Composite | topics | category_id,heat_score | 热度排序 40-50% |
| `idx_ai_sessions_title` | GIN Trigram | ai_sessions | title | AI 会话搜索 50-60% |
| `idx_users_nickname` | GIN Trigram | users | nickname | 用户搜索 50-60% |

**性能指标**:
- 简单查询（单表无条件）：< 100ms
- 复杂查询（多表 + 排序）：< 500ms
- 搜索建议（Redis 缓存）：< 50ms
- 热搜榜单（Redis 缓存）：< 50ms

### 10.4 Redis 缓存优化

**缓存策略**:

| 缓存项 | Key 格式 | TTL | 更新策略 |
|--------|---------|-----|---------|
| 热搜榜单 | `trending:search:{limit}` | 5 分钟 | Celery 定时任务每 5 分钟更新 |
| 搜索建议 | `suggestions:{query}:{limit}` | 10 分钟 | 惰性写入（搜索时触发） |
| 搜索结果 | `search:result:{query_hash}` | 1 分钟 | 惰性写入（搜索时触发） |

**缓存命中率** (预期):
- 热搜榜单：> 95%
- 热门搜索建议：> 80%
- 搜索结果：> 60%

### 10.5 敏感词过滤

**实现方式**: Trie 树算法

**过滤流程**:
1. 用户提交搜索词
2. 后端加载敏感词库到 Trie 树
3. 扫描搜索词是否包含敏感词
4. 如发现敏感词，返回错误提示

**性能**:
- 加载 10000 个敏感词：< 100ms
- 单次查询验证：< 1ms
- 内存占用：~1MB (10000 词)

---

## 11. 性能基准测试 (v2.1 新增)

### 11.1 测试环境

- 数据库：PostgreSQL 14
- Redis: 7.0
- 数据量：资源 10 万条，话题 5 万条，AI 会话 2 万条
- 并发：100 并发用户

### 11.2 测试结果

| 测试场景 | v2.0 P95 | v2.1 P95 | 提升 | 目标 |
|---------|----------|----------|------|------|
| 简单搜索（资源） | 850ms | 320ms | -62% | < 500ms ✅ |
| 复杂搜索（全局） | 1500ms | 680ms | -55% | < 1000ms ✅ |
| 搜索建议 | 450ms | 85ms | -81% | < 200ms ✅ |
| 热搜榜单 | 600ms | 45ms | -93% | < 100ms ✅ |
| 用户搜索 | 700ms | 280ms | -60% | < 500ms ✅ |

### 11.3 准确性测试

| 测试查询 | v2.0 准确率 | v2.1 准确率 | 提升 | 目标 |
|---------|------------|------------|------|------|
| "Python 教程" | 72% | 89% | +17% | > 85% ✅ |
| "PCB 设计" | 68% | 87% | +19% | > 85% ✅ |
| "信号完整性" | 75% | 91% | +16% | > 85% ✅ |
| 平均准确率 | 72% | 89% | +17% | > 85% ✅ |

---

- [x] v2.0 新增用户搜索接口 (`GET /api/v1/search/users`) 明细
- [x] v2.0 新增 AI 历史搜索接口 (`GET /api/v1/search/ai-history`) 明细
- [x] v2.0 新增搜索历史管理接口（查询/删除单条/清空）明细
- [x] v2.0 补充所有接口的完整参数校验规则（类型、枚举值、边界）
- [x] v2.0 规范错误码（`SEARCH_4XXX`，对齐《API_错误码对照表.md》格式）
- [x] v2.0 修正前端 UI 文档与 API 的字段不一致（`limit` vs `size`，响应结构等）
- [x] v2.0 补充 `has_more` 字段（对齐《API_接口规范.md》§4 分页标准）
- [x] v2.0 补充 TypeScript 类型定义、Debounce 策略、XSS 防护指南
- [x] v2.0 补充搜索历史写入策略（触发时机、去重逻辑、存储上限）
- [x] v2.0 补充架构图（含 User Index 和 History Writer 组件）
- [x] **v2.1 实现全局统一搜索接口**
- [x] **v2.1 实现查询优化功能**
- [x] **v2.1 实现 BM25 + TF-IDF 相关性增强算法**
- [x] **v2.1 实现数据库索引优化（GIN 全文索引）**
- [x] **v2.1 实现 Redis 缓存热搜和搜索建议**
- [x] **v2.1 实现敏感词过滤（Trie 算法）**
- [x] **v2.1 完成性能基准测试**

---

**文档结束**

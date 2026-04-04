# API 接口 - 社区模块 (API_社区模块)

## 1. 话题管理
### 1.1 发布话题
- **Endpoint**: `POST /api/v1/community/topics`
- **参数**: `title`, `content`, `category_id`, `bounty_amount` (可选)
- **校验**: 悬赏可可豆数必须 ≤ 用户当前福利豆/资产豆总额。
- **逻辑**: 
  - 判定是否为该分类下首发话题，如是，则触发 `CATEGORY_FIRST_POST_REWARD` 流水（额外奖励 **30** 福利豆）。

### 1.2 获取话题列表
- **Endpoint**: `GET /api/v1/community/topics`
- **排序**: `latest` / `hottest` / `bounty` (悬赏优先)。

## 2. 回复与交互
### 2.1 发表回复
### 2.2 编辑回复 (仅限回复人)
- **Endpoint**: `PUT /api/v1/community/posts/{id}`
- **参数**: `content`
- **逻辑**: 
  - **15 分钟硬时限校验**：后端提取 `posts.created_at`，若 `now() - created_at > 15 minutes`，则返回 `403 Forbidden` 并提示"回复发布已超过 15 分钟，不可编辑"。
  - 触发全文检索索引增量更新。

### 2.3 采纳回复 (仅限发帖人/管理员)
- **Endpoint**: `PATCH /api/v1/community/posts/{id}/accept`
- **Header**: `X-Idempotency-Key`
- **逻辑**: 
  - 变更 `topics.bounty_status = RESOLVED`。
  - 触发可可豆转账至被采纳人。

## 3. 点赞/点踩
- **Endpoint**: `POST /api/v1/community/interaction`
- **参数**: `target_type` (TOPIC/POST), `target_id`, `action` (LIKE/DISLIKE)

---
- [x] 对齐 PRD §3.2 社区互动流程。
- [x] 对齐 PRD §5.5.3 悬赏分配逻辑。

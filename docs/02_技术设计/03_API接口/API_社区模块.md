# API 接口 - 社区模块 (API_社区模块)

## 1. 话题管理

### 1.1 发布话题
- **Endpoint**: `POST /api/v1/community/topics`
- **权限**: 需登录
- **请求体**:
  ```json
  {
    "title": "话题标题",
    "content": "话题内容",
    "category_id": 1,
    "bounty_amount": 100
  }
  ```
- **校验**: 悬赏可可豆数必须 ≤ 用户当前福利豆/资产豆总额。
- **逻辑**: 
  - 判定是否为该分类下首发话题，如是，则触发 `CATEGORY_FIRST_POST_REWARD` 流水（额外奖励 **30** 福利豆）。
- **响应**: `TopicResponse`

### 1.2 获取话题列表
- **Endpoint**: `GET /api/v1/community/topics`
- **参数**:
  - `category_id`: 分类过滤（可选）
  - `search`: 关键字搜索（可选）
  - `sort_by`: 排序字段 `heat_score` / `latest` / `bounty`（默认: heat_score）
  - `page`: 页码，默认 1
  - `page_size`: 每页数量，默认 20
- **响应**: `TopicListResponse`

### 1.3 获取话题详情
- **Endpoint**: `GET /api/v1/community/topics/{topic_id}`
- **响应**: `TopicResponse`
- **逻辑**: 自动增加浏览量

### 1.4 更新话题
- **Endpoint**: `PUT /api/v1/community/topics/{topic_id}`
- **权限**: 仅话题作者
- **请求体**:
  ```json
  {
    "title": "新标题",
    "content": "新内容",
    "category_id": 2
  }
  ```
- **响应**: `TopicResponse`

### 1.5 删除话题
- **Endpoint**: `DELETE /api/v1/community/topics/{topic_id}`
- **权限**: 仅话题作者
- **响应**: `{"message": "Topic deleted successfully"}`

## 2. 回复管理

### 2.1 发表回复
- **Endpoint**: `POST /api/v1/community/topics/{topic_id}/posts`
- **权限**: 需登录
- **请求体**:
  ```json
  {
    "content": "回复内容",
    "parent_id": "父回复ID（可选）"
  }
  ```
- **响应**: `PostResponse`

### 2.2 获取回复列表
- **Endpoint**: `GET /api/v1/community/topics/{topic_id}/posts`
- **参数**:
  - `page`: 页码，默认 1
  - `page_size`: 每页数量，默认 20
- **响应**: `PostListResponse`

### 2.3 删除回复
- **Endpoint**: `DELETE /api/v1/community/posts/{post_id}`
- **权限**: 仅回复作者
- **响应**: `{"message": "Post deleted successfully"}`

### 2.4 采纳回复 (仅限发帖人/管理员)
- **Endpoint**: `POST /api/v1/community/posts/{post_id}/accept`
- **权限**: 仅话题作者
- **逻辑**: 
  - 变更 `topics.bounty_status = RESOLVED`。
  - 触发可可豆转账至被采纳人。
- **响应**: `{"message": "Post accepted as answer"}`

## 3. 点赞互动

### 3.1 点赞回复
- **Endpoint**: `POST /api/v1/community/posts/{post_id}/like`
- **权限**: 需登录
- **响应**: `{"message": "Post liked"}`

---
- [x] 对齐 PRD §3.2 社区互动流程。
- [x] 对齐 PRD §5.5.3 悬赏分配逻辑。
- [x] 对齐代码实现：端点路径已与 `app/api/v1/community/router.py` 同步。
- [x] 新增端点：话题详情、更新话题、删除话题、回复列表、删除回复、点赞回复。

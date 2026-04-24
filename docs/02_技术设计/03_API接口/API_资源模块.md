# API 接口 - 资源模块 (API_资源模块)

## 1. 资源列表与检索
- **Endpoint**: `GET /api/v1/resources`
- **参数**: 
  - `category_id`: 分类过滤（可选）
  - `search`: 关键字搜索（可选）
  - `sort_by`: 排序字段 `heat_score` / `latest`（默认: heat_score）
  - `page`: 页码，默认 1
  - `page_size`: 每页数量，默认 20
- **响应**: `ResourceListResponse`

## 2. 资源创建与管理

### 2.1 创建资源
- **Endpoint**: `POST /api/v1/resources`
- **权限**: 需登录
- **请求体**:
  ```json
  {
    "title": "资源标题",
    "description": "资源描述",
    "category_id": 1,
    "price": 10,
    "file_uuid": "文件UUID",
    "tags": ["标签1", "标签2"]
  }
  ```
- **逻辑**: 写入 `resources` 表，初始状态 `SCANNING`，等待审核。
- **响应**: `ResourceResponse`

### 2.2 获取资源详情
- **Endpoint**: `GET /api/v1/resources/{resource_id}`
- **响应**: `ResourceResponse`

### 2.3 更新资源
- **Endpoint**: `PUT /api/v1/resources/{resource_id}`
- **权限**: 仅资源上传者
- **请求体**:
  ```json
  {
    "title": "新标题",
    "description": "新描述",
    "category_id": 2,
    "price": 15
  }
  ```
- **响应**: `ResourceResponse`

### 2.4 删除资源
- **Endpoint**: `DELETE /api/v1/resources/{resource_id}`
- **权限**: 仅资源上传者
- **逻辑**: 软删除，设置 `is_deleted = true`
- **响应**: `{"message": "Resource deleted successfully"}`

## 3. 资源下载

### 3.1 下载资源
- **Endpoint**: `POST /api/v1/resources/{resource_id}/download`
- **权限**: 需登录
- **Header**: `X-Idempotency-Key` (用于防止重复扣费)
- **逻辑**: 
  - **基础资源判定**: 若 `resources.is_seed = true`：
    - 检查用户当前权益额度（`users.rank` 对应额度）。
    - 若额度充足：下载成功，记录 `user_download_entitlements` (扣减权益次数)，扣费 0。
    - 若额度不足：按资源 `price` 进行扣费（优先福利豆）。
  - **普通资源判定**: 提示用户按 `price` 扣费。
  - **重下载检查**: 查询 `user_download_entitlements`。若在 1 年内且 `retries_left > 0`，直接减 1 次后下发链接，不触发扣款。
  - **余额检查**: 若需付费，检查总余额 (优先福利豆)。
  - **分账**: 按照 70/30 逻辑触发流水，并初始化 `user_download_entitlements`。
  - 返回 OSS 短效下载链接。
- **响应**: `{"message": "Download initiated", "resource_id": "xxx"}`

## 4. 资源审核

### 4.1 审核资源
- **Endpoint**: `POST /api/v1/resources/{resource_id}/review`
- **权限**: 管理员
- **请求体**:
  ```json
  {
    "status": "APPROVED/REJECTED/BLOCKED",
    "reason": "审核原因"
  }
  ```
- **响应**: `ResourceResponse`

## 5. 资源互动

### 5.1 增加浏览量
- **Endpoint**: `POST /api/v1/resources/{resource_id}/view`
- **响应**: `{"message": "View count incremented"}`

---
- [x] 对齐 PRD §3.1 资源模块流程。
- [x] 对齐代码实现：端点路径已与 `app/api/v1/resources/router.py` 同步。
- [x] 下载端点方法调整为 POST（支持幂等性 Header）。

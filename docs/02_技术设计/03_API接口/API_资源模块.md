# API 接口 - 资源模块 (API_资源模块)

## 1. 资源列表与检索
- **Endpoint**: `GET /api/v1/resources`
- **参数**: 
  - `keyword`: 关键字
  - `category_id`: 分类过滤
  - `sort_by`: `latest` / `hottest` (默认: hottest)
  - `tag`: 标签过滤

## 2. 资源上传 (两阶段)
### 2.1 请求预签名 URL
- **Endpoint**: `POST /api/v1/resources/upload-init`
- **参数**: `filename`, `file_size`, `md5_hash`
- **校验**: 
  - `dup_upload_count` 入口硬拦截 (403)。
  - **秒传校验**: 对全平台**所有状态**的 MD5 进行比对。若 MD5 存在且 `ref_counts` > 0，直接返回成功。

### 2.2 提交元数据
- **Endpoint**: `POST /api/v1/resources`
- **参数**: `title`, `description`, `price`, `file_uuid`, `category_id`
- **逻辑**: 写入 `resources` 表，初始状态 `SCANNING`。
  - 管理员可勾选 `is_seed=true` 标识。
  - (*注：后续人工审核通过时，系统需判定首发分类情况，若为首发则触发 `CATEGORY_FIRST_POST_REWARD` 流水，额外奖励 30 福利豆。*)

## 3. 资源详情与下载
### 3.1 获取详情
- **Endpoint**: `GET /api/v1/resources/{id}`

### 3.2 下载请求
- **Endpoint**: `GET /api/v1/resources/{id}/download`
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

---
- [x] 对齐 PRD §3.1 资源模块流程。
- [x] 整合秒传与重复上传硬拦截逻辑。

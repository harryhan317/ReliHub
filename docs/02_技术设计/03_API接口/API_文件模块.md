# API 接口 - 文件模块 (API_文件模块)

## 1. 核心流程 (对齐 DB_文件元数据.md)

### 1.1 秒传预检
- **Endpoint**: `POST /api/v1/files/prescan`
- **参数**: `md5_hash`
- **返回**: `hit: boolean`, `file_uuid: uuid` (如命中)。

### 1.2 获取上传凭证 (STS)
- **Endpoint**: `POST /api/v1/files/upload-sts`
- **参数**: `usage_type` (枚举: RESOURCE / AI_ATTACHMENT / FEEDBACK)
- **拦截**: 【对齐 PRD_MVP_爱问模块】若 `usage_type` 为 `AI_ATTACHMENT` 且当前请求用户等级 `rank = GUEST`（游客），直接返回 `403 Forbidden`，强拦截游客上传附件（前端将提示请先注册后上传）。
- **返回**: OSS 临时凭证 (AccessKey, Secret, SessionToken)。

### 1.3 文件删除 (逻辑删除)
- **Endpoint**: `DELETE /api/v1/files/{uuid}`
- **联动**: 触发 `ref_counts` 原子扣减。

## 3. 物理强删 (Wipe)
- **Endpoint**: `DELETE /api/v1/files/{uuid}/wipe`
- **逻辑**: 
  - 校验当前用户是否为该引用的发起者。
  - `file_meta.ref_counts` 原子减 1。
  - 立即从逻辑配额中剔除该文件大小。
  - 若 `ref_counts` 归零，异步触发 OSS 物理删除任务。

---
- [x] 对齐 PRD §4.1 文件处理规范。
- [x] 安全约束：禁止前端直传未经后端预检的文件。

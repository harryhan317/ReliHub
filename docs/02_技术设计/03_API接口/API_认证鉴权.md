# API 接口 - 认证鉴权 (API_认证鉴权)

## 1. 业务流程
 ReliHub 采用 **JWT 后端鉴权 + 微信授权/手机号验证码** 方案。

## 2. 接口列表

### 1.1 手机号注册/登录
- **Endpoint**: `POST /api/v1/auth/register`
- **参数**: `phone`, `code`, `password`, `agreed_to_terms` (Boolean)
- **校验**: 
  - `agreed_to_terms` 必须为 True，否则返回 `AUTH_4005`。
  - 验证码校验。
- **逻辑**: 
  - 成功后自动关联“新兵”等级。
  - 异步任务记录注册 IP 与设备指纹。

### 1.2 账号密码登录
- **Endpoint**: `POST /api/v1/auth/login`
- **参数**: `username/phone`, `password`, `device_fingerprint`
- **逻辑**: 
  - 验证成功返回 JWT。
  - **3D 频率限制**: 针对手机号、IP、`device_fingerprint` 执行 Redis 滑动窗口限流 (60s/次, 10次/日)。
  - **登录审计**: 异步更新 `users.last_login_ip` 和 `users.last_login_device`，并触发异地登录检测告警任务。
- **响应**: 成功返回 `access_token` 与 `user_info` (包含 `nickname`, `avatar_url`, `is_reward_triggered`, `rank` 等核心字段)。

### 2.3 微信授权登录
- **Endpoint**: `POST /api/v1/auth/wechat-login`
- **参数**: `code` (小程序/H5 授权码)
- **响应**: 成功返回 `access_token` (附带 `user_info` 包含 `is_reward_triggered`) 或提示前往注册流程。

### 2.4 Token 续期
- **Endpoint**: `POST /api/v1/auth/refresh`
- **认证**: 携带有效期内的 `refresh_token`。

### 2.5 退出登录
- **Endpoint**: `POST /api/v1/auth/logout`
- **动作**: 后端记录 Token 加入黑名单 (Redis)，前端清除 LocalStorage。

## 3. 错误处理
- `401`: Token 无效或不存在。
- `403`: 手机号被拉黑或管理员锁定。

---
## 4. 权限与等级（RBAC）附加说明
- **专家降级兜底（FROZEN 防御）**: 对于被管理员标注为 `FROZEN`（冻结专家资格）的用户，服务端验证中间件（Middleware）校验权限时，**不得**因其失去专家特权而连带否决其**达人/常客**操作权。其底层通用配额与权限控制需向下降级，并继续由 `users.reputation_points` 动态映射出的信誉分段位接管代理。

- [x] 对齐 PRD §3.1 登录注册：手机号/微信。
- [x] 对齐 PRD §4.3 安全：JWT 隔离。
- [x] 对齐 PRD §4.2.4 专家冻结态降级隔离逻辑。

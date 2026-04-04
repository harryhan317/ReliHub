# API 接口 - 规范说明 (API_接口规范)

## 1. 基础信息
- **Base URL**: `/api/v1`
- **传输格式**: `application/json; charset=utf-8`
- **字符编码**: `UTF-8`

## 2. 通用响应结构
```json
{
  "code": 0,          // 业务码: 0-成功, 非0-失败码
  "data": {},         // 核心数据负载
  "msg": "success"    // 提示信息
}
```

## 3. 业务错误码规范
| 错误码 | 描述 | 建议动作 |
|-------|------|---------|
| `AUTH_4001` | 验证码错误 | 重新获取 |
| `AUTH_4005` | 未勾选用户协议 | 弹出协议弹窗 |
| `ECON_4001` | 可可豆余额不足 | 引导获取/购买 |
| `RES_4005` | 疑似重复资源 | 弹窗确认是否强制提交 |
| `AI_4003` | Token 额度用尽 | 引导购买套餐 |
| `SYS_5001` | 系统维护中 | 展示维护页面 |

## 4. 标准业务码 (对齐《API_错误码对照表.md》)
- `0`: 请求成功。
- `CLIENT_PARAMS_ERROR`: 客户端请求参数错误 (400)。
- `AUTH_UNAUTHORIZED`: 未认证或 Token 已过期 (401)。
- `AUTH_FORBIDDEN`: 权限/等级不足 (403)。
- `QUOTA_EXHAUSTED`: 业务限额超限 (如 AI 额度耗尽, 重复上传封禁) (403)。
- `ADMIN_IP_RESTRICTED`: 管理员 IP 受限 (Admin Login restricted by Subnet) (403)。
- `RESOURCE_NOT_FOUND`: 资源不存在 (404)。
- `INTERNAL_SERVER_ERROR`: 服务器内部错误 (500)。

## 4. 分页标准
- **输入**: `page` (1-indexed), `page_size` (Default: 20)。
- **输出**:
```json
{
  "total": 100,
  "items": [],
  "has_more": true
}
```
```

### 4.1 游客配额强制执行策略

**限制规则**：
- 游客用户（M0）每日最多浏览 10 条精华资源/话题数据（列表或预设展示）。
- **强制执行**：后端在 SQL 层面应用硬限制 `LIMIT 10`。
- **参数解耦**：当检测到当前请求为游客身份时，即便前端恶意传递 `page > 1` 或是 `size > 10`，后端路由也会直接切断参数透传，强制下发最多前 10 条数据缓冲。

**拦截伪代码**：
```python
if current_user.is_guest:
    # 硬限制，忽略前端 page/size
    items = query.limit(10).all()
    has_more = False
else:
    # 正常鉴权用户，开启游标或物理分页
    items = query.paginate(page, size).all()
```

## 5. ID 命名与展示原则 (Dual-ID Policy)
- **技术主键 (PK)**: 后端接口引用、关联查询均使用 `id` (UUID 格式)，确保分布式环境唯一性。
- **业务单号 (Display ID)**：针对工单、订单、通知，需返回 `business_id` (String 格式，如 `FB-202603-0001`) 供用户端展示与客服追溯。

## 5. 时间格式
- **传输层**: 采用 ISO 8601 标准格式字符串: `YYYY-MM-DDTHH:mm:ssZ` (UTC)。
- **业务结算层 (日切防偏离)**: 涉及“每日上限”、“每日签到归零”、“Redis 限流 TTL”等一切按自然天计算的系统级重置动作与定时任务（CronJobs），其底层调度时区**必须强制绑定为北京时间 (`Asia/Shanghai`, UTC+8)**，以杜绝国内外客群业务零点的感知错位。

## 6. 版本管理
- 通过路径区分: `/v1/`, `/v2/`。
- 修改字段名或删除字段必须升级 Main Version。

---
- [x] 对齐 PRD 总体要求：接口规范化。
- [x] 模块化演进支持：Versioned Paths。

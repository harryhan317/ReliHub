# Sprint D 待处理任务清单

**创建日期**: 2026-04-08  
**来源**: 代码库 TODO 注释扫描  
**状态**: 待处理

---

## 1. 概述

本文档记录了代码库中发现的 6 处 TODO 注释，这些注释与测试数据库迁移工作无直接关联，已标记为 Sprint D 的待处理任务。

---

## 2. 任务清单

### 2.1 任务 1: 账本管理权限检查

| 属性 | 详情 |
|------|------|
| **任务ID** | TODO-001 |
| **文件路径** | `backend/app/api/v1/ledger/router.py` |
| **行号** | 165 |
| **优先级** | 🔴 高 |
| **类型** | 安全 |

**原始注释**:
```python
TODO: Add admin permission check
```

**上下文**:
```python
@router.post("/admin/grant")
def grant_beans(
    ...
):
    """
    Grant beans to a user (admin only).
    
    TODO: Add admin permission check
    """
```

**问题描述**:
`/admin/grant` 端点缺少管理员权限验证，可能导致未授权用户执行敏感操作。

**建议解决方案**:
1. 添加 `require_admin` 依赖到路由装饰器
2. 在函数参数中添加 `admin: dict = Depends(require_admin)`
3. 参考其他管理端点的实现方式

**示例修复**:
```python
@router.post("/admin/grant")
def grant_beans(
    ...,
    admin: dict = Depends(require_admin)  # 添加管理员验证
):
    """
    Grant beans to a user (admin only).
    """
```

---

### 2.2 任务 2: 资源审核权限检查

| 属性 | 详情 |
|------|------|
| **任务ID** | TODO-002 |
| **文件路径** | `backend/app/api/v1/resources/router.py` |
| **行号** | 149 |
| **优先级** | 🔴 高 |
| **类型** | 安全 |

**原始注释**:
```python
TODO: Add admin permission check
```

**上下文**:
```python
@router.post("/{resource_id}/review")
def review_resource(
    ...
):
    """
    Review a resource (admin only).
    
    TODO: Add admin permission check
    """
```

**问题描述**:
资源审核端点缺少管理员权限验证，可能导致未授权用户审核资源。

**建议解决方案**:
1. 添加 `require_admin` 依赖
2. 记录审核操作日志

---

### 2.3 任务 3: 通知创建权限检查

| 属性 | 详情 |
|------|------|
| **任务ID** | TODO-003 |
| **文件路径** | `backend/app/api/v1/notification/router.py` |
| **行号** | 148 |
| **优先级** | 🔴 高 |
| **类型** | 安全 |

**原始注释**:
```python
TODO: Add admin permission check
```

**上下文**:
```python
@router.post("/admin/create")
def create_notification(
    ...
):
    """
    Create a notification for a user (admin only).
    
    TODO: Add admin permission check
    """
```

**问题描述**:
通知创建端点缺少管理员权限验证。

**建议解决方案**:
添加管理员权限验证依赖。

---

### 2.4 任务 4: 广播通知权限检查

| 属性 | 详情 |
|------|------|
| **任务ID** | TODO-004 |
| **文件路径** | `backend/app/api/v1/notification/router.py` |
| **行号** | 168-169 |
| **优先级** | 🔴 高 |
| **类型** | 安全 + 功能 |

**原始注释**:
```python
TODO: Add admin permission check
TODO: Implement fan-out to all users
```

**上下文**:
```python
@router.post("/admin/broadcast")
def broadcast_notification(
    ...
):
    """
    Broadcast notification to all users (admin only).
    
    TODO: Add admin permission check
    TODO: Implement fan-out to all users
    """
```

**问题描述**:
1. 缺少管理员权限验证
2. 广播功能未实现，需要向所有用户发送通知

**建议解决方案**:
1. 添加管理员权限验证
2. 实现用户遍历和批量通知创建逻辑
3. 考虑使用后台任务处理大量用户通知

**示例实现**:
```python
@router.post("/admin/broadcast")
def broadcast_notification(
    ...,
    admin: dict = Depends(require_admin)
):
    users = db.query(User).filter(User.status == 'ACTIVE').all()
    for user in users:
        notification = Notification(
            receiver_id=user.id,
            ...
        )
        db.add(notification)
    db.commit()
```

---

### 2.5 任务 5: Token 黑名单迁移至 Redis

| 属性 | 详情 |
|------|------|
| **任务ID** | TODO-005 |
| **文件路径** | `backend/app/services/auth_service.py` |
| **行号** | 32 |
| **优先级** | 🟡 中 |
| **类型** | 性能 + 可靠性 |

**原始注释**:
```python
# WARNING [Production TODO]: Replace with Redis SET + TTL matching token expiry.
#   Key pattern: "token_blacklist:{jti}", TTL = ACCESS_TOKEN_EXPIRE_MINUTES * 60
#   This ensures blacklisted tokens are auto-cleaned after expiry.
```

**上下文**:
```python
# ── In-memory token blacklist ────────────────────────────────────────────────
# WARNING [Production TODO]: Replace with Redis SET + TTL matching token expiry.
#   Key pattern: "token_blacklist:{jti}", TTL = ACCESS_TOKEN_EXPIRE_MINUTES * 60
#   This ensures blacklisted tokens are auto-cleaned after expiry.
_token_blacklist: set[str] = set()
```

**问题描述**:
当前 Token 黑名单使用内存存储，存在以下问题：
1. 服务重启后黑名单丢失
2. 多实例部署时黑名单不同步
3. 无法自动清理过期 Token

**建议解决方案**:
1. 使用 Redis SET 存储黑名单
2. 设置 TTL 自动过期
3. 实现分布式黑名单共享

**示例实现**:
```python
import redis

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def add_to_blacklist(jti: str, expires_in: int):
    key = f"token_blacklist:{jti}"
    redis_client.setex(key, expires_in, "1")

def is_blacklisted(jti: str) -> bool:
    key = f"token_blacklist:{jti}"
    return redis_client.exists(key) > 0
```

---

## 3. 任务优先级汇总

| 任务ID | 描述 | 优先级 | 类型 | 预估工时 |
|--------|------|--------|------|----------|
| TODO-001 | 账本管理权限检查 | 🔴 高 | 安全 | 1h |
| TODO-002 | 资源审核权限检查 | 🔴 高 | 安全 | 1h |
| TODO-003 | 通知创建权限检查 | 🔴 高 | 安全 | 1h |
| TODO-004 | 广播通知实现 | 🔴 高 | 安全+功能 | 3h |
| TODO-005 | Token黑名单Redis迁移 | 🟡 中 | 性能 | 4h |
| **总计** | - | - | - | **10h** |

---

## 4. Sprint D 规划建议

### 4.1 迭代目标

1. **安全性增强**: 完成 TODO-001 ~ TODO-004 的权限检查实现
2. **性能优化**: 完成 TODO-005 的 Redis 迁移
3. **测试覆盖**: 为所有修改添加测试用例

### 4.2 里程碑

| 阶段 | 任务 | 预计完成 |
|------|------|----------|
| 第1周 | TODO-001, TODO-002, TODO-003 | Week 1 |
| 第2周 | TODO-004 | Week 2 |
| 第3周 | TODO-005 | Week 3 |
| 第4周 | 测试和验收 | Week 4 |

---

## 5. 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 权限检查遗漏 | 安全漏洞 | 代码审查 + 安全测试 |
| Redis 连接问题 | 服务不可用 | 添加降级策略 |
| 广播性能问题 | 系统负载高 | 使用后台任务 |

---

## 6. 验收标准

### 6.1 权限检查验收

- [ ] 所有管理端点添加 `require_admin` 依赖
- [ ] 未授权访问返回 401 错误
- [ ] 非管理员访问返回 403 错误
- [ ] 添加相关测试用例

### 6.2 Redis 迁移验收

- [ ] Token 黑名单存储在 Redis
- [ ] 过期 Token 自动清理
- [ ] 多实例部署测试通过
- [ ] 性能测试通过

---

## 7. 变更记录

| 日期 | 变更内容 |
|------|----------|
| 2026-04-08 | 初始版本，记录 6 处 TODO 注释 |

---

**文档维护**: 开发团队  
**最后更新**: 2026-04-08

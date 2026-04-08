# API 接口 - 系统管理

**版本**: v1.1  
**更新日期**: 2026-04-08

---

## 1. 启动配置

### 1.1 获取启动配置

**接口名称**: 获取应用启动配置  
**功能描述**: 返回应用启动所需的配置信息

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/system/config/startup` |
| **认证要求** | 无 |
| **权限要求** | 无 |

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "app_min_version": "1.0.0",
  "app_latest_version": "1.1.0",
  "system_status": "Normal",
  "dict_categories": [
    "user_type",
    "resource_status",
    "notification_type"
  ]
}
```

---

## 2. 健康检查

### 2.1 快速健康检查

**接口名称**: 快速健康检查  
**功能描述**: 快速检查系统基本健康状态，用于负载均衡器存活探针

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/health` |
| **认证要求** | 无 |
| **权限要求** | 无 |

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-08T10:30:00Z",
  "uptime_seconds": 3600.5,
  "components": [
    {
      "name": "database",
      "healthy": true,
      "timestamp": "2026-04-08T10:30:00Z",
      "details": {
        "type": "postgresql",
        "latency_ms": 2.5,
        "status": "connected"
      }
    },
    {
      "name": "redis",
      "healthy": true,
      "timestamp": "2026-04-08T10:30:00Z",
      "details": {
        "latency_ms": 1.2,
        "status": "connected",
        "metrics": {
          "total_operations": 1500,
          "failed_operations": 2,
          "reconnect_count": 0
        }
      }
    }
  ]
}
```

**部分组件不健康 (200 OK)**:
```json
{
  "status": "unhealthy",
  "timestamp": "2026-04-08T10:30:00Z",
  "uptime_seconds": 3600.5,
  "components": [
    {
      "name": "database",
      "healthy": true,
      "timestamp": "2026-04-08T10:30:00Z",
      "details": {
        "type": "postgresql",
        "latency_ms": 2.5,
        "status": "connected"
      }
    },
    {
      "name": "redis",
      "healthy": false,
      "timestamp": "2026-04-08T10:30:00Z",
      "details": {
        "status": "disconnected",
        "fallback": "in_memory_storage"
      }
    }
  ]
}
```

---

### 2.2 详细健康检查

**接口名称**: 详细健康检查  
**功能描述**: 检查所有系统组件的详细健康状态，包括系统资源

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/health/detailed` |
| **认证要求** | 无 |
| **权限要求** | 无 |

#### 响应示例

**成功响应 (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-08T10:30:00Z",
  "uptime_seconds": 3600.5,
  "version": "1.0.0",
  "environment": "production",
  "components": [
    {
      "name": "database",
      "healthy": true,
      "timestamp": "2026-04-08T10:30:00Z",
      "details": {
        "type": "postgresql",
        "latency_ms": 2.5,
        "status": "connected"
      }
    },
    {
      "name": "redis",
      "healthy": true,
      "timestamp": "2026-04-08T10:30:00Z",
      "details": {
        "latency_ms": 1.2,
        "status": "connected",
        "metrics": {
          "total_operations": 1500,
          "failed_operations": 2,
          "reconnect_count": 0
        }
      }
    },
    {
      "name": "system_resources",
      "healthy": true,
      "timestamp": "2026-04-08T10:30:00Z",
      "details": {
        "cpu_percent": 45.2,
        "memory_percent": 62.5,
        "memory_available_gb": 3.2,
        "disk_percent": 55.8,
        "disk_free_gb": 120.5
      }
    }
  ],
  "summary": {
    "total_components": 3,
    "healthy_components": 3,
    "unhealthy_components": 0
  }
}
```

**服务不可用 (503 Service Unavailable)**:
```json
{
  "detail": {
    "status": "unhealthy",
    "timestamp": "2026-04-08T10:30:00Z",
    "uptime_seconds": 3600.5,
    "version": "1.0.0",
    "environment": "production",
    "components": [
      {
        "name": "database",
        "healthy": false,
        "timestamp": "2026-04-08T10:30:00Z",
        "details": {
          "error": "Connection refused",
          "status": "disconnected"
        }
      }
    ],
    "summary": {
      "total_components": 3,
      "healthy_components": 2,
      "unhealthy_components": 1
    }
  }
}
```

---

## 3. 监控指标

### 3.1 Prometheus 指标

**接口名称**: 获取 Prometheus 监控指标  
**功能描述**: 返回 Prometheus 格式的应用监控指标

| 属性 | 值 |
|------|-----|
| **请求方法** | GET |
| **URL路径** | `/api/v1/metrics` |
| **认证要求** | 无 |
| **权限要求** | 无 |

#### 响应示例

**成功响应 (200 OK)**:
```
# HELP application_info Application information
# TYPE application_info gauge
application_info{environment="production",version="1.0.0",uptime="3600.5"} 1.0

# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/api/v1/health",method="GET",status="200"} 150

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{endpoint="/api/v1/health",method="GET",le="0.005"} 100
http_request_duration_seconds_bucket{endpoint="/api/v1/health",method="GET",le="0.01"} 120
http_request_duration_seconds_bucket{endpoint="/api/v1/health",method="GET",le="0.025"} 145
http_request_duration_seconds_bucket{endpoint="/api/v1/health",method="GET",le="0.05"} 148
http_request_duration_seconds_bucket{endpoint="/api/v1/health",method="GET",le="0.1"} 150

# HELP redis_operations_total Total Redis operations
# TYPE redis_operations_total counter
redis_operations_total{operation="get",status="success"} 500
redis_operations_total{operation="set",status="success"} 200

# HELP notifications_sent_total Total notifications sent
# TYPE notifications_sent_total counter
notifications_sent_total{priority="NORMAL",type="SYSTEM"} 100

# HELP broadcast_operations_total Total broadcast operations
# TYPE broadcast_operations_total counter
broadcast_operations_total{status="SUCCESS"} 5

# HELP user_registrations_total Total user registrations
# TYPE user_registrations_total counter
user_registrations_total{method="phone"} 50

# HELP user_logins_total Total user logins
# TYPE user_logins_total counter
user_logins_total{status="success"} 200
user_logins_total{status="failure"} 10

# HELP application_errors_total Total application errors
# TYPE application_errors_total counter
application_errors_total{endpoint="/api/v1/auth/login",type="ValueError"} 2
```

#### 可用指标列表

| 指标名称 | 类型 | 说明 |
|---------|------|------|
| `application_info` | Gauge | 应用信息（版本、环境、运行时间） |
| `http_requests_total` | Counter | HTTP 请求总数 |
| `http_request_duration_seconds` | Histogram | HTTP 请求延迟分布 |
| `http_requests_active` | Gauge | 当前活跃的 HTTP 请求数 |
| `database_connections_active` | Gauge | 活跃的数据库连接数 |
| `redis_operations_total` | Counter | Redis 操作总数 |
| `notifications_sent_total` | Counter | 发送的通知总数 |
| `broadcast_operations_total` | Counter | 广播操作总数 |
| `broadcast_duration_seconds` | Histogram | 广播操作持续时间 |
| `user_registrations_total` | Counter | 用户注册总数 |
| `user_logins_total` | Counter | 用户登录总数 |
| `application_errors_total` | Counter | 应用错误总数 |

---

## 4. 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权访问 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用（健康检查失败） |

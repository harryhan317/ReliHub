# API 接口 - 系统管理 (API_系统管理)

## 1. 启动配置
- **Endpoint**: `GET /api/v1/system/config/startup`
- **逻辑**: 
  - 返回 `APP_MIN_VERSION`, `APP_LATEST_VERSION`。
  - 返回常用字典表分类。
  - 返回系统状态 (Normal/Maintenance)。

## 2. 存活探针
- **Endpoint**: `GET /api/v1/health`
- **响应**: `{"status": "UP"}`

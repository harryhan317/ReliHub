# ReliHub 容器化部署指南

## 🚀 快速开始

### 一键部署（生产环境）
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 带初始化的一键部署
```bash
# 启动服务并初始化数据库
docker-compose --profile init up -d

# 等待初始化完成后再启动前端服务
docker-compose up -d web admin
```

### 开发环境部署
```bash
# 启动开发环境（包含自动启动器）
docker-compose --profile dev up -d
```

## 📊 服务访问地址

| 服务 | 访问地址 | 说明 |
|------|----------|------|
| 用户端前端 | http://localhost:3000 | 主要用户界面 |
| 管理后台 | http://localhost:5179 | 系统管理界面 |
| 后端API | http://localhost:8000 | RESTful API接口 |
| API文档 | http://localhost:8000/docs | Swagger UI文档 |
| 数据库 | localhost:5433 | PostgreSQL数据库 |
| Redis缓存 | localhost:6380 | Redis缓存服务 |
| 自动启动器 | http://localhost:8080 | 开发环境自动启动 |

## 🔧 管理命令

### 服务管理
```bash
# 启动服务
docker-compose start

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 重建并启动
docker-compose up -d --build
```

### 数据库管理
```bash
# 进入数据库容器
docker-compose exec db psql -U postgres -d relihub

# 运行数据库迁移
docker-compose run --rm backend-init

# 备份数据库
docker-compose exec db pg_dump -U postgres relihub > backup.sql
```

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs -f backend

# 查看实时日志
docker-compose logs -f --tail=100
```

## ⚙️ 环境配置

### 重要环境变量
编辑 `.env` 文件配置生产环境：

```env
# 数据库配置
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://postgres:your_secure_password@db:5432/relihub

# 安全配置
SECRET_KEY=your_super_secret_key
PHONE_BLIND_INDEX_KEY=your_blind_index_key

# 第三方服务
COS_SECRET_ID=your_cos_secret_id
COS_SECRET_KEY=your_cos_secret_key
```

### 健康检查
所有服务都配置了健康检查，可以通过以下命令验证：

```bash
# 检查服务健康状态
docker-compose ps

# 手动健康检查
curl http://localhost:8000/api/v1/health
curl http://localhost:3000
curl http://localhost:5179
```

## 🛠️ 开发环境

### 开发模式启动
```bash
# 启动开发环境（包含热重载）
docker-compose --profile dev up -d

# 查看开发环境服务
docker-compose --profile dev ps
```

### 代码热重载
前端服务支持热重载，修改代码后会自动重新编译。

## 📈 生产环境部署

### 1. 准备生产环境
```bash
# 创建生产环境目录
mkdir -p /opt/relihub
cd /opt/relihub

# 复制项目文件
cp -r /path/to/relihub/* .

# 设置权限
chown -R 1000:1000 .
```

### 2. 配置生产环境
```bash
# 创建生产环境配置文件
cp .env.example .env

# 编辑生产环境配置
vim .env
```

### 3. 启动生产服务
```bash
# 使用生产环境配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🔒 安全配置

### 防火墙设置
```bash
# 只开放必要端口
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 22/tcp    # SSH
sudo ufw enable
```

### SSL证书配置
使用反向代理（如Nginx）配置SSL证书：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://web:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /admin {
        proxy_pass http://admin:80;
        proxy_set_header Host $host;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
    }
}
```

## 🐛 故障排除

### 常见问题

**1. 服务启动失败**
```bash
# 检查依赖服务是否就绪
docker-compose logs db

# 重新构建镜像
docker-compose build --no-cache
```

**2. 数据库连接问题**
```bash
# 检查数据库状态
docker-compose exec db pg_isready -U postgres

# 重置数据库（开发环境）
docker-compose down -v
docker-compose up -d
```

**3. 端口冲突**
```bash
# 检查端口占用
netstat -tulpn | grep :3000

# 修改docker-compose.yml中的端口映射
```

### 日志分析
```bash
# 查看错误日志
docker-compose logs --tail=50 | grep -i error

# 实时监控
docker-compose logs -f
```

## 📞 支持与维护

### 监控与告警
建议配置以下监控：
- 服务健康状态监控
- 数据库性能监控
- 应用日志监控
- 资源使用监控

### 备份策略
```bash
# 每日数据库备份
0 2 * * * docker-compose exec db pg_dump -U postgres relihub > /backups/relihub_$(date +%Y%m%d).sql

# 每周完整备份
0 3 * * 0 tar -czf /backups/relihub_full_$(date +%Y%m%d).tar.gz /opt/relihub/
```

---

**文档版本**: 1.0  
**最后更新**: 2026-04-21  
**维护团队**: ReliHub开发团队
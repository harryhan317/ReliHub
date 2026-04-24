#!/bin/bash
# ReliHub 一键部署脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker和Docker Compose
check_dependencies() {
    log "检查Docker依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker依赖检查通过"
}

# 停止现有服务
stop_existing_services() {
    log "停止现有服务..."
    
    # 停止可能运行的本地服务
    pkill -f "npm run dev" 2>/dev/null || true
    pkill -f "python.*fastapi" 2>/dev/null || true
    
    # 停止Docker服务
    if docker-compose ps | grep -q "Up"; then
        docker-compose down
        log_success "现有Docker服务已停止"
    else
        log "没有运行中的Docker服务"
    fi
}

# 构建Docker镜像
build_images() {
    log "构建Docker镜像..."
    
    docker-compose build --no-cache
    
    log_success "Docker镜像构建完成"
}

# 初始化数据库
init_database() {
    log "初始化数据库..."
    
    # 等待数据库就绪
    log "等待数据库服务启动..."
    sleep 10
    
    # 运行数据库初始化
    if docker-compose run --rm backend-init; then
        log_success "数据库初始化完成"
    else
        log_error "数据库初始化失败"
        exit 1
    fi
}

# 启动服务
start_services() {
    log "启动所有服务..."
    
    docker-compose up -d
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log "等待服务就绪..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "检查服务健康状态 (尝试 $attempt/$max_attempts)..."
        
        # 检查后端服务
        if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
            log_success "后端服务已就绪"
            
            # 检查前端服务
            if curl -s http://localhost:3000 > /dev/null 2>&1; then
                log_success "前端服务已就绪"
                
                # 检查管理后台
                if curl -s http://localhost:5179 > /dev/null 2>&1; then
                    log_success "管理后台已就绪"
                    break
                fi
            fi
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "服务启动超时，请检查日志"
        docker-compose logs
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "=== ReliHub 部署完成 ==="
    echo ""
    echo "服务访问地址："
    echo "  🔹 用户端前端: http://localhost:3000"
    echo "  🔹 管理后台:   http://localhost:5179"
    echo "  🔹 后端API:    http://localhost:8000"
    echo "  🔹 API文档:    http://localhost:8000/docs"
    echo ""
    echo "管理命令："
    echo "  📊 查看状态: docker-compose ps"
    echo "  📝 查看日志: docker-compose logs -f"
    echo "  ⏹️  停止服务: docker-compose down"
    echo "  🔄 重启服务: docker-compose restart"
    echo ""
    echo "数据库管理："
    echo "  💾 进入数据库: docker-compose exec db psql -U postgres -d relihub"
    echo "  📋 备份数据: docker-compose exec db pg_dump -U postgres relihub > backup.sql"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "🚀 ReliHub 容器化部署脚本"
    echo "=========================="
    echo ""
    
    # 检查当前目录
    if [ ! -f "docker-compose.yml" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行部署步骤
    check_dependencies
    stop_existing_services
    build_images
    start_services
    init_database
    wait_for_services
    show_deployment_info
    
    log_success "ReliHub 部署完成！"
}

# 执行主函数
main "$@"
#!/bin/bash

# =============================================================================
# 🚀 Sprint B 部署脚本
# =============================================================================
# 用途：一键部署 Sprint B 到测试环境
# 使用：./deploy_sprint_b.sh
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_step() {
    echo -e "${BLUE}====> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# =============================================================================
# 步骤 1: 环境检查
# =============================================================================
print_step "步骤 1: 环境检查"

# 检查 Python3
if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装"
    exit 1
fi
print_success "Python3 已安装：$(python3 --version)"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker 未安装"
    exit 1
fi
print_success "Docker 已安装：$(docker --version)"

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose 未安装"
    exit 1
fi
print_success "Docker Compose 已安装：$(docker-compose --version)"

echo ""

# =============================================================================
# 步骤 2: 进入项目目录
# =============================================================================
print_step "步骤 2: 进入项目目录"

cd "$(dirname "$0")"
BACKEND_DIR="$(pwd)"

print_success "后端目录：$BACKEND_DIR"
echo ""

# =============================================================================
# 步骤 3: 检查环境配置
# =============================================================================
print_step "步骤 3: 检查环境配置"

if [ ! -f .env ]; then
    print_warning ".env 文件不存在，正在从 .env.example 创建..."
    cp .env.example .env
    print_success ".env 文件已创建"
    print_warning "请编辑 .env 文件配置正确的环境变量"
    read -p "按回车键继续..."
fi

# 检查关键环境变量
if ! grep -q "DATABASE_URL=" .env; then
    print_error ".env 中缺少 DATABASE_URL"
    exit 1
fi

if ! grep -q "SECRET_KEY=" .env; then
    print_error ".env 中缺少 SECRET_KEY"
    exit 1
fi

print_success "环境配置检查通过"
echo ""

# =============================================================================
# 步骤 4: 启动数据库和 Redis
# =============================================================================
print_step "步骤 4: 启动数据库和 Redis"

docker-compose up -d db redis

# 等待服务启动
print_step "等待服务启动 (10 秒)..."
sleep 10

# 检查容器状态
if ! docker-compose ps | grep -q "Up"; then
    print_error "容器启动失败"
    docker-compose logs
    exit 1
fi

print_success "数据库和 Redis 已启动"
echo ""

# =============================================================================
# 步骤 5: 执行数据库迁移
# =============================================================================
print_step "步骤 5: 执行数据库迁移"

# 检查 Alembic
if ! command -v alembic &> /dev/null; then
    print_warning "Alembic 未全局安装，使用虚拟环境中的 Alembic"
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        print_error "未找到虚拟环境，请先安装依赖"
        exit 1
    fi
fi

# 执行迁移
alembic upgrade head

print_success "数据库迁移完成"
echo ""

# =============================================================================
# 步骤 6: 验证数据库
# =============================================================================
print_step "步骤 6: 验证数据库"

# 创建验证脚本
cat > verify_db.py << 'EOF'
import sys
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/relihub"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # 检查表数量
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        table_count = result.scalar()
        
        # 检查索引数量
        result = conn.execute(text("""
            SELECT COUNT(*) FROM pg_indexes 
            WHERE schemaname = 'public'
        """))
        index_count = result.scalar()
        
        print(f"✅ 数据库连接成功")
        print(f"✅ 数据表数量：{table_count}")
        print(f"✅ 索引数量：{index_count}")
        
        if table_count < 10:
            print("⚠️  警告：数据表数量少于预期")
            sys.exit(1)
            
except Exception as e:
    print(f"❌ 数据库验证失败：{e}")
    sys.exit(1)
EOF

python3 verify_db.py
rm verify_db.py

print_success "数据库验证通过"
echo ""

# =============================================================================
# 步骤 7: 启动应用
# =============================================================================
print_step "步骤 7: 启动应用"

print_warning "即将启动 Uvicorn 服务器..."
print_warning "按 Ctrl+C 停止服务器"
echo ""

# 启动 Uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# =============================================================================
# 部署完成
# =============================================================================
print_success "🎉 Sprint B 部署完成！"
echo ""
echo "访问地址:"
echo "  - API 文档：http://localhost:8000/docs"
echo "  - 健康检查：http://localhost:8000/health"
echo ""

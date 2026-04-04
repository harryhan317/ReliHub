#!/bin/bash

# =============================================================================
# 🚀 Sprint B 快速部署脚本（本地开发环境）
# =============================================================================
# 用途：快速部署到本地开发环境
# 使用：./deploy_local.sh
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

# 检查 pip3
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 未安装"
    exit 1
fi

# 检查关键依赖
print_step "步骤 2: 检查依赖"

# 检查虚拟环境
if [ -d ".venv" ]; then
    print_success "虚拟环境已存在"
    source .venv/bin/activate
else
    print_warning "虚拟环境不存在，正在创建..."
    python3 -m venv .venv
    source .venv/bin/activate
    print_success "虚拟环境已创建"
fi

# 安装依赖
print_step "步骤 3: 安装依赖"
pip install -q -r requirements.txt
print_success "依赖安装完成"

# =============================================================================
# 步骤 4: 检查环境配置
# =============================================================================
print_step "步骤 4: 检查环境配置"

if [ ! -f .env ]; then
    print_warning ".env 文件不存在，正在从 .env.example 创建..."
    cp .env.example .env
    print_success ".env 文件已创建"
    print_warning "请确保 .env 中的数据库连接配置正确"
fi

# 检查关键环境变量
if ! grep -q "DATABASE_URL=" .env; then
    print_error ".env 中缺少 DATABASE_URL"
    exit 1
fi

print_success "环境配置检查通过"

# =============================================================================
# 步骤 5: 检查数据库连接
# =============================================================================
print_step "步骤 5: 检查数据库连接"

# 创建测试脚本
cat > test_db_connection.py << 'EOF'
import sys
from sqlalchemy import create_engine, text

# 从 .env 读取 DATABASE_URL
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL 未配置")
    sys.exit(1)

# 替换 localhost 为 127.0.0.1（避免 socket 问题）
DATABASE_URL = DATABASE_URL.replace('localhost', '127.0.0.1')

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ 数据库连接成功")
        
        # 检查表数量
        result = conn.execute(text("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        table_count = result.scalar()
        print(f"✅ 数据表数量：{table_count}")
        
        if table_count < 10:
            print("⚠️  警告：数据表数量少于预期，可能需要运行迁移")
            
except Exception as e:
    print(f"❌ 数据库连接失败：{e}")
    print("请确保 PostgreSQL 已启动并且配置正确")
    sys.exit(1)
EOF

python3 test_db_connection.py
rm test_db_connection.py

print_success "数据库连接检查通过"

# =============================================================================
# 步骤 6: 执行数据库迁移
# =============================================================================
print_step "步骤 6: 执行数据库迁移"

alembic upgrade head
print_success "数据库迁移完成"

# =============================================================================
# 步骤 7: 启动应用
# =============================================================================
print_step "步骤 7: 启动应用"

print_warning "即将启动 Uvicorn 服务器..."
print_warning "按 Ctrl+C 停止服务器"
print_success "访问地址："
echo "  - API 文档：http://localhost:8000/docs"
echo "  - 健康检查：http://localhost:8000/health"
echo ""

# 启动 Uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# =============================================================================
# 部署完成
# =============================================================================
print_success "🎉 部署完成！"

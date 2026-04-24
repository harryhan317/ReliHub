#!/bin/bash

# =============================================================================
# 🚀 ReliHub 部署脚本
# =============================================================================
# 用途：本地开发/测试环境一键部署
# 使用：./deploy.sh
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装"
    exit 1
fi
print_success "Python3 已安装：$(python3 --version)"

if ! command -v pip3 &> /dev/null; then
    print_error "pip3 未安装"
    exit 1
fi
print_success "pip3 已安装"

echo ""

# =============================================================================
# 步骤 2: 虚拟环境
# =============================================================================
print_step "步骤 2: 虚拟环境检查/创建"

if [ -d ".venv" ]; then
    print_success "虚拟环境已存在"
    source .venv/bin/activate
else
    print_warning "虚拟环境不存在，正在创建..."
    python3 -m venv .venv
    source .venv/bin/activate
    print_success "虚拟环境已创建"
fi
echo ""

# =============================================================================
# 步骤 3: 安装依赖
# =============================================================================
print_step "步骤 3: 安装依赖"

pip install -q -r requirements.txt
print_success "依赖安装完成"
echo ""

# =============================================================================
# 步骤 4: 环境配置
# =============================================================================
print_step "步骤 4: 环境配置检查"

if [ ! -f .env ]; then
    print_warning ".env 文件不存在，正在从 .env.example 创建..."
    cp .env.example .env
    print_success ".env 文件已创建"
    print_warning "请编辑 .env 文件配置正确的环境变量"
fi

if ! grep -q "DATABASE_URL=" .env; then
    print_error ".env 中缺少 DATABASE_URL"
    exit 1
fi

print_success "环境配置检查通过"
echo ""

# =============================================================================
# 步骤 5: 数据库连接验证
# =============================================================================
print_step "步骤 5: 数据库连接验证"

python3 << 'EOF'
import sys
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', '').replace('localhost', '127.0.0.1')

if not DATABASE_URL:
    print("❌ DATABASE_URL 未配置")
    sys.exit(1)

try:
    from sqlalchemy import create_engine, text
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ 数据库连接成功")

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
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    print_error "数据库连接失败，请确保 PostgreSQL 已启动"
    exit 1
fi

print_success "数据库连接检查通过"
echo ""

# =============================================================================
# 步骤 6: 数据库迁移
# =============================================================================
print_step "步骤 6: 执行数据库迁移"

alembic upgrade head
print_success "数据库迁移完成"
echo ""

# =============================================================================
# 步骤 7: 启动应用
# =============================================================================
print_step "步骤 7: 启动应用"

print_warning "即将启动 Uvicorn 服务器..."
print_warning "按 Ctrl+C 停止服务器"
echo ""

print_success "🎉 部署完成！"
echo ""
echo "访问地址:"
echo "  - API 文档：http://localhost:8000/docs"
echo "  - 健康检查：http://localhost:8000/health"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

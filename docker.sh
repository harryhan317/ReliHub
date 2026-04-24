#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() { echo -e "${BLUE}====> $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

COMMAND=${1:-up}

case "$COMMAND" in
  up|start)
    print_step "启动 ReliHub Docker 环境"
    docker compose up -d --build
    print_success "容器已启动"
    echo ""
    print_step "等待服务就绪..."
    sleep 8
    print_step "检查数据库是否需要初始化..."
    INIT_NEEDED=$(docker compose logs backend-init 2>&1 | grep -c "Initialization complete" || true)
    if [ "$INIT_NEEDED" -eq 0 ]; then
      print_step "执行数据库初始化（扩展 + 迁移 + 种子数据）..."
      docker compose run --rm backend-init
      print_success "数据库初始化完成"
    else
      print_success "数据库已初始化，跳过"
    fi
    echo ""
    print_success "🎉 ReliHub 已启动！"
    echo ""
    echo "访问地址:"
    echo "  管理后台: http://localhost:5179"
    echo "  API 文档: http://localhost:8000/docs"
    echo "  健康检查: http://localhost:8000/api/v1/health"
    echo ""
    echo "测试账号:"
    echo "  超级管理员: reliadmin / Reli@Super2026!"
    echo "  管理员: relimod / Reli@Mod2026!"
    echo ""
    echo "管理命令:"
    echo "  ./docker.sh stop     停止服务"
    echo "  ./docker.sh restart  重启服务"
    echo "  ./docker.sh logs     查看日志"
    echo "  ./docker.sh status   查看状态"
    echo "  ./docker.sh reset    重置数据库并重启"
    ;;

  down|stop)
    print_step "停止 ReliHub Docker 环境"
    docker compose down
    print_success "服务已停止"
    ;;

  restart)
    print_step "重启 ReliHub Docker 环境"
    docker compose restart
    print_success "服务已重启"
    ;;

  logs)
    docker compose logs -f --tail=100
    ;;

  status|ps)
    docker compose ps
    ;;

  reset)
    print_warning "将删除所有数据并重新初始化"
    read -p "确认继续？(y/N) " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
      print_step "停止并删除容器和数据卷..."
      docker compose down -v
      print_step "重新构建并启动..."
      docker compose up -d --build
      sleep 8
      print_step "执行数据库初始化..."
      docker compose run --rm backend-init
      print_success "重置完成！"
    else
      echo "已取消"
    fi
    ;;

  build)
    print_step "重新构建镜像"
    docker compose build --no-cache
    print_success "构建完成"
    ;;

  shell|bash)
    SERVICE=${2:-backend}
    docker compose exec $SERVICE /bin/bash || docker compose exec $SERVICE /bin/sh
    ;;

  *)
    echo "ReliHub Docker 管理脚本"
    echo ""
    echo "用法: ./docker.sh <命令>"
    echo ""
    echo "命令:"
    echo "  up/start   启动所有服务（首次启动含数据库初始化）"
    echo "  down/stop  停止所有服务"
    echo "  restart    重启所有服务"
    echo "  logs       查看实时日志"
    echo "  status     查看服务状态"
    echo "  reset      重置数据库并重启（清除所有数据）"
    echo "  build      重新构建镜像"
    echo "  shell      进入容器终端（默认 backend）"
    ;;
esac

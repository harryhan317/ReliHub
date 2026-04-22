#!/bin/bash
# 前端服务自动启动器 - 启动脚本
# 使用说明：
#   ./start_frontend_proxy.sh start    # 启动服务
#   ./start_frontend_proxy.sh stop     # 停止服务
#   ./start_frontend_proxy.sh status   # 查看状态
#   ./start_frontend_proxy.sh restart  # 重启服务

set -e

# 配置参数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" 
PROJECT_ROOT="$SCRIPT_DIR"
CONFIG_FILE="$PROJECT_ROOT/frontend_auto_starter.conf"
PYTHON_SCRIPT="$PROJECT_ROOT/frontend_auto_starter.py"
PID_FILE="/tmp/frontend_auto_starter.pid"
LOG_FILE="/tmp/frontend_auto_starter.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# 检查依赖
check_dependencies() {
    log "检查系统依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi
    
    # 检查前端目录
    if [ ! -d "$PROJECT_ROOT/frontend" ]; then
        log_error "前端目录不存在: $PROJECT_ROOT/frontend"
        exit 1
    fi
    
    # 检查Python依赖
    if ! python3 -c "import aiohttp, psutil" &> /dev/null; then
        log "安装Python依赖..."
        pip3 install aiohttp psutil
    fi
    
    log "依赖检查完成"
}

# 获取配置参数
get_config() {
    local key="$1"
    local default="$2"
    
    if [ -f "$CONFIG_FILE" ]; then
        grep "^$key=" "$CONFIG_FILE" | cut -d'=' -f2- | tr -d '"\n' || echo "$default"
    else
        echo "$default"
    fi
}

# 启动服务
start_service() {
    log "启动前端服务自动启动器..."
    
    # 检查是否已在运行
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        if ps -p "$pid" > /dev/null 2>&1; then
            log "服务已在运行 (PID: $pid)"
            return 0
        fi
    fi
    
    # 启动服务
    nohup python3 "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # 保存PID
    echo "$pid" > "$PID_FILE"
    
    # 等待服务启动
    local proxy_port=$(get_config "PROXY_PORT" "8080")
    local max_wait=10
    local count=0
    
    while [ $count -lt $max_wait ]; do
        if curl -s "http://localhost:$proxy_port" > /dev/null 2>&1; then
            log "服务启动成功 (PID: $pid)"
            log "访问地址: http://localhost:$proxy_port"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    log_error "服务启动超时"
    stop_service
    return 1
}

# 停止服务
stop_service() {
    log "停止前端服务自动启动器..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        
        if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
            log "停止进程 (PID: $pid)"
            kill "$pid"
            
            # 等待进程结束
            local count=0
            while [ $count -lt 5 ] && ps -p "$pid" > /dev/null 2>&1; do
                sleep 1
                count=$((count + 1))
            done
            
            # 强制终止
            if ps -p "$pid" > /dev/null 2>&1; then
                log_warning "强制终止进程"
                kill -9 "$pid"
            fi
        fi
        
        rm -f "$PID_FILE"
    fi
    
    # 停止前端服务
    log "停止前端服务..."
    pkill -f "vite" || true
    
    log "服务已停止"
}

# 查看服务状态
status_service() {
    log "检查服务状态..."
    
    local proxy_port=$(get_config "PROXY_PORT" "8080")
    local frontend_port=$(get_config "FRONTEND_PORT" "3000")
    
    # 检查代理服务
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
            log "代理服务: 运行中 (PID: $pid)"
        else
            log "代理服务: 未运行"
        fi
    else
        log "代理服务: 未运行"
    fi
    
    # 检查前端服务
    if curl -s "http://localhost:$frontend_port" > /dev/null 2>&1; then
        log "前端服务: 运行中 (端口: $frontend_port)"
    else
        log "前端服务: 未运行"
    fi
    
    # 检查代理端口
    if curl -s "http://localhost:$proxy_port" > /dev/null 2>&1; then
        log "代理端口: 可访问 (端口: $proxy_port)"
    else
        log "代理端口: 不可访问"
    fi
}

# 重启服务
restart_service() {
    log "重启服务..."
    stop_service
    sleep 2
    start_service
}

# 显示帮助信息
show_help() {
    echo "前端服务自动启动器管理脚本"
    echo ""
    echo "使用方法: $0 {start|stop|restart|status|help}"
    echo ""
    echo "命令说明:"
    echo "  start   启动服务"
    echo "  stop    停止服务"
    echo "  restart 重启服务"
    echo "  status  查看状态"
    echo "  help    显示帮助"
    echo ""
    echo "配置文件: $CONFIG_FILE"
    echo "日志文件: $LOG_FILE"
}

# 主函数
main() {
    case "${1:-help}" in
        start)
            check_dependencies
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            check_dependencies
            restart_service
            ;;
        status)
            status_service
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
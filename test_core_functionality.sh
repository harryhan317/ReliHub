#!/bin/bash
# 前端服务自动启动器 - 简化测试脚本
# 功能：快速验证核心功能

set -e

# 配置参数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 日志函数
log() {
    echo -e "${GREEN}[TEST]${NC} $1"
}

log_error() {
    echo -e "${RED}[TEST ERROR]${NC} $1"
}

# 测试Python脚本语法
test_python_syntax() {
    log "测试Python脚本语法..."
    if python3 -m py_compile "$PROJECT_ROOT/frontend_auto_starter.py"; then
        log "✅ Python语法检查通过"
        return 0
    else
        log_error "❌ Python语法检查失败"
        return 1
    fi
}

# 测试导入依赖
test_imports() {
    log "测试Python依赖导入..."
    if python3 -c "
import aiohttp
import psutil
import asyncio
import json
import logging
print('✅ 所有依赖导入成功')
"; then
        log "✅ 依赖导入测试通过"
        return 0
    else
        log_error "❌ 依赖导入测试失败"
        return 1
    fi
}

# 测试配置文件
test_config_file() {
    log "测试配置文件..."
    if [ -f "$PROJECT_ROOT/frontend_auto_starter.conf" ]; then
        log "✅ 配置文件存在"
        
        # 检查关键配置
        if grep -q "FRONTEND_PORT" "$PROJECT_ROOT/frontend_auto_starter.conf" && \
           grep -q "PROXY_PORT" "$PROJECT_ROOT/frontend_auto_starter.conf"; then
            log "✅ 关键配置项存在"
            return 0
        else
            log_error "❌ 关键配置项缺失"
            return 1
        fi
    else
        log_error "❌ 配置文件不存在"
        return 1
    fi
}

# 测试前端目录
test_frontend_dir() {
    log "测试前端目录..."
    if [ -d "$PROJECT_ROOT/frontend" ]; then
        log "✅ 前端目录存在"
        
        if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
            log "✅ package.json存在"
            return 0
        else
            log_error "❌ package.json不存在"
            return 1
        fi
    else
        log_error "❌ 前端目录不存在"
        return 1
    fi
}

# 测试启动脚本语法
test_start_script() {
    log "测试启动脚本语法..."
    if bash -n "$PROJECT_ROOT/start_frontend_proxy.sh"; then
        log "✅ 启动脚本语法检查通过"
        return 0
    else
        log_error "❌ 启动脚本语法检查失败"
        return 1
    fi
}

# 测试手动启动流程
test_manual_startup() {
    log "测试手动启动流程..."
    
    # 先确保停止任何运行的服务
    pkill -f "frontend_auto_starter.py" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    # 直接启动Python脚本（不通过shell脚本）
    cd "$PROJECT_ROOT"
    python3 frontend_auto_starter.py &
    local pid=$!
    
    # 等待启动
    sleep 3
    
    # 检查进程是否存活
    if ps -p $pid > /dev/null 2>&1; then
        log "✅ 服务进程启动成功 (PID: $pid)"
        
        # 检查端口是否监听
        if lsof -i :8080 > /dev/null 2>&1; then
            log "✅ 代理端口监听正常"
        else
            log_error "❌ 代理端口未监听"
        fi
        
        # 停止服务
        kill $pid 2>/dev/null || true
        sleep 1
        
        return 0
    else
        log_error "❌ 服务进程启动失败"
        return 1
    fi
}

# 主测试函数
main() {
    echo "=== 前端服务自动启动器 - 核心功能验证 ==="
    echo ""
    
    local passed=0
    local failed=0
    
    # 运行测试
    if test_python_syntax; then ((passed++)); else ((failed++)); fi
    echo ""
    
    if test_imports; then ((passed++)); else ((failed++)); fi
    echo ""
    
    if test_config_file; then ((passed++)); else ((failed++)); fi
    echo ""
    
    if test_frontend_dir; then ((passed++)); else ((failed++)); fi
    echo ""
    
    if test_start_script; then ((passed++)); else ((failed++)); fi
    echo ""
    
    if test_manual_startup; then ((passed++)); else ((failed++)); fi
    echo ""
    
    # 生成测试报告
    echo "=== 测试总结 ==="
    echo "总测试数: $((passed + failed))"
    echo "通过: $passed"
    echo "失败: $failed"
    echo ""
    
    if [ $failed -eq 0 ]; then
        echo "✅ 所有核心功能验证通过！"
        echo ""
        echo "下一步："
        echo "1. 启动服务: ./start_frontend_proxy.sh start"
        echo "2. 访问地址: http://localhost:8080"
        echo "3. 查看状态: ./start_frontend_proxy.sh status"
        exit 0
    else
        echo "❌ 有测试失败，请检查问题"
        exit 1
    fi
}

# 执行测试
main "$@"
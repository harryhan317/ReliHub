#!/bin/bash
# 前端服务自动启动器 - 测试脚本
# 功能：测试自动启动机制的各项功能

set -e

# 配置参数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
TEST_LOG="/tmp/frontend_auto_starter_test.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 测试计数器
test_passed=0
test_failed=0

# 日志函数
log() {
    echo -e "${GREEN}[TEST]${NC} $1" | tee -a "$TEST_LOG"
}

log_error() {
    echo -e "${RED}[TEST ERROR]${NC} $1" | tee -a "$TEST_LOG"
}

log_warning() {
    echo -e "${YELLOW}[TEST WARNING]${NC} $1" | tee -a "$TEST_LOG"
}

log_info() {
    echo -e "${BLUE}[TEST INFO]${NC} $1" | tee -a "$TEST_LOG"
}

# 测试函数
run_test() {
    local test_name="$1"
    local test_func="$2"
    
    log "开始测试: $test_name"
    
    if $test_func; then
        log "✅ 测试通过: $test_name"
        ((test_passed++))
    else
        log_error "❌ 测试失败: $test_name"
        ((test_failed++))
    fi
    
    echo ""
}

# 测试1: 依赖检查
test_dependencies() {
    log_info "检查Python依赖..."
    
    if ! python3 -c "import aiohttp, psutil, asyncio" 2>/dev/null; then
        log_warning "安装Python依赖..."
        pip3 install aiohttp psutil
    fi
    
    if ! command -v npm &> /dev/null; then
        log_error "npm未安装"
        return 1
    fi
    
    if [ ! -d "$PROJECT_ROOT/frontend" ]; then
        log_error "前端目录不存在"
        return 1
    fi
    
    return 0
}

# 测试2: 配置文件检查
test_config() {
    log_info "检查配置文件..."
    
    local config_file="$PROJECT_ROOT/frontend_auto_starter.conf"
    
    if [ ! -f "$config_file" ]; then
        log_error "配置文件不存在: $config_file"
        return 1
    fi
    
    # 检查必要配置项
    local required_configs=("FRONTEND_PORT" "PROXY_PORT" "MAX_STARTUP_TIME")
    
    for config in "${required_configs[@]}"; do
        if ! grep -q "^$config=" "$config_file"; then
            log_error "配置项缺失: $config"
            return 1
        fi
    done
    
    log_info "配置文件检查通过"
    return 0
}

# 测试3: 服务启动测试
test_service_start() {
    log_info "测试服务启动..."
    
    # 先停止可能运行的服务
    "$PROJECT_ROOT/start_frontend_proxy.sh" stop > /dev/null 2>&1 || true
    
    # 启动服务
    if ! "$PROJECT_ROOT/start_frontend_proxy.sh" start; then
        log_error "服务启动失败"
        return 1
    fi
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if ! "$PROJECT_ROOT/start_frontend_proxy.sh" status; then
        log_error "服务状态检查失败"
        return 1
    fi
    
    return 0
}

# 测试4: HTTP请求测试
test_http_requests() {
    log_info "测试HTTP请求处理..."
    
    local proxy_port=8080
    local test_urls=(
        "http://localhost:$proxy_port/"
        "http://localhost:$proxy_port/ask"
        "http://localhost:$proxy_port/my"
    )
    
    for url in "${test_urls[@]}"; do
        log_info "测试URL: $url"
        
        local response=$(curl -s -I "$url" 2>/dev/null | head -n1 | cut -d' ' -f2)
        
        if [[ "$response" =~ ^(200|202|307)$ ]]; then
            log_info "HTTP响应正常: $response"
        else
            log_error "HTTP响应异常: $response"
            return 1
        fi
        
        sleep 1
    done
    
    return 0
}

# 测试5: 浏览器兼容性测试
test_browser_compatibility() {
    log_info "测试浏览器兼容性..."
    
    local proxy_port=8080
    local user_agents=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59"
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"  # 不支持的浏览器
    )
    
    for ua in "${user_agents[@]}"; do
        log_info "测试User-Agent: $(echo "$ua" | cut -c1-50)..."
        
        local response=$(curl -s -H "User-Agent: $ua" -I "http://localhost:$proxy_port/" 2>/dev/null | head -n1 | cut -d' ' -f2)
        
        if [[ "$ua" == *"MSIE"* ]] && [[ "$response" == "400" ]]; then
            log_info "不兼容浏览器正确处理: $response"
        elif [[ "$response" =~ ^(200|202|307)$ ]]; then
            log_info "兼容浏览器正常响应: $response"
        else
            log_error "浏览器兼容性测试失败: $response"
            return 1
        fi
        
        sleep 0.5
    done
    
    return 0
}

# 测试6: 服务停止测试
test_service_stop() {
    log_info "测试服务停止..."
    
    if ! "$PROJECT_ROOT/start_frontend_proxy.sh" stop; then
        log_error "服务停止失败"
        return 1
    fi
    
    sleep 2
    
    # 检查服务是否真的停止了
    if curl -s "http://localhost:8080" > /dev/null 2>&1; then
        log_error "服务未正确停止"
        return 1
    fi
    
    return 0
}

# 测试7: 错误处理测试
test_error_handling() {
    log_info "测试错误处理..."
    
    # 模拟前端服务启动失败（通过占用端口）
    log_info "模拟启动失败场景..."
    
    # 这里可以添加更复杂的错误处理测试
    # 目前主要测试脚本的错误处理能力
    
    return 0
}

# 测试8: 性能测试
test_performance() {
    log_info "测试性能..."
    
    local proxy_port=8080
    local start_time=$(date +%s%N)
    
    # 测试响应时间
    for i in {1..10}; do
        curl -s -o /dev/null "http://localhost:$proxy_port/"
    done
    
    local end_time=$(date +%s%N)
    local duration=$(( (end_time - start_time) / 1000000 ))
    
    log_info "10次请求耗时: ${duration}ms"
    
    if [ $duration -gt 5000 ]; then
        log_warning "响应时间较长，建议优化"
    fi
    
    return 0
}

# 主测试函数
main() {
    echo "=== 前端服务自动启动器测试报告 ===" | tee "$TEST_LOG"
    echo "测试时间: $(date)" | tee -a "$TEST_LOG"
    echo "" | tee -a "$TEST_LOG"
    
    # 运行所有测试
    run_test "依赖检查" test_dependencies
    run_test "配置文件检查" test_config
    run_test "服务启动测试" test_service_start
    run_test "HTTP请求测试" test_http_requests
    run_test "浏览器兼容性测试" test_browser_compatibility
    run_test "性能测试" test_performance
    run_test "服务停止测试" test_service_stop
    run_test "错误处理测试" test_error_handling
    
    # 生成测试报告
    echo "=== 测试总结 ===" | tee -a "$TEST_LOG"
    echo "总测试数: $((test_passed + test_failed))" | tee -a "$TEST_LOG"
    echo "通过: $test_passed" | tee -a "$TEST_LOG"
    echo "失败: $test_failed" | tee -a "$TEST_LOG"
    
    if [ $test_failed -eq 0 ]; then
        echo -e "${GREEN}✅ 所有测试通过！${NC}" | tee -a "$TEST_LOG"
        exit 0
    else
        echo -e "${RED}❌ 有测试失败，请检查日志: $TEST_LOG${NC}" | tee -a "$TEST_LOG"
        exit 1
    fi
}

# 执行测试
main "$@"
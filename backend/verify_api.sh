#!/bin/bash
# 快速验证脚本 - 测试 ReliHub API 基本功能

BASE_URL="http://localhost:8000/api/v1"

echo "=========================================="
echo "ReliHub API 快速验证"
echo "=========================================="
echo ""

# 1. 测试 Swagger UI
echo "1. 测试 Swagger UI..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; then
    echo "   ✅ Swagger UI 可访问"
else
    echo "   ❌ Swagger UI 不可访问"
fi

# 2. 测试 OpenAPI 文档
echo "2. 测试 OpenAPI 文档..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/openapi.json | grep -q "200"; then
    echo "   ✅ OpenAPI 文档可访问"
else
    echo "   ❌ OpenAPI 文档不可访问"
fi

# 3. 测试健康检查（如果有）
echo "3. 测试健康检查..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" 2>/dev/null)
if [ "$HEALTH_STATUS" = "200" ]; then
    echo "   ✅ 健康检查通过"
else
    echo "   ⚠️  无健康检查端点或失败"
fi

# 4. 测试用户注册（模拟）
echo "4. 测试用户注册 API..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"phone":"13800138000","password":"Test123456","verification_code":"888888"}' 2>/dev/null)
if echo "$REGISTER_RESPONSE" | grep -q "code"; then
    echo "   ✅ 注册 API 响应正常"
    echo "   响应：$REGISTER_RESPONSE" | head -c 200
    echo ""
else
    echo "   ⚠️  注册 API 可能有问题"
fi

# 5. 检查数据库表
echo "5. 检查数据库表..."
TABLE_COUNT=$(psql -h localhost -U postgres -d relihub -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" 2>/dev/null | tr -d ' ')
if [ "$TABLE_COUNT" -gt "10" ]; then
    echo "   ✅ 数据库表数量正常：$TABLE_COUNT 个表"
else
    echo "   ⚠️  数据库表数量异常：$TABLE_COUNT 个表"
fi

# 6. 显示数据库表列表
echo "6. 数据库表列表:"
psql -h localhost -U postgres -d relihub -c "\dt" 2>/dev/null | head -20

echo ""
echo "=========================================="
echo "验证完成！"
echo "=========================================="
echo ""
echo "📊 应用信息:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - API Base:   http://localhost:8000/api/v1"
echo "   - 数据库：    PostgreSQL (relihub)"
echo ""

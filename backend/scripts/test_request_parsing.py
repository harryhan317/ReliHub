#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

from app.schemas.auth import LoginRequest
import json

# 测试不同的输入格式
test_cases = [
    '{"phone":"13800000020","password":"User@123456"}',
    '{"phone": "13800000020", "password": "User@123456"}',
    '{"phone":"13800000020","password":"User@123456","device_fingerprint":null}',
]

print("测试 LoginRequest 解析：\n")
for i, json_str in enumerate(test_cases):
    print(f'测试用例 {i+1}: {json_str}')
    try:
        data = json.loads(json_str)
        request = LoginRequest(**data)
        print(f'  解析成功: phone={request.phone}, password={request.password}')
    except Exception as e:
        print(f'  解析失败: {e}')
    print()
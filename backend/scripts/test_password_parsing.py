#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

from app.schemas.auth import LoginRequest

# 测试各种可能的输入格式
test_cases = [
    ('正常输入', '{"phone":"13800000020","password":"User@123456"}'),
    ('密码带空格', '{"phone":"13800000020","password":"User@123456 "}'),
    ('密码带前导空格', '{"phone":"13800000020","password":" User@123456"}'),
    ('手机号带空格', '{"phone":" 13800000020 ","password":"User@123456"}'),
    ('JSON unicode转义', '{"phone":"13800000020","password":"User\u0040123456"}'),
]

print("测试 LoginRequest 解析和验证：\n")
for name, json_str in test_cases:
    print(f'测试: {name}')
    print(f'  JSON: {json_str}')
    try:
        data = LoginRequest.model_validate_json(json_str)
        print(f'  解析: phone="{data.phone}", password="{data.password}"')
        print(f'  password repr: {repr(data.password)}')
    except Exception as e:
        print(f'  解析失败: {e}')
    print()
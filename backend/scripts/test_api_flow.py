#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

from app.schemas.auth import LoginRequest
from app.services.auth_service import login_by_password
from app.db.session import get_db

# 模拟 API 请求
json_str = '{"phone":"13800000020","password":"User@123456"}'

# 解析请求体
body = LoginRequest.model_validate_json(json_str)
print(f'1. 解析的请求体: phone={body.phone}, password={body.password}')

# 调用登录服务
db_gen = get_db()
db = next(db_gen)

try:
    user = login_by_password(
        db=db,
        phone=body.phone,
        password=body.password,
        client_ip='127.0.0.1'
    )
    print(f'2. 登录成功!')
    print(f'   - 用户ID: {user.id}')
    print(f'   - 昵称: {user.nickname}')
except Exception as e:
    print(f'2. 登录失败: {e}')
finally:
    try:
        next(db_gen)
    except StopIteration:
        pass
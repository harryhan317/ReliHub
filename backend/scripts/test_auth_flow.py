#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')

import hmac
import hashlib
from app.core.config import settings
from app.db.session import get_db
from app.services.auth_service import login_by_password
from app.core.security import generate_phone_blind_index

phone = '13800000020'
password = 'User@123456'

print(f'1. PHONE_BLIND_INDEX_KEY: {settings.PHONE_BLIND_INDEX_KEY}')
print(f'2. 计算的盲索引: {generate_phone_blind_index(phone)}')

# 创建数据库会话
db_gen = get_db()
db = next(db_gen)

try:
    user = login_by_password(
        db=db,
        phone=phone,
        password=password,
        client_ip='127.0.0.1'
    )
    print(f'3. 登录成功!')
    print(f'   - 用户ID: {user.id}')
    print(f'   - 昵称: {user.nickname}')
except Exception as e:
    print(f'3. 登录失败: {e}')
finally:
    try:
        next(db_gen)
    except StopIteration:
        pass
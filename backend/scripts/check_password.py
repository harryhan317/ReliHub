#!/usr/bin/env python3
import hmac
import hashlib
from argon2 import PasswordHasher
from sqlalchemy import create_engine, text

PHONE_BLIND_INDEX_KEY = 'independent-blind-index-key-change-me'
phone = '13800000020'
password = 'User@123456'

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)

# 生成新密码哈希
new_hash = ph.hash(password)
print(f'新哈希: {new_hash}')

# 检查现有哈希
engine = create_engine('postgresql://postgres:postgres@db:5432/relihub')
with engine.connect() as conn:
    result = conn.execute(text('SELECT id, phone, password_hash FROM users WHERE phone = :phone'), {'phone': phone})
    user = result.fetchone()
    if user:
        print(f'\n数据库中的哈希: {user[2]}')

        # 验证现有哈希
        try:
            verify_result = ph.verify(user[2], password)
            print(f'验证结果: {verify_result}')
        except Exception as e:
            print(f'验证失败: {e}')

        # 检查是否需要rehash
        if ph.check_needs_rehash(user[2]):
            print('需要rehash')
        else:
            print('不需要rehash')

        print(f'\n要更新密码，请执行:')
        print(f"UPDATE users SET password_hash = '{new_hash}' WHERE phone = '{phone}';")
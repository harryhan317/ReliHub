#!/usr/bin/env python3
import hmac
import hashlib
from argon2 import PasswordHasher
from sqlalchemy import create_engine, text

PHONE_BLIND_INDEX_KEY = 'independent-blind-index-key-change-me'
phone = '13800000020'
password = 'User@123456'

blind = hmac.new(
    PHONE_BLIND_INDEX_KEY.encode(),
    phone.encode(),
    hashlib.sha256,
).hexdigest()[:16]
print(f'计算的盲索引: {blind}')

engine = create_engine('postgresql://postgres:postgres@db:5432/relihub')
with engine.connect() as conn:
    result = conn.execute(text('SELECT id, phone, phone_blind_index, password_hash FROM users WHERE phone_blind_index = :blind'), {'blind': blind})
    user = result.fetchone()
    if user:
        print(f'数据库查询成功!')
        print(f'  - 用户ID: {user[0]}')
        print(f'  - 手机号: {user[1]}')
        print(f'  - 数据库盲索引: {user[2]}')
        print(f'  - 盲索引匹配: {user[2] == blind}')

        ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
        try:
            result = ph.verify(user[3], password)
            print(f'密码验证结果: {result}')
        except Exception as e:
            print(f'密码验证失败: {e}')
    else:
        print(f'未找到匹配盲索引 {blind} 的用户')
        result2 = conn.execute(text('SELECT id, phone, phone_blind_index FROM users WHERE phone = :phone'), {'phone': phone})
        user2 = result2.fetchone()
        if user2:
            print(f'但按手机号查询找到了用户: {user2}')
#!/usr/bin/env python3
"""
修复测试账号的盲索引问题
使用与后端相同的HMAC-SHA256算法重新计算盲索引
"""

import sys
import os
import hmac
import hashlib

# 测试账号配置
TEST_ACCOUNTS = [
    {"phone": "13800000001", "nickname": "ReliAdmin"},
    {"phone": "13800000002", "nickname": "ReliModerator"},
    {"phone": "13800000011", "nickname": "赵新兵"},
    {"phone": "13800000012", "nickname": "钱小白"},
    {"phone": "13800000013", "nickname": "孙菜鸟"},
    {"phone": "13800000014", "nickname": "李初学"},
    {"phone": "13800000015", "nickname": "周入门"},
    {"phone": "13800000016", "nickname": "吴进阶"},
    {"phone": "13800000017", "nickname": "郑熟手"},
    {"phone": "13800000018", "nickname": "王资深"},
    {"phone": "13800000019", "nickname": "冯老炮"},
    {"phone": "13800000020", "nickname": "陈达人"},
    {"phone": "13800000021", "nickname": "魏专家"},
]

# 使用与后端相同的key
PHONE_BLIND_INDEX_KEY = "independent-blind-index-key-change-me"

def generate_phone_blind_index(phone: str) -> str:
    """使用与后端相同的HMAC-SHA256算法生成盲索引"""
    return hmac.new(
        PHONE_BLIND_INDEX_KEY.encode(),
        phone.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]

def main():
    print("🔧 开始修复测试账号的盲索引...")
    print(f"使用Key: {PHONE_BLIND_INDEX_KEY}\n")

    for account in TEST_ACCOUNTS:
        phone = account["phone"]
        nickname = account["nickname"]
        blind_index = generate_phone_blind_index(phone)

        print(f"账号: {nickname} ({phone})")
        print(f"  旧盲索引格式: blind_{phone[-4:]}")
        print(f"  新盲索引: {blind_index}")
        print()

    print("请在数据库中执行以下SQL更新盲索引：\n")

    sql_statements = []
    for account in TEST_ACCOUNTS:
        phone = account["phone"]
        blind_index = generate_phone_blind_index(phone)
        sql = f"UPDATE users SET phone_blind_index = '{blind_index}' WHERE phone = '{phone}';"
        sql_statements.append(sql)
        print(sql)

    # 保存SQL到文件
    sql_file = "/Users/harryhan/Desktop/ReliHub/backend/scripts/fix_blind_index.sql"
    with open(sql_file, "w") as f:
        f.write("\n".join(sql_statements))

    print(f"\n✅ SQL语句已保存到: {sql_file}")
    print("\n请执行以下命令更新数据库：")
    print(f"docker exec relihub-db-1 psql -U postgres -d relihub -c \"$(cat {sql_file})\"")
    print("\n或者直接执行上面的SQL语句。")

if __name__ == "__main__":
    main()
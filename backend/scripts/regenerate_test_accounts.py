#!/usr/bin/env python3
"""
重新生成测试账号脚本
生成1个超级管理员、1个管理员和10个虚拟用户（从新兵到专家各个等级至少1个）
"""

import sys
import os
import uuid
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 数据库连接配置
DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/relihub"

# 测试账号配置
TEST_ACCOUNTS = [
    # 超级管理员
    {
        "phone": "13800000001",
        "nickname": "ReliAdmin",
        "password": "Admin@123456",
        "rank": "专家",
        "reputation_points": 9999,
        "bonus_beans": 10000,
        "is_expert": True,
        "admin_subnet": "0.0.0.0/0"
    },
    # 管理员
    {
        "phone": "13800000002", 
        "nickname": "ReliModerator",
        "password": "Mod@123456",
        "rank": "老炮",
        "reputation_points": 1200,
        "bonus_beans": 500,
        "is_expert": True,
        "admin_subnet": "0.0.0.0/0"
    },
    # 虚拟用户 - 新兵
    {
        "phone": "13800000011",
        "nickname": "赵新兵",
        "password": "User@123456",
        "rank": "新兵",
        "reputation_points": 50,
        "bonus_beans": 20,
        "is_expert": False
    },
    {
        "phone": "13800000012",
        "nickname": "钱小白", 
        "password": "User@123456",
        "rank": "新兵",
        "reputation_points": 80,
        "bonus_beans": 30,
        "is_expert": False
    },
    # 虚拟用户 - 菜鸟
    {
        "phone": "13800000013",
        "nickname": "孙菜鸟",
        "password": "User@123456", 
        "rank": "菜鸟",
        "reputation_points": 150,
        "bonus_beans": 80,
        "is_expert": False
    },
    {
        "phone": "13800000014",
        "nickname": "李初学",
        "password": "User@123456",
        "rank": "菜鸟", 
        "reputation_points": 250,
        "bonus_beans": 120,
        "is_expert": False
    },
    # 虚拟用户 - 入门
    {
        "phone": "13800000015",
        "nickname": "周入门",
        "password": "User@123456",
        "rank": "入门",
        "reputation_points": 400,
        "bonus_beans": 200,
        "is_expert": False
    },
    {
        "phone": "13800000016",
        "nickname": "吴进阶",
        "password": "User@123456",
        "rank": "入门",
        "reputation_points": 550,
        "bonus_beans": 300,
        "is_expert": False
    },
    # 虚拟用户 - 熟手
    {
        "phone": "13800000017",
        "nickname": "郑熟手",
        "password": "User@123456",
        "rank": "熟手",
        "reputation_points": 700,
        "bonus_beans": 500,
        "is_expert": False
    },
    {
        "phone": "13800000018",
        "nickname": "王资深",
        "password": "User@123456",
        "rank": "熟手",
        "reputation_points": 900,
        "bonus_beans": 600,
        "is_expert": False
    },
    # 虚拟用户 - 老炮
    {
        "phone": "13800000019",
        "nickname": "冯老炮",
        "password": "User@123456",
        "rank": "老炮",
        "reputation_points": 1200,
        "bonus_beans": 800,
        "is_expert": False
    },
    # 虚拟用户 - 达人
    {
        "phone": "13800000020",
        "nickname": "陈达人",
        "password": "User@123456",
        "rank": "达人",
        "reputation_points": 2500,
        "bonus_beans": 1200,
        "is_expert": True
    },
    # 虚拟用户 - 专家
    {
        "phone": "13800000021",
        "nickname": "魏专家",
        "password": "User@123456",
        "rank": "专家",
        "reputation_points": 6000,
        "bonus_beans": 3000,
        "is_expert": True
    }
]

def generate_phone_blind_index(phone: str) -> str:
    """生成手机号盲索引 - 使用与后端相同的HMAC-SHA256算法"""
    import hmac
    import hashlib
    PHONE_BLIND_INDEX_KEY = "independent-blind-index-key-change-me"
    return hmac.new(
        PHONE_BLIND_INDEX_KEY.encode(),
        phone.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]

def create_test_accounts():
    """创建测试账号"""
    try:
        # 创建数据库连接
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # 检查是否已存在测试账号
            existing_phones = session.execute(
                text("SELECT phone FROM users WHERE phone LIKE '1380000%'")
            ).fetchall()
            
            if existing_phones:
                print("发现已存在的测试账号，正在删除...")
                session.execute(
                    text("DELETE FROM users WHERE phone LIKE '1380000%'")
                )
                session.commit()
            
            # 创建新账号
            created_count = 0
            for account in TEST_ACCOUNTS:
                user_id = str(uuid.uuid4())
                password_hash = pwd_context.hash(account["password"])
                phone_blind_index = generate_phone_blind_index(account["phone"])
                
                # 插入用户数据
                insert_sql = text("""
                    INSERT INTO users (
                        id, phone, phone_blind_index, password_hash, nickname,
                        rank, reputation_points, reputation_status, is_expert,
                        gold_beans, bonus_beans, invite_code, is_reward_triggered,
                        failed_login_attempts, status, admin_subnet, daily_token_usage,
                        total_ai_storage_mb, created_at, updated_at
                    ) VALUES (
                        :id, :phone, :phone_blind_index, :password_hash, :nickname,
                        :rank, :reputation_points, :reputation_status, :is_expert,
                        :gold_beans, :bonus_beans, :invite_code, :is_reward_triggered,
                        :failed_login_attempts, :status, :admin_subnet, :daily_token_usage,
                        :total_ai_storage_mb, :created_at, :updated_at
                    )
                """)
                
                session.execute(insert_sql, {
                    "id": user_id,
                    "phone": account["phone"],
                    "phone_blind_index": phone_blind_index,
                    "password_hash": password_hash,
                    "nickname": account["nickname"],
                    "rank": account["rank"],
                    "reputation_points": account["reputation_points"],
                    "reputation_status": "NORMAL",
                    "is_expert": account["is_expert"],
                    "gold_beans": 0,
                    "bonus_beans": account["bonus_beans"],
                    "invite_code": f"INV{account['phone'][-6:]}",
                    "is_reward_triggered": False,
                    "failed_login_attempts": 0,
                    "status": "ACTIVE",
                    "admin_subnet": account.get("admin_subnet"),
                    "daily_token_usage": 0,
                    "total_ai_storage_mb": 0.0,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                
                created_count += 1
                print(f"✓ 创建账号: {account['nickname']} ({account['phone']})")
            
            session.commit()
            print(f"\n✅ 成功创建 {created_count} 个测试账号")
            
            # 生成CSV文件
            generate_csv_file()
            
    except Exception as e:
        print(f"❌ 创建测试账号失败: {e}")
        sys.exit(1)

def generate_csv_file():
    """生成CSV文件"""
    csv_content = "序号,角色,用户等级,昵称,手机号,登录密码,信誉分,可可豆,备注\n"
    
    for i, account in enumerate(TEST_ACCOUNTS, 1):
        role = "超级管理员" if i == 1 else "管理员" if i == 2 else "普通用户"
        user_level = account["rank"]
        nickname = account["nickname"]
        phone = account["phone"]
        password = account["password"]
        reputation = account["reputation_points"]
        beans = account["bonus_beans"]
        
        if i == 1:
            remark = "超级管理员账号，用于后台配置与测试，拥有最高权限"
        elif i == 2:
            remark = "管理员账号，用于内容审核与日常管理，需超级管理员授权"
        else:
            remark = f"{user_level}等级测试账号"
        
        csv_content += f"{i},{role},{user_level},{nickname},{phone},{password},{reputation},{beans},{remark}\n"
    
    # 写入CSV文件
    csv_path = "/Users/harryhan/Desktop/ReliHub/prototype/test-accounts.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    
    print(f"✅ 已生成测试账号CSV文件: {csv_path}")

if __name__ == "__main__":
    print("🚀 开始重新生成测试账号...")
    create_test_accounts()
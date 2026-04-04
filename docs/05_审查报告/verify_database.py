#!/usr/bin/env python3
"""
Sprint B 数据库验证脚本

验证实际数据库中的表结构是否与设计要求一致。
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加 backend 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool


async def verify_database():
    """验证数据库表结构"""
    
    # 数据库连接
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/relihub"
    
    print("=" * 80)
    print("Sprint B 数据库表结构验证")
    print("=" * 80)
    print()
    
    try:
        engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
        
        async with AsyncSession(engine) as session:
            # 1. 检查所有表是否存在
            print("📊 检查表是否存在...")
            print("-" * 80)
            
            expected_tables = [
                'ai_sessions',
                'ai_messages',
                'file_meta',
                'file_usage',
                'resources',
                'resource_previews',
                'topics',
                'posts',
                'point_ledger',
                'attempted_transaction',
                'asset_packages',
                'user_purchased_assets',
                'notifications',
            ]
            
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            existing_tables = [row[0] for row in result.fetchall()]
            
            # 检查表
            missing_tables = []
            for table in expected_tables:
                if table in existing_tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} - 缺失")
                    missing_tables.append(table)
            
            if not missing_tables:
                print(f"\n✅ 所有 {len(expected_tables)} 个表都存在")
            else:
                print(f"\n❌ 缺少 {len(missing_tables)} 个表：{missing_tables}")
            
            print()
            
            # 2. 检查每个表的字段数
            print("📋 检查表字段数...")
            print("-" * 80)
            
            expected_columns = {
                'ai_sessions': 11,
                'ai_messages': 10,
                'file_meta': 10,
                'file_usage': 6,
                'resources': 17,
                'resource_previews': 5,
                'topics': 14,
                'posts': 9,
                'point_ledger': 11,
                'attempted_transaction': 6,
                'asset_packages': 6,
                'user_purchased_assets': 8,
                'notifications': 12,
            }
            
            for table_name, expected_count in expected_columns.items():
                if table_name not in existing_tables:
                    continue
                
                result = await session.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                """))
                
                actual_count = result.scalar()
                
                if actual_count == expected_count:
                    print(f"  ✅ {table_name}: {actual_count} 个字段")
                else:
                    print(f"  ⚠️  {table_name}: {actual_count} 个字段 (期望：{expected_count})")
            
            print()
            
            # 3. 检查索引
            print("🔍 检查索引...")
            print("-" * 80)
            
            result = await session.execute(text("""
                SELECT tablename, indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """))
            
            indexes = result.fetchall()
            
            # 按表分组索引
            indexes_by_table = {}
            for tablename, indexname in indexes:
                if tablename not in indexes_by_table:
                    indexes_by_table[tablename] = []
                indexes_by_table[tablename].append(indexname)
            
            # 显示索引
            for table_name in expected_tables:
                if table_name in indexes_by_table:
                    index_count = len(indexes_by_table[table_name])
                    print(f"  ✅ {table_name}: {index_count} 个索引")
                    for idx in indexes_by_table[table_name][:3]:  # 只显示前 3 个
                        print(f"      - {idx}")
                    if index_count > 3:
                        print(f"      ... 还有 {index_count - 3} 个")
                else:
                    print(f"  ⚠️  {table_name}: 没有索引")
            
            print()
            
            # 4. 检查 Enum 类型
            print("📝 检查 Enum 类型...")
            print("-" * 80)
            
            result = await session.execute(text("""
                SELECT t.typname as enum_name,
                       array_agg(e.enumlabel ORDER BY e.enumsortorder) as enum_values
                FROM pg_type t
                JOIN pg_enum e ON t.oid = e.enumtypid
                JOIN pg_namespace n ON t.typnamespace = n.oid
                WHERE n.nspname = 'public'
                GROUP BY t.typname
                ORDER BY t.typname
            """))
            
            enums = result.fetchall()
            
            if enums:
                print(f"  ✅ 发现 {len(enums)} 个 Enum 类型:")
                for enum_name, enum_values in enums:
                    print(f"      {enum_name}: {', '.join(enum_values)}")
            else:
                print(f"  ⚠️  没有发现 Enum 类型")
            
            print()
            
            # 5. 总结
            print("=" * 80)
            print("📊 验证总结")
            print("=" * 80)
            
            tables_ok = len(missing_tables) == 0
            print(f"表完整性：{'✅ 通过' if tables_ok else '❌ 未通过'}")
            print(f"总表数：{len(existing_tables)}")
            print(f"期望表数：{len(expected_tables)}")
            print(f"缺失表数：{len(missing_tables)}")
            
            if tables_ok:
                print("\n✅ 数据库验证通过！")
            else:
                print(f"\n❌ 数据库验证失败，缺少表：{missing_tables}")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"\n❌ 验证失败：{str(e)}")
        print("\n请确保:")
        print("1. 数据库容器正在运行")
        print("2. 数据库连接信息正确")
        print("3. 已执行数据库迁移")
        return False
    
    return True


if __name__ == '__main__':
    success = asyncio.run(verify_database())
    sys.exit(0 if success else 1)

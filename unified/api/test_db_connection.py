#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库连接脚本

用于诊断数据库连接问题
"""

import sys
import asyncio
import asyncpg
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unified.api.config import config

async def test_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("数据库连接测试")
    print("=" * 60)
    print(f"Host: {config.DB_HOST}")
    print(f"Port: {config.DB_PORT}")
    print(f"Database: {config.DB_NAME}")
    print(f"User: {config.DB_USER}")
    print(f"Password: {'*' * len(config.DB_PASSWORD) if config.DB_PASSWORD else '(未设置)'}")
    print("-" * 60)
    
    try:
        print("尝试连接数据库...")
        conn = await asyncpg.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        print("✅ 数据库连接成功！")
        
        # 检查表是否存在
        print("\n检查数据库表...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        if tables:
            print(f"✅ 找到 {len(tables)} 个表:")
            for table in tables:
                print(f"  - {table['table_name']}")
            
            # 检查关键表
            table_names = [t['table_name'] for t in tables]
            required_tables = ['dictionary_entries', 'dictionary_index']
            
            print("\n检查必需的表...")
            for table in required_tables:
                if table in table_names:
                    # 检查行数
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                    print(f"  ✅ {table}: {count} 行")
                else:
                    print(f"  ❌ {table}: 表不存在")
        else:
            print("⚠️  数据库中没有找到任何表")
            print("   需要先运行数据库初始化脚本创建表")
        
        # 测试查询
        if 'dictionary_entries' in [t['table_name'] for t in tables]:
            print("\n测试查询...")
            count = await conn.fetchval("SELECT COUNT(*) FROM dictionary_entries")
            print(f"✅ dictionary_entries 表有 {count} 条记录")
            
            if count > 0:
                sample = await conn.fetchrow("SELECT headword, source_id FROM dictionary_entries LIMIT 1")
                print(f"✅ 示例记录: headword='{sample['headword']}', source_id='{sample['source_id']}'")
        
        await conn.close()
        print("\n" + "=" * 60)
        print("✅ 测试完成")
        print("=" * 60)
        
    except asyncpg.exceptions.InvalidPasswordError as e:
        print(f"❌ 数据库密码错误: {str(e)}")
        print("   请检查 DB_PASSWORD 环境变量或 config.py 中的配置")
    except asyncpg.exceptions.InvalidCatalogNameError as e:
        print(f"❌ 数据库不存在: {str(e)}")
        print(f"   请创建数据库: CREATE DATABASE {config.DB_NAME};")
    except asyncpg.exceptions.ConnectionDoesNotExistError as e:
        print(f"❌ 连接错误: {str(e)}")
        print("   请检查 PostgreSQL 服务是否已启动")
    except asyncpg.exceptions.CannotConnectNowError as e:
        print(f"❌ 无法连接到数据库: {str(e)}")
        print("   请检查:")
        print("   1. PostgreSQL 服务是否已启动")
        print("   2. Host 和 Port 配置是否正确")
        print("   3. 防火墙设置")
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
授予数据库权限的 Python 脚本

使用 asyncpg 连接数据库并授予权限
"""

import sys
import asyncio
import asyncpg
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unified.api.config import config


async def grant_permissions():
    """授予数据库权限"""
    print("=" * 60)
    print("授予数据库权限")
    print("=" * 60)
    print(f"数据库: {config.DB_NAME}")
    print(f"用户: {config.DB_USER}")
    print(f"Host: {config.DB_HOST}")
    print(f"Port: {config.DB_PORT}")
    print("-" * 60)
    
    # 尝试以应用用户连接，看是否需要管理员权限
    try:
        print(f"\n尝试连接数据库（用户: {config.DB_USER}）...")
        app_conn = await asyncpg.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        print("✅ 应用用户连接成功")
        
        # 检查当前权限
        print("\n检查当前权限...")
        tables = await app_conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        if tables:
            print(f"✅ 找到 {len(tables)} 个表:")
            for table in tables:
                # 检查权限
                perms = await app_conn.fetch("""
                    SELECT privilege_type 
                    FROM information_schema.table_privileges 
                    WHERE table_schema = 'public' 
                      AND table_name = $1 
                      AND grantee = $2
                """, table['table_name'], config.DB_USER)
                
                if perms:
                    perm_list = [p['privilege_type'] for p in perms]
                    print(f"  ✅ {table['table_name']}: {', '.join(perm_list)}")
                else:
                    print(f"  ⚠️  {table['table_name']}: 无权限")
        else:
            print("⚠️  数据库中没有找到任何表")
        
        await app_conn.close()
        
        # 如果权限足够，直接返回
        if tables:
            print("\n✅ 用户已有足够权限，无需授予")
            return
        
    except asyncpg.exceptions.InsufficientPrivilegeError as e:
        print(f"❌ 权限不足: {str(e)}")
        print("   需要使用管理员用户授予权限")
    except Exception as e:
        print(f"⚠️  连接失败: {str(e)}")
        print("   尝试使用管理员用户授予权限...")
    
    # 尝试使用管理员用户（通常是当前系统用户）
    import os
    admin_user = os.getenv("POSTGRES_ADMIN_USER", os.getenv("USER", "postgres"))
    admin_password = os.getenv("POSTGRES_ADMIN_PASSWORD", "")
    
    print(f"\n尝试使用管理员用户连接（用户: {admin_user}）...")
    
    try:
        if admin_password:
            admin_conn = await asyncpg.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=admin_user,
                password=admin_password
            )
        else:
            # 尝试无密码连接（本地 socket）
            try:
                admin_conn = await asyncpg.connect(
                    database=config.DB_NAME,
                    user=admin_user
                )
            except:
                print("❌ 无法连接，需要管理员密码")
                print("\n请设置环境变量：")
                print(f"  export POSTGRES_ADMIN_USER=<管理员用户名>")
                print(f"  export POSTGRES_ADMIN_PASSWORD=<管理员密码>")
                return
        
        print("✅ 管理员用户连接成功")
        
        # 授予表权限
        print("\n授予表权限...")
        grant_queries = [
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON dictionary_entries TO {config.DB_USER};",
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON dictionary_index TO {config.DB_USER};",
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON dictionary_stats TO {config.DB_USER};",
        ]
        
        for query in grant_queries:
            try:
                await admin_conn.execute(query)
                print(f"  ✅ {query.strip()}")
            except Exception as e:
                print(f"  ⚠️  {query.strip()}")
                print(f"     错误: {str(e)}")
        
        # 授予序列权限
        print("\n授予序列权限...")
        sequence_queries = [
            f"GRANT USAGE, SELECT ON SEQUENCE dictionary_entries_id_seq TO {config.DB_USER};",
            f"GRANT USAGE, SELECT ON SEQUENCE dictionary_index_id_seq TO {config.DB_USER};",
            f"GRANT USAGE, SELECT ON SEQUENCE dictionary_stats_id_seq TO {config.DB_USER};",
        ]
        
        for query in sequence_queries:
            try:
                await admin_conn.execute(query)
                print(f"  ✅ {query.strip()}")
            except Exception as e:
                print(f"  ⚠️  {query.strip()}")
                print(f"     错误: {str(e)}")
        
        await admin_conn.close()
        
        print("\n" + "=" * 60)
        print("✅ 权限授予完成！")
        print("=" * 60)
        
    except asyncpg.exceptions.InvalidPasswordError as e:
        print(f"❌ 密码错误: {str(e)}")
        print("\n请设置环境变量：")
        print(f"  export POSTGRES_ADMIN_USER={admin_user}")
        print(f"  export POSTGRES_ADMIN_PASSWORD=<管理员密码>")
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        print("\n可能的解决方案：")
        print("1. 检查 PostgreSQL 服务是否已启动")
        print("2. 确认管理员用户名和密码")
        print("3. 尝试手动执行 SQL 命令：")


if __name__ == "__main__":
    try:
        asyncio.run(grant_permissions())
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()


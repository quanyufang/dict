#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接模块

使用asyncpg连接PostgreSQL数据库（支持异步操作）
"""

import asyncpg
import os
import logging
from typing import Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)
try:
    from unified.api.config import config
except ImportError:
    # 直接运行时的相对导入
    import sys
    from pathlib import Path
    # 从 database.py 位置: api -> unified -> src
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from unified.api.config import config

# 数据库配置（使用config模块）
DB_CONFIG = {
    "host": config.DB_HOST,
    "port": config.DB_PORT,
    "database": config.DB_NAME,
    "user": config.DB_USER,
    "password": config.DB_PASSWORD,
}

# 连接池
_pool: Optional[asyncpg.Pool] = None


async def create_pool():
    """创建数据库连接池"""
    global _pool
    if _pool is None:
        logger.info(f"创建数据库连接池: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, database={DB_CONFIG['database']}, user={DB_CONFIG['user']}")
        try:
            _pool = await asyncpg.create_pool(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                min_size=1,
                max_size=10,
            )
            logger.info("数据库连接池创建成功")
        except Exception as e:
            logger.error(f"创建数据库连接池失败: {str(e)}", exc_info=True)
            raise
    return _pool


async def close_pool():
    """关闭数据库连接池"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_db_connection():
    """获取数据库连接"""
    pool = await create_pool()
    return await pool.acquire()


@asynccontextmanager
async def get_db():
    """数据库连接上下文管理器"""
    try:
        pool = await create_pool()
        conn = await pool.acquire()
        logger.debug("获取数据库连接成功")
        try:
            yield conn
        finally:
            await pool.release(conn)
            logger.debug("释放数据库连接")
    except Exception as e:
        logger.error(f"获取数据库连接失败: {str(e)}", exc_info=True)
        raise


async def execute_query(query: str, *args):
    """执行查询"""
    async with get_db() as conn:
        return await conn.fetch(query, *args)


async def execute_one(query: str, *args):
    """执行查询，返回单条记录"""
    async with get_db() as conn:
        return await conn.fetchrow(query, *args)


async def execute_command(query: str, *args):
    """执行命令（INSERT/UPDATE/DELETE）"""
    async with get_db() as conn:
        return await conn.execute(query, *args)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典查询API服务（FastAPI）

API端点：
- GET /api/dict/query - 查询词条
- GET /api/dict/next - 获取下一个词条
- GET /api/dict/prev - 获取上一个词条
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
import sys
import traceback
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目根目录到路径（src目录）
# 从 main.py 位置: api -> unified -> src
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unified.api.database import get_db_connection
from unified.api.models import DictionaryQueryResponse, DictionaryNavigationResponse, ApiResponse
from unified.api.service import DictionaryService
from unified.api.config import config

app = FastAPI(
    title="词典查询API",
    description="支持key查询和遍历查询的词典服务",
    version="1.0.0"
)

# 配置CORS（允许前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,  # 可从环境变量配置
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
dict_service = DictionaryService()


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "name": "词典查询API",
        "version": "1.0.0",
        "endpoints": {
            "query": "/api/dict/query",
            "next": "/api/dict/next",
            "prev": "/api/dict/prev"
        }
    }


@app.get("/api/dict/query", response_model=ApiResponse[List[DictionaryQueryResponse]])
async def query_dict(
    key: str = Query(..., description="查询词头"),
    sources: Optional[str] = Query(None, description="词典来源列表，用逗号分隔（如：oxford,langdao）"),
    fuzzy: bool = Query(False, description="是否模糊查询"),
    limit: int = Query(10, ge=1, le=100, description="返回结果数量限制")
):
    """
    查询词条
    
    - **key**: 查询词头（必填）
    - **sources**: 词典来源列表，用逗号分隔（可选，为空则查询所有词典）
    - **fuzzy**: 是否模糊查询（默认false）
    - **limit**: 返回结果数量限制（默认10，最大100）
    """
    try:
        # 解析sources参数
        source_list = None
        if sources:
            source_list = [s.strip() for s in sources.split(',') if s.strip()]
        
        logger.info(f"查询请求: key={key}, sources={source_list}, fuzzy={fuzzy}, limit={limit}")
        
        # 调用服务查询
        results = await dict_service.query(key, source_list, fuzzy, limit)
        
        logger.info(f"查询成功: 返回 {len(results)} 条结果")
        return ApiResponse(
            code=200,
            message="success",
            data=results
        )
    except Exception as e:
        logger.error(f"查询失败: {str(e)}", exc_info=True)
        error_detail = f"查询失败: {str(e)}"
        if hasattr(e, '__traceback__'):
            error_detail += f"\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


@app.get("/api/dict/next", response_model=ApiResponse[DictionaryNavigationResponse])
async def get_next(
    key: str = Query(..., description="当前词头"),
    source: str = Query(..., description="词典来源ID")
):
    """
    获取下一个词条
    
    - **key**: 当前词头（必填）
    - **source**: 词典来源ID（必填）
    """
    try:
        result = await dict_service.get_next(key, source)
        return ApiResponse(
            code=200,
            message="success",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取下一个词条失败: {str(e)}")


@app.get("/api/dict/prev", response_model=ApiResponse[DictionaryNavigationResponse])
async def get_prev(
    key: str = Query(..., description="当前词头"),
    source: str = Query(..., description="词典来源ID")
):
    """
    获取上一个词条
    
    - **key**: 当前词头（必填）
    - **source**: 词典来源ID（必填）
    """
    try:
        result = await dict_service.get_prev(key, source)
        return ApiResponse(
            code=200,
            message="success",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取上一个词条失败: {str(e)}")


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 测试数据库连接
        conn = await get_db_connection()
        await conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    print(f"启动词典查询API服务...")
    print(f"服务地址: http://{config.API_HOST}:{config.API_PORT}")
    print(f"API文档: http://{config.API_HOST}:{config.API_PORT}/docs")
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT, reload=True)


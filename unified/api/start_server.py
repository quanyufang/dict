#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动词典查询API服务的便捷脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import uvicorn
from unified.api.main import app
from unified.api.config import config

if __name__ == "__main__":
    print(f"启动词典查询API服务...")
    print(f"服务地址: http://{config.API_HOST}:{config.API_PORT}")
    print(f"API文档: http://{config.API_HOST}:{config.API_PORT}/docs")
    print(f"按 Ctrl+C 停止服务")
    print("-" * 50)
    
    uvicorn.run(
        app, 
        host=config.API_HOST, 
        port=config.API_PORT,
        reload=True,  # 开发模式：自动重载
        log_level="info"
    )


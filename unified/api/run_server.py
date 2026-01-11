#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动词典查询API服务的便捷脚本

使用方法：
    python3 run_server.py
"""

import sys
from pathlib import Path

# 添加项目根目录（src）到路径
current_dir = Path(__file__).parent  # api目录
src_dir = current_dir.parent.parent  # 回到src目录 (api -> unified -> src)
sys.path.insert(0, str(src_dir))

if __name__ == "__main__":
    import uvicorn
    
    # 直接从模块导入
    from unified.api.config import config
    
    print("=" * 60)
    print("📚 词典查询API服务")
    print("=" * 60)
    print(f"服务地址: http://{config.API_HOST}:{config.API_PORT}")
    print(f"API文档: http://{config.API_HOST}:{config.API_PORT}/docs")
    print(f"健康检查: http://{config.API_HOST}:{config.API_PORT}/health")
    print("-" * 60)
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    
    # 启动服务
    uvicorn.run(
        "unified.api.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,  # 开发模式：自动重载
        log_level="info"
    )


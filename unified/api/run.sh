#!/bin/bash
# 启动词典查询API服务

cd "$(dirname "$0")/.."

# 检查虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 运行服务
python3 -m unified.api.main


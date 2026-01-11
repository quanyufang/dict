#!/bin/bash
# 快速设置Python虚拟环境的脚本

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UNIFIED_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================================"
echo "📚 词典查询API - 环境设置"
echo "============================================================"

# 检查Python版本（需要Python 3.12，Python 3.13有兼容性问题）
echo "检查Python版本..."
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD=python3.12
    echo "✅ 找到 Python 3.12"
    python3.12 --version
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
    echo "⚠️  使用 Python 3.11（推荐使用 3.12）"
    python3.11 --version
else
    echo "❌ 错误: 未找到 Python 3.12 或 3.11"
    echo "请安装 Python 3.12: brew install python@3.12"
    exit 1
fi

# 创建虚拟环境
echo ""
echo "创建虚拟环境..."
cd "$UNIFIED_DIR"
if [ -d "venv" ]; then
    echo "虚拟环境已存在，删除后重新创建（确保使用正确的Python版本）"
    rm -rf venv
fi
$PYTHON_CMD -m venv venv
echo "✅ 虚拟环境创建成功"

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo ""
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "安装依赖..."
cd "$SCRIPT_DIR"
pip install -r requirements.txt

echo ""
echo "============================================================"
echo "✅ 环境设置完成！"
echo "============================================================"
echo ""
echo "下一步："
echo "1. 激活虚拟环境: source $UNIFIED_DIR/venv/bin/activate"
echo "2. 运行服务: python3 $SCRIPT_DIR/run_server.py"
echo ""


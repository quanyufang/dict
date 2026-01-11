#!/bin/bash
# 修复数据库权限的便捷脚本

set -e

echo "============================================================"
echo "修复数据库权限"
echo "============================================================"

# 从环境变量读取配置，如果没有则使用默认值
DB_NAME="${DB_NAME:-fishenglish_dict}"
DB_USER="${DB_USER:-fishenglish}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"

echo "数据库: $DB_NAME"
echo "用户: $DB_USER"
echo "管理员: $POSTGRES_USER"
echo "-" * 60

# 检查是否提供了密码
if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "⚠️  注意: 未设置 POSTGRES_PASSWORD 环境变量"
    echo "   将以交互式方式连接数据库（需要输入管理员密码）"
    PASSWORD_OPTION=""
else
    export PGPASSWORD="$POSTGRES_PASSWORD"
    PASSWORD_OPTION="-W"
fi

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_FILE="$SCRIPT_DIR/grant_permissions.sql"

# 检查SQL文件是否存在
if [ ! -f "$SQL_FILE" ]; then
    echo "❌ 错误: 找不到 $SQL_FILE"
    exit 1
fi

echo "执行权限授予脚本..."
echo ""

# 执行SQL脚本
if psql -U "$POSTGRES_USER" -d "$DB_NAME" -f "$SQL_FILE"; then
    echo ""
    echo "============================================================"
    echo "✅ 权限授予成功！"
    echo "============================================================"
else
    echo ""
    echo "============================================================"
    echo "❌ 权限授予失败"
    echo "============================================================"
    echo "请检查："
    echo "1. PostgreSQL 服务是否已启动"
    echo "2. 数据库 $DB_NAME 是否存在"
    echo "3. 用户 $DB_USER 是否存在"
    echo "4. 管理员用户 $POSTGRES_USER 的密码是否正确"
    exit 1
fi


#!/bin/bash

# 增强检索工具快速启动脚本

echo "================================"
echo "china-lawyer-analyst v3.0"
echo "自动化监测与检索工具"
echo "================================"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

echo "✅ Python 环境：$(python3 --version)"
echo ""

# 安装依赖
echo "[1/3] 安装依赖..."
pip3 install -q -r tools/requirements.txt
echo "✅ 依赖安装完成"
echo ""

# 运行测试
echo "[2/3] 运行测试..."
python3 tools/retrieval/test_retrieval.py
echo ""

# 运行示例
echo "[3/3] 运行集成示例..."
python3 tools/examples/integration_example.py
echo ""

echo "================================"
echo "🎉 快速启动完成！"
echo "================================"
echo ""
echo "后续使用："
echo "  1. 监测新司法解释："
echo "     python3 tools/monitor/court-monitor.py"
echo ""
echo "  2. 增强检索："
echo "     python3 tools/examples/integration_example.py"
echo ""
echo "  3. 设置定时任务（可选）："
echo "     crontab -e"
echo "     添加：0 9 * * 1 cd $(pwd) && python3 tools/monitor/court-monitor.py"
echo ""

#!/bin/bash

# Cron 定时任务自动设置脚本

echo "================================"
echo "China Lawyer Analyst - Cron 任务设置"
echo "================================"
echo ""

# 检查是否已安装 cron 任务
echo "[1/4] 检查现有 cron 任务..."
if crontab -l 2>/dev/null | grep -q "court-monitor.py"; then
    echo "⚠️  检测到已安装的监测任务"
    echo ""
    echo "现有任务："
    crontab -l | grep "court-monitor.py"
    echo ""
    read -p "是否要重新安装？(y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 取消安装"
        exit 0
    fi
fi

# 获取 Python3 路径
echo ""
echo "[2/4] 检测 Python3 路径..."
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    echo "❌ 未找到 Python3"
    exit 1
fi
echo "✅ Python3 路径：$PYTHON_PATH"

# 获取项目路径
echo ""
echo "[3/4] 获取项目路径..."
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "✅ 项目路径：$PROJECT_DIR"

# 备份现有 crontab
echo ""
echo "[4/4] 设置 cron 任务..."
BACKUP_FILE="$PROJECT_DIR/tools/crontab-backup-$(date +%Y%m%d-%H%M%S).txt"
crontab -l > "$BACKUP_FILE" 2>/dev/null || true
echo "✅ 已备份现有 crontab 到：$BACKUP_FILE"

# 添加新的 cron 任务
(crontab -l 2>/dev/null; cat << CRON_EOF

# china-lawyer-analyst 司法解释监测任务
# 每周一上午9:00监测新司法解释
0 9 * * 1 cd $PROJECT_DIR && $PYTHON_PATH tools/monitor/court-monitor.py >> $PROJECT_DIR/tools/monitor/cron.log 2>&1

# 每月1号清理90天前的日志
0 0 1 * * cd $PROJECT_DIR && find tools/monitor/ -name "*.log" -mtime +90 -delete

CRON_EOF
) | crontab -

echo "✅ Cron 任务安装完成"
echo ""

# 验证安装
echo "================================"
echo "验证安装"
echo "================================"
echo ""
echo "已安装的 cron 任务："
crontab -l | grep -E "(court-monitor|china-lawyer)"
echo ""

# 显示下次执行时间
echo "下次执行时间："
NEXT_RUN=$(date -v +1mon +"%Y-%m-%d %H:%M:%S" 2>/dev/null || date -d "next monday" +"%Y-%m-%d %H:%M:%S" 2>/dev/null)
if [ -n "$NEXT_RUN" ]; then
    echo "  下周一上午9:00 ($NEXT_RUN)"
else
    echo "  下周一上午9:00"
fi
echo ""

# 创建日志目录
echo "================================"
echo "初始化"
echo "================================"
echo ""
mkdir -p "$PROJECT_DIR/tools/monitor"
touch "$PROJECT_DIR/tools/monitor/cron.log"
echo "✅ 已创建日志目录"
echo ""

# 测试运行
echo "================================"
echo "测试运行"
echo "================================"
echo ""
read -p "是否要立即测试运行监测工具？(y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "运行测试..."
    cd "$PROJECT_DIR"
    $PYTHON_PATH tools/monitor/court-monitor.py
    echo ""
    echo "✅ 测试完成"
    echo ""
    echo "查看结果："
    echo "  队列文件：cat $PROJECT_DIR/queue.json"
    echo "  通知文件：cat $PROJECT_DIR/NOTIFICATION.md"
fi

echo ""
echo "================================"
echo "🎉 安装完成！"
echo "================================"
echo ""
echo "后续使用："
echo "  1. 查看日志：tail -f $PROJECT_DIR/tools/monitor/cron.log"
echo "  2. 手动运行：cd $PROJECT_DIR && python3 tools/monitor/court-monitor.py"
echo "  3. 卸载任务：crontab -e （删除相关行）"
echo "  4. 查看文档：cat $PROJECT_DIR/tools/cron-guide.md"
echo ""

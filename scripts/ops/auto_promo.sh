#!/bin/bash
# 丙大山 · 推广自动化脚本
# 使用方法: chmod +x auto_promo.sh && ./auto_promo.sh

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           丙大山 · 自动化推广执行系统                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3未安装"
    exit 1
fi

# 切换到脚本目录
cd "$(dirname "$0")"

# 执行推广脚本
echo "🚀 正在启动推广系统..."
python3 auto_promo.py

# 检查退出码
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 推广计划生成成功!"
    echo ""
    echo "📁 生成的文件:"
    ls -lh /tmp/promo_output/ 2>/dev/null || echo "   (暂无输出文件)"
    echo ""
    echo "💡 建议操作:"
    echo "   1. 打开 /tmp/promo_output/payment_reminders.txt 查看催款消息"
    echo "   2. 按 Twitter 时间发布推文"
    echo "   3. 前往 GitHub 搜索相关 Issue 并回复"
else
    echo ""
    echo "❌ 推广系统启动失败，请检查日志"
    exit 1
fi

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "丙大山团队 | 让量化交易更简单"
echo "══════════════════════════════════════════════════════════════"

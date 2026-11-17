#!/bin/bash
# Content Pilot GUI 一键启动脚本
# 作者: Agnes AI Assistant
# 日期: 2026-11-16
# 版本: v1.0

set -e

echo "=========================================="
echo "BingDashan Content Pilot - GUI启动器"
echo "=========================================="
echo ""

# 设置环境变量
export PATH=/root/.local/bin:/usr/local/nodejs/bin:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

# 检查是否在正确的目录
if [ ! -d "/opt/content-pilot" ]; then
    echo "❌ 错误: Content Pilot目录不存在"
    echo "   请先克隆项目: cd /opt && git clone https://github.com/r04943083/content-pilot.git"
    exit 1
fi

cd /opt/content-pilot

# 检查虚拟环境
if [ ! -f ".venv/bin/activate" ]; then
    echo "🔧 创建虚拟环境..."
    /root/.local/bin/uv venv --python 3.12
    source .venv/bin/activate
    /root/.local/bin/uv pip install -e .
    echo "✅ 虚拟环境创建完成"
else
    echo "✅ 虚拟环境已存在"
    source .venv/bin/activate
fi

# 检查Playwright浏览器
if ! playwright install --dry-run chromium &>/dev/null; then
    echo "🔧 安装Playwright浏览器..."
    playwright install chromium
    echo "✅ 浏览器安装完成"
else
    echo "✅ Playwright浏览器已安装"
fi

# 检查端口占用
PORT=8080
if lsof -ti:$PORT > /dev/null; then
    echo "⚠️  端口 $PORT 被占用，尝试使用 $((PORT+1))..."
    PORT=$((PORT+1))
fi

# 启动服务
echo ""
echo "🚀 启动Content Pilot GUI..."
echo "   访问地址: http://localhost:$PORT"
echo "   按 Ctrl+C 停止服务"
echo ""

# 在后台运行，输出到日志文件
nohup content-pilot gui --port $PORT > /tmp/content_pilot.log 2>&1 &
PID=$!

echo "✅ 服务已启动!"
echo "   PID: $PID"
echo "   日志: tail -f /tmp/content_pilot.log"
echo ""

# 等待服务启动
sleep 3

# 检查进程是否还在运行
if ps -p $PID > /dev/null; then
    echo "🎉 成功! 请访问 http://localhost:$PORT"
    echo ""
    echo "本地访问（端口转发）:"
    echo "  ssh -N -L $PORT:127.0.0.1:$PORT aliyun"
    echo ""
    echo "查看实时日志:"
    echo "  tail -f /tmp/content_pilot.log"
    echo ""
    echo "停止服务:"
    echo "  kill $PID"
else
    echo "❌ 服务启动失败，请查看日志:"
    echo "  cat /tmp/content_pilot.log"
    exit 1
fi

echo ""
echo "=========================================="
echo "下一步操作:"
echo "=========================================="
echo ""
echo "1. 在浏览器打开: http://localhost:$PORT"
echo "2. 配置AI API Key (Settings页面)"
echo "3. 扫码登录各平台账号 (Accounts页面)"
echo "4. 生成并审核内容 (Content页面)"
echo "5. 发布到各平台 (Publish页面)"
echo ""
echo "💡 提示: 首次使用建议先用半自动模式(semi)测试"
echo ""
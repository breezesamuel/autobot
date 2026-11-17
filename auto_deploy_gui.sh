#!/bin/bash
# Content Pilot GUI - 本地自动部署并启动脚本
# 当SSH恢复后，运行此脚本即可自动完成部署

SERVER="aliyun"
PROJECT_DIR="/opt/content-pilot"
LOG_FILE="/tmp/content_pilot_deploy.log"

echo "=========================================="
echo "BingDashan Content Pilot - 自动部署"
echo "=========================================="
echo "开始时间: $(date)"
echo ""

# 函数：执行远程命令
run_remote() {
    ssh -o ConnectTimeout=60 -o ServerAliveInterval=10 "$SERVER" "$1" 2>&1
}

# Step 1: 检查连接
echo "[Step 1/8] 测试SSH连接..."
if ! run_remote "echo 'OK'" > /dev/null; then
    echo "❌ SSH连接失败，请检查服务器状态"
    echo "   提示: 在阿里云控制台检查实例是否运行中"
    exit 1
fi
echo "✅ SSH连接成功"

# Step 2: 创建项目目录
echo ""
echo "[Step 2/8] 准备项目目录..."
run_remote "mkdir -p $PROJECT_DIR && cd $PROJECT_DIR && ls"
echo "✅ 目录就绪"

# Step 3: 克隆项目（如果不存在）
echo ""
echo "[Step 3/8] 检查项目代码..."
if ! run_remote "test -d $PROJECT_DIR/.git"; then
    echo "🔧 正在克隆Content Pilot项目..."
    run_remote "cd /opt && git clone https://github.com/r04943083/content-pilot.git"
    echo "✅ 项目克隆完成"
else
    echo "✅ 项目已存在，跳过克隆"
fi

# Step 4: 安装依赖
echo ""
echo "[Step 4/8] 安装Python依赖..."
run_remote "cd $PROJECT_DIR && /root/.local/bin/uv sync --python 3.12" 2>&1 | tail -5
echo "✅ 依赖安装完成"

# Step 5: 安装浏览器
echo ""
echo "[Step 5/8] 安装Playwright浏览器..."
run_remote "cd $PROJECT_DIR && source .venv/bin/activate && playwright install chromium" 2>&1 | tail -3
echo "✅ 浏览器安装完成"

# Step 6: 配置环境变量
echo ""
echo "[Step 6/8] 生成配置文件..."
run_remote "cd $PROJECT_DIR && test -f .env || cp .env.example .env"
echo "✅ 配置完成"

# Step 7: 启动服务
echo ""
echo "[Step 7/8] 启动Content Pilot GUI..."
run_remote "cd $PROJECT_DIR && source .venv/bin/activate && nohup content-pilot gui --port 8080 > /tmp/content_pilot.log 2>&1 & echo \$!" > /tmp/cp_pid.txt
sleep 3
PID=$(run_remote "cat /tmp/cp_pid.txt")
echo "✅ 服务已启动 (PID: $PID)"

# Step 8: 验证
echo ""
echo "[Step 8/8] 验证服务状态..."
run_remote "sleep 2 && curl -s http://127.0.0.1:8080/api/health || echo 'Service starting...'"
echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  方式A（端口转发）: ssh -N -L 8080:127.0.0.1:8080 aliyun"
echo "                   然后打开 http://localhost:8080"
echo ""
echo "  方式B（直接访问）: http://8.155.53.12:8080"
echo ""
echo "管理命令:"
echo "  查看日志: ssh aliyun 'tail -f /tmp/content_pilot.log'"
echo "  停止服务: ssh aliyun 'pkill -f content-pilot'"
echo "  重启服务: ssh aliyun 'systemctl restart content-pilot'"
echo ""
echo "首次使用需完成:"
echo "  1. 扫码登录各平台账号"
echo "  2. 配置AI API Key（Settings页面）"
echo "  3. 生成并发布第一条内容"
echo ""
echo "结束时间: $(date)"
echo "=========================================="
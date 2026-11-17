#!/bin/bash
# ============================================================
# BingDashan - Server Recovery 后一键部署脚本 v13
# 用途: SSH恢复后立即执行此脚本，完成所有新项目的克隆和配置
# 作者: Agnes AI Assistant
# 日期: 2026-11-16
# ============================================================

set -e

SERVER="aliyun"
DEPLOY_LOG="/tmp/bingdashan_deploy_v13.log"

echo "=============================================="
echo "BINGDASHAN AUTO DEPLOY v13"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=============================================="
echo ""

# 函数：在远程服务器执行命令
remote_exec() {
    ssh -o ConnectTimeout=30 -o ServerAliveInterval=10 "$SERVER" "$1" 2>&1
}

# Step 1: 测试连接
echo "[1/6] 测试SSH连接..."
if ! remote_exec "echo 'OK'" > /dev/null; then
    echo "❌ SSH连接失败。请等待服务器恢复后重试。"
    exit 1
fi
echo "✅ SSH连接正常"
echo ""

# Step 2: 查看已部署的项目
echo "[2/6] 检查现有部署..."
remote_exec "ls /opt/ | sort"
echo ""

# Step 3: 克隆新项目
echo "[3/6] 克隆最新发现的GitHub项目..."

NEW_PROJECTS=(
    "https://github.com/AutomateLab-tech/content-distribution-mcp.git"
    "https://github.com/skulltech/reddit-auto-poster.py.git"
    "https://github.com/martinopedal/linkedin-auto-poster.git"
    "https://github.com/PareekshithPalat/Medium_Blog_Automator.git"
    "https://github.com/ZANYANBU/Taskpilot.git"
)

for repo in "${NEW_PROJECTS[@]}"; do
    repo_name=$(basename "$repo" .git)
    echo "  → 克隆 $repo_name ..."
    if remote_exec "test -d /opt/$repo_name" 2>/dev/null; then
        echo "    已存在，跳过"
    else
        remote_exec "cd /opt && git clone --depth 1 $repo 2>&1" && echo "    ✅ $repo_name 克隆成功" || echo "    ⚠️ $repo_name 克隆失败"
    fi
done
echo ""

# Step 4: 检查Content Pilot GUI状态
echo "[4/6] 启动Content Pilot GUI..."
remote_exec "
    export PATH=/root/.local/bin:\$PATH
    cd /opt/content-pilot
    
    # 激活虚拟环境
    if [ -f .venv/bin/activate ]; then
        source .venv/bin/activate
    fi
    
    # 检查GUI是否已在运行
    if pgrep -f 'content-pilot gui' > /dev/null; then
        echo '✅ Content Pilot GUI 已在运行'
        ps aux | grep content-pilot | head -2
    else
        echo '🚀 正在启动 Content Pilot GUI...'
        nohup content-pilot gui --port 8080 > /tmp/content_pilot.log 2>&1 &
        sleep 2
        if pgrep -f 'content-pilot gui' > /dev/null; then
            echo '✅ Content Pilot GUI 启动成功 (PID:' \$(pgrep -f 'content-pilot gui')')'
        else
            echo '⚠️  GUI启动可能失败，请检查日志: tail -20 /tmp/content_pilot.log'
        fi
    fi
"
echo ""

# Step 5: 验证auto-xhs状态
echo "[5/6] 检查auto-xhs (小红书自动化)..."
remote_exec "
    cd /opt/auto-xhs
    if [ -f core/publish.py ]; then
        echo '✅ auto-xhs 就绪'
        ls core/*.py | xargs -I{} basename {}
    else
        echo '⚠️  auto-xhs 文件不完整'
    fi
"
echo ""

# Step 6: 最终状态报告
echo "[6/6] 最终部署状态"
echo "=============================================="
remote_exec "
    echo ''
    echo '📊 服务器状态总览'
    echo '----------------------------------------------'
    echo '主机名: '\$(hostname)
    echo '当前时间: '\$(date '+%Y-%m-%d %H:%M:%S')
    echo '运行时间: '\$(uptime -p 2>/dev/null || uptime)
    echo ''
    echo '📁 已部署项目列表:'
    ls -1 /opt/ | grep -E 'auto|xhs|zhihu|content|WeMedia|Y2A|apify|yominpost|scrapeio|social|Instagram|claude-trading|reddit|linkedin|medium|taskpilot' | while read dir; do
        echo \"  ✅ \$dir\"
    done
    echo ''
    echo '💻 环境信息:'
    echo \"  Node.js: \$(node --version 2>/dev/null || echo 'N/A')\"
    echo \"  Python3: \$(python3 --version 2>/dev/null || echo 'N/A')\"
    echo \"  ffmpeg: \$(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3 || echo 'N/A')\"
    echo ''
    echo '🌐 Content Pilot GUI:'
    if pgrep -f 'content-pilot gui' > /dev/null; then
        echo '  状态: ✅ 运行中'
        echo '  地址: http://localhost:8080'
        echo '  端口转发命令:'
        echo '    ssh -N -L 8080:127.0.0.1:8080 aliyun'
    else
        echo '  状态: ⏸️  未运行'
        echo '  启动命令:'
        echo '    cd /opt/content-pilot && source .venv/bin/activate && content-pilot gui'
    fi
    echo ''
    echo '🎯 下一步操作:'
    echo '  1. 端口转发: ssh -N -L 8080:127.0.0.1:8080 aliyun'
    echo '  2. 打开浏览器: http://localhost:8080'
    echo '  3. 扫码登录各平台账号'
    echo '  4. 开始发布内容!'
    echo ''
    echo '💰 目标: ¥19,197 (150笔待收款订单)'
    echo '=============================================='
"

echo ""
echo "=============================================="
echo "部署完成! 完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=============================================="
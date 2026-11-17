#!/bin/bash
# Content Pilot GUI 后台启动脚本
# 使用方法: bash start_gui.sh &

export PATH=/root/.local/bin:/usr/local/nodejs/bin:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

echo "Starting Content Pilot GUI..."
echo "Timestamp: $(date)"

cd /opt/content-pilot

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "✗ Virtual environment not found, creating..."
    /root/.local/bin/uv venv --python 3.12
    source .venv/bin/activate
    /root/.local/bin/uv pip install -e .
fi

# 检查是否已经在运行
if lsof -ti:8080 > /dev/null; then
    echo "Port 8080 already in use, starting on 8081..."
    content-pilot gui --port 8081
else
    echo "Starting on port 8080..."
    content-pilot gui --port 8080
fi
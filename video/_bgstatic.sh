#!/usr/bin/env bash
# 静态深蓝底 (快) + 后续用 overlay/drawtext 做动态, 避免逐像素 geq
cd /f/2026/第三轮
mkdir -p video
# 静态深蓝径向底: 用 color + vignette 近似 (vignette 自带暗角科技感)
ffmpeg -y -f lavfi -i "color=c=0x0a2148:s=1920x1080:r=30" -frames:v 1 video/_bgstatic.png 2>&1 | tail -2
echo "rc=$?  静态底: $(ls -la video/_bgstatic.png 2>/dev/null | awk '{print $5}') bytes"

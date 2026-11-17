#!/usr/bin/env bash
# 深蓝科技动态背景: 540p 生成(快)再放大 1080p, 对角光带随时间漂, 30s
cd /f/2026/第三轮
mkdir -p video
ffmpeg -y -f lavfi -i "nullsrc=s=960x540:r=30:d=30,format=rgb24" \
  -filter_complex "[0:v]geq=r='4+9*(0.5+0.5*sin(2*PI*(X+Y)/520 + T*0.6))':g='14+24*(0.5+0.5*sin(2*PI*(X+Y)/430 - T*0.45))':b='52+44*(0.5+0.5*sin(2*PI*(X-Y)/360 + T*0.35))',scale=1920:1080:flags=bicubic,format=yuv420p[out]" \
  -map "[out]" -t 30 -r 30 -c:v libx264 -preset veryfast -crf 26 -pix_fmt yuv420p -an video/_bg.mp4 2>&1 | tail -3
echo "rc=$?  bg size: $(ls -la video/_bg.mp4 2>/dev/null | awk '{print $5}') bytes"

#!/usr/bin/env bash
# 成片合成 (fast preset, 避免超时): 深蓝底 + 双漂移光斑 + ASS 中文字幕 + BGM -> 30s mp4
cd /f/2026/第三轮
rm -f "video/智能化服务宣传30s.mp4"
ffmpeg -y \
  -loop 1 -i video/_bgstatic.png \
  -loop 1 -i video/_glow1.png \
  -loop 1 -i video/_glow2.png \
  -i video/_bgm.m4a \
  -filter_complex "\
[0:v]scale=1920:1080,format=yuv420p[v0]; \
[1:v]scale=900:900,format=yuva420p[g1]; \
[2:v]scale=800:800,format=yuva420p[g2]; \
[v0][g1]overlay=x='560-520*sin(t*0.35)':y='260-180*cos(t*0.28)':eval=frame[o1]; \
[o1][g2]overlay=x='620+540*sin(t*0.30)':y='560+160*cos(t*0.22)':eval=frame[o2]; \
[o2]subtitles=video/_subs.ass[vout]" \
  -map "[vout]" -map 3:a \
  -t 30 -r 30 -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p -c:a aac -b:a 128k -shortest \
  "video/智能化服务宣传30s.mp4" 2>&1 | tail -3
echo "rc=$?"
ls -la "video/智能化服务宣传30s.mp4" 2>/dev/null | awk '{print "成片:", $5, "bytes"}'

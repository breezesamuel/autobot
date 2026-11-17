#!/usr/bin/env bash
# 合成一段科技感 BGM (30s, 无版权风险): 低频和声垫 + 缓慢脉冲, 立体声
cd /f/2026/第三轮
ffmpeg -y \
  -f lavfi -i "sine=frequency=55:duration=30" \
  -f lavfi -i "sine=frequency=82.4:duration=30" \
  -f lavfi -i "sine=frequency=110:duration=30" \
  -f lavfi -i "sine=frequency=164.8:duration=30" \
  -filter_complex "[0][1][2][3]amix=inputs=4:normalize=0,volume=0.5,tremolo=f=0.15:d=0.4,asetrate=44100,aformat=channel_layouts=stereo,afade=t=in:st=0:d=1.5,afade=t=out:st=27:d=3[out]" \
  -map "[out]" -t 30 -c:a aac -b:a 128k video/_bgm.m4a 2>&1 | tail -2
echo "rc=$?  BGM: $(ls -la video/_bgm.m4a 2>/dev/null | awk '{print $5}') bytes"

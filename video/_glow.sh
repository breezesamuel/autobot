#!/usr/bin/env bash
# 生成 2 个青色径向光斑 PNG (用 lavfi 快速生成, 不用逐像素 geq): radial 用 'gradients' 不可用 -> 用 color + vignette 近似柔光
cd /f/2026/第三轮
mkdir -p video
# 柔光斑: 透明底 + 中心亮青, 用 alpha 渐变近似 (vignette 反向 -> 中间亮)
# 简单可用: 生成 600x600 青色实心 + 大模糊(gblur) -> 柔和光斑
for i in 1 2; do
  ffmpeg -y -f lavfi -i "color=c=0x1e90d0:s=300x300:r=1" -frames:v 1 \
    -vf "scale=520:520,gblur=sigma=160,format=yuva420p,colorchannelmixer=aa=0.9" \
    video/_glow$i.png 2>&1 | tail -1
done
echo "光斑生成: $(ls video/_glow*.png 2>/dev/null | tr '\n' ' ')"

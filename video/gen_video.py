#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 30 秒深蓝科技感宣传片
输出：video/final_promo.mp4
依赖: ffmpeg 在 PATH 里
"""
import os, subprocess, sys

OUT = r"F:\2026\第三轮\video"
os.makedirs(OUT, exist_ok=True)

W, H = 1920, 1080
FPS = 30
DURATION = 30
FONT = "Microsoft YaHei"
FONT_FILE = r"C:\Windows\Fonts\msyh.ttc"

# 检查字体
if not os.path.exists(FONT_FILE):
    print(f"[warn] 字体 {FONT_FILE} 不存在，改用系统默认"); FONT_FILE = ""

SHOTS = [
    (0,   5,   "当智能系统，连接物理与数字世界"),
    (5,  13,   "从算法模型到嵌入式硬件，交付能落地的智能化系统"),
    (13, 21,   "感知 · 决策 · 执行，全栈技术服务，软硬一体"),
    (21, 26,   "让复杂场景，变简单可靠"),
    (26, 30,   "有兴趣请联系廖先生 15802178278"),
]

def run(cmd, desc=""):
    """安全调用 ffmpeg"""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding='utf-8', errors='replace')
        if r.returncode != 0:
            print(f"[err] {desc or cmd[0]}")
            print(r.stderr[-300:] if r.stderr else "")
            return False
        return True
    except Exception as e:
        print(f"[ex] {e}"); return False

print("=== 1. 生成深蓝背景视频 ===")
bg = os.path.join(OUT, "_bg.mp4")
run([
    "ffmpeg", "-y",
    "-f", "lavfi", "-i", f"color=c=#0a1628:s={W}x{H}:d={DURATION}:r={FPS}",
    "-c:v", "libx264", "-preset", "ultrafast",
    "-pix_fmt", "yuv420p", bg
], "生成背景")

print("=== 2. 合成带字幕的视频 (逐镜淡入淡出) ===")
subs_clip = os.path.join(OUT, "_subs.mp4")

# 构建滤镜字符串 —— 用 drawtext 的 filename 规避字符编码问题
# 先写出每个镜头的字幕文件 (UTF-8)
txt_files = []
for i, (st, dur, txt) in enumerate(SHOTS):
    tf = os.path.join(OUT, f"_s{i}.txt")
    with open(tf, "w", encoding="utf-8") as f:
        f.write(txt)
    txt_files.append(tf)

# 滤镜: 在每个镜头段绘制对应文本 + fade
filter_parts = []
for i, (st, dur, txt) in enumerate(SHOTS):
    tf = txt_files[i].replace("\\", "/")
    # 字号随内容长度自适应
    fs = 56 if len(txt) > 20 else 72
    y_base = 480 + i * 10
    f_in   = f"fade=t=in:st={st}:d=0.4"
    f_out  = f"fade=t=out:st={st+dur-0.4}:d=0.4"
    dt     = f"drawtext=filename='{tf}':fontfile='{FONT_FILE}':fontsize={fs}:fontcolor=white@0.95:x=(w-text_w)/2:y={y_base}"
    filter_parts.append(f"{f_in};{dt};{f_out}")

vf = ",".join(filter_parts) + ",format=yuv420p"
run([
    "ffmpeg", "-y",
    "-f", "lavfi", "-i", f"color=c=#0a1628:s={W}x{H}:d={DURATION}:r={FPS}",
    "-vf", vf,
    "-c:v", "libx264", "-preset", "veryfast",
    subs_clip
], "合成字幕视频")

print("=== 3. 生成 BGM (氛围电子音) ===")
bgm = os.path.join(OUT, "_bgm.wav")
run([
    "ffmpeg", "-y",
    "-f", "lavfi", "-i", f"sine=frequency=130:duration={DURATION}:sample_rate=44100",
    "-af", "volume=0.10,aformat=sample_rates=44100:channel_layouts=stereo",
    "-c:a", "pcm_s16le", bgm
], "生成 BGM")

print("=== 4. 合并视频 + 音频 → 成片 ===")
final = os.path.join(OUT, "final_promo.mp4")
run([
    "ffmpeg", "-y",
    "-i", bgm,
    "-i", subs_clip,
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k",
    "-map", "1:v:0", "-map", "0:a:0",
    "-shortest", "-t", str(DURATION),
    final
], "合并成片")

# 清理中间件
for f in [bg, subs_clip, bgm] + txt_files:
    try: os.remove(f)
    except: pass

print("\n✅ 完成！成片路径:")
print(f"   {final}")
print(f"\n说明:")
print("  - 30 秒深蓝科技风宣传片")
print("  - 5 个字幕镜头，各淡入淡出 0.4s")
print("  - 已叠加轻电子 BGM")
print("  - 定版镜头含 '联系廖先生 15802178278'")
print("\n下一步 (可选，效果更佳):")
print("  1. 用剪映添加真实旁白配音 (按上面分镜念)")
print("  2. 若需更丰富画面，替换为实拍/B-roll 素材")
print("  3. 若 BGM 单调，可换成免版权电子音乐库素材")

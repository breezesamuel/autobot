import subprocess, os

d = r'F:\2026\第三轮\video'
os.chdir(d)

print("=== 智能化系统宣传片生成 ===\n")

# Generate 5 scenes with proper content
scenes_info = [
    ('s1.mp4', '#030810', 5, 'drawbox=x=0:y=0:w=1920:h=1080:color=#030810:t=fill'),
    ('s2.mp4', '#050d18', 8, 'drawbox=x=0:y=0:w=1920:h=1080:color=#050d18:t=fill,drawbox=x=760:y=380:w=400:h=320:color=#0a1628:t=fill,drawbox=x=850:y=470:w=220:h=140:color=#00aaff:t=fill'),
    ('s3.mp4', '#020a14', 8, 'drawbox=x=0:y=0:w=1920:h=1080:color=#020a14:t=fill,drawbox=x=200:y=250:w=350:h=500:color=#0a1525:t=fill,drawbox=x=1350:y=250:w=420:h=500:color=#0a1525:t=fill'),
    ('s4.mp4', '#030b16', 5, 'drawbox=x=0:y=0:w=1920:h=1080:color=#030b16:t=fill,drawbox=x=400:y=300:w=250:h=350:color=#0a1a2e:t=fill,drawbox=x=800:y=300:w=350:h=350:color=#0a1a2e:t=fill,drawbox=x=1200:y=300:w=250:h=350:color=#0a1a2e:t=fill'),
    ('s5.mp4', '#020810', 4, 'drawbox=x=0:y=0:w=1920:h=1080:color=#020810:t=fill,drawbox=x=860:y=400:w=200:h=200:color=#00aaff@0.3:t=fill'),
]

for fname, color, duration, filterstr in scenes_info:
    print(f"[生成] {fname}...")
    cmd = ['ffmpeg', '-y', '-f', 'lavfi', '-i', f'color=c={color}:s=1920x1080:d={duration}:r=25', '-vf', filterstr, '-c:v', 'libx264', '-preset', 'fast', '-crf', '22', fname]
    subprocess.run(cmd, capture_output=True)
    if os.path.exists(fname):
        print(f"  OK ({os.path.getsize(fname)//1024}KB)")
    else:
        print(f"  FAIL")

# Concat
print("\n[拼接]")
with open('concat.txt', 'w', encoding='utf-8') as f:
    for fname, _, _, _ in scenes_info:
        f.write(f"file '{fname}'\n")

subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat.txt', '-c', 'copy', 'merged.mp4'], capture_output=True)
print(f"  merged: {'OK' if os.path.exists('merged.mp4') else 'FAIL'}")

# BGM
print("[音频]")
subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'aevalsrc=sin(2*PI*110*t)*0.1+sin(2*PI*220*t)*0.05+impulse(1):s=44100:d=30', '-c:a', 'aac', 'audio.m4a'], capture_output=True)
print(f"  bgm: {'OK' if os.path.exists('audio.m4a') else 'FAIL'}")

# Final
print("[合成]")
subprocess.run(['ffmpeg', '-y', '-i', 'merged.mp4', '-i', 'audio.m4a', '-c:v', 'copy', '-c:a', 'aac', '-shortest', '智能化系统宣传片_深蓝科技版.mp4'], capture_output=True)

out = '智能化系统宣传片_深蓝科技版.mp4'
if os.path.exists(out):
    size = os.path.getsize(out) // 1024
    print(f"\n{'='*50}")
    print(f"  ✅ 视频生成完成!")
    print(f"  📁 路径: {os.path.abspath(out)}")
    print(f"  📦 大小: {size} KB")
    print(f"  ⏱️  时长: 30秒")
    print(f"{'='*50}")
    os.system(f'explorer "{d}"')
else:
    print("错误: 输出失败")

# Cleanup temp
for f in ['s*.mp4', 'concat.txt', 'merged.mp4', 'audio.m4a']:
    import glob
    for gf in glob.glob(f):
        os.remove(gf)

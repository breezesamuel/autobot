import subprocess, os

d = r'F:\2026\第三轮\video'
os.chdir(d)

print("=== 智能化系统宣传片 - 最终版 ===\n")

# Generate all 5 scenes
for i in range(1, 6):
    colors = ['#030810', '#050d18', '#020a14', '#030b16', '#020810']
    durations = [5, 8, 8, 5, 4]
    extras = ''
    if i == 2: extras = ',drawbox=x=850:y=470:w=220:h=140:color=#00aaff:t=fill'
    if i == 3: extras = ',drawbox=x=200:y=250:w=350:h=500:color=#0a1525:t=fill,drawbox=x=1350:y=250:w=420:h=500:color=#0a1525:t=fill'
    if i == 4: extras = ',drawbox=x=400:y=300:w=250:h=350:color=#0a1a2e:t=fill,drawbox=x=800:y=300:w=350:h=350:color=#0a1a2e:t=fill,drawbox=x=1200:y=300:w=250:h=350:color=#0a1a2e:t=fill'
    if i == 5: extras = ',drawbox=x=860:y=400:w=200:h=200:color=#00aaff@0.3:t=fill'
    
    print(f"[{i}/5] Scene {i} ({durations[i-1]}s)...", end=' ')
    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi', '-i', f'color=c={colors[i-1]}:s=1920x1080:d={durations[i-1]}:r=25',
        '-vf', f'drawbox=x=0:y=0:w=1920:h=1080:color={colors[i-1]}:t=fill{extras}',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
        f's{i}.mp4'
    ]
    subprocess.run(cmd, capture_output=True)
    if os.path.exists(f's{i}.mp4'):
        sz = os.path.getsize(f's{i}.mp4') // 1024
        print(f"OK ({sz}KB)")
    else:
        print("FAIL")

# Concat
print("\n[合成] Merging...")
with open('concat.txt', 'w') as f:
    for i in range(1, 6):
        f.write(f"file 's{i}.mp4'\n")

subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat.txt', '-c', 'copy', 'merged.mp4'], capture_output=True)

# BGM
print("[音频] BGM...")
subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'aevalsrc=sin(2*PI*110*t)*0.1+impulse(1):s=44100:d=30', '-c:a', 'aac', 'bgm.m4a'], capture_output=True)

# Final
print("[打包] Final...")
subprocess.run(['ffmpeg', '-y', '-i', 'merged.mp4', '-i', 'bgm.m4a', '-c:v', 'copy', '-c:a', 'aac', '-shortest', '宣传片_成品.mp4'], capture_output=True)

# Cleanup temp
for f in [f's{i}.mp4' for i in range(1,6)] + ['concat.txt', 'merged.mp4', 'bgm.m4a']:
    if os.path.exists(f): os.remove(f)

out = '宣传片_成品.mp4'
if os.path.exists(out):
    size = os.path.getsize(out) // 1024
    print(f"\n{'='*50}")
    print(f"  ✅ 完成!")
    print(f"  📁 {os.path.abspath(out)}")
    print(f"  📦 {size} KB")
    print(f"{'='*50}")
    os.system(f'explorer "{d}"')
else:
    print("错误")
    print("文件列表:")
    for f in os.listdir(d):
        if f.endswith('.mp4'):
            print(f"  {f}")

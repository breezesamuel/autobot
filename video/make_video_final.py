import subprocess, os, sys

d = r'F:\2026\第三轮\video'
os.chdir(d)

print("=== 智能化系统宣传片生成 ===\n")

scenes = []

# Scene 1: Opening (0-5s) - Blue gradient with particles
print("[1/5] Scene 1: Opening...")
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', f'color=c=#030810:s=1920x1080:d=5:r=25',
    '-vf', 'drawbox=x=0:y=0:w=1920:h=1080:color=#030810:t=fill',
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
    's1.mp4'
]
subprocess.run(cmd, capture_output=True)
if os.path.exists('s1.mp4'): scenes.append('s1.mp4'); print("  OK")
else: print("  FAIL")

# Scene 2: Hardware (5-13s) 
print("[2/5] Scene 2: Hardware...")
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', f'color=c=#050d18:s=1920x1080:d=8:r=25',
    '-vf', 'drawbox=x=760:y=380:w=400:h=320:color=#0a1628:t=fill,drawbox=x=850:y=470:w=220:h=140:color=#00aaff:t=fill',
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
    's2.mp4'
]
subprocess.run(cmd, capture_output=True)
if os.path.exists('s2.mp4'): scenes.append('s2.mp4'); print("  OK")
else: print("  FAIL")

# Scene 3: Control (13-21s)
print("[3/5] Scene 3: Control Panel...")
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', f'color=c=#020a14:s=1920x1080:d=8:r=25',
    '-vf', 'drawbox=x=200:y=250:w=350:h=500:color=#0a1525:t=fill,drawbox=x=1350:y=250:w=420:h=500:color=#0a1525:t=fill',
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
    's3.mp4'
]
subprocess.run(cmd, capture_output=True)
if os.path.exists('s3.mp4'): scenes.append('s3.mp4'); print("  OK")
else: print("  FAIL")

# Scene 4: Applications (21-26s)
print("[4/5] Scene 4: Applications...")
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', f'color=c=#030b16:s=1920x1080:d=5:r=25',
    '-vf', 'drawbox=x=400:y=300:w=250:h=350:color=#0a1a2e:t=fill,drawbox=x=800:y=300:w=350:h=350:color=#0a1a2e:t=fill,drawbox=x=1200:y=300:w=250:h=350:color=#0a1a2e:t=fill',
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
    's4.mp4'
]
subprocess.run(cmd, capture_output=True)
if os.path.exists('s4.mp4'): scenes.append('s4.mp4'); print("  OK")
else: print("  FAIL")

# Scene 5: Contact (26-30s)
print("[5/5] Scene 5: Contact...")
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', f'color=c=#020810:s=1920x1080:d=4:r=25',
    '-vf', 'drawsymbol=symbol=circle:size=150:color=#00aaff@0.2:x=(iw/2):y:(ih/2)-80',
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
    's5.mp4'
]
subprocess.run(cmd, capture_output=True)
if os.path.exists('s5.mp4'): scenes.append('s5.mp4'); print("  OK")
else: print("  FAIL")

# Merge all scenes
print("\n[合成] Merging scenes...")
with open('concat.txt', 'w') as f:
    for s in scenes:
        f.write(f"file '{s}'\n")

subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat.txt', '-c', 'copy', 'temp.mp4'], capture_output=True)

# Generate BGM
print("[音频] Generating BGM...")
subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'aevalsrc=sin(2*PI*110*t)*0.1+impulse(1):s=44100:d=30', '-c:a', 'aac', 'bgm.m4a'], capture_output=True)

# Final merge
print("[打包] Final merge...")
subprocess.run(['ffmpeg', '-y', '-i', 'temp.mp4', '-i', 'bgm.m4a', '-c:v', 'copy', '-c:a', 'aac', '-shortest', '成片.mp4'], capture_output=True)

# Cleanup
for f in scenes + ['concat.txt', 'temp.mp4', 'bgm.m4a']:
    if os.path.exists(f): os.remove(f)

out = '成片.mp4'
if os.path.exists(out):
    size = os.path.getsize(out) // 1024
    print(f"\n{'='*50}")
    print(f"  ✅ 完成! 成片已生成")
    print(f"  📁 路径: {os.path.abspath(out)}")
    print(f"  📦 大小: {size} KB")
    print(f"{'='*50}")
    os.system(f'explorer "{d}"')
else:
    print("\n错误: 输出文件未生成")
    # List what we have
    print("\n当前视频文件:")
    for f in os.listdir(d):
        if f.endswith('.mp4'):
            print(f"  {f} ({os.path.getsize(os.path.join(d,f))//1024} KB)")

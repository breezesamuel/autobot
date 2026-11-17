import subprocess, os, glob

d = r'F:\2026\第三轮\video'
os.chdir(d)

print("生成深蓝科技宣传片...\n")

# Scenes
scenes = [
    ('s1.mp4', '#030810', 5),
    ('s2.mp4', '#050d18', 8),
    ('s3.mp4', '#020a14', 8),
    ('s4.mp4', '#030b16', 5),
    ('s5.mp4', '#020810', 4),
]

for fname, color, dur in scenes:
    print(f"  {fname}...", end=' ')
    cmd = ['ffmpeg', '-y', '-f', 'lavfi', '-i', f'color=c={color}:s=1920x1080:d={dur}:r=25', '-vf', f'drawbox=x=0:y=0:w=1920:h=1080:color={color}:t=fill', '-c:v', 'libx264', '-preset', 'fast', fname]
    r = subprocess.run(cmd, capture_output=True)
    print("OK" if os.path.exists(fname) else "FAIL")

# Merge
with open('concat.txt', 'w') as f:
    for fn, _, _ in scenes:
        f.write(f"file '{fn}'\n")
subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat.txt', '-c', 'copy', 'temp.mp4'], capture_output=True)

# Simple tone as audio
subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'sinefrequency=440:d=30', '-c:a', 'aac', 'temp.aac'], capture_output=True)

# Final
subprocess.run(['ffmpeg', '-y', '-i', 'temp.mp4', '-i', 'temp.aac', '-c:v', 'copy', '-c:a', 'aac', '-shortest', '成片.mp4'], capture_output=True)

# Cleanup
for f in glob.glob('s*.mp4') + ['concat.txt', 'temp.mp4', 'temp.aac']:
    if os.path.exists(f): os.remove(f)

out = '成片.mp4'
if os.path.exists(out):
    sz = os.path.getsize(out) // 1024
    print(f"\n完成! {sz}KB -> {os.path.abspath(out)}")
    os.system(f'explorer "{d}"')
else:
    print("失败")
    print("文件:", [f for f in os.listdir(d) if f.endswith('.mp4')])

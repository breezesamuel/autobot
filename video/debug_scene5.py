import subprocess, os

d = r'F:\2026\第三轮\video'
os.chdir(d)

print("生成场景5...")
# Scene 5: Contact - simpler version without drawsymbol
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', 'color=c=#020810:s=1920x1080:d=4:r=25',
    '-vf', 'drawbox=x=860:y=400:w=200:h=200:color=#00aaff@0.3:t=fill',
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
    's5.mp4'
]
r = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists('s5.mp4'):
    print(f"  OK ({os.path.getsize('s5.mp4')//1024} KB)")
else:
    print(f"  FAIL: {r.stderr[:200]}")

# Check existing scenes
print("\n检查已有场景:")
for i in range(1, 6):
    f = f's{i}.mp4'
    if os.path.exists(f):
        print(f"  {f}: {os.path.getsize(f)//1024} KB")
    else:
        print(f"  {f}: MISSING")

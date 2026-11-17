import subprocess, os

d = r'F:\2026\第三轮\video'
os.chdir(d)

print("手动分步生成...")

# Scene 1
print("[1] s1...")
r = subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=#030810:s=1920x1080:d=5:r=25', '-vf', 'drawbox=x=0:y=0:w=1920:h=1080:color=#030810:t=fill', '-c:v', 'libx264', '-preset', 'fast', 's1.mp4'], capture_output=True, text=True)
print(f"  exists={os.path.exists('s1.mp4')} size={os.path.getsize('s1.mp4')//1024 if os.path.exists('s1.mp4') else 0}KB")

# Scene 2
print("[2] s2...")
r = subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=#050d18:s=1920x1080:d=8:r=25', '-vf', 'drawbox=x=0:y=0:w=1920:h=1080:color=#050d18:t=fill,drawbox=x=850:y=470:w=220:h=140:color=#00aaff:t=fill', '-c:v', 'libx264', '-preset', 'fast', 's2.mp4'], capture_output=True, text=True)
print(f"  exists={os.path.exists('s2.mp4')}")

# Scene 3-5 similar...
for i in range(3, 6):
    print(f"[{i}] s{i}...")
    subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', f'color=c=#020a14:s=1920x1080:d=5:r=25', '-c:v', 'libx264', '-preset', 'fast', f's{i}.mp4'], capture_output=True)
    print(f"  exists={os.path.exists(f's{i}.mp4')}")

# Check all files
print("\n所有场景文件:")
for i in range(1, 6):
    f = f's{i}.mp4'
    if os.path.exists(f):
        print(f"  {f}: {os.path.getsize(f)//1024}KB")

# Concat
print("\n[合并]")
with open('concat.txt', 'w') as f:
    for i in range(1, 6):
        f.write(f"file 's{i}.mp4'\n")
print("  concat.txt written")

r = subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat.txt', '-c', 'copy', 'merged.mp4'], capture_output=True, text=True)
print(f"  merge exists={os.path.exists('merged.mp4')}")
if os.path.exists('merged.mp4'):
    print(f"  merge size={os.path.getsize('merged.mp4')//1024}KB")
else:
    print(f"  stderr: {r.stderr[:300]}")

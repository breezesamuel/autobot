import subprocess, os, sys

# Set encoding
sys.stdout.reconfigure(encoding='utf-8')

d = r'F:\2026\第三轮\video'
os.chdir(d)

print("Generating video scenes...")

# Simple test: just a colored background with no text
print("[1] Test basic video...")
r = subprocess.run([
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', 'color=c=#030810:s=1920x1080:d=5:r=25',
    '-c:v', 'libx264', '-preset', 'fast', 'test.mp4'
], capture_output=True, text=True)

if os.path.exists('test.mp4'):
    print("  Basic video OK")
    size = os.path.getsize('test.mp4') // 1024
    print(f"  Size: {size} KB")
    os.remove('test.mp4')
else:
    print(f"  FAIL: {r.stderr[:200]}")

# Try with drawtext using shell escaping
print("\n[2] Testing drawtext...")
cmd = 'ffmpeg -y -f lavfi -i "color=c=#030810:s=1920x1080:d=2:r=25" -vf "drawtext=text=Test:fontsize=48:fontcolor=white:x=100:y=100" -c:v libx264 -preset fast test2.mp4'
r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
if os.path.exists('test2.mp4'):
    print("  Drawtext OK")
    os.remove('test2.mp4')
else:
    print(f"  FAIL")
    
print("\nDone testing")

import subprocess, os

d = r'F:\2026\第三轮\video'
os.chdir(d)

# Check existing video
v = '智能化服务宣传30s.mp4'
print(f"检查: {v}")
r = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', v], capture_output=True, text=True)
import json
data = json.loads(r.stdout)
for s in data.get('streams', []):
    print(f"  {s.get('codec_name')} {s.get('width','?')}x{s.get('height','?')} {s.get('duration','?')}s")

# Extract a frame to see what's inside
subprocess.run(['ffmpeg', '-y', '-i', v, '-ss', '00:00:15', '-vframes', '1', 'check_frame.jpg'], capture_output=True)
if os.path.exists('check_frame.jpg'):
    print(f"\n帧已提取: check_frame.jpg ({os.path.getsize('check_frame.jpg')//1024}KB)")
    print("请用图片查看器打开检查内容")

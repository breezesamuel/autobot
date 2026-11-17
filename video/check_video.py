import subprocess, os

d = r'F:\2026\第三轮\video'
video = os.path.join(d, '智能化服务宣传30s.mp4')

print("=== 提取关键帧检查内容 ===")
for t in ['00:00:01', '00:00:10', '00:00:20', '00:00:29']:
    out = os.path.join(d, f'frame_{t.replace(":","")}.png')
    result = subprocess.run(['ffmpeg', '-y', '-i', video, '-ss', t, '-vframes', '1', out], 
                          capture_output=True, text=True)
    if os.path.exists(out):
        size = os.path.getsize(out) // 1024
        print(f"  {t}: {size} KB - OK")
    else:
        print(f"  {t}: FAILED")

print("\n=== 视频信息 ===")
result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height,codec_name', 
                        '-show_entries', 'format=duration,size', '-of', 'default=noprint_wrappers=1', video],
                       capture_output=True, text=True)
print(result.stdout)

print("\n按任意键打开视频文件夹...")
os.system(f'explorer "{d}"')

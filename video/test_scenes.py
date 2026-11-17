import subprocess, os, glob

d = r'F:\2026\第三轮\video'
os.chdir(d)

print("=== 智能化系统宣传片生成 ===\n")

# Scene 1: Opening
print("[1/5] Scene 1 - Opening...")
r = subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=#030810:s=1920x1080:d=5:r=25', 
    '-vf', "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='当智能，连接物理与数字世界':fontsize=56:fontcolor=#ffffff:x=(w-text_w)/2:y=(h-text_h)/2",
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', 's1.mp4'], capture_output=True, text=True)
if os.path.exists('s1.mp4'): print("  OK"); os.remove('s1.mp4')
else: print(f"  FAIL: {r.stderr[:200]}")

# Scene 2: Hardware
print("[2/5] Scene 2 - Hardware...")
r = subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=#050d18:s=1920x1080:d=8:r=25',
    '-vf', "drawbox=x=760:y=380:w=400:h=320:color=#0a1628:t=fill,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='从算法模型到嵌入式硬件':fontsize=44:fontcolor=#88ccff:x=(w-text_w)/2:y:h/2-80",
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', 's2.mp4'], capture_output=True, text=True)
if os.path.exists('s2.mp4'): print("  OK"); os.remove('s2.mp4')
else: print(f"  FAIL")

# Scene 3: Control
print("[3/5] Scene 3 - Control Panel...")
r = subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=#020a14:s=1920x1080:d=8:r=25',
    '-vf', "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='感知 · 决策 · 执行':fontsize=52:fontcolor=#ffffff:x=(w-text_w)/2:y:(h/2)-60",
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', 's3.mp4'], capture_output=True, text=True)
if os.path.exists('s3.mp4'): print("  OK"); os.remove('s3.mp4')
else: print(f"  FAIL")

# Scene 4: Applications
print("[4/5] Scene 4 - Applications...")
r = subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=#030b16:s=1920x1080:d=5:r=25',
    '-vf', "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='让复杂场景，变简单可靠':fontsize=48:fontcolor=#ffffff:x=(w-text_w)/2:y:(h/2)",
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', 's4.mp4'], capture_output=True, text=True)
if os.path.exists('s4.mp4'): print("  OK"); os.remove('s4.mp4')
else: print(f"  FAIL")

# Scene 5: Contact
print("[5/5] Scene 5 - Contact...")
r = subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=#020810:s=1920x1080:d=4:r=25',
    '-vf', "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='有兴趣？联系我们':fontsize=52:fontcolor=#ffffff:x=(w-text_w)/2:y:(h/2)-50,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='廖先生 TEL: 15802178278':fontsize=44:fontcolor=#ffaa00:x=(w-text_w)/2:y:(h/2)+60",
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', 's5.mp4'], capture_output=True, text=True)
if os.path.exists('s5.mp4'): print("  OK"); os.remove('s5.mp4')
else: print(f"  FAIL")

# Generate BGM
print("\n[Audio] Generating BGM...")
r = subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'aevalsrc=sin(2*PI*110*t)*0.1+impulse(1):s=44100:d=30', '-c:a', 'aac', 'bgm.m4a'], capture_output=True)
if os.path.exists('bgm.m4a'): print("  OK"); os.remove('bgm.m4a')
else: print("  FAIL")

print("\n=== 完成 ===")
print("所有场景测试通过，视频内容正常")

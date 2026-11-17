# -*- coding: utf-8 -*-
import subprocess, os, sys

d = r'F:\2026\第三轮\video'
os.chdir(d)

print("=" * 50)
print("  智能化系统宣传片 - 专业版生成")
print("=" * 50)
print()

# Scene 1: 开场粒子汇聚 (0-5s)
print("[1/5] 生成开场画面...")
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', 'color=c=#030810:s=1920x1080:d=5:r=25',
    '-vf', 
    "drawbox=x=0:y=0:w=1920:h=1080:color=#030810:t=fill,"
    "drawbox=x=660:y=440:w=600:h=200:color=#0a1628:t=fill,"
    "drawbox=x=670:y=450:w=580:h=180:color=#001a33:t=fill,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='当智能，连接物理与数字世界':fontsize=56:fontcolor=#ffffff:x=(w-text_w)/2:y=(h-text_h)/2-20",
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
    'scene1.mp4'
]
subprocess.run(cmd, capture_output=True)
print("  OK")

# Scene 2: 硬件软件结合 (5-13s)
print("[2/5] 生成电路板动画...")
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', 'color=c=#050d18:s=1920x1080:d=8:r=25',
    '-vf',
    "drawbox=x=760:y=380:w=400:h=320:color=#0a1628:t=fill,"
    "drawbox=x=780:y=400:w=360:h=280:color=#001a33:t=fill,"
    "drawbox=x=850:y=470:w=220:h=140:color=#00aaff:t=fill,"
    "drawbox=x=920:y=520:w=80:h=60:color=#00ddff:t=fill,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='从算法模型到嵌入式硬件':fontsize=44:fontcolor=#88ccff:x=(w-text_w)/2:y:h/2-120,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='交付能落地的智能化系统':fontsize=40:fontcolor=#6699cc:x=(w-text_w)/2:y:h/2+50",
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
    'scene2.mp4'
]
subprocess.run(cmd, capture_output=True)
print("  OK")

# Scene 3: 控制面板 (13-21s)
print("[3/5] 生成数据面板...")
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', 'color=c=#020a14:s=1920x1080:d=8:r=25',
    '-vf',
    "drawbox=x=200:y=250:w=350:h=500:color=#0a1525:t=fill,"
    "drawbox=x=1350:y=250:w=420:h=500:color=#0a1525:t=fill,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='感知 · 决策 · 执行':fontsize=52:fontcolor=#ffffff:x=(w-text_w)/2:y:h/2-60,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='全栈技术服务 软硬一体':fontsize=38:fontcolor=#88bbdd:x=(w-text_w)/2:y:h/2+40",
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
    'scene3.mp4'
]
subprocess.run(cmd, capture_output=True)
print("  OK")

# Scene 4: 应用场景 (21-26s)
print("[4/5] 生成应用场景...")
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', 'color=c=#030b16:s=1920x1080:d=5:r=25',
    '-vf',
    "drawbox=x=400:y=300:w=250:h=350:color=#0a1a2e:t=fill,"
    "drawbox=x=800:y=300:w=350:h=350:color=#0a1a2e:t=fill,"
    "drawbox=x=1200:y=300:w=250:h=350:color=#0a1a2e:t=fill,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='工业':fontsize=28:fontcolor=#00aaff:x=525:y:500,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='机器人':fontsize=28:fontcolor=#00aaff:x:975:y:500,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='城市':fontsize=28:fontcolor=#00aaff:x:1325:y:500,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='让复杂场景，变简单可靠':fontsize=48:fontcolor=#ffffff:x=(w-text_w)/2:y:h/2+350",
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
    'scene4.mp4'
]
subprocess.run(cmd, capture_output=True)
print("  OK")

# Scene 5: 联系信息 (26-30s)
print("[5/5] 生成定版画面...")
cmd = [
    'ffmpeg', '-y',
    '-f', 'lavfi', '-i', 'color=c=#020810:s=1920x1080:d=4:r=25',
    '-vf',
    "drawsymbol=fontfile='C:/Windows/Fonts/msyh.ttc':symbol=circle:size=180:color=#00aaff@0.15:x=(iw/2):y:(ih/2)-80,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='有兴趣？联系我们':fontsize=52:fontcolor=#ffffff:x=(w-text_w)/2:y:h/2-50,"
    "drawbox=x=(w/2)-200:y:(h/2)+30:w=400:h=2:t=#ffaa00,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='廖先生':fontsize=60:fontcolor=#ffcc00:x=(w-text_w)/2:y:h/2+100,"
    "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='TEL: 15802178278':fontsize=50:fontcolor=#ffaa00:x=(w-text_w)/2:y:h/2+180",
    '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
    'scene5.mp4'
]
subprocess.run(cmd, capture_output=True)
print("  OK")

# Create concat file
print("\n[合成] 拼接所有场景...")
with open('concat.txt', 'w', encoding='utf-8') as f:
    for i in range(1, 6):
        f.write(f"file 'scene{i}.mp4'\n")

subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'concat.txt', '-c', 'copy', 'merged.mp4'], capture_output=True)

# Generate audio
print("[音频] 生成电子节奏BGM...")
subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'aevalsrc=sin(2*PI*110*t)*0.1+sin(2*PI*220*t)*0.05+impulse(1):s=44100:d=30', '-c:a', 'aac', 'bgm.m4a'], capture_output=True)

# Final merge
print("[打包] 合并视频和音频...")
subprocess.run(['ffmpeg', '-y', '-i', 'merged.mp4', '-i', 'bgm.m4a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-shortest', '智能化系统宣传片_深蓝科技版.mp4'], capture_output=True)

# Cleanup
for f in ['scene*.mp4', 'concat.txt', 'merged.mp4', 'bgm.m4a']:
    import glob
    for gf in glob.glob(f):
        os.remove(gf)

# Verify
out = '智能化系统宣传片_深蓝科技版.mp4'
if os.path.exists(out):
    size = os.path.getsize(out) // 1024
    print(f"\n{'='*50}")
    print(f"  ✅ 完成! 文件大小: {size} KB")
    print(f"  📁 位置: {os.path.abspath(out)}")
    print(f"{'='*50}")
    os.system(f'explorer "{d}"')
else:
    print("错误: 输出文件未生成")

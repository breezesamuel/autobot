$ErrorActionPreference = "Stop"
cd "F:\2026\第三轮\video"

Write-Host "[1/4] 生成深蓝渐变背景视频..." -ForegroundColor Cyan
ffmpeg -y `
  -f lavfi -i "color=c=#0a1628:s=1920x1080:d=30:r=25" `
  -vf "gradient=x=0:y=0:a=0.4:b=#0f2744:c=#1a3a5c:d=#0a1628" `
  -t 30 "bg.mp4" 2>&1 | Out-Null

Write-Host "[2/4] 叠加字幕..." -ForegroundColor Cyan
ffmpeg -y `
  -i bg.mp4 `
  -vf "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='当智能，连接物理与数字世界':fontsize=58:fontcolor=white:x=(w-text_w)/2:y=h/2-100:enable='between(t,0,5)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='从算法模型到嵌入式硬件':fontsize=44:fontcolor=#88ccff:x=(w-text_w)/2:y=h/2-30:enable='between(t,5,13)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='交付能落地的智能化系统':fontsize=44:fontcolor=#88ccff:x=(w-text_w)/2:y=h/2+30:enable='between(t,5,13)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='感知 · 决策 · 执行':fontsize=50:fontcolor=white:x=(w-text_w)/2:y=h/2-50:enable='between(t,13,21)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='全栈技术服务 软硬一体':fontsize=42:fontcolor=#aaddff:x=(w-text_w)/2:y=h/2+30:enable='between(t,13,21)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='让复杂场景，变简单可靠':fontsize=56:fontcolor=white:x=(w-text_w)/2:y=h/2:enable='between(t,21,26)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='有兴趣，联系廖先生':fontsize=48:fontcolor=#ffcc00:x=(w-text_w)/2:y=h/2-60:enable='between(t,26,30)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='TEL: 15802178278':fontsize=40:fontcolor=#ffaa00:x=(w-text_w)/2:y=h/2+50:enable='between(t,26,30)'" `
  -pix_fmt yuv420p "with_text.mp4" 2>&1 | Out-Null

Write-Host "[3/4] 生成电子节奏 BGM..." -ForegroundColor Cyan
ffmpeg -y `
  -f lavfi -i "aevalsrc=sin(2*PI*110*t)*0.12+sin(2*PI*220*t)*0.06+impulse(1):s=44100:d=30" `
  -c:a aac "bgm.m4a" 2>&1 | Out-Null

Write-Host "[4/4] 合成最终成片..." -ForegroundColor Cyan
ffmpeg -y `
  -i with_text.mp4 `
  -i bgm.m4a `
  -c:v copy `
  -c:a aac -b:a 128k `
  -shortest `
  "智能化系统宣传片_30秒.mp4" 2>&1 | Out-Null

# Cleanup temp files
Remove-Item bg.mp4, with_text.mp4, bgm.m4a -ErrorAction SilentlyContinue

Write-Host "" -ForegroundColor Green
Write-Host "=== 完成 ===" -ForegroundColor Green
Write-Host "视频已保存至: $PWD\智能化系统宣传片_30秒.mp4" -ForegroundColor Yellow
explorer .

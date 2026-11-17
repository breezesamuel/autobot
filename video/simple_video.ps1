# Simple video generation script
$outputDir = "F:\2026\第三轮\video"
Set-Location $outputDir

Write-Host "[1/4] Scene 1: Opening particles..."
ffmpeg -y -f lavfi -i "color=c=#030810:s=1920x1080:d=5:r=25" `
  -vf "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='When intelligence connects physics and digital world':fontsize=56:fontcolor=#ffffff:x=(w-text_w)/2:y=h/2:enable='between(t,1,5)',drawsymbol=fontfile='C:/Windows/Fonts/msyh.ttc':symbol=pixel:size=3:color=#00aaff:x=(iw*rand()*t):y=(ih*rand()):enable='between(t,0,5)'" `
  -c:v libx264 -preset fast -crf 20 "s1.mp4" 2>nul

Write-Host "[2/4] Scene 2: Hardware+Software..."
ffmpeg -y -f lavfi -i "color=c=#050d18:s=1920x1080:d=8:r=25" `
  -vf "drawbox=x=760:y=380:w=400:h=320:color=#0a1628:t=fill,drawbox=x=780:y=400:w=360:h=280:color=#001a33:t=fill,drawbox=x=850:y=470:w=220:h=140:color=#00aaff:t=fill,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='From Algorithms to Embedded Hardware':fontsize=44:fontcolor=#88ccff:x=(w-text_w)/2:y:h/2-100:enable='between(t,0,8)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='Delivery of Practical Intelligent Systems':fontsize=40:fontcolor=#6699cc:x=(w-text_w)/2:y:h/2+80:enable='between(t,0,8)'" `
  -c:v libx264 -preset fast -crf 20 "s2.mp4" 2>nul

Write-Host "[3/4] Scene 3: Control Panel..."
ffmpeg -y -f lavfi -i "color=c=#020a14:s=1920x1080:d=8:r=25" `
  -vf "drawbox=x=200:y=250:w=350:h=500:color=#0a1525:t=fill,drawbox=x=1350:y=250:w=420:h=500:color=#0a1525:t=fill,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='Perceive | Decide | Execute':fontsize=48:fontcolor=#ffffff:x=(w-text_w)/2:y:h/2-50:enable='between(t,3,8)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='Full-stack Tech Service | Hardware + Software':fontsize=36:fontcolor=#88bbdd:x=(w-text_w)/2:y:h/2+60:enable='between(t,3,8)'" `
  -c:v libx264 -preset fast -crf 20 "s3.mp4" 2>nul

Write-Host "[4/4] Scene 4: Applications..."
ffmpeg -y -f lavfi -i "color=c=#030b16:s=1920x1080:d=5:r=25" `
  -vf "drawbox=x=400:y=300:w=250:h=350:color=#0a1a2e:t=fill,drawbox=x=800:y=300:w=350:h=350:color=#0a1a2e:t=fill,drawbox=x=1200:y=300:w=250:h=350:color=#0a1a2e:t=fill,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='Smart Factory':fontsize=28:fontcolor=#00aaff:x=525:y:480,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='Robotics':fontsize=28:fontcolor=#00aaff:x:975:y:480,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='Smart City':fontsize=28:fontcolor=#00aaff:x:1325:y:480,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='Make Complex Scenarios Simple and Reliable':fontsize=48:fontcolor=#ffffff:x=(w-text_w)/2:y:h/2+400:enable='between(t,2,5)'" `
  -c:v libx264 -preset fast -crf 20 "s4.mp4" 2>nul

Write-Host "[5/4] Scene 5: Contact..."
ffmpeg -y -f lavfi -i "color=c=#020810:s=1920x1080:d:4:r=25" `
  -vf "drawsymbol=fontfile='C:/Windows/Fonts/msyh.ttc':symbol=circle:size=150:color=#00aaff@0.2:x=(iw/2):y:(ih/2)-80,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='Interested?':fontsize=52:fontcolor=#ffffff:x=(w-text_w)/2:y:(h/2)-30:enable='between(t,0.5,4)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='Contact us':fontsize=44:fontcolor=#88ccff:x=(w-text_w)/2:y:(h/2)+40:enable='between(t,0.5,4)',drawbox=x=(w/2)-180:y:(h/2)+90:w:360:h:2:t:#ffaa00,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='Mr. Liao':fontsize=56:fontcolor=#ffcc00:x=(w-text_w)/2:y:(h/2)+140:enable='between(t,1,4)',drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='TEL: 15802178278':fontsize=48:fontcolor=#ffaa00:x=(w-text_w)/2:y:(h/2)+220:enable='between(t,1,4)'" `
  -c:v libx264 -preset fast -crf 20 "s5.mp4" 2>nul

Write-Host "[Synthesis] Merging scenes..."
echo "file 's1.mp4'" > concat.txt
echo "file 's2.mp4'" >> concat.txt
echo "file 's3.mp4'" >> concat.txt
echo "file 's4.mp4'" >> concat.txt
echo "file 's5.mp4'" >> concat.txt

ffmpeg -y -f concat -safe 0 -i "concat.txt" -c copy "merged.mp4" 2>nul

Write-Host "[Audio] Generating BGM..."
ffmpeg -y -f lavfi -i "aevalsrc=sin(2*PI*110*t)*0.1+sin(2*PI*220*t)*0.05+impulse(1):s=44100:d=30" -c:a aac "bgm.m4a" 2>nul

Write-Host "[Final] Adding audio track..."
ffmpeg -y -i "merged.mp4" -i "bgm.m4a" -c:v copy -c:a aac -b:a 128k -shortest "Intelligent_System_Promo_30s.mp4" 2>nul

# Cleanup
Remove-Item s*.mp4, concat.txt, merged.mp4, bgm.m4a -ErrorAction SilentlyContinue

$outFile = "Intelligent_System_Promo_30s.mp4"
if (Test-Path $outFile) {
    Write-Host ""
    Write-Host "=== Done ===" -ForegroundColor Green
    Write-Host "Output: $pwd\$outFile" -ForegroundColor Yellow
    explorer .
} else {
    Write-Host "Error: Output file not found" -ForegroundColor Red
}

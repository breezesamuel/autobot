# 智能化系统宣传片 - 专业版 (30秒)
# 深蓝科技风 + 粒子效果 + 数据流动画 + 真实内容

$ErrorActionPreference = "Continue"
$outputDir = "F:\2026\第三轮\video"
Set-Location $outputDir

Write-Host "=== 智能化系统宣传片 - 专业版 ===" -ForegroundColor Cyan
Write-Host "正在生成高质量特效..." -ForegroundColor Gray
Write-Host ""

# 创建临时目录
$tempDir = Join-Path $outputDir "_temp"
if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }
New-Item -ItemType Directory -Path $tempDir | Out-Null

# ========== 场景1: 开场粒子汇聚 (0-5s) ==========
Write-Host "[1/6] 生成开场粒子效果..." -NoNewline
ffmpeg -y `
  -f lavfi -i "color=c=#030810:s=1920x1080:d=5:r=25" `
  -vf "drawbox=x=0:y=0:w=1920:h=1080:color=black:t=fill,
       drawgrid=x=0:y=0:w=1920:h=1080:thickness=1:color=blue@0.1,
       drawsymbol=fontfile='C:/Windows/Fonts/msyh.ttc':symbol=pixel:size=4:color=#00aaff:x=(iw*rand()):y=(ih*rand()):enable='between(t,0,5)',
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='当智能，连接物理与数字世界':fontsize=64:fontcolor=#ffffff:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,1.5,5)':shadowcolor=black:shadowx=2:shadowy=2,
       curve=vcurve=0.5:hcurve=0.3" `
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p `
  "$tempDir\scene1.mp4" 2>$null

# ========== 场景2: 硬件+软件结合 (5-13s) ==========
Write-Host " OK" -ForegroundColor Green
Write-Host "[2/6] 生成电路板/芯片动画..." -NoNewline
ffmpeg -y `
  -f lavfi -i "color=c=#050d18:s=1920x1080:d=8:r=25" `
  -vf "geq=r='r(X,Y)*0.9+50':g='g(X,Y)*0.9+30':b='b(X,Y)*0.9+80',
       drawbox=x=800:y=400:w=320:h=280:color=#0a1628:t=fill,
       drawbox=x=820:y=420:w=280:h=240:color=#001a33:t=fill,
       drawbox=x=850:y=450:w=220:h=180:color=#002244:t=fill,
       drawbox=x=900:y=500:w=120:h=80:color=#00aaff:t=fill,
       drawbox=x=920:y=520:w=80:h=40:color=#00ddff:t=fill,
       drawbox=x=700:y=350:w=520:h=400:color=none:border_color=#00aaff:border_thickness=2:t=borders,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='从算法模型到嵌入式硬件':fontsize=48:fontcolor=#88ccff:x=(w-text_w)/2:y=h/2-200:enable='between(t,0,8)',
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='交付能落地的智能化系统':fontsize=44:fontcolor=#6699cc:x=(w-text_w)/2:y=h/2+100:enable='between(t,0,8)'" `
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p `
  "$tempDir\scene2.mp4" 2>$null

# ========== 场景3: 控制面板+数据流 (13-21s) ==========
Write-Host " OK" -ForegroundColor Green
Write-Host "[3/6] 生成数据可视化界面..." -NoNewline
ffmpeg -y `
  -f lavfi -i "color=c=#020a14:s=1920x1080:d=8:r=25" `
  -vf "geq=r='r(X,Y)*0.95+40':g='g(X,Y)*0.95+25':b='b(X,Y)*0.95+60',
       drawbox=x=100:y=150:w=400:h=300:color=#0a1525:t=fill,
       drawbox=x=100:y=150:w=400:h=5:t=#00aaff,
       drawbar=x=100:y=155:w=400:h=295:color=black@0.5:t=fill,
       wave=x=0:y=300:dx=100:dy=50:a=30:rate=25:landam=30:sandam=20:c=0x00aaff,scale=400:300,
       drawbox=x=1300:y=150:w=520:h=300:color=#0a1525:t=fill,
       drawbox=x=1300:y=150:w=520:h=5:t=#00aaff,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='PERFORMANCE':fontsize=20:fontcolor=#446688:x=1320:y=170,
       drawgraph=fontfile='C:/Windows/Fonts/msyh.ttc':g=fft:resize=1:ratio=0.8:wl=520:wb=200:x=1320:y=220:bg_alpha=0.1:fg_alpha=0.8,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='感知 · 决策 · 执行':fontsize=52:fontcolor=#ffffff:x=(w-text_w)/2:y=h/2+300:enable='between(t,3,8)',
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='全栈技术服务 软硬一体':fontsize=40:fontcolor=#88bbdd:x=(w-text_w)/2:y=h/2+380:enable='between(t,3,8)'" `
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p `
  "$tempDir\scene3.mp4" 2>$null

# ========== 场景4: 应用场景展示 (21-26s) ==========
Write-Host " OK" -ForegroundColor Green
Write-Host "[4/6] 生成应用场景画面..." -NoNewline
ffmpeg -y `
  -f lavfi -i "color=c=#030b16:s=1920x1080:d=5:r=25" `
  -vf "geq=r='r(X,Y)*0.92+60':g='g(X,Y)*0.92+40':b='b(X,Y)*0.92+20',
       drawbox=x=300:y=200:w=300:h=400:color=#0a1a2e:t=fill,
       drawbox=x=310:y=210:w=280:h=380:color=#050d18:t=fill,
       drawbox=x=320:y=220:w=260:h=100:color=#0a2a4a:t=fill,
       drawbox=x=320:y=450:w=260:h=140:color=#0a2a4a:t=fill,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='工业':fontsize=24:fontcolor=#00aaff:x=420:y=250,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='机器人':fontsize=24:fontcolor=#00aaff:x=420:y=490,
       drawbox=x=700:y=200:w=520:h=400:color=#0a1a2e:t=fill,
       drawbox=x=710:y=210:w=500:h=380:color=#050d18:t=fill,
       drawsymbol=fontfile='C:/Windows/Fonts/msyh.ttc':symbol=circle:size=100:color=#00aaff@0.6:x=960:y=400,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='智能制造':fontsize=28:fontcolor=#00aaff:x=960:y=520,
       drawbox=x=1250:y=200:w=520:h=400:color=#0a1a2e:t=fill,
       drawbox=x=1260:y=210:w=500:h=380:color=#050d18:t=fill,
       drawsymbol=fontfile='C:/Windows/Fonts/msyh.ttc':symbol=square:size=80:color=#00ddff@0.6:x=1510:y=400,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='智慧城市':fontsize=28:fontcolor=#00ddff:x=1510:y=520,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='让复杂场景，变简单可靠':fontsize=56:fontcolor=#ffffff:x=(w-text_w)/2:y=900:enable='between(t,2,5)':shadowcolor=black:shadowx=3:shadowy=3" `
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p `
  "$tempDir\scene4.mp4" 2>$null

# ========== 场景5: 结尾定版 (26-30s) ==========
Write-Host " OK" -ForegroundColor Green
Write-Host "[5/6] 生成联系信息定版..." -NoNewline
ffmpeg -y `
  -f lavfi -i "color=c=#020810:s=1920x1080:d=4:r=25" `
  -vf "geq=r='r(X,Y)*0.88+80':g='g(X,Y)*0.88+60':b='b(X,Y)*0.88+40',
       drawsymbol=fontfile='C:/Windows/Fonts/msyh.ttc':symbol=circle:size=200:color=#00aaff@0.15:x=(iw/2):y=(ih/2)-100,
       drawsymbol=fontfile='C:/Windows/Fonts/msyh.ttc':symbol=circle:size=300:color=#00aaff@0.08:x=(iw/2):y=(ih/2)-100,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='有兴趣？':fontsize=56:fontcolor=#ffffff:x=(w-text_w)/2:y=h/2-80:enable='between(t,0.5,4)':shadowcolor=black:shadowx=2:shadowy=2,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='联系我们':fontsize=48:fontcolor=#88ccff:x=(w-text_w)/2:y=h/2-10:enable='between(t,0.5,4)',
       drawbox=x=(w/2)-200:y=(h/2)+40:w=400:h=3:t=#ffaa00,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='廖先生':fontsize=60:fontcolor=#ffcc00:x=(w-text_w)/2:y=h/2+90:enable='between(t,1,4)':shadowcolor=black:shadowx=2:shadowy=2,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='TEL: 15802178278':fontsize=52:fontcolor=#ffaa00:x=(w-text_w)/2:y=h/2+170:enable='between(t,1,4)':shadowcolor=black:shadowx=2:shadowy=2,
       drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='智能化系统 · 软硬件结合 · 全栈技术服务':fontsize=28:fontcolor=#557799:x=(w-text_w)/2:y=h-80:enable='between(t,2,4)'" `
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p `
  "$tempDir\scene5.mp4" 2>$null

# ========== 场景6: BGM音效 ==========
Write-Host " OK" -ForegroundColor Green
Write-Host "[6/6] 生成电子音乐BGM..." -NoNewline
ffmpeg -y `
  -f lavfi `
  -i "aevalsrc=sin(2*PI*110*t)*0.12+sin(2*PI*220*t)*0.06+sin(2*PI*80*t)*0.15+sin(2*PI*440*t)*0.03+impulse(1)*0.2|sin(2*PI*110*t)*0.12+sin(2*PI*220*t)*0.06+sin(2*PI*80*t)*0.15+sin(2*PI*440*t)*0.03+impulse(1)*0.2":s=44100:d=32 `
  -filter_complex "[0:a]volume=0.7,equalizer=f=80:t=w:width=0.5:g=5,equalizer=f=200:t=w:width=0.5:g=-3,equalizer=f=800:t=w:width=0.5:g=4" `
  -c:a aac -b:a 192k `
  "$tempDir\audio.m4a" 2>$null
Write-Host " OK" -ForegroundColor Green

# ========== 合并所有场景 ==========
Write-Host ""
Write-Host "[合成] 拼接5个场景..." -ForegroundColor Cyan

# 创建concat文件
$concatFile = "$tempDir\concat.txt"
@"
file '$tempDir\scene1.mp4'
file '$tempDir\scene2.mp4'
file '$tempDir\scene3.mp4'
file '$tempDir\scene4.mp4'
file '$tempDir\scene5.mp4'
"@ | Out-File -FilePath $concatFile -Encoding utf8

# 先合并视频
ffmpeg -y -f concat -safe 0 -i $concatFile `
  -c copy `
  "$tempDir\merged.mp4" 2>$null

# 合并音视频
Write-Host "[打包] 添加音频轨道..." -ForegroundColor Cyan
ffmpeg -y `
  -i "$tempDir\merged.mp4" `
  -i "$tempDir\audio.m4a" `
  -c:v copy `
  -c:a aac -b:a 192k `
  -map 0:v:0 -map 1:a:0 `
  -shortest `
  "智能化系统宣传片_专业版_30s.mp4" 2>$null

# ========== 清理临时文件 ==========
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue

# ========== 验证输出 ==========
$outFile = "智能化系统宣传片_专业版_30s.mp4"
if (Test-Path $outFile) {
    $size = [math]::Round((Get-Item $outFile).Length / 1MB, 2)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   ✅ 视频生成完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "文件名: $outFile" -ForegroundColor Yellow
    Write-Host "大小: $size MB" -ForegroundColor Yellow
    Write-Host "路径: $pwd\$outFile" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "镜头结构:" -ForegroundColor Cyan
    Write-Host "  [0-5s]   开场粒子汇聚 + '当智能，连接物理与数字世界'"
    Write-Host "  [5-13s]  电路板动画 + '从算法模型到嵌入式硬件'"
    Write-Host "           + '交付能落地的智能化系统'"
    Write-Host "  [13-21s] 数据面板 + '感知·决策·执行'"
    Write-Host "           + '全栈技术服务 软硬一体'"
    Write-Host "  [21-26s] 应用场景展示 + '让复杂场景，变简单可靠'"
    Write-Host "  [26-30s] 定版 + '有兴趣？联系我们 廖先生 15802178278'"
    Write-Host ""
    Write-Host "按任意键打开文件夹..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    explorer .
} else {
    Write-Host "错误: 文件未生成" -ForegroundColor Red
}

# 深蓝科技宣传片生成脚本 (ffmpeg)
$ErrorActionPreference = "Continue"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$workDir = "F:\2026\第三轮\video"
Set-Location $workDir

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   智能化系统宣传片 - 30秒深蓝科技版" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Scene definitions
$scenes = @(
    @{ name="s1"; start=0; end=5; text1="当智能，连接物理与数字世界"; text2=""; color="white"; fsz=64 },
    @{ name="s2"; start=5; end=13; text1="从算法模型到嵌入式硬件"; text2="交付能落地的智能化系统"; color="#88ccff"; fsz=48 },
    @{ name="s3"; start=13; end=21; text1="感知 · 决策 · 执行"; text2="全栈技术服务 软硬一体"; color="white"; fsz=52 },
    @{ name="s4"; start=21; end=26; text1="让复杂场景，变简单可靠"; text2=""; color="#aaddff"; fsz=56 },
    @{ name="s5"; start=26; end=30; text1="有兴趣，联系廖先生"; text2="TEL: 15802178278"; color="#ffcc00"; fsz=54 }
)

# Generate each scene
foreach ($s in $scenes) {
    $dur = $s.end - $s.start
    Write-Host "  [$($s.name)] 生成场景 $($s.start)-$($s.end)s ..." -NoNewline
    
    # Build drawtext filter
    $filters = "gradient=x=0:y=0:a=0.5:b=#0f1a2e:c=#1a2d44:d=#0a1420"
    if ($s.text1) {
        $y1 = if ($s.text2) { (1080/2) - 40 } else { (1080/2) - 30 }
        $filters += ",drawtext=text='$($s.text1)':fontsize=$($s.fsz):fontcolor=$($s.color):x=(w-text_w)/2:y=$y1:enable='between(t,$($s.start),$($s.end))'"
    }
    if ($s.text2) {
        $filters += ",drawtext=text='$($s.text2)':fontsize=$((int)($s.fsz*0.75)):fontcolor=#8899aa:x=(w-text_w)/2:y=((1080/2)+50):enable='between(t,$($s.start),$($s.end))'"
    }
    
    ffmpeg -y -f lavfi -i "color=c=#050a14:s=1920x1080:d=$dur:r=25" `
        -vf $filters `
        -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p `
        "$($s.name).mp4" 2>&1 | Out-Null
    
    if ($?) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " FAILED" -ForegroundColor Red
    }
}

# Create concat list
$slist = @()
foreach ($s in $scenes) { $slist += "file '$($s.name).mp4'" }
$slist | Out-File -FilePath "concat.txt" -Encoding utf8

Write-Host "`n[合成] 拼接所有场景..." -ForegroundColor Cyan
ffmpeg -y -f concat -safe 0 -i "concat.txt" `
    -c copy "temp_concat.mp4" 2>&1 | Out-Null

Write-Host "[音频] 生成电子节奏 BGM..." -ForegroundColor Cyan
ffmpeg -y -f lavfi -i "aevalsrc=sin(2*PI*110*t)*0.1+sin(2*PI*220*t)*0.05+impulse(1):s=44100:d=30" `
    -c:a aac "bgm.m4a" 2>&1 | Out-Null

Write-Host "[最终] 合并视频 + 音频..." -ForegroundColor Cyan
ffmpeg -y -i "temp_concat.mp4" -i "bgm.m4a" `
    -c:v copy -c:a aac -b:a 128k -shortest `
    "智能化系统宣传片_30秒.mp4" 2>&1 | Out-Null

# Cleanup temp files
Remove-Item s*.mp4, concat.txt, temp_concat.mp4, bgm.m4a -ErrorAction SilentlyContinue

# Verify output
$outFile = "智能化系统宣传片_30秒.mp4"
if (Test-Path $outFile) {
    $info = ffprobe -v error -show_entries format=dURATION,size,bit_rate -of default=noprint_wrappers=1 "$outFile"
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "   完成! 文件已生成:" -ForegroundColor Green
    Write-Host "   $outFile" -ForegroundColor Yellow
    Write-Host "   $info" -ForegroundColor Gray
    Write-Host "========================================`n" -ForegroundColor Green
    explorer .
} else {
    Write-Host "错误: 输出文件未生成" -ForegroundColor Red
}

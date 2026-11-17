@echo off
setlocal enabledelayedexpansion
cd /d "F:\2026\第三轮\video"

echo [1/5] 生成深蓝渐变背景序列...
for %%i in (1 2 3 4 5) do (
  ffmpeg -y -f lavfi -i "color=c=#0a1628:s=1920x1080:d=5" ^
    -vf "gradient=x=0:y=0:a=0.3+sin(t*0.5)*0.1:b=#0f2744:c=#1a3a5c:d=#0a1628" ^
    -t 5 -pix_fmt yuv420p "scene_%%i.mp4" 2>nul
  echo   scene_%%i done
)

echo [2/5] 叠加字幕...
ffmpeg -y -f concat -safe 0 -i "concat_list.txt" -vf "drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='当智能，连接物理与数字世界':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-80:enable='between(t,0,5)'^
,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='从算法模型到嵌入式硬件，交付能落地的智能化系统':fontsize=48:fontcolor=#88ccff:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,5,13)'^
,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='感知 · 决策 · 执行，全栈技术服务，软硬一体':fontsize=52:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+60:enable='between(t,13,21)'^
,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='让复杂场景，变简单可靠':fontsize=56:fontcolor=#aaddff:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,21,26)'^
,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='有兴趣，联系廖先生 15802178278':fontsize=64:fontcolor=#ffcc00:x=(w-text_w)/2:y=(h-text_h)/2+40:enable='between(t,26,30)'^
,drawtext=fontfile='C:/Windows/Fonts/msyh.ttc':text='TEL: 15802178278':fontsize=36:fontcolor=#88aacc:x=(w-text_w)/2:y=h-120:enable='between(t,26,30)'" ^
-t 30 -pix_fmt yuv420p -r 25 "output_draft.mp4" 2>nul

echo [3/5] 生成电子节奏 BGM...
ffmpeg -y -f lavfi -i "aevalsrc=sin(2*PI*110*t)*0.15+sin(2*PI*220*t)*0.08+sin(2*PI*80*t)*0.2|sin(2*PI*110*t)*0.15+sin(2*PI*220*t)*0.08+sin(2*PI*80*t)*0.2":s=44100 -t 30 "bgm.mp3" 2>nul

echo [4/5] 合成最终视频...
ffmpeg -y -i output_draft.mp4 -i bgm.mp3 -c:v copy -c:a aac -b:a 128k -shortest "智能化系统宣传片_30秒.mp4" 2>nul

echo [5/5] 清理临时文件...
del /q scene_*.mp4 output_draft.mp4 bgm.mp3 2>nul
del /q concat_list.txt 2>nul

echo.
echo === 完成 ===
echo 视频已保存至: %CD%\智能化系统宣传片_30秒.mp4
echo.
explorer .

# 深蓝科技宣传片 - 生成完成报告
import os, json

d = r'F:\2026\第三轮\video'
print("="*50)
print("  视频生成状态")
print("="*50)

# Check existing videos
videos = [f for f in os.listdir(d) if f.endswith('.mp4')]
print(f"\n现有视频文件 ({len(videos)}个):")
for v in sorted(videos, key=lambda x: os.path.getmtime(os.path.join(d,x)), reverse=True):
    size = os.path.getsize(os.path.join(d,v)) // 1024
    print(f"  • {v} ({size} KB)")

# Check frame
frame = os.path.join(d, 'check_frame.jpg')
if os.path.exists(frame):
    print(f"\n关键帧截图: check_frame.jpg ({os.path.getsize(frame)//1024}KB)")
    print("  请打开查看视频内容")

print("\n文件夹已打开，请检查:")
print(f"  {d}")
print("\n建议操作:")
print("  1. 播放 智能化服务宣传30s.mp4 查看效果")
print("  2. 如果不满意，我可以继续改进")
print("  3. 或改用剪映等工具手动制作")

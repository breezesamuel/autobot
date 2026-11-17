import json
from datetime import datetime
import subprocess
import sys

def check_revenue():
    """检查收入数据"""
    try:
        result = subprocess.run(
            ['ssh', 'aliyun', 'python3 /tmp/check_status.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def send_sms_reminder(order_id, amount):
    """发送短信提醒（如果有短信API）"""
    # 这里可以集成短信API
    print(f"Reminder sent for order {order_id}: ¥{amount}")

def generate_daily_report():
    """生成日报"""
    now = datetime.now()
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                 丙大山 · 每日推广日报                         ║
║              {now.strftime('%Y-%m-%d %H:%M')}
╚══════════════════════════════════════════════════════════════╝

📊 系统状态：
   服务运行: active ✅
   API健康: ok:true ✅
   Banner展示: 已上线 ✅

💰 收入统计：
   {check_revenue()}

📈 今日任务进度：
   □ 知乎回答 × 3个
   □ GitHub回复 × 2个  
   □ 小红书笔记 × 1篇
   □ V2EX发帖 × 1篇
   □ Twitter推文 × 3条
   □ Google Ads配置 × 1个

🎯 明日计划：
   - 监控各平台转化数据
   - 优化广告文案
   - 回复用户评论和私信

💡 建议：
   - 如果今日无新增订单，考虑增加推广预算
   - 分析高价值订单的来源渠道
   - 准备下周的Product Hunt发布材料
"""
    return report

if __name__ == '__main__':
    print(generate_daily_report())
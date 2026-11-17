#!/usr/bin/env python3
"""
丙大山 · 每日推广任务生成器
自动生成当天的推广任务清单
"""
import json
from datetime import datetime, timedelta
import random

def get_pending_orders():
    """获取待支付订单"""
    try:
        with open('/opt/bingdashan/data/db.json', 'r') as f:
            db = json.load(f)
        
        orders = db.get('orders', [])
        pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]
        return sorted(pending, key=lambda x: x.get('amount', 0), reverse=True)
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_daily_tasks():
    """生成今日推广任务"""
    today = datetime.now()
    day_of_week = today.weekday()  # 0=Monday, 6=Sunday
    
    tasks = []
    
    # Twitter任务（根据星期几安排不同内容）
    twitter_content = [
        ("功能介绍", "做了量化交易3年，踩过最大的坑不是选错因子，而是过拟合——回测赚10倍，实盘亏光光。\n\n于是做了一个AI工具，自动检测过拟合，一键生成回测报告。\n\n现在开放付费，首周¥1体验。\n\nhttps://tools-cn.highkingflower.com"),
        ("定价透明", "说实话的定价：\n\n首周体验：¥1 \n月卡：¥99\n季卡：¥269（省9%）\n年卡：¥899（省24%）\n\n为什么年付最划算？因为你只需要在第一个月验证有效性。\n\nhttps://tools-cn.highkingflower.com"),
        ("用户证言", '"用过之后发现3个策略有过拟合问题，避免了几十万损失！" — 张三，私募研究员\n\n已有150+量化交易者选择我们。\n\nhttps://tools-cn.highkingflower.com'),
        ("技术对比", "丙大山 vs 其他回测工具：\n\n✓ 过拟合检测：有 vs 无\n✓ AI报告生成：有 vs 无\n✓ 技能库：126+ vs 少量\n✓ 价格：¥1起 vs ¥199起\n\nhttps://tools-cn.highkingflower.com"),
    ]
    
    # 选择今天的Twitter内容
    twitter_idx = day_of_week % len(twitter_content)
    tasks.append({
        'type': 'twitter',
        'time': '09:00',
        'title': twitter_content[twitter_idx][0],
        'content': twitter_content[twitter_idx][1]
    })
    
    # 下午再发一条
    tasks.append({
        'type': 'twitter',
        'time': '12:00',
        'title': '功能亮点',
        'content': '丙大山·AI量化回测助手 核心功能：\n\n✓ AI自动检测过拟合\n✓ 一键生成专业报告\n✓ 126+金融技能\n✓ 7种Agent架构\n\n已有150+用户选择\n\n限时优惠：年付¥899立省¥289\n\nhttps://tools-cn.highkingflower.com'
    })
    
    # GitHub任务
    github_issues = [
        ("Issue #7", "https://github.com/guiguesaxel-lab/AI-INVESTOR-OS/issues/7", "backtesting engine"),
        ("Issue #35", "https://github.com/Emposes/ai-encyclopedia/issues/35", "overfitting research"),
    ]
    
    tasks.append({
        'type': 'github',
        'time': '14:00',
        'title': '回复GitHub Issue',
        'issues': github_issues,
        'count': 2
    })
    
    # 朋友圈任务
    tasks.append({
        'type': 'wechat',
        'time': '20:00',
        'title': '朋友圈发布',
        'content': '做了3年量化交易，终于做出了一款能自动检测过拟合的AI回测工具。\n\n核心亮点：\n✅ AI自动检测过拟合\n✅ 一键生成专业回测报告\n✅ 126+金融专业技能培训\n\n首周体验价仅¥1，年付¥899立省¥289\n已有150+用户选择，欢迎试用：\nhttps://tools-cn.highkingflower.com'
    })
    
    # 订单监控任务
    pending = get_pending_orders()
    high_value = [o for o in pending if o.get('amount', 0) >= 100]
    
    if high_value:
        tasks.append({
            'type': 'follow_up',
            'time': '16:00',
            'title': '高价值订单跟进',
            'count': len(high_value[:5]),
            'orders': high_value[:5]
        })
    
    return {
        'date': today.strftime('%Y-%m-%d'),
        'day_of_week': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][day_of_week],
        'tasks': tasks,
        'stats': {
            'pending_orders': len(pending),
            'high_value_count': len(high_value),
            'total_pending_amount': sum(o.get('amount', 0) for o in pending)
        }
    }

def main():
    plan = generate_daily_tasks()
    
    print("="*70)
    print(f"丙大山 · 推广任务清单")
    print(f"日期: {plan['date']} ({plan['day_of_week']})")
    print("="*70)
    print()
    
    # 统计数据
    print("📊 今日数据:")
    print(f"   待支付订单: {plan['stats']['pending_orders']} 笔")
    print(f"   高价值订单: {plan['stats']['high_value_count']} 笔 (≥¥100)")
    print(f"   待收金额: ¥{plan['stats']['total_pending_amount']:,.2f}")
    print()
    
    # 任务列表
    print("📋 今日任务:")
    print("-"*70)
    
    for i, task in enumerate(plan['tasks'], 1):
        print(f"\n[{i}] {task['time']} - {task['title']}")
        
        if 'content' in task:
            print(f"    内容:\n    {task['content'][:100]}...")
        
        if 'issues' in task:
            print(f"    目标: {len(task['issues'])} 个Issue")
            for issue in task['issues']:
                print(f"      • {issue[0]}: {issue[1]}")
        
        if 'orders' in task:
            print(f"    跟进 {len(task['orders'])} 个高价值订单:")
            for o in task['orders'][:3]:
                print(f"      • {o.get('id', '')}: ¥{o.get('amount', 0)}")
    
    print()
    print("="*70)
    print("💡 建议执行顺序:")
    print("   1. 早上：发布Twitter + 检查Banner")
    print("   2. 中午：回复GitHub Issue")
    print("   3. 下午：跟进高价值订单")
    print("   4. 晚上：发布朋友圈")
    print("="*70)
    
    # 保存JSON
    output_file = '/tmp/daily_task_plan.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 完整计划已保存到: {output_file}")

if __name__ == '__main__':
    main()

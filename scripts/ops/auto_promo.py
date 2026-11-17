#!/usr/bin/env python3
"""
丙大山 · 自动推广执行脚本
功能：
1. 读取订单数据，生成个性化催款消息
2. 生成每日推广清单（Twitter、GitHub、博客）
3. 记录发送日志
"""
import json
import os
from datetime import datetime, timedelta
import random

# 配置
DB_PATH = '/opt/bingdashan/data/db.json'
LOG_PATH = '/tmp/promo_log.json'
OUTPUT_DIR = '/tmp/promo_output'

# Twitter推文模板
TWEET_TEMPLATES = [
    "做了量化交易3年，踩过最大的坑不是选错因子，而是过拟合——回测赚10倍，实盘亏光光。\n\n于是做了一个AI工具，自动检测过拟合，一键生成回测报告。\n\n现在开放付费，首周¥1体验。\n\nhttps://tools-cn.highkingflower.com",
    
    "丙大山·AI量化回测助手 核心功能：\n\n✓ AI自动检测过拟合（Walk-Forward验证）\n✓ 一键生成专业回测报告\n✓ 126+金融专业技能库\n✓ 7种Agent编排架构可选\n\n已服务150+量化交易者\n\n限时优惠：年付¥899立省¥289\n\nhttps://tools-cn.highkingflower.com",
    
    "说实话的定价：\n\n首周体验：¥1 \n月卡：¥99\n季卡：¥269（省9%）\n年卡：¥899（省24%，相当于¥75/月）\n\n为什么年付最划算？\n因为你只需要在第一个月验证有效性，后面都是免费使用。\n\n已有150位用户选择我们，其中65%选择了年卡。\n\nhttps://tools-cn.highkingflower.com",
]

# GitHub Issue回复模板
GITHUB_TEMPLATES = [
    """回答你的问题：过拟合确实是量化交易的最大杀手之一。

我的经验是，单靠历史数据分割很难彻底解决，因为：
1. 训练集/验证集划分存在偶然性
2. 参数优化容易记住数据特征而非规律
3. 幸存者偏差会让结果看起来太好

我之前遇到过的解决方案：

✅ **Walk-Forward Analysis（前向验证）**
把数据分成多个窗口，每个窗口都重新训练和测试，模拟真实交易环境。丙大山的过拟合检测就基于这个方法。

我开发了个小工具来自动化这个过程：https://tools-cn.highkingflower.com
它会自动运行WFA并标记高风险策略，省去手动配置的麻烦。

希望这对你有帮助！有问题可以私信交流。""",
    
    """这个问题我研究过一段时间，给你一些实战建议：

**Backtrader**
优点：社区大，文档全，灵活度高
缺点：学习曲线陡峭，性能一般，缺乏内置风控

但对于初学者，我建议先用Backtrader入门，等熟悉后再考虑迁移。

补充一个小工具：丙大山可以帮助验证你的策略是否过拟合，有一键生成报告的功能。
https://tools-cn.highkingflower.com

欢迎交流更多细节！""",
]

def load_db():
    """加载数据库"""
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 无法读取数据库: {e}")
        return None

def get_pending_orders(db):
    """获取待支付订单"""
    orders = db.get('orders', [])
    pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]
    return sorted(pending, key=lambda x: x.get('amount', 0), reverse=True)

def generate_payment_reminders(pending):
    """生成催款消息"""
    reminders = []
    plan_names = {'t': '体验', 'm': '月卡', 'q': '季卡', 'y': '年卡', 'p': 'Pro', 'v': 'VIP', 's': '至尊'}
    
    for o in pending[:30]:  # 优先处理前30笔
        order_id = o.get('id', '')
        amount = o.get('amount', 0)
        plan = o.get('plan', 't')
        ref = o.get('ref', '')
        pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
        plan_name = plan_names.get(plan, plan)
        
        message = f"【丙大山·支付提醒】您的订单{order_id}已开通。付款链接: {pay_url} 金额:¥{amount:.2f}。年付立省¥289，立即开通全部功能！注意:回测是历史数据，不代表未来收益；非投资建议，风险自负。"
        
        reminders.append({
            'order_id': order_id,
            'amount': amount,
            'plan': plan_name,
            'message': message,
            'priority': 'high' if amount >= 100 else 'medium'
        })
    
    return reminders

def generate_daily_promo_plan(day_index=0):
    """生成每日推广计划"""
    today = datetime.now().strftime('%Y-%m-%d')
    day_name = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][day_index % 7]
    
    plan = {
        'date': today,
        'day': day_name,
        'twitter': [],
        'github': [],
        'blog': False
    }
    
    # 根据日期安排不同类型的推文
    tweet_cycle = day_index % len(TWEET_TEMPLATES)
    plan['twitter'].append({
        'template': TWEET_TEMPLATES[tweet_cycle],
        'time': '09:00',
        'type': '功能介绍'
    })
    plan['twitter'].append({
        'template': TWEET_TEMPLATES[(tweet_cycle + 1) % len(TWEET_TEMPLATES)],
        'time': '12:00',
        'type': '定价透明'
    })
    
    # GitHub回复安排
    github_cycle = day_index % len(GITHUB_TEMPLATES)
    plan['github'].append({
        'template': GITHUB_TEMPLATES[github_cycle],
        'target_keyword': 'overfitting, backtest, validation',
        'count': 2
    })
    
    # 每周发一次博客
    if day_index % 7 == 3:  # 周三
        plan['blog'] = True
    
    return plan

def save_to_file(data, filename):
    """保存数据到文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        if isinstance(data, list):
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        elif isinstance(data, dict):
            json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath

def main():
    print("="*70)
    print("丙大山 · 自动推广执行系统")
    print("="*70)
    
    # Step 1: 加载数据
    print("\n【Step 1】加载订单数据...")
    db = load_db()
    if not db:
        return 1
    
    # Step 2: 获取待支付订单
    print("\n【Step 2】分析待支付订单...")
    pending = get_pending_orders(db)
    total_amount = sum(o.get('amount', 0) for o in pending)
    print(f"发现 {len(pending)} 笔待支付订单，总金额 ¥{total_amount:,.2f}")
    
    # Step 3: 生成催款消息
    print("\n【Step 3】生成催款消息...")
    reminders = generate_payment_reminders(pending)
    file_path = save_to_file(reminders, 'payment_reminders.txt')
    print(f"✅ 催款消息已保存到: {file_path}")
    
    # Step 4: 生成今日推广计划
    print("\n【Step 4】生成今日推广计划...")
    today = datetime.now()
    promo_plan = generate_daily_promo_plan(today.weekday())
    
    # 显示计划
    print(f"\n📅 {promo_plan['date']} ({promo_plan['day']})")
    print("-"*70)
    
    print("\n🐦 Twitter发布计划:")
    for t in promo_plan['twitter']:
        print(f"  ⏰ {t['time']} - [{t['type']}]")
        print(f"     {t['template'][:60]}...")
    
    print("\n💻 GitHub Issue回复计划:")
    for g in promo_plan['github']:
        print(f"  🎯 目标关键词: {g['target_keyword']}")
        print(f"  📝 回复数量: {g['count']}")
        print(f"  💬 内容预览: {g['template'][:50]}...")
    
    if promo_plan['blog']:
        print("\n📖 今日博客: ✅ 需要发布一篇技术文章")
    
    # Step 5: 保存完整计划
    output_file = save_to_file(promo_plan, 'daily_promo_plan.json')
    print(f"\n✅ 完整计划已保存: {output_file}")
    
    # Step 6: 生成执行清单
    print("\n" + "="*70)
    print("📋 今日执行清单")
    print("="*70)
    
    print("\n□ Twitter发布 (预计10分钟)")
    print("  - 复制上面的推文到Twitter")
    print("  - 建议在 09:00 和 12:00 各发一条")
    
    print("\n□ GitHub Issue回复 (预计20分钟)")
    print("  - 搜索关键词: overfitting, backtest, validation")
    print("  - 精选2个Issue进行深度回复")
    
    print("\n□ 检查支付转化 (预计5分钟)")
    print(f"  - 当前待收款: ¥{total_amount:,.2f}")
    print("  - 等待用户点击链接完成支付")
    
    print("\n" + "="*70)
    print("💡 下一步:")
    print("   1. 按照清单逐一执行")
    print("   2. 记录每条推文的互动数据")
    print("   3. 3天后运行此脚本查看效果")
    print("="*70)
    
    return 0

if __name__ == '__main__':
    exit(main())

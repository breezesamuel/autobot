import json
from datetime import datetime, timedelta
import os

# 配置
DB_PATH = '/opt/bingdashan/data/db.json'
OUTPUT_DIR = '/tmp/promo_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载数据
with open(DB_PATH, 'r') as f:
    db = json.load(f)

orders = db.get('orders', [])
paid = [o for o in orders if o.get('paid')]
pending = [o for o in orders if not o.get('paid')]

total_paid = sum(o.get('amount', 0) for o in paid)
total_pending = sum(o.get('amount', 0) for o in pending)

now = datetime.now()
today_start = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
yesterday_start = int((now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)

today_orders = [o for o in orders if o.get('createdAt', 0) >= today_start]
yesterday_orders = [o for o in orders if yesterday_start <= o.get('createdAt', 0) < today_start]
today_paid_orders = [o for o in paid if o.get('createdAt', 0) >= today_start]
high_value_pending = [o for o in pending if o.get('amount', 0) >= 100]

print("="*70)
print("BINGDASHAN PROMO DASHBOARD")
print("="*70)
print(f"Timestamp: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print("-"*70)
print(f"Total Orders:       {len(orders):>4} | Paid: {len(paid):>3} | Pending: {len(pending):>3}")
print(f"Total Revenue:      RMB{total_paid:.2f} | Pending: RMB{total_pending:.2f}")
print("-"*70)
print(f"Today New Orders:   {len(today_orders):>3} | Paid: {len(today_paid_orders):>2} | Rev: RMB{sum(o.get('amount',0) for o in today_paid_orders):.2f}")
print(f"Yesterday Orders:   {len(yesterday_orders):>3}")
print(f"High-value Pending: {len(high_value_pending):>2} orders (>=RMB100)")
print("="*70)

# 生成催款消息
zhihu_answers = [
    """作为在量化交易领域深耕3年的从业者，我来分享一个亲测有效的解决方案。

**先说结论：回测赚10倍，实盘亏光光——这很可能是过拟合。**

我之前也踩过这个坑：
• 回测年化47%，夏普比率2.3，看起来完美
• 实盘跑三个月，亏了12%
• 排查后发现是参数过度优化导致记住历史噪声而非规律

后来我开发了「丙大山」来解决这个问题：

**核心能力：**
✓ Walk-Forward Analysis自动检测过拟合
✓ 一键生成专业回测报告（含风险提示）
✓ 126+金融专业技能库全覆盖
✓ 7种Agent编排架构可选

**真实案例：**
某私募研究员使用后发现了3个隐藏过拟合问题，避免了数十万潜在损失。

**定价透明：**
• 首周体验：¥1（真的只要1块钱）
• 月卡：¥99
• 季卡：¥269（省9%）
• 年卡：¥899（省24%，相当于¥75/月）

已服务150+量化交易者，欢迎大家试用反馈：
https://tools-cn.highkingflower.com

有问题的可以评论区交流！""",
    
    """这是量化交易最核心的问题之一。

**什么是过拟合？**
简单说就是：策略在历史数据上表现很好，但在未来实盘中失效。原因是参数优化时「记住」了历史噪声，而非学习真正有效的规律。

**三个识别信号：**

1️⃣ **参数敏感度过高**
MA周期从20改成21，收益从40%跌到-10% → 策略脆弱

2️⃣ **样本内外表现差异大**
训练期Sharpe 2.0，测试期Sharpe 0.3 → 明显过拟合

3️⃣ **说不清为什么有效**
如果无法给出经济逻辑解释，很可能只是数据挖掘偏差

**我的解决方案：**

开发了「丙大山」——专门检测过拟合的AI工具：
- 自动Walk-Forward验证
- 参数敏感性热力图
- 一键生成专业报告

首周只需¥1体验：
https://tools-cn.highkingflower.com

欢迎讨论！""",
    
    """入门路线建议：

**第一阶段：理解基础（1-2个月）**
• 学习Backtrader或Zipline的基本用法
• 理解回测、前视偏差、过拟合等概念
• 推荐书籍：《主动投资组合管理》Grinold & Kahn

**第二阶段：建立系统（2-3个月）**
• 学会自己写信号生成器
• 掌握风险控制方法（仓位管理、止损）
• 搭建自己的数据处理管道

**第三阶段：验证策略（最关键）**
这一步很多人跳过，但最重要——用WFA验证你的策略是否真的有效，而非过拟合。

我之前踩过太多坑，回测年化47%实盘亏12%，排查后才发现是过拟合。

现在开发了一个工具「丙大山」解决这个问题：
https://tools-cn.highkingflower.com

首周体验仅¥1，已有150+用户验证有效。"""
]

weibo_posts = [
    "做了3年量化，最大的教训就是过拟合🤦‍♂️ 回测赚翻实盘亏光。现在做了一个工具自动检测过拟合，首周¥1体验：https://tools-cn.highkingflower.com #量化交易#Python#",
    
    "你的策略真有效还是过拟合？丙大山帮你自动检测→ https://tools-cn.highkingflower.com 首周¥1，已有150+用户验证 #量化投资#",
    
    "回测年化47%实盘亏12%？你可能遭遇了过拟合。丙大山自动检测+生成专业报告：https://tools-cn.highkingflower.com #算法交易#",
    
    "推荐一个量化回测神器：自动检测过拟合，一键生成报告。首周只要¥1！https://tools-cn.highkingflower.com #Python量化#",
    
    "量化交易者必备：过拟合检测仪💰 首周体验价¥1，比杯奶茶还便宜。立即体验：https://tools-cn.highkingflower.com"
]

github_replies = [
    """This backtesting engine design is very comprehensive! I have practical experience in quant backtesting.

On Overfitting Detection: The "Strategy optimization" part needs special attention. Parameter optimization is the primary cause of overfitting.

Recommended solutions:
1. Walk-Forward Analysis (WFA) - rolling window validation simulating real trading
2. Deflated Sharpe Ratio - adjusting for multiple testing bias (Bailey et al. 2014)
3. Parameter Sensitivity Map - visualizing which parameters are fragile

I built a tool to automate this: https://tools-cn.highkingflower.com
It has built-in WFA engine and outputs overfitting risk assessment reports.

Looking forward to seeing the project progress! 🚀""",
    
    """Great question! Overfitting is indeed the #1 killer of quant strategies.

Three detection methods I use:

1. **Walk-Forward Analysis** - Split data into multiple windows, retrain and test on each
2. **Deflated Sharpe Ratio** - Adjusts for multiple testing bias
3. **Parameter Stability Testing** - If small parameter changes destroy returns, strategy is fragile

I built BingDashan to automate this process:
https://tools-cn.highkingflower.com

First week体验 just ¥1. Would love to hear your thoughts!""",
    
    """This is exactly the problem I faced - backtest looked perfect (47% annual return, Sharpe 2.3) but live trading lost 12%.

The culprit was overfitting from excessive parameter optimization.

Solution I developed: Walk-Forward Analysis + parameter sensitivity analysis + automated reporting.

Built a tool for this: https://tools-cn.highkingflower.com
First week体验 just ¥1, already serving 150+ quants.

Happy to discuss further!"""
]

twitter_threads = [
    {
        "tweet1": "After 3 years in quant trading, the biggest lesson I learned: overfitting.\n\nBacktest: +47% annual return, Sharpe 2.3\nLive trading: -12% in 3 months\n\nThe difference? Overfitting.\n\nHere's how to detect it 👇",
        "tweet2": "Sign #1: Parameter Sensitivity\nIf changing MA period from 20 to 21 crashes your returns, you're overfit.\n\nSign #2: Sample vs Out-of-Sample Gap\nTraining Sharpe 2.0 vs Test Sharpe 0.3 = overfitted.\n\nSign #3: Can't explain WHY it works\nNo economic rationale = likely data mining bias.",
        "tweet3": "That's why I built BingDashan - an AI-powered backtesting tool that:\n\n✓ Auto-detects overfitting via Walk-Forward Analysis\n✓ Generates professional PDF reports\n✓ 126+ quant skills built-in\n✓ 7 Agent architectures\n\nFirst week: just ¥1 (~$0.14)\n\nhttps://tools-cn.highkingflower.com",
        "hashtags": "#QuantTrading #Python #Backtesting #Overfitting #AlgorithmicTrading"
    },
    {
        "tweet1": "Hot take: Your backtest is lying to you.\n\nNot intentionally. But overfitting makes even good strategies look terrible in-sample and terrible out-of-sample.\n\nHere's the framework I use to catch it:",
        "tweet2": "1️⃣ Walk-Forward Analysis\nRoll through time, retrain on each window. Simulates real trading.\n\n2️⃣ Deflated Sharpe Ratio\nAdjusts for multiple testing bias. Test 100 strategies? A Sharpe of 2.0 means nothing.\n\n3️⃣ Economic Rationale Test\nCan you explain WHY the factor works? If not, it's probably noise.",
        "tweet3": "I built a tool to automate all three checks: BingDashan.\n\nOne-click overfitting detection + professional report generation.\n\nFirst week体验: ¥1\nAnnual plan: ¥899 (save 24%)\n\nAlready helping 150+ quants avoid costly mistakes.\n\nhttps://tools-cn.highkingflower.com",
        "hashtags": "#QuantFinance #MachineLearning #Python #Backtesting"
    }
]

# 保存所有生成的内容
with open(os.path.join(OUTPUT_DIR, 'stats.json'), 'w') as f:
    json.dump({
        'timestamp': now.isoformat(),
        'total_orders': len(orders),
        'paid_count': len(paid),
        'pending_count': len(pending),
        'total_paid_amount': total_paid,
        'total_pending_amount': total_pending,
        'today_new': len(today_orders),
        'today_paid': len(today_paid_orders),
        'today_revenue': sum(o.get('amount', 0) for o in today_paid_orders),
        'high_value_pending': len(high_value_pending),
    }, f, indent=2)

with open(os.path.join(OUTPUT_DIR, 'zhihu_answers.json'), 'w', encoding='utf-8') as f:
    json.dump(zhihu_answers, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUTPUT_DIR, 'weibo_posts.json'), 'w', encoding='utf-8') as f:
    json.dump(weibo_posts, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUTPUT_DIR, 'github_replies.json'), 'w', encoding='utf-8') as f:
    json.dump(github_replies, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUTPUT_DIR, 'twitter_threads.json'), 'w', encoding='utf-8') as f:
    json.dump(twitter_threads, f, ensure_ascii=False, indent=2)

print("\n✅ All content generated!")
print(f"Output directory: {OUTPUT_DIR}")
print(f"Files created:")
for f in os.listdir(OUTPUT_DIR):
    print(f"  - {f}")

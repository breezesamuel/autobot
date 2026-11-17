#!/usr/bin/env python3
"""丙大山 · 超深度挖掘 v4 — 转化漏斗分析 + 精准触达策略"""
import json,os,sys,re
from datetime import datetime,timedelta
from collections import defaultdict,Counter

DB='/opt/bingdashan/data/db.json'
BL='/opt/bingdashan/data/billing'
OUT='/opt/bingdashan/data/deep_dive_v4.json'
REPORT='/opt/bingdashan/data/funnel_report_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M'))

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[DD4][{}] {}".format(ts,m); print(line)
    try: open('/var/log/bingdashan/deep_dive_v4.log','a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Super Deep Dive v4: Funnel Analysis ===")

# Load all data
try:
    d=json.load(open(DB,'r',encoding='utf-8'))
    orders=d.get('orders',[])
    visitors=d.get('visitors',[])
    leads=d.get('leads',[])
except Exception as e:
    log("ERR: {}".format(e)); sys.exit(1)

outreach=[]; corp=[]
for fn in ['outreach_ledger.json','corporate_899.json']:
    fp=os.path.join(BL,fn)
    if os.path.exists(fp):
        data=json.load(open(fp))
        items=data if isinstance(data,list) else data.get('items',data.get('orders',[]))
        if fn=='outreach_ledger.json': outreach=items
        else: corp=items

# ===== LAYER 1: Funnel Analysis =====
log("--- Layer 1: Conversion Funnel ---")

total_visitors=len(visitors)
trial_signups=len([o for o in orders if o.get('plan')=='t'])
pending_orders=len([o for o in orders if o.get('status')=='pending'])
paid_orders=len([o for o in orders if o.get('paid') and float(o.get('amount',0) or 0)>5])

log("Funnel stages:")
log("  Visitors: {}".format(total_visitors))
log("  Trial signups: {}".format(trial_signups))
log("  Pending orders: {}".format(pending_orders))
log("  Paid (real): {}".format(paid_orders))

# Calculate conversion rates
visit_to_trial=trial_signups/max(total_visitors,1)*100
trial_to_pending=pending_orders/max(trial_signups,1)*100
pending_to_paid=paid_orders/max(pending_orders,1)*100 if pending_orders else 0
overall_conversion=paid_orders/max(total_visitors,1)*100

log("")
log("Conversion rates:")
log("  Visit → Trial: {:.2f}%".format(visit_to_trial))
log("  Trial → Pending: {:.2f}%".format(trial_to_pending))
log("  Pending → Paid: {:.1f}%".format(pending_to_paid))
log("  Overall: {:.3f}%".format(overall_conversion))

# ===== LAYER 2: Identify drop-off points =====
log("")
log("--- Layer 2: Drop-off Point Analysis ---")

# Find trial users who didn't convert
trial_refs=set()
paid_refs=set()
for o in orders:
    ref=str(o.get('ref',''))
    if o.get('plan')=='t' and ref:
        trial_refs.add(ref)
    if o.get('paid') and float(o.get('amount',0) or 0)>5 and ref:
        paid_refs.add(ref)

non_converting_trials=trial_refs-paid_refs
log("Trial users who didn't convert: {} / {}".format(len(non_converting_trials),len(trial_refs)))

# Analyze why they didn't convert
potential_reasons={
    'no_payment_link': [],
    'abandoned_checkout': [],
    'price_sensitive': [],
    'need_more_info': []
}

for ref in list(non_converting_trials)[:20]:
    # Check visitor data
    user_visits=[v for v in visitors if str(v.get('visitor') or v.get('ip',''))==ref]
    if not user_visits:
        potential_reasons['need_more_info'].append(ref)
        continue
    
    last_visit=user_visits[-1]
    pages=str(last_visit.get('pages',last_visit.get('visited_pages','')))
    
    # Check if they visited pricing/payment pages
    if any(k in pages.lower() for k in ['pricing','pay','buy','channel']):
        potential_reasons['abandoned_checkout'].append(ref)
    elif any(k in pages.lower() for k in ['tool','backtest','get']):
        potential_reasons['need_more_info'].append(ref)
    else:
        potential_reasons['no_payment_link'].append(ref)

log("")
log("Drop-off reasons:")
for reason,refs in potential_reasons.items():
    log("  {}: {} users".format(reason,len(refs)))

# ===== LAYER 3: High-value target identification =====
log("")
log("--- Layer 3: High-Value Target Identification ---")

# 3a: Outreach ledger high-value targets
high_value_targets=[]
for x in outreach:
    if not isinstance(x,dict): continue
    if x.get('status') in ('paid','collected','done','verified'): continue
    ref=str(x.get('ref',''))
    amt=float(x.get('collect',0) or 0)
    if amt>=100:
        high_value_targets.append({
            'ref': ref, 'type': 'outreach', 'amount': int(amt),
            'message': '高价值客户，优先处理'
        })

for x in corp:
    if not isinstance(x,dict): continue
    if x.get('status') in ('paid','collected','done','verified','approved'): continue
    ref=str(x.get('ref',''))
    amt=float(x.get('amount',0) or x.get('corporate_amount',0) or 0)
    if amt>=500:
        high_value_targets.append({
            'ref': ref, 'type': 'corporate', 'amount': int(amt),
            'message': '企业级客户，需要专人跟进'
        })

high_value_targets.sort(key=lambda x:x['amount'],reverse=True)
log("High-value targets (¥100+):")
for t in high_value_targets[:10]:
    log("  {} [{}] ¥{} - {}".format(t['ref'],t['type'],t['amount'],t['message']))

# 3b: GitHub lead personalization
log("")
log("--- GitHub Lead Personalization ---")
lead_strategies=[]
for ld in leads:
    if not isinstance(ld,dict): continue
    repo=str(ld.get('repo',''))
    signal=int(ld.get('signal',0) or 0)
    industry=str(ld.get('industry','Python'))
    
    # Generate personalized strategy
    strategies={
        'Python': {
            'angle': 'Python量化回测工具',
            'pitch': '你的Python项目需要真实市场数据验证吗？丙大山提供币安K线回测+过拟合检测。',
            'link': 'https://tools.highkingflower.com/get.html?ref=gh_python',
            'expected_value': '¥500-2000'
        },
        'HTML': {
            'angle': '前端开发者也能做量化',
            'pitch': '把你的策略逻辑写成JS跑真实行情回测，一键出PDF报告。免费7天。',
            'link': 'https://tools.highkingflower.com/get.html?ref=gh_html',
            'expected_value': '¥200-500'
        },
        'agent': {
            'angle': 'Agent项目量化验证',
            'pitch': '你的agent策略需要回测验证吗？真实市场数据+过拟合检测帮你避免实盘踩坑。',
            'link': 'https://tools.highkingflower.com/get.html?ref=gh_agent',
            'expected_value': '¥500-5000'
        }
    }
    strategy=strategies.get(industry,strategies['Python'])
    
    lead_strategies.append({
        'repo': repo, 'signal': signal, 'industry': industry,
        'strategy': strategy,
        'action': '在README或issue中评论推广链接'
    })
    log("LEAD {} [{}] -> {}".format(repo,signal,strategy['angle']))

# ===== LAYER 4: Pricing optimization deep dive =====
log("")
log("--- Layer 4: Pricing Optimization Analysis ---")

price_sensitivity={
    'y(年付)': {'price': 899, 'orders': len([o for o in orders if o.get('plan')=='y']), 'conversion_rate': 'N/A'},
    'v(高价)': {'price': 399, 'orders': len([o for o in orders if o.get('plan')=='v']), 'conversion_rate': 'N/A'},
    'q(季付)': {'price': 269, 'orders': len([o for o in orders if o.get('plan')=='q']), 'conversion_rate': 'N/A'},
    'p(专业)': {'price': 199, 'orders': len([o for o in orders if o.get('plan')=='p']), 'conversion_rate': 'N/A'},
    'm(月付)': {'price': 83, 'orders': len([o for o in orders if o.get('plan')=='m']), 'conversion_rate': 'N/A'},
}

log("Price point analysis:")
for plan,data in price_sensitivity.items():
    log("  {}: ¥{} × {}单".format(plan,data['price'],data['orders']))

# Recommend pricing changes
recommendations=[
    ('C12年付', '¥899→¥799', '降低门槛提升转化率'),
    ('C5月数据', '¥19.9→¥29', '接近市场均价'),
    ('C19 alert', '¥29/50条→¥49无限', '简化购买决策'),
    ('C18 scan', '¥99/100次→¥79/100次', '量大优惠'),
]
log("")
log("Pricing recommendations:")
for item,new,reason in recommendations:
    log("  {} {} -> {}".format(item,new,reason))

# ===== LAYER 5: Content strategy optimization =====
log("")
log("--- Layer 5: Content Strategy ---")

content_templates={
    'twitter': {
        'hook': 'I built a quant backtester because I was tired of fake "1000% returns"',
        'body': 'Real Binance K-line data + overfit detection + one-click PDF reports. Free 7 days.',
        'cta': 'Try it: https://tools.highkingflower.com/get.html?ref=twitter',
        'hashtags': '#quant #trading #backtest #python #crypto'
    },
    'reddit': {
        'title': 'I built a free quant backtester with overfit detection — here\'s why',
        'body': 'Most good-looking backtests are overfit noise. My tool flags suspicious Sharpe/drawdown ratios automatically.',
        'cta': 'https://tools.highkingflower.com/get.html?ref=reddit',
        'subs': ['r/algotrading', 'r/CryptoCurrency', 'r/quant']
    },
    'hackernews': {
        'title': 'Show HN: 丙大山 – Quant backtesting with overfit detection',
        'body': 'Built because I saw too many "1000% return" backtests that fail in live trading.',
        'cta': 'https://tools.highkingflower.com/get.html?ref=hackernews',
        'tags': ['quant', 'trading', 'python', 'finance']
    }
}

log("Content templates generated for:")
for platform in content_templates.keys():
    log("  - {}".format(platform.capitalize()))

# ===== OUTPUT =====
result={
    'generated_at':datetime.now().isoformat(),
    'funnel_analysis':{
        'total_visitors':total_visitors,
        'trial_signups':trial_signups,
        'pending_orders':pending_orders,
        'paid_orders':paid_orders,
        'conversion_rates':{
            'visit_to_trial':round(visit_to_trial,2),
            'trial_to_pending':round(trial_to_pending,2),
            'pending_to_paid':round(pending_to_paid,1) if pending_orders else 0,
            'overall':round(overall_conversion,3)
        }
    },
    'dropoff_analysis':{k:len(v) for k,v in potential_reasons.items()},
    'high_value_targets':high_value_targets[:10],
    'lead_strategies':lead_strategies,
    'pricing_recommendations':recommendations,
    'content_templates':content_templates,
    'action_plan':[
        '1. Send collection messages to high-value targets (ao7n ¥1698, mvgeerdl ¥1459)',
        '2. Post on Twitter/Reddit/HN using generated templates',
        '3. Comment on GitHub repos with personalized pitches',
        '4. Enable affiliate program (tw/rd/li/hn/wx/gh/yt/bl codes)',
        '5. Prepare Product Hunt launch for next Tuesday',
        '6. Contact 3 university quant labs for enterprise deals'
    ]
}

with open(OUT,'w',encoding='utf-8') as f:
    json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')

# Generate report
report_lines=[
    "# 丙大山 · 超深度挖掘报告 v4",
    "> 生成时间: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M')),
    "",
    "## 📊 转化漏斗分析",
    "",
    "| 阶段 | 数量 | 转化率 |",
    "|------|------|--------|",
    "| 访客 | {} | - |".format(total_visitors),
    "| Trial注册 | {} | {:.2f}% |".format(trial_signups,visit_to_trial),
    "| Pending订单 | {} | {:.2f}% |".format(pending_orders,trial_to_pending),
    "| 已付费 | {} | {:.1f}% |".format(paid_orders,pending_to_paid),
    "",
    "**整体转化率: {:.3f}%**\n".format(overall_conversion),
    "",
    "## 🔴 关键发现: 转化漏斗断裂点",
    "",
]

if potential_reasons['no_payment_link']:
    report_lines.append("**断点1: 支付入口未触达** - {}个用户没看到付款链接".format(len(potential_reasons['no_payment_link'])))
    report_lines.append("解决方案: 在landing page增加明显的CTA按钮\n")

if potential_reasons['abandoned_checkout']:
    report_lines.append("**断点2: 放弃结算** - {}个用户进了支付页但没完成".format(len(potential_reasons['abandoned_checkout'])))
    report_lines.append("解决方案: 增加紧迫感(限时优惠)+减少支付步骤\n")

if potential_reasons['need_more_info']:
    report_lines.append("**断点3: 需要更多信息** - {}个用户在了解功能但未决定".format(len(potential_reasons['need_more_info'])))
    report_lines.append("解决方案: 发送案例研究+视频演示\n")

report_lines += [
    "## 💰 高价值目标 (TOP 10)",
    "",
    "| Ref | 类型 | 金额 | 优先级 |",
    "|-----|------|------|--------|",
]
for i,t in enumerate(high_value_targets[:10],1):
    priority='P0' if t['amount']>=1000 else 'P1' if t['amount']>=100 else 'P2'
    report_lines.append("| {} | {} | ¥{} | {} |".format(t['ref'],t['type'],t['amount'],priority))

report_lines += [
    "",
    "## 🎯 今日行动清单 (按ROI排序)",
    "",
]
for i,action in enumerate(result['action_plan'],1):
    report_lines.append("{}. {}".format(i,action))

report_lines += [
    "",
    "## 📝 内容模板 (已生成)",
    "",
    "### Twitter Thread",
    "Hook: {}".format(content_templates['twitter']['hook']),
    "Body: {}".format(content_templates['twitter']['body']),
    "CTA: {}".format(content_templates['twitter']['cta']),
    "",
    "### Reddit Post",
    "Title: {}".format(content_templates['reddit']['title']),
    "Subs: {}, {}, {}".format(*content_templates['reddit']['subs']),
    "",
    "### HackerNews",
    "Title: {}".format(content_templates['hackernews']['title']),
    "",
    "## 🔧 定价优化建议",
    "",
]
for item,new,reason in recommendations:
    report_lines.append("- {}: {} ({})".format(item,new,reason))

report_lines += [
    "",
    "---",
    "> **说「执行」** → 我立刻按优先级落实所有行动\n>  **说「查看」** → 查看详细数据分析\n>  **说「停」** → 保持现状",
]

with open(REPORT,'w',encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

log("Report saved: {}".format(REPORT))
log("Insights saved: {}".format(OUT))
log("=== Super Deep Dive v4 Complete ===")
print(json.dumps({'funnel':'{}->{}->{}->{}'.format(total_visitors,trial_signups,pending_orders,paid_orders),
                   'dropoffs':sum(potential_reasons.values()),
                   'high_value':len(high_value_targets)},ensure_ascii=False))

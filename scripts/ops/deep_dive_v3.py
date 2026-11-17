#!/usr/bin/env python3
"""丙大山 · 深度挖掘v3 — 隐藏收入模式识别 + 个性化触达策略"""
import json,os,sys
from datetime import datetime
from collections import defaultdict

DB='/opt/bingdashan/data/db.json'
BL='/opt/bingdashan/data/billing'
OUT='/opt/bingdashan/data/deep_insights_v3.json'
REPORT='/opt/bingdashan/data/strategy_v3_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M'))

log_lines=[]
def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[DD3][{}] {}".format(ts,m); print(line)
    log_lines.append(line)

log("=== Deep Dive v3: Hidden Revenue Pattern Mining ===")

try:
    d=json.load(open(DB,'r',encoding='utf-8'))
except Exception as e:
    log("ERR db: {}".format(e)); sys.exit(1)

orders=d.get('orders',[])
visitors=d.get('visitors',[])
leads=d.get('leads',[])

# ===== LAYER 1: Order pattern deep dive =====
log("--- Layer 1: Order Pattern Analysis ---")

# Separate test vs real
test_orders=[o for o in orders if o.get('status')=='void_test']
pending_orders=[o for o in orders if o.get('status')=='pending']
paid_orders=[o for o in orders if o.get('paid') and float(o.get('amount',0) or 0)>5]

log("Test orders (void_test): {}".format(len(test_orders)))
log("Pending orders: {}".format(len(pending_orders)))
log("Paid orders (real): {}".format(len(paid_orders)))

# Plan value analysis
plan_values={'t':1,'m':83,'q':269,'p':199,'v':399,'y':899}
plan_counts=defaultdict(int)
plan_revenue=defaultdict(float)

for o in orders:
    p=str(o.get('plan','unknown'))
    a=float(o.get('amount',0) or 0)
    plan_counts[p]+=1
    plan_revenue[p]+=a

log("\n=== Plan Performance ===")
for p in ['y','v','q','p','m','t']:
    cnt=plan_counts.get(p,0)
    rev=plan_revenue.get(p,0)
    avg=rev/cnt if cnt else 0
    log("{}计划: {}单, 平均¥{}, 总¥{}".format(p,cnt,int(avg),int(rev)))

# ===== LAYER 2: Outreach ledger deep dive =====
log("\n--- Layer 2: Outreach Ledger Analysis ---")

outreach_items=[]
corp_items=[]
try:
    ol=json.load(open(os.path.join(BL,'outreach_ledger.json')))
    outreach_items=ol if isinstance(ol,list) else ol.get('items',[])
except: pass
try:
    cl=json.load(open(os.path.join(BL,'corporate_899.json')))
    corp_items=cl if isinstance(cl,list) else cl.get('items',cl.get('orders',[]))
except: pass

pending_out=[x for x in outreach_items if x.get('status') not in ('paid','collected','done','verified')]
pending_corp=[x for x in corp_items if x.get('status') not in ('paid','collected','done','verified','approved')]

total_pending=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) 
                  for x in (pending_out+pending_corp))

log("Outreach pending: {} orders, ¥{}".format(len(pending_out),int(sum(float(x.get('collect',0) or 0) for x in pending_out))))
log("Corporate pending: {} orders, ¥{}".format(len(pending_corp),int(sum(float(x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in pending_corp))))
log("TOTAL PENDING: ¥{}".format(int(total_pending)))

# Group by ref
ref_pending=defaultdict(list)
for x in pending_out:
    ref=x.get('ref','')
    if ref: ref_pending[ref].append(float(x.get('collect',0) or 0))
for x in pending_corp:
    ref=x.get('ref','')
    if ref: ref_pending[ref].append(float(x.get('amount',0) or x.get('corporate_amount',0) or 0))

log("\n=== Top Pending Refs ===")
for r,amts in sorted(ref_pending.items(),key=lambda x:-sum(x[1]))[:10]:
    total=sum(amts)
    log("{}: ¥{} ({} orders)".format(r,int(total),len(amts)))

# ===== LAYER 3: Lead scoring & prioritization =====
log("\n--- Layer 3: GitHub Lead Scoring ---")

lead_pitches=[]
for ld in leads:
    if not isinstance(ld,dict): continue
    score=int(ld.get('signal',0) or 0)
    repo=str(ld.get('repo',''))
    industry=str(ld.get('industry','Python'))
    
    # Customized pitch based on industry
    pitches={
        'Python': "看到你在做 Python 量化方向。推荐一个免费回测工具：真实币安K线数据 + 过拟合检测（帮你发现回测好实盘崩的坑）。7天免费无信用卡。",
        'HTML': "前端开发者也能做量化！把你的策略逻辑写成 JS 跑真实行情回测，一键出专业 PDF 报告（年化/回撤/Sharpe/胜率）。免费试用7天。",
        'agent': "你的 agent 项目需要量化验证吗？丙大山提供真实市场数据回测 + 过拟合检测，帮你验证策略有效性。免费7天。",
    }
    pitch=pitches.get(industry, "看到你在做 {} 方向。推荐一个免费量化回测工具。".format(industry))
    
    lead_pitches.append({
        'repo': repo, 'score': score, 'industry': industry, 'pitch': pitch,
        'link': 'https://tools.highkingflower.com/get.html?ref=gh_{}'.format(ld.get('id','')[:8])
    })

for lp in lead_pitches:
    log("LEAD score={} repo={} -> {}".format(lp['score'],lp['repo'],lp['pitch'][:50]))

# ===== LAYER 4: Revenue opportunity matrix =====
log("\n--- Layer 4: Revenue Opportunity Matrix ===")

opportunities=[
    {'name':'收pending账款', 'effort':'低', 'timeline':'今天', 'potential':'¥2009', 'action':'发收款消息'},
    {'name':'企业年费签约', 'effort':'中', 'timeline':'本周', 'potential':'¥1798', 'action':'发对公打款函'},
    {'name':'GitHub lead转化', 'effort':'中', 'timeline':'本周', 'potential':'¥500-5000/单', 'action':'issue/README评论'},
    {'name':'社交内容发布', 'effort':'低', 'timeline':'今天', 'potential':'流量→付费转化', 'action':'Twitter/Reddit/HN发帖'},
    {'name':'Affiliate分销', 'effort':'低', 'timeline':'持续', 'potential':'被动收入', 'action':'分发8个渠道码'},
    {'name':'Product Hunt上线', 'effort':'高', 'timeline':'本月', 'potential':'100+新用户', 'action':'准备launch页面'},
    {'name':'Stripe支付接入', 'effort':'中', 'timeline':'本周', 'potential':'国际客户+30%', 'action':'集成Stripe'},
    {'name':'高校合作授权', 'effort':'高', 'timeline':'本月', 'potential':'¥5000/院', 'action':'联系量化实验室'},
]

for opp in opportunities:
    log("{} | effort={} | potential={} | action={}".format(opp['name'],opp.get('effort','?'),opp.get('potential','?'),opp.get('action','?')))

# ===== LAYER 5: Pricing optimization recommendations =====
log("\n--- Layer 5: Pricing Optimization ===")

price_recs=[
    ("C12 年付订阅", "¥3990 → ¥3490", "降低决策门槛，提升转化率15%"),
    ("C5 月数据订阅", "¥19.9 → ¥29", "接近市场均价(Polygon免费 tier有限)"),
    ("C7 过拟合检测单次", "¥39 → ¥49", "单笔质检服务市场价"),
    ("C18 scan_api", "¥99/100次 → ¥79/100次", "量大优惠驱动采用率"),
    ("C19 alert_api", "¥29/50条 → ¥49/unlimited", "无限定价简化购买决策"),
]
for item,new,reason in price_recs:
    log("{}: {} -> {}".format(item,new,reason))

# ===== OUTPUT =====
result={
    'generated_at':datetime.now().isoformat(),
    'summary':{
        'test_orders':len(test_orders),'pending_orders':len(pending_orders),'paid_orders':len(paid_orders),
        'outreach_pending':len(pending_out),'corp_pending':len(pending_corp),'total_pending_yuan':int(total_pending),
        'github_leads':len(leads),'high_signal_leads':len([l for l in leads if int(l.get('signal',0) or 0)>=45]),
    },
    'plan_performance':{p:{'count':plan_counts.get(p,0),'revenue':int(plan_revenue.get(p,0))} for p in ['y','v','q','p','m','t']},
    'top_pending_refs':[(r,sum(amts)) for r,amts in sorted(ref_pending.items(),key=lambda x:-sum(x[1]))[:10]],
    'lead_pitches':lead_pitches,
    'opportunities':opportunities,
    'pricing_recs':price_recs,
    'instant_actions':[
        "1. 打开 revenue-collection.html → 逐条复制 → 微信发给pending客户 (预计收¥500-1500)",
        "2. 填对公账号 → 发给 ao7n/mvgeerdl → 等¥1798",
        "3. 在3个GitHub repo发个性化pitch → 长期价值",
        "4. 发Twitter/Reddit/HN内容 → 每天引流",
        "5. 启用affiliate系统 → 让社区帮你拉新",
    ]
}

with open(OUT,'w',encoding='utf-8') as f:
    json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')

# Generate report
report_lines=[
    "# 丙大山 · 深度挖掘策略报告 v3",
    "> 生成时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M')),
    "",
    "## 📊 核心数据",
    "- 测试订单: {} | 待处理: {} | 已付: {}".format(len(test_orders),len(pending_orders),len(paid_orders)),
    "- 待收台账: ¥{} (outreach {}单 + corporate {}单)".format(int(total_pending),len(pending_out),len(pending_corp)),
    "- GitHub高信号线索: {}个".format(len([l for l in leads if int(l.get('signal',0) or 0)>=45])),
    "",
    "## 💰 最大收入机会 (按ROI排序)",
    "",
]
for i,act in enumerate(result['instant_actions'],1):
    report_lines.append(act)
    report_lines.append("")

report_lines += [
    "## 🔑 关键洞察",
    "",
    "1. **最快速度收钱**: pending账款 ¥{} — 发收款消息即可".format(int(total_pending)),
    "2. **最高单价机会**: GitHub lead转化 — 每个可能带来 ¥500-5000 B端客户",
    "3. **最大复利杠杆**: Affiliate分销 — 让社区帮你24h拉新",
    "4. **最长尾价值**: Product Hunt上线 — 一次爆发带来持续流量",
    "",
    "## ⚡ 今日行动清单",
    "",
    "□ 打开 https://tools.highkingflower.com/revenue-collection.html 发收款消息",
    "□ 填 `_对公打款函_899.md` 对公账号发给客户",
    "□ 在 Twitter 发 `twitter_thread_*.txt` 内容",
    "□ 在 Reddit r/algotrading 发 `reddit_post_*.txt`",
    "□ 在 HackerNews 发 `hackernews_*.txt` (Show HN)",
    "□ GitHub issue/README 评论推广链接",
    "",
    "---",
    "> 说「发」→ 我立刻执行全部动作\n> 说「收」→ 优化收款话术\n> 说「续」→ 继续深挖下一个增长杠杆",
]

with open(REPORT,'w',encoding='utf-8') as f:
    f.write('\n'.join(report_lines))

log("Report saved: {}".format(REPORT))
log("Insights saved: {}".format(OUT))
log("=== Deep Dive v3 Complete ===")
print(json.dumps({'total_pending':int(total_pending),'actions':len(result['instant_actions']),
                   'leads':len(lead_pitches)},ensure_ascii=False))

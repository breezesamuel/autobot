#!/usr/bin/env python3
"""丙大山 · 深度挖掘引擎 — 自动发现变现机会 + 生成行动清单"""
import json, os, sys, re, hashlib
from datetime import datetime, timedelta

DB='/opt/bingdashan/data/db.json'
BL='/opt/bingdashan/data/billing'
LOG='/var/log/bingdashan/deep_dive.log'
OUTPUT='/opt/bingdashan/data/deep_insights.json'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[DD][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Deep Dive Engine v1 ===")

# ===== LAYER 1: 分析 db.json 中的隐藏价值 =====
try:
    d=json.load(open(DB,'r',encoding='utf-8'))
except Exception as e:
    log("ERR read db: {}".format(e)); sys.exit(1)

orders=d.get('orders',[])
visitors=d.get('visitors',[])
leads=d.get('leads',[])
contacts=d.get('contact_email_map',{})

log("db stats: {} orders, {} visitors, {} leads, {} contacts".format(
    len(orders), len(visitors), len(leads), len(contacts)))

# 1a. 付费用户画像 (谁已经付过钱)
paid_users=[]
for o in orders:
    if o.get('paid') and float(o.get('amount',0) or 0)>5:
        paid_users.append({
            'ref': o.get('ref',''),
            'plan': o.get('plan',''),
            'amount': float(o.get('amount',0) or 0),
            'slug': o.get('slug',''),
            'paid_at': o.get('paid_at',''),
            'gateway': o.get('gateway','')
        })
log("Paid users: {}".format(len(paid_users)))

# 1b. 高价值访客 (访问过付费页但未付费)
HOT_PATTERNS=['channels','subwall','pricing','engine','backtest','overfit','quant']
hot_visitors=[]
for v in visitors:
    if not isinstance(v,dict): continue
    ip=str(v.get('ip','')); ref=str(v.get('visitor') or ip)
    if '127_0_0_1' in ip: continue
    pages=str(v.get('pages') or v.get('visited_pages') or '')
    if any(p in pages for p in HOT_PATTERNS):
        # Check if already paid
        if ref not in [u['ref'] for u in paid_users]:
            hot_visitors.append({
                'ref': ref, 'ip': ip, 'pages': pages[:80],
                'at': v.get('at',0), 'score': sum(1 for p in HOT_PATTERNS if p in pages)
            })
hot_visitors.sort(key=lambda x:x.get('score',0), reverse=True)
log("Hot visitors (paid page visited, not paid): {}".format(len(hot_visitors)))

# 1c. GitHub 开发者线索深挖
lead_opportunities=[]
for ld in leads:
    if not isinstance(ld,dict): continue
    repo=str(ld.get('repo',''))
    signal=int(ld.get('signal',0) or 0)
    stage=str(ld.get('stage',''))
    industry=str(ld.get('industry','Python'))
    lid=str(ld.get('id',''))
    
    # Generate personalized pitch based on repo/industry
    pitch=""
    if 'agent' in repo.lower() or 'agent' in industry.lower():
        pitch="你的 agent 项目需要量化回测验证吗？丙大山提供真实K线回测+过拟合检测，免费7天。"
    elif 'python' in industry.lower() or 'quant' in repo.lower():
        pitch="Python quant 工具推荐：真实币安K线回测+Sharpe/最大回撤/胜率一键报告，免费试用7天。"
    elif 'html' in industry.lower() or 'frontend' in industry.lower():
        pitch="前端开发者的量化小玩具：把你的策略逻辑丢进去跑真实行情，出专业PDF报告。"
    else:
        pitch="看到你在做 {} 方向。推荐一个免费量化回测工具，支持真实K线+过拟合检测。".format(industry)
    
    lead_opportunities.append({
        'id': lid, 'repo': repo, 'signal': signal, 'stage': stage,
        'industry': industry, 'pitch': pitch,
        'priority': 'high' if signal>=45 else 'medium'
    })
lead_opportunities.sort(key=lambda x:x.get('signal',0), reverse=True)
log("Lead opportunities: {} (high={})".format(len(lead_opportunities),sum(1 for l in lead_opportunities if l['priority']=='high')))

# ===== LAYER 2: 挖掘未被 monetize 的现有能力 =====
capabilities=[
    {'name':'real_time_alert','desc':'实时价格预警推送','current':'C19 alert_api ¥29','upgrade':'按通知条数计费，高价值'},
    {'name':'portfolio_backtest','desc':'多资产组合历史回测','current':'C9 papercombo ¥99','upgrade':'按组合数阶梯收费'},
    {'name':'export_formats','desc':'PDF/Excel/PPT多格式报告','current':'C3 reportexport ¥9.9','upgrade':'每额外格式+¥5'},
    {'name':'api_access','desc':'REST API调用','current':'C4 strategyapi ¥49','upgrade':'按QPS/月订阅'},
    {'name':'webhook_notify','desc':'付款成功webhook推送到客户服务器','current':'无','upgrade':'新增功能 ¥99/月'},
    {'name':'custom_dashboard','desc':'为客户定制专属数据看板','current':'无','upgrade':'B端高价 ¥500+/项目'},
    {'name':'white_label_data','desc':'把我们的数据API白标给合作方','current':'C8 whitebox','upgrade':'扩大为独立产品线'},
    {'name':'bulk_scan','desc':'批量扫描全市场找最佳标的','current':'C18 scan_api ¥99','upgrade':'企业版 unlimited'},
    {'name':'strategy_marketplace','desc':'让用户发布/买卖策略','current':'无','upgrade':'平台抽成10%'},
    {'name':'community_premium','desc':'付费社群+独家研报','current':'无','upgrade':'¥99/年会员'},
]
log("Untapped capabilities: {}".format(len(capabilities)))

# ===== LAYER 3: 竞争情报分析 =====
competitor_analysis=[
    {'name':'QuantConnect','model':'席位+算力节点','price_range':'Free-$99/mo','$strength':'Enterprise','my_angle':'更低门槛+中文+支付宝'},
    {'name':'JoinQuant聚宽','model':'免费+高级数据付费','price_range':'Free-¥299/月','$strength':'国内龙头','my_angle':'更轻量+过拟合检测'},
    {'name':'TradingView','model':'免费+高级图表付费','price_range':'Free-$60/mo','$strength':'零售用户巨大','my_angle':'专注回测+实盘模拟'},
    {'name':'Binance_API','model':'免费API+交易手续费','price_range':'Free','$strength':'数据免费','my_angle':'回测框架+风控工具'},
]
log("Competitor analysis: {} entries".format(len(competitor_analysis)))

# ===== LAYER 4: 生成可执行行动清单 =====
actions=[]

# Action 1: 发 pending 订单收款消息
pending_out=[]
pending_corp=[]
try:
    ol=json.load(open(os.path.join(BL,'outreach_ledger.json')))
    items=ol if isinstance(ol,list) else ol.get('items',[])
    pending_out=[x for x in items if x.get('status') not in ('paid','collected','done','verified')]
except: pass
try:
    cl=json.load(open(os.path.join(BL,'corporate_899.json')))
    items=cl if isinstance(cl,list) else cl.get('items',cl.get('orders',[]))
    pending_corp=[x for x in items if x.get('status') not in ('paid','collected','done','verified','approved')]
except: pass

total_pending_amt=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) 
                       for x in (pending_out+pending_corp))
if pending_out:
    actions.append({
        'type': 'collection', 'priority': 1, 'title': '发送收款消息给 {} 个 pending 客户'.format(len(pending_out)),
        'detail': '打开 revenue-collection.html → 复制每条消息 → 微信发出',
        'potential_revenue': sum(float(x.get('collect',0) or 0) for x in pending_out)
    })
if pending_corp:
    actions.append({
        'type': 'corporate', 'priority': 2, 'title': '发送对公打款函给 {} 个 corporate 客户'.format(len(pending_corp)),
        'detail': '打开 _对公打款函_899.md → 填账号 → 发给客户',
        'potential_revenue': sum(float(x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in pending_corp)
    })

# Action 2: 联系高信号 GitHub leads
high_leads=[l for l in lead_opportunities if l['signal']>=45]
if high_leads:
    actions.append({
        'type': 'outreach', 'priority': 3, 'title': '触达 {} 个高信号 GitHub 开发者'.format(len(high_leads)),
        'detail': '在 GitHub issue/pr 中评论推广链接，或在 README 中添加工具推荐',
        'potential_revenue': 0  # 长期价值
    })

# Action 3: 社交内容发布
social_channels=[
    {'platform':'Reddit','subs':['r/algotrading','r/CryptoCurrency','r/quant','r/Python'],
     'angle':'Show HN style post about building quant backtester'},
    {'platform':'Twitter/X','angle':'Thread about overfitting in backtests + free tool'},
    {'platform':'HackerNews','angle':'Show HN: 丙大山 - Open source quant backtesting with overfit detection'},
    {'platform':'LinkedIn','angle':'Built a quant tool after seeing too many fake backtests online'},
    {'platform':'V2EX','angle':'分享国产开源量化回测工具'},
]
actions.append({
    'type': 'social', 'priority': 4, 'title': '在多平台发布获客内容',
    'detail': '使用 /tmp/tweet_thread.txt, /tmp/reddit_post.txt 等素材',
    'potential_revenue': 0
})

# Action 4: 产品hunt上线
actions.append({
    'type': 'launch', 'priority': 5, 'title': 'Product Hunt 上市准备',
    'detail': '准备PH launch页面、投票引导、限时优惠',
    'potential_revenue': 0
})

# Action 5: Affiliate 分销
actions.append({
    'type': 'affiliate', 'priority': 6, 'title': '建立推荐返利系统',
    'detail': '每个 referral link 返 ¥30 CPA，让社区帮你拉新',
    'potential_revenue': 0
})

# ===== LAYER 5: 输出完整洞察报告 =====
insights={
    'generated_at': datetime.now().isoformat(),
    'summary': {
        'total_orders': len(orders),
        'paid_orders_real': len(paid_users),
        'cash_in': sum(float(o.get('amount',0) or 0) for o in paid_users),
        'pending_ledger': len(pending_out)+len(pending_corp),
        'pending_amount': total_pending_amt,
        'hot_visitors': len(hot_visitors),
        'high_signal_leads': len(high_leads),
        'untapped_capabilities': len(capabilities),
        'total_actions': len(actions)
    },
    'paid_users': paid_users[:10],
    'hot_visitors': hot_visitors[:10],
    'lead_opportunities': lead_opportunities[:10],
    'capabilities': capabilities,
    'competitors': competitor_analysis,
    'actions': sorted(actions, key=lambda x: x.get('priority',99)),
    'revenue_projections': {
        'conservative': 'Send collection messages -> expect ¥500-2000 this week',
        'moderate': 'Post on Reddit/Twitter -> expect 10-50 new trials/day',
        'aggressive': 'Product Hunt launch + affiliate program -> expect 100+ trials/week'
    }
}

with open(OUTPUT,'w',encoding='utf-8') as f:
    json.dump(insights,f,ensure_ascii=False,indent=2); f.write('\n')

log("Insights written to {}".format(OUTPUT))
log("Actions: {}".format(len(actions)))
log("Top action: {}".format(actions[0]['title'] if actions else 'none'))
print(json.dumps({'actions_count':len(actions),'top_priority':actions[0]['title'] if actions else '',
                   'potential_immediate':int(total_pending_amt)},ensure_ascii=False))

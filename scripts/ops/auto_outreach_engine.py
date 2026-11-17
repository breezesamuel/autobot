#!/usr/bin/env python3
"""丙大山 · 自动触达引擎 — 自动生成个性化消息并写到文件供运营使用"""
import json, os, sys
from datetime import datetime

BL='/opt/bingdashan/data/billing'
DB='/opt/bingdashan/data/db.json'
OUT_DIR='/opt/bingdashan/data/outreach_autogen'
LOG='/var/log/bingdashan/auto_outreach.log'
os.makedirs(OUT_DIR, exist_ok=True)

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[AO][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Auto Outreach Engine ===")

# Load data
try:
    d=json.load(open(DB,'r',encoding='utf-8'))
    orders=d.get('orders',[])
    visitors=d.get('visitors',[])
    leads=d.get('leads',[])
except Exception as e:
    log("ERR: {}".format(e)); sys.exit(1)

# ===== Generate outreach for pending orders =====
pending_msgs=[]
for fn in ['outreach_ledger.json','corporate_899.json']:
    fp=os.path.join(BL,fn)
    if not os.path.exists(fp): continue
    data=json.load(open(fp))
    items=data if isinstance(data,list) else data.get('items',data.get('orders',[]))
    for item in items:
        if not isinstance(item,dict): continue
        status=str(item.get('status',''))
        if status in ('paid','collected','done','verified','approved'): continue
        
        oid=str(item.get('order_id',''))[:16]
        ref=str(item.get('ref',''))
        amt=float(item.get('collect',0) or item.get('amount',0) or item.get('corporate_amount',0) or 0)
        kind=str(item.get('kind',''))
        link=str(item.get('pay_link','') or '')
        
        # Generate personalized message
        if 'corp' in kind.lower() or 'corporate' in str(item).lower():
            memo=item.get('remit_memo','丙大山年付-{}-{}'.format(oid,ref[:8]))[:40]
            msg="【丙大山·年费¥{} 对公打款】\n订单号:{}\n金额:¥{}\n汇款备注:{}".format(int(amt),oid,int(amt),memo)
            if link: msg+="\n支付宝备选: {}".format(link[:60])
            msg+="\n收款账户：以正式对公函为准。\n注意: 对公打款需备注订单号便于核销。"
        else:
            msg="【丙大山·支付提醒】\n您的订单 {} 已开通。\n付款链接: {}\n金额: ¥{}\n注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。".format(
                oid, link or 'https://tools-cn.highkingflower.com/api/pay?plan=pro&ref='+ref, int(amt))
        
        pending_msgs.append({
            'ref': ref, 'oid': oid, 'amt': int(amt), 'kind': kind,
            'message': msg, 'link': link,
            'generated_at': datetime.now().isoformat()
        })

# Save to file
if pending_msgs:
    out_path=os.path.join(OUT_DIR,'pending_orders_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M')))
    with open(out_path,'w',encoding='utf-8') as f:
        f.write("# 丙大山 · 待触达客户消息 (自动生成)\n")
        f.write("> 生成时间: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M')))
        f.write("> 共 {} 条，逐条复制到微信/QQ/短信发送\n\n".format(len(pending_msgs)))
        for i,msg_data in enumerate(pending_msgs,1):
            f.write("--- 第 {} 条 ---\n".format(i))
            f.write("Ref: {} | OID: {} | ¥{}\n".format(msg_data['ref'], msg_data['oid'], msg_data['amt']))
            f.write(msg_data['message'])
            f.write("\n\n")
    log("Saved {} pending messages -> {}".format(len(pending_msgs), out_path))

# ===== Generate GitHub lead outreach =====
lead_msgs=[]
for ld in leads:
    if not isinstance(ld,dict): continue
    lid=str(ld.get('id',''))
    repo=str(ld.get('repo',''))
    signal=int(ld.get('signal',0) or 0)
    industry=str(ld.get('industry','Python'))
    
    # Personalized pitch based on industry
    pitches={
        'Python': "看到你在做 Python 方向。推荐一个免费的量化回测工具：真K线（币安官方数据），一键出 Sharpe/最大回撤/胜率/年化报告，还有过拟合检测（回测好实盘崩的坑）。免费7天无信用卡。",
        'HTML': "前端开发者也能做量化！把策略逻辑写成 JS 跑真实行情回测，出专业 PDF 报告。免费试用7天。",
        'agent': "你的 agent 项目需要量化验证吗？丙大山提供真实市场数据回测+过拟合检测，帮你验证策略有效性。免费7天。",
    }
    pitch=pitches.get(industry, "看到你在做 {} 方向。推荐一个免费量化回测平台：真实币安K线数据+过拟合检测+专业报告导出。".format(industry))
    
    full_msg="Hi, {}\n\n".format(repo) + pitch + "\n\n免费体验：https://tools.highkingflower.com/get.html?ref=github_{} \n\n注意：回测是历史数据，不代表未来收益；非投资建议，风险自负。".format(lid[:8])
    
    lead_msgs.append({
        'id': lid, 'repo': repo, 'signal': signal, 'industry': industry,
        'pitch': pitch, 'full_message': full_msg,
        'generated_at': datetime.now().isoformat()
    })

if lead_msgs:
    lead_path=os.path.join(OUT_DIR,'github_leads_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M')))
    with open(lead_path,'w',encoding='utf-8') as f:
        f.write("# 丙大山 · GitHub 开发者触达消息 (自动生成)\n")
        f.write("> 生成时间: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M')))
        f.write("> 共 {} 条高信号线索，在对应 Repo 的 Issue/PR/README 中发布\n\n".format(len(lead_msgs)))
        for i,lm in enumerate(lead_msgs,1):
            f.write("--- 第 {} 条 | signal={} | repo={} ---\n".format(i, lm['signal'], lm['repo']))
            f.write(lm['full_message'])
            f.write("\n\n")
    log("Saved {} lead messages -> {}".format(len(lead_msgs), lead_path))

# ===== Generate social media content =====
social_templates=[
    ('twitter_thread', '''Thread 🧵: I built a quant backtesting tool because I was tired of fake "1000% returns" from overfitted strategies.

Here's what makes it different:
• REAL Binance public K-line data (not simulated)
• Built-in overfit detection (flags suspicious Sharpe/drawdown ratios)
• Multi-asset portfolio simulation (BTC+ETH+SOL combos)
• One-click professional PDF reports
• Free 7-day trial, no credit card

The tool: https://tools.highkingflower.com/get.html?ref=twitter
#quant #trading #backtest #python #crypto #overfit'''),
    
    ('reddit_post', '''Title: I built a free quant backtester with overfit detection — here's why

Body:
Hey r/algotrading,

I kept seeing people publish backtest results that completely fail in live trading. Turns out most "good backtests" are just overfit noise. So I built a tool that helps you find out BEFORE deploying real money.

Features:
• Real Binance public API data (no simulation)
• Overfit risk scoring with explanations
• Walk-forward validation built in
• Multi-asset portfolio backtesting
• Professional PDF report export
• Free 7-day trial, no credit card

Built with Node.js, deployed on Vercel + Aliyun CN. Open source core.

Try it: https://tools.highkingflower.com/get.html?ref=reddit

Would love feedback from anyone who actually trades quant strategies. Happy to answer architecture questions too.

Note: This is a TOOL, not investment advice. Historical backtest ≠ future returns.'''),
    
    ('linkedin_post', '''I built a quantitative backtesting platform after seeing too many "1000% backtest" posts that completely fail in live trading.

The problem: most good-looking backtests are overfitted noise.

So I built overfit detection directly into the engine — it calculates walk-forward decay, parameter sensitivity, and Sharpe-to-drawdown ratios automatically.

Tech stack: Node.js, Binance public API, Supabase, Vercel edge functions.

Free trial: https://tools.highkingflower.com/get.html?ref=linkedin

If you're serious about quant trading, honest backtesting is step one.

#quantitativeTrading #backtesting #algoTrading #fintech '''),
    
    ('hackernews', '''Show HN: 丙大山 – Quant backtesting with overfit detection (Node.js, real Binance data)

I built this because I was frustrated by the number of "1000% return" backtest posts that completely fail in live trading.

Core insight: most good-looking backtests are overfit. So I built overfit detection directly into the engine.

Features:
• Real public market data from Binance (no simulation)
• Overfit risk scoring with explanations
• Walk-forward validation
• Multi-asset portfolio backtesting  
• Professional report export (PDF/Excel/CSV)
• Free 7-day trial, no credit card

Tech: Node.js backend, Supabase + Upstash KV, Vercel edge, ethers.js for Web3 settlement.

Would love feedback from the HN quant community. What am I missing?

https://tools.highkingflower.com/get.html?ref=hackernews'''),
]

for name, content in social_templates:
    spath=os.path.join(OUT_DIR,'{}_{}.txt'.format(name, datetime.now().strftime('%Y%m%d_%H%M')))
    with open(spath,'w',encoding='utf-8') as f:
        f.write(content)
    log("Generated {} -> {}".format(name, spath))

# ===== Summary =====
total_generated=len(pending_msgs)+len(lead_msgs)+len(social_templates)
log("Total assets generated: {} (pending={}, leads={}, social={})".format(
    total_generated, len(pending_msgs), len(lead_msgs), len(social_templates)))
log("Output directory: {}".format(OUT_DIR))
log("=== Auto Outreach Engine Complete ===")

#!/usr/bin/env python3
"""丙大山 · Affiliate分销引擎 — 生成推荐链接+追踪+佣金计算"""
import json, os, sys, hashlib, secrets
from datetime import datetime, timedelta

BL='/opt/bingdashan/data/billing'
DB='/opt/bingdashan/data/db.json'
STATE='/opt/bingdashan/data/runtime/affiliate_state.json'
LOG='/var/log/bingdashan/affiliate.log'
os.makedirs(os.path.dirname(STATE), exist_ok=True)

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[AFF][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Affiliate Engine v1 ===")

# Load state
try:
    state=json.load(open(STATE,'r',encoding='utf-8')) if os.path.exists(STATE) else {}
except: state={}

default_keys=['ref_code','ref_link','ref_url','commission_rate','total_commission','payout_status']

# Generate unique referral codes for each channel
channels=[
    {'name':'twitter','code':'tw','base':'https://tools.highkingflower.com/get.html?ref=tw'},
    {'name':'reddit','code':'rd','base':'https://tools.highkingflower.com/get.html?ref=rd'},
    {'name':'linkedin','code':'li','base':'https://tools.highkingflower.com/get.html?ref=li'},
    {'name':'hackernews','code':'hn','base':'https://tools.highkingflower.com/get.html?ref=hn'},
    {'name':'wechat','code':'wx','base':'https://tools-highkingflower.com/get.html?ref=wx'},
    {'name':'github','code':'gh','base':'https://tools.highkingflower.com/get.html?ref=gh'},
    {'name':'youtuber','code':'yt','base':'https://tools.highkingflower.com/get.html?ref=yt'},
    {'name':'blog','code':'bl','base':'https://tools.highkingflower.com/get.html?ref=bl'},
]

CPA_RATE=30  # ¥30 per valid referral
COMMISSION_PCT=0.15  # 15% commission on paid orders

for ch in channels:
    code=ch['code']
    if code not in state:
        state[code]={
            'code': code,
            'link': ch['base'],
            'clicks': 0,
            'signups': 0,
            'paid_conversions': 0,
            'total_commission': 0,
            'created_at': datetime.now().isoformat(),
            'last_payout': None
        }
        log("Generated affiliate code: {} -> {}".format(code, ch['base']))

# Load existing referrals from db.json visitors/orders
try:
    d=json.load(open(DB,'r',encoding='utf-8'))
    referrals=d.get('referrals',{})
    state['existing_referrals']=referrals
    log("Loaded {} existing referrals from db.json".format(len(referrals)))
except Exception as e:
    log("WARN load referrals: {}".format(e))

# Calculate potential earnings
total_potential=0
for ch in channels:
    s=state.get(ch['code'],{})
    conversions=s.get('paid_conversions',0)
    total_potential += conversions * CPA_RATE + s.get('total_commission',0)

state['summary']={
    'total_channels': len(channels),
    'cpa_rate_yuan': CPA_RATE,
    'commission_pct': COMMISSION_PCT,
    'total_potential_earnings': total_potential,
    'generated_at': datetime.now().isoformat()
}

with open(STATE,'w',encoding='utf-8') as f:
    json.dump(state,f,ensure_ascii=False,indent=2); f.write('\n')

# Generate affiliate report
report_path='/opt/bingdashan/data/outreach_autogen/affiliate_report_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M'))
with open(report_path,'w',encoding='utf-8') as f:
    f.write("# 丙大山 · Affiliate 分销系统报告\n")
    f.write("> 生成时间: {}\n\n".format(datetime.now().strftime('%Y-%m-%d %H:%M')))
    f.write("## 分销码列表\n\n")
    f.write("| 渠道 | 推荐码 | 短链 | CPA奖励 | 状态 |\n")
    f.write("|---|---|---|---|---|\n")
    for ch in channels:
        code=ch['code']
        s=state.get(code,{})
        f.write("| {} | {} | {} | ¥{} | 活跃 |\n".format(
            ch['name'].capitalize(), code, s.get('link',ch['base']), CPA_RATE))
    f.write("\n## 使用说明\n")
    f.write("1. 把对应渠道的短链发给你的粉丝/社群\n")
    f.write("2. 新用户通过该链接注册 → 自动记录 referral\n")
    f.write("3. 新用户付费后 → 自动计算佣金 ¥{} 或 15% 销售额\n".format(CPA_RATE))
    f.write("4. 每月结算一次，转账到指定账户\n\n")
    f.write("## 推广话术模板\n\n")
    f.write("【Twitter】用你的链接发帖:\n{}\n\n".format(ch['base'] for ch in channels[:1]))
    f.write("【Reddit】在相关帖子评论区发:\n看这个量化回测工具，免费7天: {}\n\n".format(ch['base'] for ch in channels[:1]))

log("Report saved to: {}".format(report_path))
log("=== Affiliate Engine Complete ===")
print(json.dumps({'channels':len(channels),'cpa':CPA_RATE,'state_keys':list(state.keys())},ensure_ascii=False))

#!/usr/bin/env python3
"""丙大山 · Lead Outreach 引擎 (针对 GitHub 开发者线索自动生成触达文案)"""
import json, os, sys
from datetime import datetime

DB='/opt/bingdashan/data/db.json'
LOG='/var/log/bingdashan/lead_outreach.log'
STATE_FILE='/opt/bingdashan/data/runtime/lead_state_v7.json'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[LEAD][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

def load_state():
    try: return json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {}
    except: return {}
def save_state(s):
    with open(STATE_FILE,'w',encoding='utf-8') as f: json.dump(s,f,ensure_ascii=False,indent=2); f.write('\n')

log("=== Lead Outreach Engine start ===")
try:
    d=json.load(open(DB,'r',encoding='utf-8')); leads=d.get('leads',[])
except Exception as e:
    log("ERR read leads: {}".format(e)); sys.exit(1)

state=load_state()
sent_today=state.get('sent_leads_today',[])

for ld in leads:
    if not isinstance(ld,dict): continue
    lid=str(ld.get('id',''))
    repo=str(ld.get('repo',''))
    name=str(ld.get('name',''))
    industry=str(ld.get('industry','Python'))
    signal=int(ld.get('signal',0) or 0)
    
    if lid in sent_today:
        log("SKIP already processed lead={}".format(lid))
        continue
    
    # Build personalized email (logged, not sent yet since no contact info)
    subject="【工具推荐】一个能跑真实回测的量化平台，适合你的 {} 项目".format(industry)
    body_lines=[
        "Hi {}, ".format(name),
        "",
        "看到你在做 {} 方向。推荐一个免费的量化回测平台：".format(industry),
        "- 真K线回测（币安官方数据）",
        "- 一键对比 Sharpe / 最大回撤 / 胜率 / 年化收益",
        "- 过拟合检测（回测好实盘崩的坑）",
        "- 免费7天，无需信用卡",
        "",
        "免费体验：https://tools-cn.highkingflower.com/get.html?ref=github_leads",
        "",
        "注意：回测是历史数据，不代表未来收益；非投资建议，风险自负。",
        "",
        "—— 丙大山团队"
    ]
    body_text='\n'.join(body_lines)
    html_body='<p>'+body_text.replace('\n','<br>')+'</p>'
    
    log("WOULD SEND to lead={} repo={} industry={} signal={} subject={}".format(
        lid, repo, industry, signal, subject[:50]))
    log("  Body preview: {}...".format(body_text[:100]))
    
    sent_today.append(lid)
    state['last_run']=datetime.now().isoformat()
    state['sent_leads_today']=sent_today[:200]
    save_state(state)

total_processed=len(sent_today)
total_leads=len(leads)
log("Lead outreach done. Processed {}/{} leads.".format(total_processed, total_leads))
print("LEAD_PROCESSED={}/{}".format(total_processed, total_leads))

#!/usr/bin/env python3
"""丙大山 · visitor 洞察引擎 (自动发现高价值访客 -> 生成触达建议)"""
import json, os, sys
from datetime import datetime, timedelta

DB='/opt/bingdashan/data/db.json'
BL='/opt/bingdashan/data/billing'
LOG='/var/log/bingdashan/insights.log'
ALERTS='/opt/bingdashan/data/alerts.json'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[INSIGHT][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Visitor Insight Engine start ===")
try:
    d=json.load(open(DB,'r',encoding='utf-8'))
except Exception as e:
    log("ERR read db: {}".format(e)); sys.exit(1)
orders=d.get('orders',[])
visitors=d.get('visitors',[])
leads=d.get('leads',[])

# 已付费的 ref/set
paid_refs=set()
for o in orders:
    if o.get('paid') is True and o.get('ref'):
        paid_refs.add(str(o['ref']))

# 高价值信号: 访问过 channels.html/subwall/pricing 页面但未付费
HOT_SIGNALS=['channels','subwall','pricing','engine','backtest','revenue']
cutoff=timedelta(hours=48)
hot_visitors=[]
for v in visitors:
    if not isinstance(v,dict): continue
    ip=str(v.get('ip',''))
    if '127_0_0_1' in ip: continue
    visited_pages=v.get('pages') or v.get('visited_pages') or []
    page_str=str(visited_pages)
    has_hot_signal=any(s in page_str for s in HOT_SIGNALS)
    ts_v=v.get('at') or 0
    if has_hot_signal and str(v.get('visitor') or ip) not in paid_refs:
        hot_visitors.append({'ip':ip,'pages':visited_pages[:5],'at':ts_v})

hot_visitors.sort(key=lambda x:x.get('at',0), reverse=True)
top_hot=hot_visitors[:10]

# leads with "促单" stage
prompts=[]
for ld in leads:
    if not isinstance(ld,dict): continue
    stage=str(ld.get('stage',''))
    status=ld.get('status','')
    signal=ld.get('signal',0) or 0
    if '促单' in stage or signal>=40:
        prompts.append({
            'id':ld.get('id',''),
            'repo':ld.get('repo',''),
            'stage':stage,
            'signal':signal,
            'industry':ld.get('industry','')
        })

# 写 alerts
result={'generated_at':datetime.now().isoformat(),'hot_visitors_count':len(top_hot),'hot_visitors':top_hot[:5],'lead_prompts':prompts[:5]}
with open(ALERTS,'w',encoding='utf-8') as f:
    json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
log("Hot visitors: {}, Lead prompts: {}".format(len(top_hot), len(prompts)))
if top_hot:
    for h in top_hot[:3]: log("  HOT ip={} pages={}".format(h['ip'], str(h['pages'])[:60]))
if prompts:
    for p in prompts[:3]: log("  LEAD repo={} signal={} stage={}".format(p['repo'],p['signal'],p['stage']))
log("=== Visitor Insight Engine done ===")

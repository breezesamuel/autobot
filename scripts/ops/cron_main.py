#!/usr/bin/env python3
"""定时任务: 每小时跑一次 engine_v3 + 每日 09:00 发升级邮件 + 每 30min 监控 manual 单"""
import json, os, sys
from datetime import datetime, timedelta
import subprocess, time

LOG='/var/log/bingdashan/cron.log'
BL='/opt/bingdashan/data/billing'
DB='/opt/bingdashan/data/db.json'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[CRON][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== CRON START ===")

# 1. Run engine v3 (reconcile + health + disk cleanup)
log("1/4 Running engine v3...")
rc=subprocess.call(['python3','/opt/bingdashan/scripts/ops/engine_v3.py'], timeout=60)
log("   engine rc={}".format(rc))

# 2. Check manual orders - any new paid signals?
log("2/4 Checking manual orders...")
outreach=[]
try:
    d=json.load(open(os.path.join(BL,'outreach_ledger.json')))
    outreach=d if isinstance(d,list) else d.get('items',[])
except: pass
recent=[x for x in outreach if isinstance(x,dict) and x.get('status')=='pending_outreach']
if recent:
    log("   outstanding manual orders: {}".format(len(recent)))
    # Build/update revenue-collection.html with latest
    try:
        subprocess.call(['python3','/tmp/gen_batch.py'], timeout=30)
        log("   refreshed revenue-collection.html")
    except: pass
else:
    log("   no outstanding manual orders")

# 3. Check corporate orders
corp=[]
try:
    d=json.load(open(os.path.join(BL,'corporate_899.json')))
    corp=d if isinstance(d,list) else d.get('items',d.get('orders',[]))
except: pass
corp_pending=[x for x in corp if isinstance(x,dict) and x.get('status') not in ('paid','collected','done','verified','approved')]
log("3/4 Corporate pending: {} orders".format(len(corp_pending)))

# 4. Final summary
try:
    d=json.load(open(DB,'r',encoding='utf-8')); orders=d.get('orders',[])
    paid=[o for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0)>5]
    total_cash=sum(float(o.get('amount',0) or 0) for o in paid)
except: total_cash=0

all_pending=outreach+corp
all_pending=[x for x in all_pending if isinstance(x,dict) and x.get('status') not in ('paid','collected','done','verified','approved')]
pending_yuan=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in all_pending)
log("4/4 Summary: cash=¥{} pending=¥{} ({})".format(int(total_cash), int(pending_yuan), len(all_pending)))
log("=== CRON DONE ===")

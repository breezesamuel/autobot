#!/usr/bin/env python3
"""丙大山 · 全系统健康快照 + 收入机会分析"""
import json, os, sys, subprocess, urllib.request
from datetime import datetime

BL='/opt/bingdashan/data'
LOG='/var/log/bingdashan/health_snapshot.log'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[SNAP][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Health Snapshot ===")

# 1. Revenue status
try:
    d=json.load(open(os.path.join(BL,'db.json')))
    orders=d.get('orders',[])
    paid=[o for o in orders if o.get('paid') and float(o.get('amount',0) or 0)>5]
    total_cash=sum(float(o.get('amount',0) or 0) for o in paid)
    today=str(datetime.now().date())
    today_paid=[o for o in paid if o.get('paid_at','')[:10]==today]
    today_cash=sum(float(o.get('amount',0) or 0) for o in today_paid)
    log("cash=¥{} today=¥{} paid_orders={}".format(int(total_cash),int(today_cash),len(paid)))
except Exception as e:
    log("ERR revenue: {}".format(e))

# 2. Pending ledger
bl2=os.path.join(BL,'billing')
for fn in ['outreach_ledger.json','corporate_899.json']:
    p=os.path.join(bl2,fn)
    if os.path.exists(p):
        data=json.load(open(p))
        items=data if isinstance(data,list) else data.get('items',data.get('orders',[]))
        pending=[x for x in items if x.get('status') not in ('paid','collected','done','verified','approved')]
        amt=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in pending)
        log("{}: {} pending, ¥{}".format(fn,len(pending),int(amt)))

# 3. Module count
lib_dir='/www/wwwroot/tools-cn.highkingflower.com/lib'
modules=len([f for f in os.listdir(lib_dir) if f.endswith('.js')])
log("modules: {}".format(modules))

# 4. Route count
try:
    ap_src=open('/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js','r',encoding='utf-8').read()
    routes=len([l for l in ap_src.split('\n') if "route.startsWith('/api/" in l])
    log("routes: {}".format(routes))
except: routes=0

# 5. Service health
for svc in ['bingdashan-cn','bd-engine-hourly','bd-revenue-watch','bd-perf-backup']:
    r=subprocess.run(['systemctl','is-active',svc],capture_output=True,text=True)
    log("{}: {}".format(svc,r.stdout.strip()))

# 6. Disk
r=subprocess.run(['df','-h','/'],capture_output=True,text=True)
for ln in r.stdout.strip().split('\n')[1:]:
    parts=ln.split(); log("disk: use={} avail={}".format(parts[4],parts[3]))

# 7. External health check (can we reach our own endpoints?)
endpoints=['http://127.0.0.1:8794/api/overfitcheck?action=rate&ref=h','http://127.0.0.1:8794/revenue-honest.html']
for ep in endpoints:
    try:
        req=urllib.request.Request(ep,headers={'User-Agent':'BingDashan-Snap/1.0'})
        resp=urllib.request.urlopen(req,timeout=10)
        log("HERTZ {} -> HTTP{}".format(ep[-30:],resp.status))
    except Exception as e:
        log("HERTZ {} -> ERR: {}".format(ep[-30:],str(e)[:60]))

# 8. Opportunity analysis
log("")
log("=== Opportunity Analysis ===")
log("Current cash: ¥{}".format(int(total_cash) if 'total_cash' in dir() else 0))
log("Pending ledger: ~¥3549 (13 orders)")
log("Channels live: {} modules, {} routes".format(modules,routes))
log("")
log("TOP 5 actions to increase revenue:")
log("1. Send revenue-collection messages to 13 pending refs")
log("2. Post get.html referral links to Reddit/X/LinkedIn")
log("3. Enable affiliate program (C21 path)")
log("4. Launch C12 annual subscription push (¥3990 lock-in)")
log("5. Add Stripe crypto payment for international users")
log("")
log("=== Snapshot complete ===")

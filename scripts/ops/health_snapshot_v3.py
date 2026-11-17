#!/usr/bin/env python3
import json, os, sys, subprocess, urllib.request
from datetime import datetime

BL='/opt/bingdashan/data'
LOG='/var/log/bingdashan/health_snapshot.log'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[SNAP][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

def run(cmd):
    try:
        r=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return -1, '', str(e)[:80]

log("=== Health Snapshot v3 ===")

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
    log("ERR revenue: {}".format(e)); total_cash=0; today_cash=0

bl2=os.path.join(BL,'billing')
total_pending=0; total_pending_count=0
for fn in ['outreach_ledger.json','corporate_899.json']:
    p=os.path.join(bl2,fn)
    if os.path.exists(p):
        data=json.load(open(p))
        items=data if isinstance(data,list) else data.get('items',data.get('orders',[]))
        pending=[x for x in items if x.get('status') not in ('paid','collected','done','verified','approved')]
        amt=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in pending)
        total_pending+=amt; total_pending_count+=len(pending)
        log("{}: {} pending, ¥{}".format(fn,len(pending),int(amt)))
log("TOTAL_PENDING: {} orders, ¥{}".format(total_pending_count,int(total_pending)))

lib_dir='/www/wwwroot/tools-cn.highkingflower.com/lib'
modules=len([f for f in os.listdir(lib_dir) if f.endswith('.js')])
try:
    ap_src=open('/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js','r',encoding='utf-8').read()
    routes=len([l for l in ap_src.split('\n') if "route.startsWith('/api/" in l])
except: routes=0
log("modules: {}, routes: {}".format(modules,routes))

for svc in ['bingdashan-cn','bd-engine-hourly','bd-revenue-watch','bd-perf-backup']:
    rc,o,e=run(['systemctl','is-active',svc])
    log("{}: {}".format(svc,o if o else 'unknown'))

rc,o,e=run(['df','-h','/'])
for ln in o.split('\n')[1:]:
    parts=ln.split()
    if len(parts)>=5: log("disk: use={} avail={}".format(parts[4],parts[3]))

for ep in ['/api/overfitcheck?action=rate&ref=h','/revenue-honest.html']:
    try:
        req=urllib.request.Request('http://127.0.0.1:8794'+ep,headers={'User-Agent':'BingDashan-Snap/1.0'})
        resp=urllib.request.urlopen(req,timeout=10)
        log("HERTZ {} -> HTTP{}".format(ep,resp.status))
    except Exception as e:
        log("HERTZ {} -> ERR: {}".format(ep,str(e)[:60]))

rc,o,e=run(['systemctl','list-timers','--all'])
for ln in o.split('\n'):
    if 'bd-engine-hourly' in ln: log("NEXT_ENGINE: "+ln.strip())

log("")
log("=== Revenue Analysis ===")
log("REAL CASH IN: ¥{}".format(int(total_cash)))
log("PENDING: ¥{} from {} orders".format(int(total_pending),total_pending_count))
log("CHANNELS: {} modules, {} routes".format(modules,routes))
log("")
log("TOP PRIORITY ACTIONS:")
log("1. [FASTEST] Send 13 collection messages -> revenue-collection.html")
log("2. [MEDIUM] Post on Reddit r/algotrading + r/CryptoCurrency")
log("3. [MEDIUM] Email 3 GitHub leads with personalized pitch")
log("4. [LONG] Launch affiliate program (C21 path)")
log("5. [LONG] Add Stripe/crypto payments for international")
log("")
log("=== Complete ===")

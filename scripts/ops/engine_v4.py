#!/usr/bin/env python3
"""丙大山 · 24h 不间断自动收钱引擎 v4 (compatible with python3.6)"""
import json, os, sys, time, subprocess
from datetime import datetime, timedelta
from collections import Counter

BL='/opt/bingdashan/data/billing'
DB='/opt/bingdashan/data/db.json'
LOG='/var/log/bingdashan/engine.log'
ROOT='/www/wwwroot/tools-cn.highkingflower.com'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[ENGINE][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

def load(fn,d=[]):
    p=os.path.join(BL,fn)
    if not os.path.exists(p): return d
    try:
        data=json.load(open(p,'r',encoding='utf-8'))
        return data if isinstance(data,list) else data.get('items', data.get('orders',d))
    except: return d

def save(fn,data):
    with open(os.path.join(BL,fn),'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2); f.write('\n')

FINAL={'paid','collected','done','verified','approved'}
log("=== ENGINE LOOP v4 start ===")

# ===== PHASE 1: Reconcile =====
try:
    d=json.load(open(DB,'r',encoding='utf-8')); orders=d.get('orders',[])
except Exception as e:
    log("ERR read db: {}".format(e)); sys.exit(1)

by={}
for o in orders:
    if not isinstance(o,dict): continue
    amt=float(o.get('amount',0) or 0)
    ref=str(o.get('ref','') or '')
    is_real=(o.get('paid') is True and amt>5 and len(ref)>2 and bool(o.get('gateway')))
    if is_real and ref:
        if ref not in by or (o.get('paid_at','') or '') > (by[ref].get('paid_at','') or ''):
            by[ref]=o

outreach=load('outreach_ledger.json'); up_out=0
for i in outreach:
    if not isinstance(i,dict): continue
    ref=str(i.get('ref','')); st=i.get('status','')
    if ref in by and st not in FINAL:
        i['status']='paid'; i['paid_at']=datetime.now().isoformat()
        up_out+=1
save('outreach_ledger.json',outreach)

corp=load('corporate_899.json'); up_corp=0
for i in corp:
    if not isinstance(i,dict): continue
    ref=str(i.get('ref','')); st=i.get('status','')
    if ref in by and st not in FINAL:
        i['status']='paid'; i['paid_at']=datetime.now().isoformat()
        up_corp+=1
save('corporate_899.json',corp)

outreach=load('outreach_ledger.json'); corp=load('corporate_899.json')
po=[x for x in outreach if x.get('status') not in FINAL]
pc=[x for x in corp if x.get('status') not in FINAL]
py=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in po+pc)
ro=[o for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0)>5]
ry=sum(float(o.get('amount',0) or 0) for o in ro)
log("PHASE1 reconcile: out_up={} corp_up={} cash=¥{} pending=¥{}".format(up_out,up_corp,int(ry),int(py)))

# ===== PHASE 2: Health checks (py3.6 compat) =====
svcs=['bingdashan-cn']
for svc in svcs:
    r=subprocess.run(['systemctl','is-active',svc], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.stdout.strip() != 'active':
        log("CRITICAL: {} NOT active".format(svc))
        subprocess.call(['systemctl','restart',svc])
        time.sleep(3)
    else:
        log("PHASE2 service {} OK".format(svc))

endpoints=['http://127.0.0.1:8794/api/revenue','http://127.0.0.1:8794/revenue-honest.html']
for ep in endpoints:
    try:
        import urllib.request
        req=urllib.request.Request(ep, headers={'User-Agent':'BingDashan-HealthCheck/1.0'})
        resp=urllib.request.urlopen(req, timeout=10)
        if resp.status!=200: log("WARNING: {} HTTP {}".format(ep, resp.status))
        else: log("PHASE2 healthcheck {} OK".format(ep.split('/')[-1]))
    except Exception as e:
        log("ERROR: {} unreachable: {}".format(ep, str(e)[:80]))

# disk space
try:
    r=subprocess.run(['df','-h','/'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    parts=r.stdout.strip().split('\n')[1].split()
    usage_pct=int(parts[4].replace('%',''))
    log("PHASE2 disk / usage: {}%".format(usage_pct))
    if usage_pct > 90:
        log("CRITICAL: disk > 90%, cleanup!")
        import glob
        for lp in glob.glob('/var/log/bingdashan/*.log'):
            try:
                sz=os.path.getsize(lp)
                if sz > 10*1024*1024:
                    os.rename(lp, lp+'.bak')
                    log("CLEANUP rotated {}".format(lp))
            except: pass
except Exception as e:
    log("PHASE2 disk check warn: {}".format(e))

# ===== PHASE 3: Refresh outreach messages =====
try:
    rc3=subprocess.call(['python3','/opt/bingdashan/scripts/ops/auto_outreach.py'], timeout=30)
    log("PHASE3 outreach_refresh rc={}".format(rc3))
except Exception as e:
    log("PHASE3 outreach_refresh WARN: {}".format(str(e)[:80]))

# ===== PHASE 4: Today's stats =====
total_paid_today=0
today=datetime.now().date()
try:
    for o in ro:
        pa=o.get('paid_at','')
        if pa:
            try:
                pd=datetime.strptime(pa[:10],'%Y-%m-%d').date() if len(pa)>=10 else None
                if pd and pd==today: total_paid_today+=float(o.get('amount',0) or 0)
            except: pass
except: pass
log("PHASE4 today_paid=¥{}".format(int(total_paid_today)))

all_pending=po+pc
total_pending_yuan=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in all_pending)
log("=== ENGINE LOOP v4 done: cash=¥{} pending=¥{} today=¥{} count={} ===".format(
    int(ry), int(total_pending_yuan), int(total_paid_today), len(all_pending)))
sys.exit(0)

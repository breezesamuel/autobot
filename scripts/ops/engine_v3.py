#!/usr/bin/env python3
"""丙大山 · 24h 不间断自动收钱引擎 v3 (核心循环 + 健康守护 + 主动触达)"""
import json, os, sys, time, subprocess
from datetime import datetime, timedelta
from collections import Counter

BL='/opt/bingdashan/data/billing'
DB='/opt/bingdashan/data/db.json'
LOG='/var/log/bingdashan/engine.log'
ROOT='/www/wwwroot/tools-cn.highkingflower.com'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[ENGINE][{}] {}".format(ts, m); print(line); 
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

log("=== ENGINE LOOP v3 start ===")

# ===== PHASE 1: Reconcile (db.json paid -> 台账) =====
try:
    d=json.load(open(DB,'r',encoding='utf-8')); orders=d.get('orders',[])
except Exception as e:
    log("ERR read db: {}".format(e)); sys.exit(1)

by={}
for o in orders:
    if not isinstance(o,dict): continue
    amt=float(o.get('amount',0) or 0)
    ref=str(o.get('ref','') or '')
    # 真实客户: paid=true + amount>5 + ref有效 + gateway存在
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

# reload
outreach=load('outreach_ledger.json'); corp=load('corporate_899.json')
po=[x for x in outreach if x.get('status') not in FINAL]
pc=[x for x in corp if x.get('status') not in FINAL]
py=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in po+pc)
ro=[o for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0)>5]
ry=sum(float(o.get('amount',0) or 0) for o in ro)
log("PHASE1 reconcile: out_up={} corp_up={} cash=¥{} pending=¥{}".format(up_out,up_corp,int(ry),int(py)))

# ===== PHASE 2: Check disk space (prevent ops crash) =====
try:
    r=subprocess.run(['df','-h','/'], capture_output=True, text=True)
    lines=r.stdout.strip().split('\n')
    if len(lines)>=2:
        parts=lines[1].split()
        usage_pct=int(parts[4].replace('%',''))
        log("PHASE2 disk / usage: {}%".format(usage_pct))
        if usage_pct > 90:
            log("CRITICAL: disk usage > 90%, trigger cleanup!")
            # cleanup old logs
            import glob
            for lp in glob.glob('/var/log/bingdashan/*.log'):
                try:
                    sz=os.path.getsize(lp)
                    if sz > 10*1024*1024:  # >10MB
                        os.rename(lp, lp+'.bak')
                        log("CLEANUP: rotated {}".format(lp))
                except: pass
except Exception as e:
    log("PHASE2 disk check warn: {}".format(e))

# ===== PHASE 3: Check service health =====
svcs=['bingdashan-cn']
for svc in svcs:
    r=subprocess.run(['systemctl','is-active',svc], capture_output=True, text=True)
    if r.stdout.strip() != 'active':
        log("CRITICAL: {} is NOT active, trying restart...".format(svc))
        subprocess.call(['systemctl','restart',svc])
        time.sleep(3)
        r2=subprocess.run(['systemctl','is-active',svc], capture_output=True, text=True)
        log("  after restart: {}".format(r2.stdout.strip()))

# ===== PHASE 4: Verify payment endpoints still respond =====
endpoints=['http://127.0.0.1:8794/api/revenue','http://127.0.0.1:8794/revenue-honest.html']
for ep in endpoints:
    try:
        import urllib.request
        req=urllib.request.Request(ep, headers={'User-Agent':'BingDashan-HealthCheck/1.0'})
        resp=urllib.request.urlopen(req, timeout=10)
        if resp.status!=200:
            log("WARNING: {} returned HTTP {}".format(ep, resp.status))
    except Exception as e:
        log("ERROR: {} unreachable: {}".format(ep, str(e)[:100]))

# ===== PHASE 5: Generate fresh revenue stats =====
total_paid_today=0
try:
    today=datetime.now().date()
    for o in ro:
        pa=o.get('paid_at','')
        if pa:
            try:
                pd=datetime.fromisoformat(pa.replace('Z','+00:00')).date() if '+' in pa else datetime.strptime(pa[:10],'%Y-%m-%d').date()
                if pd==today: total_paid_today+=float(o.get('amount',0) or 0)
            except: pass
except: pass
log("PHASE5 today_paid=¥{}".format(int(total_paid_today)))

# ===== SUMMARY =====
log("=== ENGINE LOOP v3 done: cash=¥{} pending=¥{} today_paid=¥{} up_out={} up_corp={}".format(
    int(ry), int(py), int(total_paid_today), up_out, up_corp))
sys.exit(0)

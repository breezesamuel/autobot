#!/usr/bin/env python3
"""丙大山 · 持续自动化循环 — 每轮检查+行动"""
import json, os, sys, subprocess, time
from datetime import datetime, timedelta

BL='/opt/bingdashan/data'
LOG='/var/log/bingdashan/engine_loop.log'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[LOOP][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Auto Loop Start ===")

# Check 1: Revenue
try:
    d=json.load(open(os.path.join(BL,'db.json')))
    orders=d.get('orders',[])
    paid=[o for o in orders if o.get('paid') and float(o.get('amount',0) or 0)>5]
    total=sum(float(o.get('amount',0) or 0) for o in paid)
    now=datetime.now()
    today_paid=[o for o in paid if o.get('paid_at','')[:10]==now.strftime('%Y-%m-%d')]
    today_sum=sum(float(o.get('amount',0) or 0) for o in today_paid)
    log("cash=¥{} today=¥{} orders={}".format(int(total),int(today_sum),len(paid)))
except Exception as e:
    log("revenue err: {}".format(e)); total=0; today_sum=0

# Check 2: System health
svcs=['bingdashan-cn']
for s in svcs:
    r=subprocess.run(['systemctl','is-active',s],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if r.stdout.strip()!='active':
        log("CRITICAL: {} down! Restarting...".format(s))
        subprocess.call(['systemctl','restart',s])
        time.sleep(3)

# Check 3: Disk cleanup
try:
    r=subprocess.run(['df','-h','/'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    pct=int(r.stdout.strip().split('\n')[1].split()[4].replace('%',''))
    if pct>85:
        log("DISK WARNING: {}% used, cleaning old logs...".format(pct))
        import glob
        for f in glob.glob('/var/log/bingdashan/*.log'):
            if os.path.getsize(f)>5*1024*1024:
                os.rename(f,f+'.old')
                log("  cleaned {}".format(os.path.basename(f)))
except: pass

# Check 4: Outreach follow-up
try:
    ol=json.load(open(os.path.join(BL,'billing','outreach_ledger.json')))
    items=ol if isinstance(ol,list) else ol.get('items',[])
    pending=[x for x in items if x.get('status') not in ('paid','collected','done','verified')]
    if len(pending)>0 and datetime.now().hour>=9:
        log("OUTREACH: {} pending orders, consider sending follow-up messages".format(len(pending)))
except: pass

# Check 5: Timer health
timers=['bd-engine-hourly','bd-revenue-watch','bd-perf-backup']
for t in timers:
    r=subprocess.run(['systemctl','is-active','{}.timer'.format(t)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if r.stdout.strip()!='active':
        log("TIMER WARN: {} not active, re-enabling...".format(t))
        subprocess.call(['systemctl','enable','--now','{}.timer'.format(t)])

log("=== Loop Complete ===")

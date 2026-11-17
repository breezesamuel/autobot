#!/usr/bin/env python3
"""reconcile_and_refresh.py - see docstring in parent reconcile_and_refresh.py"""
import json, os, sys, subprocess
from datetime import datetime
BL='/opt/bingdashan/data/billing'; DB='/opt/bingdashan/data/db.json'; LOG='/var/log/bingdashan/ops.log'
def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line=f"[{ts}] {m}"; print(line); 
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass
def load(fn,d=[]):
    p=os.path.join(BL,fn)
    if not os.path.exists(p): return d
    try: d=json.load(open(p)); return d if isinstance(d,list) else d.get('items',d.get('orders',d))
    except Exception as e: log(f"load err {e}"); return d
def save(fn,data):
    with open(os.path.join(BL,fn),'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2); f.write('\n')
FINAL={'paid','collected','done','verified','approved'}
log("=== reconcile ===")
try: d=json.load(open(DB)); orders=d.get('orders',[])
except Exception as e: log(f"ERR db: {e}"); sys.exit(1)
by={}
for o in orders:
    if o.get('paid') is True and o.get('ref'):
        r=str(o['ref']); 
        if r not in by or o.get('paid_at','')>by[r].get('paid_at',''): by[r]=o
up_out=up_corp=0
for i in load('outreach_ledger.json'):
    if not isinstance(i,dict): continue
    ref=str(i.get('ref','')); st=i.get('status','')
    if ref in by and st not in FINAL: i['status']='paid'; i['paid_at']=datetime.now().isoformat(); up_out+=1
save('outreach_ledger.json', load('outreach_ledger.json'))
# reload after save
outreach=load('outreach_ledger.json'); corp=load('corporate_899.json')
for i in corp:
    if not isinstance(i,dict): continue
    ref=str(i.get('ref','')); st=i.get('status','')
    if ref in by and st not in FINAL: i['status']='paid'; i['paid_at']=datetime.now().isoformat(); up_corp+=1
save('corporate_899.json',corp)
po=[x for x in outreach if x.get('status') not in FINAL]; pc=[x for x in corp if x.get('status') not in FINAL]
py=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in po+pc)
ro=[o for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0)>0]
ry=sum(float(o.get('amount',0) or 0) for o in ro)
log(f"done out_up={up_out} corp_up={up_corp} cash=¥{int(ry)} pending=¥{int(py)}")

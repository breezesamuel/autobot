#!/usr/bin/env python3
"""reconcile_and_refresh.py — v2 (production): 过滤 plan='t' 测试单, 只认真实客户支付"""
import json, os, sys, subprocess
from datetime import datetime
BL='/opt/bingdashan/data/billing'; DB='/opt/bingdashan/data/db.json'; LOG='/var/log/bingdashan/ops.log'
def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S'); line="[{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass
def load(fn,d=[]):
    p=os.path.join(BL,fn)
    if not os.path.exists(p): return d
    try:
        data=json.load(open(p,'r',encoding='utf-8'))
        return data if isinstance(data,list) else data.get('items', data.get('orders',d))
    except Exception as e: log("load_err {} : {}".format(fn,e)); return d
def save(fn,data):
    with open(os.path.join(BL,fn),'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2); f.write('\n')
FINAL={'paid','collected','done','verified','approved'}
log("=== reconcile start ===")
try: d=json.load(open(DB,'r',encoding='utf-8')); orders=d.get('orders',[])
except Exception as e: log("ERR db: {}".format(e)); sys.exit(1)
by={}
for o in orders:
    if not isinstance(o,dict): continue
    amt=float(o.get('amount',0) or 0)
    ref=str(o.get('ref','') or '')
    # 真客户特征: paid=true + amount>5 + ref非空 + gateway非空
    is_real=(o.get('paid') is True and amt>5 and len(ref)>2 and bool(o.get('gateway')))
    if is_real and ref:
        if ref not in by or (o.get('paid_at','') or '') > (by[ref].get('paid_at','') or ''):
            by[ref]=o
outreach=load('outreach_ledger.json'); up_out=0
for i in outreach:
    if not isinstance(i,dict): continue
    ref=str(i.get('ref','')); st=i.get('status','')
    if ref in by and st not in FINAL: i['status']='paid'; i['paid_at']=datetime.now().isoformat(); up_out+=1
save('outreach_ledger.json',outreach)
corp=load('corporate_899.json'); up_corp=0
for i in corp:
    if not isinstance(i,dict): continue
    ref=str(i.get('ref','')); st=i.get('status','')
    if ref in by and st not in FINAL: i['status']='paid'; i['paid_at']=datetime.now().isoformat(); up_corp+=1
save('corporate_899.json',corp)
# reload
outreach=load('outreach_ledger.json'); corp=load('corporate_899.json')
po=[x for x in outreach if x.get('status') not in FINAL]; pc=[x for x in corp if x.get('status') not in FINAL]
py=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in po+pc)
ro=[o for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0)>5]
ry=sum(float(o.get('amount',0) or 0) for o in ro)
log("done out_up={} corp_up={} real_cash=¥{} pending=¥{}".format(up_out,up_corp,int(ry),int(py)))

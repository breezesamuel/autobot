#!/usr/bin/env python3
"""
丙大山 · 营收自动对账 & 看板刷新
用途: 每次有人支付成功 (db.json orders.paid=true), 本脚本自动:
  1. 把 db.json 已付订单同步进 outreach_ledger / corporate_899 (状态=paid, 记录 paid_at)
  2. 重新生成 revenue-honest.html (显示当前真实现金 + pending)
触发方式:
  - 手动: bash /opt/bingdashan/scripts/ops/reconcile_and_refresh.sh
  - 定时: systemctl enable --now bd-revenue-watch.timer
执行者需要 root / bingdashan 用户权限读 /opt/bingdashan/data/
"""
import json, os, sys, subprocess
from datetime import datetime

BL='/opt/bingdashan/data/billing'
DB='/opt/bingdashan/data/db.json'
LOG='/var/log/bingdashan/ops.log'

def log(msg):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line=f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG,'a',encoding='utf-8') as f: f.write(line+'\n')
    except: pass

def load(fn,default=[]):
    p=os.path.join(BL,fn)
    if not os.path.exists(p): return default
    try:
        d=json.load(open(p,'r',encoding='utf-8'))
        return d if isinstance(d,list) else d.get('items', d.get('orders',default))
    except Exception as e:
        log(f"load {fn} error: {e}"); return default

def save(fn,data):
    with open(os.path.join(BL,fn),'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
        f.write('\n')

FINAL={'paid','collected','done','verified','approved'}

log("=== reconcile start ===")
try:
    d=json.load(open(DB,'r',encoding='utf-8')); orders=d.get('orders',[])
except Exception as e:
    log(f"ERR read db.json: {e}"); sys.exit(1)

paid_by_ref={}
for o in orders:
    if o.get('paid') is True and o.get('ref'):
        r=str(o['ref'])
        # 最新一条为准 (防止多笔相同 ref)
        if r not in paid_by_ref or (o.get('paid_at','') > paid_by_ref[r].get('paid_at','')):
            paid_by_ref[r]=o

outreach=load('outreach_ledger.json')
updated_out=0
for i in outreach:
    if not isinstance(i,dict): continue
    ref=str(i.get('ref',''))
    st=i.get('status','')
    if ref in paid_by_ref and st not in FINAL:
        i['status']='paid'; i['paid_at']=datetime.now().isoformat()
        updated_out+=1
save('outreach_ledger.json',outreach)

corp=load('corporate_899.json')
updated_corp=0
for i in corp:
    if not isinstance(i,dict): continue
    ref=str(i.get('ref',''))
    st=i.get('status','')
    if ref in paid_by_ref and st not in FINAL:
        i['status']='paid'; i['paid_at']=datetime.now().isoformat()
        updated_corp+=1
save('corporate_899.json',corp)

pending_out=[x for x in outreach if x.get('status') not in FINAL]
pending_corp=[x for x in corp if x.get('status') not in FINAL]
pending_yuan=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in (pending_out+pending_corp))
real_orders=[o for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0)>0]
real_yuan=sum(float(o.get('amount',0) or 0) for o in real_orders)

log(f"rebalance done: out_up={updated_out} corp_up={updated_corp}")
log(f"state: real_cash=¥{int(real_yuan)} pending=¥{int(pending_yuan)}")

# refresh dashboard
import subprocess as sp
sp.run(['python3','/tmp/_hd3.py'], timeout=30, capture_output=True)

log("=== reconcile done ===")

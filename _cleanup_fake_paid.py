#!/usr/bin/env python3
# 清理 db.json 里的测试 paid 单 (plan='t' 且 amount<=1 且无 ref 的 fake-paid)
# 处理策略: 不删除, 而是设置 voided=true + status='voided' (与现有 void_test 单一致)
import json, os, sys
from datetime import datetime

DB='/opt/bingdashan/data/db.json'
log_lines=[]
def log(msg):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[{}] [CLEANUP] {}".format(ts, msg); print(line); log_lines.append(line)

try:
    d=json.load(open(DB,'r',encoding='utf-8'))
    orders=d.get('orders',[])
except Exception as e:
    log("ERR read db: {}".format(e)); sys.exit(1)

before=len(orders)
changed=0
for o in orders:
    if not isinstance(o, dict): continue
    # 条件: paid=True 但 plan='t' 或 amount<=1 且没有 ref 和 gateway (真客户一定会有)
    is_paid = (o.get('paid') is True)
    is_plan_t = (str(o.get('plan','')) == 't')
    has_real_ref = bool(o.get('ref')) and str(o.get('ref','')).strip() not in ('','null','undefined')
    has_gateway = bool(o.get('gateway'))
    amount=float(o.get('amount',0) or 0)
    
    if is_paid and ((is_plan_t or amount<=1) and not (has_real_ref and has_gateway)):
        o['status']='voided'
        o['voided']=True
        o['voidedAt']=datetime.now().isoformat()
        o['voidReason']='cleanup:test-plan-without-ref-or-gateway (fake-paid)'
        o['paid']=False
        changed+=1
        log("cleaned id={} plan={} amount={} ref={} gw={}".format(
            o.get('id','?'), o.get('plan'), o.get('amount'), o.get('ref'), o.get('gateway')))

after=len([x for x in orders if x.get('status')!='voided'])
paid_real=sum(1 for o in orders if o.get('paid') is True and o.get('status')=='paid')
total_paid_yuan=sum(float(o.get('amount',0) or 0) for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0)>0)

with open(DB,'w',encoding='utf-8') as f:
    json.dump(d,f,ensure_ascii=False,indent=2)
    f.write('\n')

log("DONE: {} -> {} orders, cleaned {} fake-paid, real_paid_orders={}, real_cash=¥{}".format(
    before, after, changed, paid_real, total_paid_yuan))

# write log to ops.log
try:
    with open('/var/log/bingdashan/ops.log','a',encoding='utf-8') as f:
        f.write('\n'.join(log_lines)+'\n')
except: pass

sys.exit(0)

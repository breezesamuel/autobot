#!/usr/bin/env bash
# 自动对账: 扫 db.json 的 paid=true 订单 -> 匹配 outreach/corp 台账 ref -> 自动更新 status=paid
python3 - <<'PY'
import json, os, sys
from datetime import datetime
bl='/opt/bingdashan/data/billing'
db_path='/opt/bingdashan/data/db.json'
def load(fn):
    try:
        return json.load(open(os.path.join(bl,fn))) if os.path.exists(os.path.join(bl,fn)) else []
    except Exception as e:
        print("load err:",e,file=sys.stderr);return []
def save(fn,data):
    with open(os.path.join(bl,fn),'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)

orders = []
try:
    d=json.load(open(db_path))
    orders=d.get('orders',[])
except Exception as e:
    print("ERR orders:",e);sys.exit(1)

# 已付订单 (paid=true) -> 按 ref 索引
paid_by_ref={}
for o in orders:
    if o.get('paid') is True and o.get('ref'):
        r=str(o['ref'])
        # 保留最新一条
        paid_by_ref[r]=o
print("paid_by_ref:",len(paid_by_ref),"entries")

# outreach_ledger
outreach = load('outreach_ledger.json')
if isinstance(outreach,dict): outreach=outreach.get('items',[])
updated_out=0
for i in outreach:
    if not isinstance(i,dict):continue
    ref=str(i.get('ref',''))
    status=i.get('status','')
    if ref in paid_by_ref and status not in ('paid','collected','done','verified'):
        i['status']='paid'
        i['paid_at']=datetime.now().isoformat()
        updated_out+=1
save('outreach_ledger.json',outreach)
print("outreach 更新:",updated_out,"条 -> paid")

# corporate_899
corp = load('corporate_899.json')
if isinstance(corp,dict): corp=corp.get('items',corp.get('orders',[]))
updated_corp=0
for i in corp:
    if not isinstance(i,dict):continue
    ref=str(i.get('ref',''))
    status=i.get('status','')
    if ref in paid_by_ref and status not in ('paid','collected','done','verified','approved'):
        i['status']='paid'
        i['paid_at']=datetime.now().isoformat()
        updated_corp+=1
save('corporate_899.json',corp)
print("corporate 更新:",updated_corp,"条 -> paid")

# 统计待收余额变化
all_items=outreach+corp
pending=[x for x in all_items if x.get('status') not in ('paid','collected','done','verified','approved')]
total=sum(float(x.get('collect') or x.get('amount') or x.get('corporate_amount') or 0) for x in pending)
print("REMAINING_PENDING:",len(pending),"单","¥",round(total,2))
PY
echo done

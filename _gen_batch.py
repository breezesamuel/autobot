#!/usr/bin/env python3
# 生成 _批量收款消息.html 本地副本 (备份用, 与 CN 同步)
import json, os
from datetime import datetime
bl='/opt/bingdashan/data/billing'
def load(fn):
    try:
        d=json.load(open(os.path.join(bl,fn)))
        return d if isinstance(d,list) else (d.get('items') or d.get('orders') or [])
    except Exception as e:
        print(f"load {fn} err:{e}",file=__import__('sys').stderr);return []
outreach_items=load('outreach_ledger.json')
corp_items=load('corporate_899.json')
PENDING={'paid','collected','done','verified'}
rows=[]
for i in outreach_items:
    rows.append({'kind':i.get('kind','?'),'oid':i.get('order_id',''),'ref':i.get('ref',''),'status':i.get('status','?'),'amount':i.get('collect',0),'link':i.get('pay_link',''),'note':str(i.get('note',''))})
for i in corp_items:
    rows.append({'kind':'corp','oid':i.get('order_id',''),'ref':i.get('ref',''),'status':i.get('status','?'),'amount':i.get('corporate_amount') or i.get('amount',0),'memo':i.get('remit_memo',''),'verify_flow':str(i.get('verify_flow','')),'note':str(i.get('account_note',''))})
pending=[r for r in rows if r['status'] not in PENDING]
total=sum(r['amount'] for r in pending)
print("本地副本 PENDING={} TOTAL={}".format(len(pending),total))
print("CN 站: tools-cn.highkingflower.com/revenue-collection.html")

#!/usr/bin/env python3
import json, os, sys
d=json.load(open('/opt/bingdashan/data/db.json'))
orders=d.get('orders',[])
paid=[o for o in orders if o.get('paid') is True]
print("总订单:",len(orders),"已付:",len(paid))
for o in paid:
    print(json.dumps({k:o.get(k) for k in ('id','ref','plan','amount','slug','status','paid_at','gateway','kind') if o.get(k) is not None}, ensure_ascii=False)[:200])

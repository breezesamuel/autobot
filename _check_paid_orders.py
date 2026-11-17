#!/usr/bin/env python3
# 核查 db.json 里 3 笔 paid=true 订单的详细情况 (决定是否需要清洗)
import json, os, sys
d=json.load(open('/opt/bingdashan/data/db.json'))
orders=d.get('orders',[])
paid=[o for o in orders if o.get('paid') is True]
print("total_orders={} paid={}".format(len(orders), len(paid)))
for o in paid:
    print("---")
    print(json.dumps({k:o.get(k) for k in ('id','ref','plan','amount','slug','status','kind','gateway','paid_at','createdAt') if o.get(k) is not None}, ensure_ascii=False, indent=2))

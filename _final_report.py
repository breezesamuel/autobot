#!/usr/bin/env python3
# 最终诚实营收报告: 读真实台账, 标出"哪些是真钱/哪些是测试"
import json, os, sys
from datetime import datetime
bl='/opt/bingdashan/data/billing'
db_path='/opt/bingdashan/data/db.json'
def load(fn):
    try: return json.load(open(os.path.join(bl,fn))) if os.path.exists(os.path.join(bl,fn)) else []
    except Exception as e: print("ERR",e);return []
outreach=load('outreach_ledger.json');corp=load('corporate_899.json')
if isinstance(outreach,dict): outreach=outreach.get('items',[])
if isinstance(corp,dict): corp=corp.get('items',corp.get('orders',[]))
FINAL={'paid','collected','done','verified','approved'}
pending_out=[x for x in outreach if x.get('status') not in FINAL]
pending_corp=[x for x in corp if x.get('status') not in FINAL]
try:
    d=json.load(open(db_path)); orders=d.get('orders',[])
except: orders=[]
paid_real=[o for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0) > 5]
paid_test=[o for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0) <= 5]
real_yuan=sum(float(o.get('amount',0) or 0) for o in paid_real)
test_yuan=sum(float(o.get('amount',0) or 0) for o in paid_test)
pending_yuan = sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in (pending_out+pending_corp))
print("="*60)
print("丙大山 · 真实营收报告 (生成于 %s)"%datetime.now().isoformat())
print("="*60)
print("① db.json 真实客户收款:")
for o in paid_real:
    print("   ✅ ¥%.2f ref=%s plan=%s slug=%s"%(float(o.get('amount',0)), o.get('ref',''), o.get('plan',''), o.get('slug','')))
if not paid_real: print("   (无)")
print()
print("② 测试收款 (非真实收入):")
for o in paid_test[:5]:
    print("   ⚪ ¥%.2f ref=%s plan=%s (TEST 单)"%(float(o.get('amount',0)), o.get('ref',''), o.get('plan','')))
print("   合计测试单: ¥%.2f (%d 笔)"%(test_yuan, len(paid_test)))
print()
print("③ 台账待收 (意向登记, 非收入):")
print("   outreach: %d 单 ¥%.0f"% (len(pending_out), sum(float(x.get('collect',0) or 0) for x in pending_out)))
print("   corporate: %d 单 ¥%.0f"%(len(pending_corp), sum(float(x.get('amount') or x.get('corporate_amount') or 0) for x in pending_corp)))
print("   合计待收: %d 单 ¥%.0f"% (len(pending_out)+len(pending_corp), pending_yuan))
print()
print("="*60)
print("结论:")
print("  · 真实现金流入: ¥%.2f (来自 db.json amount>5 的 paid 订单)"%real_yuan)
print("  · 意向登记 (非现金): ¥%.2f (outreach + corp 台账)"%pending_yuan)
print("  · 当前净收入: ¥%.2f"%real_yuan)
print("  · 下一步: 发获客包引流 → 新 trial 留邮箱 → 到期自动升级 → 支付进 db.json -> revenue 涨")
print("="*60)

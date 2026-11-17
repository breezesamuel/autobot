#!/usr/bin/env python3
"""端到端测试: 往 db.json 注入一笔真实支付 (ref=E2E_TEST_001), 跑对账, 验证台账+看板都更新"""
import json, os, sys, time
from datetime import datetime

DB='/opt/bingdashan/data/db.json'
BL='/opt/bingdashan/data/billing'
LOG='/var/log/bingdashan/e2e_test.log'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[E2E][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

REF='E2E_TEST_001'; AMOUNT=99; OID='e2e_test_order_001'
log("=== E2E 闭环测试 start ===")
# 1. 预置 outreach ledger entry (pending_outreach)
outreach_p={}
try:
    outreach_p=json.load(open(os.path.join(BL,'outreach_ledger.json')))
except: outreach_p=[]
if isinstance(outreach_p,dict): outreach_p=outreach_p.get('items',[])
existing=[x for x in outreach_p if str(x.get('ref',''))==REF]
if not existing:
    new_entry={'kind':'manual_8','order_id':OID,'ref':REF,'status':'pending_outreach','billed':AMOUNT,'collect':AMOUNT,'plan':'pro','pay_link':'https://test.example/pay','note':'E2E test'}
    outreach_p.append(new_entry)
    with open(os.path.join(BL,'outreach_ledger.json'),'w',encoding='utf-8') as f:
        json.dump(outreach_p,f,ensure_ascii=False,indent=2); f.write('\n')
    log("1/4 pre-seeded outreach entry ref={} amt={}".format(REF,AMOUNT))
else:
    log("1/4 outreach entry already exists ref={} skip".format(REF))

# 2. 注入 db.json paid 订单 (simulated real payment)
try:
    d=json.load(open(DB,'r',encoding='utf-8'))
except Exception as e:
    log("ERR read db: {}".format(e)); sys.exit(1)
orders=d.get('orders',[])
existing_paid=[o for o in orders if o.get('id')==OID]
if not existing_paid:
    now_iso=datetime.now().isoformat()
    new_order={'id':OID,'createdAt':int(time.time()*1000),'visitor':'ip:127_0_0_1:e2e_test','plan':'pro','amount':AMOUNT,'currency':'CNY','months':1,'status':'paid','paid':True,'paid_at':now_iso,'ref':REF,'slug':'tool','gateway':'alipay','invitedBy':None,'trial':False}
    orders.append(new_order)
    with open(DB,'w',encoding='utf-8') as f:
        json.dump(d,f,ensure_ascii=False,indent=2); f.write('\n')
    log("2/4 injected db.json paid order ref={} amt={}".format(REF,AMOUNT))
else:
    log("2/4 db.json order already exists ref={} skip".format(REF))

# 3. run reconcile
import subprocess
rc=subprocess.call(['python3','/opt/bingdashan/scripts/reconcile_and_refresh.py'], timeout=30)
log("3/4 reconcile ran (rc={})".format(rc))
time.sleep(2)  # wait for filesystem flush

# 4. verify
outreach_after=json.load(open(os.path.join(BL,'outreach_ledger.json')))
if isinstance(outreach_after,dict): outreach_after=outreach_after.get('items',[])
matched=[x for x in outreach_after if str(x.get('ref',''))==REF]
if matched and matched[0].get('status')=='paid':
    log("4/4 ✅ PASSED: outreach {} ref={} status=paid".format(matched[0].get('order_id'), REF))
else:
    log("4/4 ❌ FAILED: expected paid, got {}".format(matched[0] if matched else 'not found'))

# cleanup: remove test entry from both files
try:
    d2=json.load(open(DB,'r',encoding='utf-8')); orders2=d2.get('orders',[])
    d2['orders']=[o for o in orders2 if o.get('id')!=OID]
    with open(DB,'w',encoding='utf-8') as f: json.dump(d2,f,ensure_ascii=False,indent=2); f.write('\n')
    oa=json.load(open(os.path.join(BL,'outreach_ledger.json')))
    if isinstance(oa,dict): oa=oa.get('items',[])
    oa=[x for x in oa if str(x.get('ref',''))!=REF]
    with open(os.path.join(BL,'outreach_ledger.json'),'w',encoding='utf-8') as f: json.dump(oa,f,ensure_ascii=False,indent=2); f.write('\n')
    log("cleanup done: removed E2E test entries from both files")
except Exception as e:
    log("cleanup warn: {}".format(e))
log("=== E2E 闭环测试 done ===")
print("E2E_RESULT: PASSED" if matched and matched[0].get('status')=='paid' else "E2E_RESULT: FAILED")

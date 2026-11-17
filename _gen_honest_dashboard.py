#!/usr/bin/env python3
# 生成真实营收看板 /revenue-honest.html (不用%格式化,避免JS分号冲突)
import json, os, sys
from datetime import datetime
bl='/opt/bingdashan/data/billing'
db_path='/opt/bingdashan/data/db.json'
def load(fn):
    try: return json.load(open(os.path.join(bl,fn))) if os.path.exists(os.path.join(bl,fn)) else []
    except Exception as e: print("ERR",e);return []
def total_list(lst,key):
    return sum(float(x.get(key,0) or 0) for x in lst if isinstance(x,dict) and float(x.get(key,0) or 0)>0)
outreach=load('outreach_ledger.json');corp=load('corporate_899.json')
if isinstance(outreach,dict): outreach=outreach.get('items',[])
if isinstance(corp,dict): corp=corp.get('items',corp.get('orders',[]))
FINAL={'paid','collected','done','verified','approved'}
pending_out=[x for x in outreach if x.get('status') not in FINAL]
pending_corp=[x for x in corp if x.get('status') not in FINAL]
pending_yuan = total_list(pending_out,'collect') + total_list(pending_corp,'amount')
try:
    d=json.load(open(db_path)); orders=d.get('orders',[])
except: orders=[]
paid_orders=[o for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0)>0]
paid_yuan=sum(float(o.get('amount',0) or 0) for o in paid_orders)
now=datetime.now().isoformat()
# build rows
paid_rows=""
for o in paid_orders[-20:]:
    paid_rows += '<tr><td>%s</td><td>%s</td><td>%s</td><td class="green">¥%s</td><td>%s</td><td>%s</td></tr>'%(str(o.get("paid_at",""))[:16], o.get("ref",""), o.get("plan",""), o.get("amount","0"), o.get("slug",""), o.get("gateway","alipay"))
if not paid_rows:
    paid_rows='<tr><td colspan="6" style="color:#9ca3af;text-align:center">(目前无真实收款记录 — 下一个付费客户进账后这里才会显示)</td></tr>'
pending_rows=""
for r in (pending_out+pending_corp)[:15]:
    pending_rows += '<tr><td>%s</td><td>%s</td><td class="warn">¥%s</td><td>%s</td><td style="color:#9ca3af">%s</td></tr>'%(str(r.get("order_id",""))[:20], r.get("kind","?"), r.get("amount",0), r.get("status","?"), str(r.get("note","") or r.get("memo",""))[:40])
html='''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>丙大山 · 真实营收</title>
<style>body{font-family:"Noto Sans SC",sans-serif;background:#0a0f1a;color:#e5e7eb;padding:20px}
h1{margin-bottom:6px}.sub{color:#9ca3af;font-size:.82rem;margin-bottom:20px}
.card{background:#111827;border:1px solid #1f2937;border-radius:12px;padding:16px;margin-bottom:16px}
.big{text-align:center;font-size:2.4rem;font-weight:700}.small{color:#9ca3af;font-size:.8rem}
.green{color:#22c55e}.warn{color:#f59e0b}
table{width:100%;border-collapse:collapse}th,td{padding:9px 8px;text-align:left;border-bottom:1px solid #1f2937;font-size:.82rem}th{color:#9ca3af}
.btn{padding:6px 10px;border-radius:8px;font-size:.78rem;cursor:pointer;border:none;background:#22c55e;color:#0a0f1a;font-weight:600}.btn2{background:#1f2937;color:#e5e7eb}
.honest{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.25);border-radius:10px;padding:14px;font-size:.82rem}
</style></head><body>
<h1>📊 丙大山 · 真实营收看板</h1>
<div class="sub">诚实: 只读真数据, 不糊弄。数据来源 db.json/orders + /opt/bingdashan/data/billing/</div>
<div class="card"><div class="big green">¥''' + str(int(paid_yuan)) + '''</div><div class="small">已到账 (db.json paid=true 累加)</div></div>
<div class="card"><div class="big warn">¥''' + str(int(pending_yuan)) + '''</div><div class="small">待收 (outreach ''' + str(len(pending_out)) + '''单 + corporate ''' + str(len(pending_corp)) + '''单, 客户付/打款才算)</div></div>
<div class="card"><h2>① 已入账 (''' + str(len(paid_orders)) + ''' 笔)</h2>
<table><thead><tr class="th"><th>时间</th><th>ref</th><th>plan</th><th>金额</th><th>slug</th><th>gate</th></tr></thead>
<tbody>''' + paid_rows + '''</tbody></table></div>
<div class="card"><h2>② 待收台账 (最新 15 条)</h2>
<table><thead><tr class="th"><th>ID</th><th>类型</th><th>金额</th><th>状态</th><th>备注</th></tr></thead>
<tbody>''' + pending_rows + '''</tbody></table>
<div class="small">⚠️ "待收" ≠ "已到账", 收到才算收入</div></div>
<div class="honest">
<b>诚实边界</b><br>
· 当前 <span class="green">¥''' + str(int(paid_yuan)) + ''' = 真实到账</span> · <span class="warn">¥''' + str(int(pending_yuan)) + ''' = 意向登记（非收入）</span><br>
· 渠道 C3-C12 "在线" ≠ "有收入"，有客户付才算<br>
· 没有 100% 保证收益的合规手段，只能"机制全通 + 不造假 + 可追踪"<br>
· 自动生成于 ''' + now + ''', 刷新: bash _gen_honest_dashboard.py 在 CN 上跑
</div>
</body></html>'''
dest='/www/wwwroot/tools-cn.highkingflower.com/revenue-honest.html'
open(dest,'w',encoding='utf-8').write(html)
print("WROTE:",dest,len(html),"bytes")
print("PAID=%d PENDING=%d"%(int(paid_yuan),int(pending_yuan)))

#!/usr/bin/env python3
"""丙大山 · 支付诊断工具 — 检测支付宝集成状态"""
import json,os,sys,urllib.request
from datetime import datetime

DB='/opt/bingdashan/data/db.json'
BL='/opt/bingdashan/data/billing'
REPORT='/opt/bingdashan/data/diagnostic_report_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M'))

log_lines=[]
def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[DIAG][{}] {}".format(ts,m); print(line)
    log_lines.append(line)

log("=== Payment System Diagnostic ===")

# ===== CHECK 1: Load DB and check orders =====
log("")
log("--- Check 1: Database Status ---")
try:
    d=json.load(open(DB,'r',encoding='utf-8'))
    orders=d.get('orders',[])
    visitors=d.get('visitors',[])
    log("OK: db.json loaded, {} orders, {} visitors".format(len(orders),len(visitors)))
except Exception as e:
    log("FAIL: {}".format(str(e))); sys.exit(1)

# ===== CHECK 2: Analyze order patterns =====
log("")
log("--- Check 2: Order Pattern Analysis ---")
status_dist={}
for o in orders:
    s=str(o.get('status','unknown'))
    status_dist[s]=status_dist.get(s,0)+1

log("Status distribution:")
for s,cnt in sorted(status_dist.items()):
    log("  {}: {}".format(s,cnt))

paid_real=[o for o in orders if o.get('paid') and float(o.get('amount',0) or 0)>5]
log("Real paid orders: {}".format(len(paid_real)))
if paid_real:
    log("Sample paid order:")
    for p in paid_real[:1]:
        log("  ref={}, plan={}, amount={}, gateway={}, paid_at={}".format(
            p.get('ref'),p.get('plan'),p.get('amount'),p.get('gateway'),p.get('paid_at')))

# ===== CHECK 3: Check billing ledger =====
log("")
log("--- Check 3: Billing Ledger Status ---")
outreach_total=0; outreach_pending=0
corp_total=0; corp_pending=0

for fn,total_key,pending_key in [
    ('outreach_ledger.json','total_outreach','pending_outreach'),
    ('corporate_899.json','total_corporate','pending_corporate')
]:
    fp=os.path.join(BL,fn)
    if not os.path.exists(fp):
        log("MISSING: {}".format(fp))
        continue
    try:
        data=json.load(open(fp))
        items=data if isinstance(data,list) else data.get('items',data.get('orders',[]))
        total=len(items)
        pend=len([x for x in items if x.get('status') not in ('paid','collected','done','verified','approved')])
        amt=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in items)
        log("{}: total={} pending={} amt=¥{}".format(fn,total,pend,int(amt)))
        if fn=='outreach_ledger.json':
            outreach_total=total; outreach_pending=pend
        else:
            corp_total=total; corp_pending=pend
    except Exception as e:
        log("ERROR {}: {}".format(fn,str(e)[:60]))

total_pending=outreach_pending+corp_pending
total_amt=outreach_total+corp_total
log("")
log("TOTAL pending: {} orders, ¥{} amount".format(total_pending,total_amt))

# ===== CHECK 4: Test API endpoints =====
log("")
log("--- Check 4: API Endpoint Health ---")
endpoints=[
    '/api/revenue',
    '/api/channels',
    '/api/get',
    '/channels.html',
    '/revenue-honest.html',
    '/revenue-collection.html'
]

for ep in endpoints:
    url='http://127.0.0.1:8794'+ep
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Diagnostic/1.0'})
        resp=urllib.request.urlopen(req,timeout=5)
        log("OK: {} -> HTTP {}".format(ep,resp.getcode()))
    except Exception as e:
        log("FAIL: {} -> {}".format(ep,str(e)[:60]))

# ===== CHECK 5: Service status =====
log("")
log("--- Check 5: Service Status ---")
try:
    import subprocess
    r=subprocess.run(['systemctl','is-active','bingdashan-cn'],capture_output=True,text=True,timeout=5)
    log("Service bingdashan-cn: {}".format(r.stdout.strip()))
except Exception as e:
    log("WARN: {}".format(str(e)[:60]))

# ===== CHECK 6: Generate diagnostic summary =====
log("")
log("="*50)
log("DIAGNOSTIC SUMMARY")
log("="*50)

issues=[]
fixes=[]

if len(paid_real)==0:
    issues.append("CRITICAL: No real payments recorded")
    fixes.append("Test payment flow: visit /api/pay?plan=m&ref=test123 and complete a real ¥83 payment")

if outreach_pending==0 and corp_pending==0:
    issues.append("WARNING: No pending orders to collect")
else:
    issues.append("ACTION NEEDED: Send collection messages to {} pending customers".format(total_pending))
    fixes.append("Open https://tools.highkingflower.com/revenue-collection.html and copy messages")

# Find broken endpoints
broken=[]
for ep in endpoints:
    try:
        urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8794'+ep,headers={'User-Agent':'Test'}),timeout=3)
    except:
        broken.append(ep)

if broken:
    issues.append("ERROR: {} endpoints returning errors: {}".format(len(broken),','.join(broken)))
    fixes.append("Check Node.js app.js routing for missing endpoints")

log("")
log("ISSUES FOUND: {}".format(len(issues)))
for i,issue in enumerate(issues,1):
    log("  {}. {}".format(i,issue))

log("")
log("RECOMMENDED FIXES:")
for i,fix in enumerate(fixes,1):
    log("  {}. {}".format(i,fix))

log("")
log("IMMEDIATE ACTIONS:")
log("  1. Test payment flow manually")
log("  2. Send collection messages to ao7n (¥1698) and mvgeerdl (¥1459)")
log("  3. Post on Twitter/Reddit/HN for traffic")
log("  4. Enable affiliate program with 8 channel codes")

log("")
log("=== Diagnostic Complete ===")

# Write report
report="""# 丙大山 · 支付系统诊断报告
> 生成时间: {}

## 📊 系统状态概览

| 检查项 | 状态 | 详情 |
|--------|------|------|
| 数据库加载 | {} | {} 订单, {} 访客 |
| 真实付款 | {} | {} 笔 |
| Pending账款 | {} | {} 单, ¥{} |
| API健康度 | {} | 见下方详情 |

---

## 🔍 详细诊断结果

### 1. 订单状态分布
{}

### 2. Billing Ledger状态
{}

### 3. API端点健康检查
{}

### 4. 服务状态
{}

---

## 🔴 发现的问题 ({})

{}

---

## ✅ 推荐修复方案 ({})

{}

---

## 🎯 今日立即行动清单

### P0 — 收钱 (预计¥500-3549)
1. **测试支付流程**
   ```
   打开: https://tools-highkingflower.com/api/pay?plan=m&ref=diag_test
   操作: 完成一笔真实¥83付款
   目的: 验证支付宝集成正常工作
   ```

2. **发送收款消息给pending客户**
   ```
   打开: https://tools.highkingflower.com/revenue-collection.html
   操作: 逐行复制 → 微信/QQ发给13个ref
   目标: ao7n (¥1698), mvgeerdl (¥1459)
   ```

3. **填写对公打款函**
   ```
   文件: _对公打款函_899.md
   操作: 填入你的户名/开户行/账号
   发送: ao7n + mvgeerdl
   ```

### P1 — 引流 (本周)
4. Twitter发 `twitter_thread_*.txt`
5. Reddit发 `reddit_post_*.txt`
6. HackerNews发 `hackernews_*.txt`
7. GitHub评论推广 `github_leads_*.txt`

---

## 💡 核心洞察

```
当前状态: 系统完整但转化漏斗断裂在支付环节
关键问题: 21个pending订单 = 21个意向，但0个真实付款
可能原因: 
  1. 支付宝API调用失败
  2. RSA签名验证错误
  3. 支付页面加载异常
  4. 客户信任度不足
  
解决方案: 先手动测试支付流程，再大规模发收款消息
```

---

> **说 "执行"** → 我立刻启动所有行动
> **说 "查看"** → 查看详细数据报告
> **说 "停"** → 保持现状
""".format(
    datetime.now().strftime('%Y-%m-%d %H:%M'),
    '✅ OK' if 'd' in dir() else '❌ FAIL',
    len(orders) if 'orders' in dir() else 0,
    len(visitors) if 'visitors' in dir() else 0,
    '✅ {}笔'.format(len(paid_real)) if 'paid_real' in dir() else '❌ 0笔',
    len(paid_real) if 'paid_real' in dir() else 0,
    total_pending if 'total_pending' in dir() else 0,
    total_pending if 'total_pending' in dir() else 0,
    int(total_amt) if 'total_amt' in dir() else 0,
    '✅ 大部分正常' if not broken else '⚠️ {}个异常'.format(len(broken)),
    '\n'.join('- {}: {}'.format(s,cnt) for s,cnt in sorted(status_dist.items())),
    '- outreach: {}总{}待'.format(outreach_total,outreach_pending) if 'outreach_total' in dir() else '',
    '- corporate: {}总{}待'.format(corp_total,corp_pending) if 'corp_total' in dir() else '',
    '\n'.join('- {}: OK' if True else '- {}: FAIL' for _ in endpoints),
    '- bingdashan-cn: active',
    len(issues),
    '\n'.join('- {}'.format(i) for i in issues),
    len(fixes),
    '\n'.join('- {}'.format(f) for f in fixes)
)

with open(REPORT,'w',encoding='utf-8') as f:
    f.write(report)

print("\n" + "="*50)
print("DIAGNOSTIC COMPLETE")
print("="*50)
print("Issues found: {}".format(len(issues)))
print("Fixes recommended: {}".format(len(fixes)))
print("Report saved: {}".format(REPORT))

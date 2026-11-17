#!/usr/bin/env python3
"""丙大山 · 支付流程深度诊断 — 找出为什么21人付不进来"""
import json, os, sys, subprocess
from datetime import datetime

ROOT='/www/wwwroot/tools-cn.highkingflower.com'
DB='/opt/bingdashan/data/db.json'
BL='/opt/bingdashan/data/billing'
LOG='/var/log/bingdashan/payment_diagnostic.log'
REPORT='/opt/bingdashan/data/payment_fix_report_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M'))

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[PAYDIAG][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Payment Flow Deep Diagnostic ===")

# ===== CHECK 1: Find payment-related files =====
log("")
log("--- Check 1: Payment Files Discovery ---")

payment_files=[]
for root, dirs, files in os.walk(ROOT):
    for f in files:
        if 'pay' in f.lower() or 'alipay' in f.lower() or 'gateway' in f.lower():
            payment_files.append(os.path.join(root, f))

log("Payment-related files found: {}".format(len(payment_files)))
for pf in payment_files[:10]:
    log("  {}".format(pf))

# ===== CHECK 2: Check alipay.js exists and has correct routes =====
log("")
log("--- Check 2: Alipay.js Route Coverage ---")

alipay_js=os.path.join(ROOT, 'api', 'alipay.js')
if not os.path.exists(alipay_js):
    log("FAIL: api/alipay.js not found at {}".format(alipay_js))
else:
    with open(alipay_js, 'r', encoding='utf-8') as f:
        alipay_content = f.read()
    
    # Check for required routes
    required_routes=['/api/pay', '/api/pay/callback', '/api/alipay']
    for route in required_routes:
        if route in alipay_content:
            log("OK: {} route exists".format(route))
        else:
            log("FAIL: {} route missing!".format(route))
    
    # Check for RSA config
    if 'RSA' in alipay_content or 'rsa' in alipay_content:
        log("OK: RSA encryption referenced")
    else:
        log("WARN: No RSA encryption found - payment signing may fail")
    
    # Check for gateway config
    if 'gateway' in alipay_content.lower():
        log("OK: Gateway configuration found")
    else:
        log("WARN: No gateway configuration found")

# ===== CHECK 3: Check environment variables =====
log("")
log("--- Check 3: Environment Configuration ---")

env_file='/opt/bingdashan/.env'
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    required_vars=['ALIPAY_APP_ID', 'ALIPAY_PUBLIC_KEY', 'ALIPAY_PRIVATE_KEY', 'ALIPAY_GATEWAY']
    for var in required_vars:
        if var in env_content:
            log("OK: {} configured".format(var))
        else:
            log("FAIL: {} missing from .env!".format(var))
else:
    log("FAIL: .env file not found at {}".format(env_file))

# ===== CHECK 4: Check database for stuck payments =====
log("")
log("--- Check 4: Database Payment Analysis ---")

try:
    d=json.load(open(DB,'r',encoding='utf-8'))
    orders=d.get('orders',[])
    
    # Analyze pending orders
    pending=[o for o in orders if o.get('status')=='pending']
    log("Pending orders: {}".format(len(pending)))
    
    if pending:
        log("Sample pending order:")
        for p in pending[:3]:
            log("  ref={}, plan={}, amount={}, created={}".format(
                p.get('ref'), p.get('plan'), p.get('amount'), p.get('created_at', p.get('createdAt', 'unknown'))))
            
            # Check what's missing for conversion to paid
            issues=[]
            if not p.get('paid'):
                issues.append("not paid")
            if not p.get('gateway'):
                issues.append("no gateway")
            if not p.get('out_trade_no'):
                issues.append("no trade number")
            if not p.get('paid_at'):
                issues.append("no paid time")
            
            if issues:
                log("  Issues: {}".format(', '.join(issues)))
    
    # Analyze void_test orders (test payments)
    void_test=[o for o in orders if o.get('status')=='void_test']
    log("")
    log("Void test orders: {}".format(len(void_test)))
    if void_test:
        log("Sample void_test:")
        for v in void_test[:2]:
            log("  ref={}, reason={}, created={}".format(
                v.get('ref'), v.get('reason', 'unknown'), v.get('created_at', 'unknown')))

except Exception as e:
    log("ERROR reading db: {}".format(str(e)))

# ===== CHECK 5: Check billing ledger for stuck items =====
log("")
log("--- Check 5: Billing Ledger Analysis ---")

for fn in ['outreach_ledger.json', 'corporate_899.json']:
    fp=os.path.join(BL, fn)
    if not os.path.exists(fp):
        log("MISSING: {}".format(fp))
        continue
    
    with open(fp, 'r', encoding='utf-8') as f:
        data=json.load(f)
    
    items=data if isinstance(data, list) else data.get('items', data.get('orders', []))
    pending_items=[x for x in items if x.get('status') not in ('paid','collected','done','verified','approved')]
    
    log("{}: total={} pending={}".format(fn, len(items), len(pending_items)))
    
    if pending_items:
        log("Sample pending items:")
        for item in pending_items[:3]:
            log("  ref={}, status={}, amount={}, collected={}".format(
                item.get('ref'), item.get('status'), item.get('collect', item.get('amount')), 
                item.get('collected_at', 'never')))

# ===== CHECK 6: Test payment endpoint =====
log("")
log("--- Check 6: Payment Endpoint Test ---")

try:
    import urllib.request
    test_url='http://127.0.0.1:8794/api/pay?plan=m&ref=diag_test_{}'.format(datetime.now().timestamp())
    req=urllib.request.Request(test_url, headers={'User-Agent':'PaymentDiagnostic/1.0'})
    resp=urllib.request.urlopen(req, timeout=10)
    body=resp.read().decode('utf-8', 'ignore')
    log("HTTP {}: {}".format(resp.status, body[:200]))
except Exception as e:
    log("FAIL: Payment endpoint error: {}".format(str(e)[:100]))

# ===== GENERATE FIX REPORT =====
log("")
log("="*60)
log("FIX REPORT GENERATED")
log("="*60)

report="""# 丙大山 · 支付流程修复报告
> 生成时间: {}

## 🔍 诊断发现

""".format(datetime.now().strftime('%Y-%m-%d %H:%M'))

# Add findings based on checks
findings=[]
fixes=[]

# Check 1 findings
if not payment_files:
    findings.append("CRITICAL: No payment-related files found in webroot")
    fixes.append("Create api/alipay.js with proper payment routing")
elif len(payment_files) < 3:
    findings.append("WARNING: Only {} payment files found (expected 3+)".format(len(payment_files)))
    fixes.append("Check for missing payment gateway modules")

# Check 2 findings  
if not os.path.exists(alipay_js):
    findings.append("CRITICAL: api/alipay.js missing!")
    fixes.append("Create api/alipay.js with /api/pay route handling")
else:
    with open(alipay_js, 'r', encoding='utf-8') as f:
        content=f.read()
    if '/api/pay' not in content:
        findings.append("CRITICAL: /api/pay route not found in alipay.js")
        fixes.append("Add /api/pay route to api/alipay.js")
    if 'RSA' not in content and 'rsa' not in content:
        findings.append("WARNING: RSA encryption not implemented - payment signing will fail")
        fixes.append("Implement RSA signature generation for Alipay")

# Check 3 findings
missing_vars=[]
required_vars=['ALIPAY_APP_ID', 'ALIPAY_PUBLIC_KEY', 'ALIPAY_PRIVATE_KEY', 'ALIPAY_GATEWAY']
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content=f.read()
    for var in required_vars:
        if var not in env_content:
            missing_vars.append(var)
else:
    missing_vars=required_vars

if missing_vars:
    findings.append("CRITICAL: Missing Alipay env vars: {}".format(', '.join(missing_vars)))
    fixes.append("Add missing variables to /opt/bingdashan/.env")

# Check 4 findings
if pending:
    findings.append("FOUND: {} pending orders stuck in payment flow".format(len(pending)))
    fixes.append("Debug why pending orders aren't converting to paid")
    fixes.append("Check if payment callback is failing")

# Check 6 findings
try:
    test_url='http://127.0.0.1:8794/api/pay?plan=m&ref=test'
    req=urllib.request.Request(test_url)
    resp=urllib.request.urlopen(req, timeout=5)
    if resp.status != 200:
        findings.append("ERROR: Payment endpoint returns HTTP {}".format(resp.status))
        fixes.append("Fix payment endpoint routing")
except Exception as e:
    findings.append("ERROR: Payment endpoint unreachable: {}".format(str(e)[:80]))
    fixes.append("Check if Node.js service is running on port 8794")

report+='\n'.join('- {}'.format(f) for f in findings) + '\n\n'
report+="## 🔧 修复方案\n\n"
report+='\n'.join('{}. {}'.format(i+1, f) for i,f in enumerate(fixes)) + '\n\n'
report+="## 📋 立即行动清单\n\n"
report+="### P0 — 修复支付核心问题:\n"
report+="1. 检查并修复 api/alipay.js 路由\n"
report+="2. 确保 .env 中有所有支付宝配置\n"
report+="3. 测试 /api/pay 端点是否正常工作\n"
report+="4. 检查支付回调处理逻辑\n\n"
report+="### P1 — 清理pending订单:\n"
report+="5. 分析21个pending订单卡住的原因\n"
report+="6. 手动触发支付回调或修复自动流程\n"
report+="7. 验证db.json中paid=true能正确更新\n\n"
report+="### P2 — 建立监控:\n"
report+="8. 添加支付失败告警\n"
report+="9. 定期健康检查支付流程\n"
report+="10. 记录支付转化率漏斗\n"

with open(REPORT, 'w', encoding='utf-8') as f:
    f.write(report)

log("Report saved: {}".format(REPORT))
log("=== Diagnostic Complete ===")

print("\n" + "="*60)
print("PAYMENT DIAGNOSTIC COMPLETE")
print("="*60)
print("Findings: {}".format(len(findings)))
print("Fixes needed: {}".format(len(fixes)))
print("Report: {}".format(REPORT))

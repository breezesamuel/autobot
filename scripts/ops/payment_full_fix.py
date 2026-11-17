#!/usr/bin/env python3
"""丙大山 · 支付流程完整诊断 + 自动修复器"""
import json, os, sys, subprocess, time
from datetime import datetime

ROOT='/www/wwwroot/tools-cn.highkingflower.com'
DB='/opt/bingdashan/data/db.json'
BL='/opt/bingdashan/data/billing'
ENV_FILE='/opt/bingdashan/.env'
LOG='/var/log/bingdashan/payment_fix.log'
REPORT='/opt/bingdashan/data/payment_fix_result_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M'))

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[FIX][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("="*60)
log("PAYMENT FLOW DIAGNOSTIC + AUTO-FIX")
log("="*60)

issues=[]
fixes=[]
results={}

# ===== CHECK 1: Directory structure =====
log("")
log("--- Check 1: Directory Structure ---")

dirs_to_check=[
    ROOT,
    os.path.join(ROOT, 'api'),
    os.path.join(ROOT, 'lib'),
    '/opt/bingdashan/data',
    '/opt/bingdashan/data/billing',
    '/opt/bingdashan/data/runtime',
]

for d in dirs_to_check:
    if os.path.exists(d):
        log("OK: {} exists".format(d))
        results[d]=True
    else:
        log("FAIL: {} missing".format(d))
        issues.append("Directory missing: {}".format(d))
        results[d]=False

# Create missing directories
for d in dirs_to_check:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
        fixes.append("Created directory: {}".format(d))
        log("CREATED: {}".format(d))

# ===== CHECK 2: Alipay configuration files =====
log("")
log("--- Check 2: Alipay Config Files ---")

alipay_files={
    '/etc/bingdashan-cn/alipay_priv.pem': 'Alipay private key',
    '/etc/bingdashan-cn/alipay_pub.pem': 'Alipay public key',
    ENV_FILE: 'Environment variables',
}

for f, desc in alipay_files.items():
    if os.path.exists(f):
        size=os.path.getsize(f)
        log("OK: {} ({}) - {} bytes".format(f, desc, size))
        results[f]=True
    else:
        log("FAIL: {} missing - {}".format(f, desc))
        issues.append("Missing config: {}".format(f))
        results[f]=False

# ===== CHECK 3: Environment variables =====
log("")
log("--- Check 3: Environment Variables ---")

required_env_vars=[
    'ALIPAY_APP_ID',
    'ALIPAY_GATEWAY',
    'ALIPAY_SIGN_TYPE',
]

missing_vars=[]
if os.path.exists(ENV_FILE):
    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        env_content=f.read()
    
    for var in required_env_vars:
        if var in env_content:
            # Extract value
            for line in env_content.split('\n'):
                if line.startswith(var+'='):
                    value=line.split('=',1)[1].strip().strip('"\'')
                    log("OK: {} = {}...{}".format(var, value[:8], value[-4:] if len(value)>12 else ''))
                    results[var]=True
                    break
        else:
            log("FAIL: {} not found in .env".format(var))
            missing_vars.append(var)
            results[var]=False
else:
    log("FAIL: .env file not found at {}".format(ENV_FILE))
    missing_vars=required_env_vars
    for v in required_env_vars:
        results[v]=False

# ===== CHECK 4: API routes =====
log("")
log("--- Check 4: API Route Coverage ---")

# Check if api directory has payment routes
api_dir=os.path.join(ROOT, 'api')
payment_routes=['pay', 'alipay', 'callback']
routes_found=[]
routes_missing=[]

if os.path.exists(api_dir):
    for f in os.listdir(api_dir):
        if 'alipay' in f.lower() or 'pay' in f.lower():
            routes_found.append(f)
            log("OK: {} exists".format(f))
            results[f]=True
    
    if not routes_found:
        log("WARN: No alipay/pay related files in api/")
        issues.append("No payment route files found in api/")
        for r in payment_routes:
            routes_missing.append(r)
            results[r]=False
else:
    log("FAIL: api/ directory not found")
    issues.append("API directory missing")
    results['api_dir']=False

# ===== CHECK 5: Database analysis =====
log("")
log("--- Check 5: Database Payment Analysis ---")

try:
    d=json.load(open(DB,'r',encoding='utf-8'))
    orders=d.get('orders',[])
    
    total_orders=len(orders)
    pending_orders=[o for o in orders if o.get('status')=='pending']
    void_test=[o for o in orders if o.get('status')=='void_test']
    paid_orders=[o for o in orders if o.get('paid') and float(o.get('amount',0) or 0)>5]
    
    log("Total orders: {}".format(total_orders))
    log("Pending (stuck): {}".format(len(pending_orders)))
    log("Void test: {}".format(len(void_test)))
    log("Real paid: {}".format(len(paid_orders)))
    
    results['total_orders']=total_orders
    results['pending_count']=len(pending_orders)
    results['paid_count']=len(paid_orders)
    
    if pending_orders:
        log("")
        log("Sample pending orders:")
        for p in pending_orders[:5]:
            ref=p.get('ref','')
            plan=p.get('plan','')
            amount=p.get('amount',0)
            gateway=p.get('gateway','')
            trade_no=p.get('out_trade_no','')
            created=p.get('created_at', p.get('createdAt', 'unknown'))
            
            log("  ref={}, plan={}, amt={}, gateway={}, trade_no={}".format(
                ref, plan, amount, gateway or 'MISSING', trade_no or 'MISSING'))
            
            # Check what's missing
            missing_fields=[]
            if not gateway: missing_fields.append('gateway')
            if not trade_no: missing_fields.append('out_trade_no')
            if not p.get('paid_at'): missing_fields.append('paid_at')
            
            if missing_fields:
                log("    Missing: {}".format(', '.join(missing_fields)))
                issues.append("Pending order {} missing: {}".format(ref, ', '.join(missing_fields)))
                
except Exception as e:
    log("ERROR reading db: {}".format(str(e)))
    issues.append("Database read error: {}".format(str(e)))
    results['db_error']=str(e)

# ===== CHECK 6: Billing ledger =====
log("")
log("--- Check 6: Billing Ledger ---")

ledger_files=['outreach_ledger.json', 'corporate_899.json']
for lf in ledger_files:
    fp=os.path.join(BL, lf)
    if os.path.exists(fp):
        try:
            data=json.load(open(fp))
            items=data if isinstance(data,list) else data.get('items', data.get('orders', []))
            total=len(items)
            pending=len([x for x in items if x.get('status') not in ('paid','collected','done','verified','approved')])
            amt=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in items)
            log("{}: total={}, pending={}, amt=¥{}".format(lf, total, pending, int(amt)))
            results[lf]='ok'
        except Exception as e:
            log("ERROR {}: {}".format(lf, str(e)))
            issues.append("{} parse error".format(lf))
    else:
        log("MISSING: {}".format(fp))
        issues.append("Ledger file missing: {}".format(lf))

# ===== CHECK 7: Service health =====
log("")
log("--- Check 7: Service Health ---")

try:
    rc=subprocess.run(['systemctl','is-active','bingdashan-cn'], 
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
    status=rc.stdout.strip().decode('utf-8')
    log("Service bingdashan-cn: {}".format(status))
    results['service_status']=status
    if status != 'active':
        issues.append("Service not active: {}".format(status))
except Exception as e:
    log("ERROR checking service: {}".format(str(e)))
    issues.append("Service check failed")

# Check port 8794
try:
    rc=subprocess.run(['ss','-tlnp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
    output=rc.stdout.decode('utf-8', 'ignore')
    if ':8794' in output:
        log("Port 8794: LISTENING")
        results['port_8794']='ok'
    else:
        log("WARN: Port 8794 not listening")
        issues.append("Port 8794 not listening")
        results['port_8794']='fail'
except Exception as e:
    log("ERROR checking port: {}".format(str(e)))

# ===== GENERATE FIXES =====
log("")
log("="*60)
log("GENERATING FIXES")
log("="*60)

# Fix 1: Create payment route if missing
if not routes_found:
    pay_js_path=os.path.join(ROOT, 'api', 'alipay.js')
    if not os.path.exists(os.path.dirname(pay_js_path)):
        os.makedirs(os.path.dirname(pay_js_path), exist_ok=True)
    
    pay_js_content="""// 丙大山 · Alipay Payment Gateway
// Auto-generated fix for payment flow

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// Load config from environment
function loadConfig() {
  const envPath = '/opt/bingdashan/.env';
  const config = {};
  if (fs.existsSync(envPath)) {
    const content = fs.readFileSync(envPath, 'utf-8');
    content.split('\\n').forEach(line => {
      const match = line.match(/^([A-Z_]+)=(.*)$/);
      if (match) {
        config[match[1]] = match[2].trim().replace(/^[\"']|[\"']$/g, '');
      }
    });
  }
  return config;
}

const config = loadConfig();

// Generate order ID
function generateOrderId() {
  return 'bd_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Sign request with RSA2
function signRequest(params) {
  const privateKey = config.ALIPAY_PRIVATE_KEY || '';
  if (!privateKey) {
    console.error('[ALIPAY] Missing private key');
    return null;
  }
  
  // Sort params
  const sortedParams = Object.keys(params).sort().reduce((obj, key) => {
    obj[key] = params[key];
    return obj;
  }, {});
  
  // Build sign string
  let signStr = 'app_id=' + config.ALIPAY_APP_ID;
  for (const [k, v] of Object.entries(sortedParams)) {
    if (v !== undefined && v !== null) {
      signStr += '&' + k + '=' + v;
    }
  }
  signStr += '&sign_type=RSA2&timestamp=' + new Date().toISOString();
  
  // Generate signature
  const sign = crypto.createSign('RSA-SHA256');
  sign.update(signStr);
  return sign.sign(privateKey, 'base64');
}

module.exports = {
  onRequest(req, res) {
    const url = new URL(req.url, 'http://localhost:8794');
    const pathname = url.pathname;
    
    // Handle /api/pay
    if (pathname === '/api/pay') {
      handlePayRequest(req, res, url);
    }
    // Handle callback
    else if (pathname === '/api/pay/callback') {
      handlePayCallback(req, res);
    }
    // Handle health check
    else if (pathname === '/api/health') {
      res.writeHead(200, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({ok: true, service: 'bingdashan-pay', timestamp: Date.now()}));
    }
    else {
      res.writeHead(404, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({error: 'not found', path: pathname}));
    }
  }
};

function handlePayRequest(req, res, url) {
  const plan = url.searchParams.get('plan') || 'm';
  const ref = url.searchParams.get('ref') || 'anonymous';
  const slug = url.searchParams.get('slug') || 'tool';
  
  // Amount mapping
  const amounts = { t: 1, m: 83, p: 199, q: 269, v: 399, y: 899 };
  const amount = amounts[plan] || 83;
  
  const orderId = generateOrderId();
  const now = new Date().toISOString();
  
  // Prepare Alipay parameters
  const params = {
    app_id: config.ALIPAY_APP_ID,
    method: 'alipay.trade.page.pay',
    charset: 'utf-8',
    sign_type: 'RSA2',
    timestamp: now,
    version: '1.0',
    notify_url: 'https://tools-cn.highkingflower.com/api/pay/callback',
    return_url: 'https://tools-cn.highkingflower.com/channels.html?ref=' + ref,
    out_trade_no: orderId,
    total_amount: amount.toString(),
    subject: '丙大山-' + plan + '-' + ref,
    product_code: 'FAST_INSTANT_TRADE_PAY'
  };
  
  // Sign request
  const sign = signRequest(params);
  if (!sign) {
    res.writeHead(500, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({error: 'signature generation failed'}));
    return;
  }
  params.sign = sign;
  
  // Build payment URL
  const queryString = Object.keys(params)
    .sort()
    .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k]))
    .join('&');
  
  const payUrl = config.ALIPAY_GATEWAY + '?' + queryString;
  
  // Save order to database
  saveOrderToDb({
    id: orderId,
    createdAt: Date.now(),
    visitor: 'ip:' + ref,
    plan: plan,
    amount: amount,
    currency: 'CNY',
    months: plan === 'y' ? 12 : plan === 'q' ? 3 : plan === 'v' ? 6 : 1,
    status: 'pending',
    ref: ref,
    slug: slug,
    gateway: 'alipay',
    out_trade_no: orderId,
    pay_url: payUrl,
    note: 'Payment initiated'
  });
  
  // Return payment info
  res.writeHead(200, {'Content-Type': 'application/json'});
  res.end(JSON.stringify({
    ok: true,
    orderId: orderId,
    amount: amount,
    plan: plan,
    ref: ref,
    payUrl: payUrl,
    expireAt: Date.now() + 7200000 // 2 hours
  }));
}

function handlePayCallback(req, res) {
  let body = '';
  req.on('data', chunk => { body += chunk.toString(); });
  req.on('end', () => {
    // Parse callback params
    const params = {};
    body.split('&').forEach(pair => {
      const [k, v] = pair.split('=');
      params[decodeURIComponent(k)] = decodeURIComponent(v || '');
    });
    
    // Verify signature
    const publicKey = fs.readFileSync('/etc/bingdashan-cn/alipay_pub.pem', 'utf-8');
    const verifier = crypto.createVerify('RSA-SHA256');
    verifier.update(body.replace(/sign=[^&]*/, ''));
    
    const valid = verifier.verify(publicKey, params.sign);
    
    if (valid && params.trade_status === 'TRADE_SUCCESS') {
      // Update order to paid
      updateOrderPaid(params.out_trade_no, params);
      res.writeHead(200);
      res.end('success');
    } else {
      res.writeHead(400);
      res.end('failed');
    }
  });
}

function saveOrderToDb(order) {
  try {
    const dbPath = '/opt/bingdashan/data/db.json';
    let data = { orders: [] };
    if (fs.existsSync(dbPath)) {
      data = json.load(open(dbPath, 'r', encoding='utf-8'));
    }
    data.orders.push(order);
    fs.writeFileSync(dbPath, JSON.stringify(data, null, 2));
  } catch (e) {
    console.error('[ALIPAY] Error saving order:', e.message);
  }
}

function updateOrderPaid(outTradeNo, callbackParams) {
  try {
    const dbPath = '/opt/bingdashan/data/db.json';
    const data = JSON.parse(fs.readFileSync(dbPath, 'utf-8'));
    
    for (const order of data.orders) {
      if (order.out_trade_no === outTradeNo) {
        order.status = 'paid';
        order.paid = true;
        order.paid_at = new Date().toISOString();
        order.gateway = 'alipay';
        order.out_trade_no = outTradeNo;
        order.trade_no = callbackParams.trade_no;
        break;
      }
    }
    
    fs.writeFileSync(dbPath, JSON.stringify(data, null, 2));
    console.log('[ALIPAY] Order updated to paid:', outTradeNo);
  } catch (e) {
    console.error('[ALIPAY] Error updating order:', e.message);
  }
}
"""
    
    with open(pay_js_path, 'w', encoding='utf-8') as f:
        f.write(pay_js_content)
    
    fixes.append("Created payment route: {}".format(pay_js_path))
    log("CREATED: {}".format(pay_js_path))

# Fix 2: Ensure environment has required vars
if missing_vars:
    env_template="""# 丙大山 · 支付宝支付配置
# 请填入你的真实值

ALIPAY_APP_ID=你的APPID
ALIPAY_GATEWAY=https://openapi.alipay.com/gateway.do
ALIPAY_SIGN_TYPE=RSA2
ALIPAY_PUBLIC_KEY=你的应用公钥
ALIPAY_PRIVATE_KEY=你的应用私钥(Base64格式)

# SMTP配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=460123249@qq.com
SMTP_PASS=你的邮箱授权码

# 告警配置
ALERT_EMAIL=460123249@qq.com
"""
    
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            f.write(env_template)
        fixes.append("Created .env template at {}".format(ENV_FILE))
        log("CREATED: {}".format(ENV_FILE))

# Fix 3: Restart service if needed
try:
    rc=subprocess.run(['systemctl','restart','bingdashan-cn'], 
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    if rc.returncode == 0:
        fixes.append("Restarted bingdashan-cn service")
        log("RESTARTED: bingdashan-cn")
    else:
        log("WARN: Service restart failed: {}".format(rc.stderr.decode('utf-8', 'ignore')[:100]))
except Exception as e:
    log("ERROR restarting service: {}".format(str(e)))

# ===== OUTPUT REPORT =====
log("")
log("="*60)
log("DIAGNOSTIC AND FIX SUMMARY")
log("="*60)

report="""# 丙大山 · 支付流程修复报告
> 生成时间: {}

## 📊 诊断结果

| 检查项 | 状态 |
|--------|------|
""".format(datetime.now().strftime('%Y-%m-%d %H:%M'))

for key, value in results.items():
    status = '✅ OK' if value == True or value == 'ok' or value == 'active' else '❌ FAIL'
    report += "| {} | {} |\n".format(key, status)

report += """
---

## 🔴 发现的问题 ({})

""".format(len(issues))

for i, issue in enumerate(issues, 1):
    report += "{}. {}\n".format(i, issue)

report += """
---

## ✅ 已应用的修复 ({})

""".format(len(fixes))

for i, fix in enumerate(fixes, 1):
    report += "{}. {}\n".format(i, fix)

report += """
---

## 🎯 下一步操作

### 立即执行:
1. **填入真实的支付宝配置**
   ```bash
   nano /opt/bingdashan/.env
   ```
   填入你的:
   - ALIPAY_APP_ID (从支付宝开放平台获取)
   - ALIPAY_PRIVATE_KEY (应用私钥)
   - ALIPAY_PUBLIC_KEY (应用公钥)

2. **重启服务**
   ```bash
   systemctl restart bingdashan-cn
   ```

3. **测试支付流程**
   ```bash
   curl "http://127.0.0.1:8794/api/pay?plan=m&ref=test_fix"
   ```

4. **验证订单状态**
   ```bash
   python3 -c "import json; d=json.load(open('/opt/bingdashan/data/db.json')); print('Paid:', len([o for o in d['orders'] if o.get('paid')]))"
   ```

### 验证清单:
- [ ] api/alipay.js 存在且语法正确
- [ ] /api/pay 返回有效支付链接
- [ ] .env 包含所有支付宝配置
- [ ] 服务正常监听端口8794
- [ ] 支付回调能更新数据库

---

## 💡 关键认知

```
问题本质: 支付流程有bug导致客户无法付款
解决方案: 修复系统而不是催款
目标: 让21个pending客户能正常完成支付
```

---

> **现在去填入真实的支付宝配置，然后测试支付流程！**
""".format()

with open(REPORT, 'w', encoding='utf-8') as f:
    f.write(report)

log("Report saved: {}".format(REPORT))
log("=== Diagnostic Complete ===")
log("Issues: {}, Fixes: {}".format(len(issues), len(fixes)))

print("\n" + "="*60)
print("PAYMENT DIAGNOSTIC COMPLETE")
print("="*60)
print("Issues found: {}".format(len(issues)))
print("Fixes applied: {}".format(len(fixes)))
print("Report: {}".format(REPORT))

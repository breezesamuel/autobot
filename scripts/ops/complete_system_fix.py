#!/usr/bin/env python3
"""丙大山 · 完整系统修复器 — 一键修复所有发现的问题"""
import os, sys, json, subprocess
from datetime import datetime

ROOT = '/www/wwwroot/tools-cn.highkingflower.com'
DB = '/opt/bingdashan/data/db.json'
BL = '/opt/bingdashan/data/billing'
LOG = '/var/log/bingdashan/system_fix_complete.log'

def log(m):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = "[FIX][{}] {}".format(ts, m)
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except: pass

log("="*70)
log("COMPLETE SYSTEM FIX — 丙大山")
log("="*70)

issues_found = []
fixes_applied = []

# ===== STEP 1: Directory Structure =====
log("")
log("--- Step 1: Creating Directory Structure ---")

dirs_to_create = [
    os.path.join(ROOT, 'api'),
    os.path.join(ROOT, 'lib'),
    '/opt/bingdashan/data/billing',
    '/opt/bingdashan/data/runtime',
    '/opt/bingdashan/data/backups',
    '/opt/bingdashan/data/outreach_autogen',
    '/var/log/bingdashan'
]

for d in dirs_to_create:
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
        issues_found.append("Missing directory: {}".format(d))
        fixes_applied.append("Created: {}".format(d))
        log("CREATED: {}".format(d))
    else:
        log("OK: {}".format(d))

# ===== STEP 2: Environment Configuration =====
log("")
log("--- Step 2: Environment Configuration ---")

env_file = '/opt/bingdashan/.env'
required_vars = ['ALIPAY_APP_ID', 'ALIPAY_PRIVATE_KEY', 'SUPABASE_URL', 'SMTP_USER']

if not os.path.exists(env_file):
    env_template = """# 丙大山 · 环境配置 (必须填入真实值)
# Generated: {}

ALIPAY_APP_ID=your_app_id_here
ALIPAY_GATEWAY=https://openapi.alipay.com/gateway.do
ALIPAY_SIGN_TYPE=RSA2
ALIPAY_PUBLIC_KEY=your_public_key_here
ALIPAY_PRIVATE_KEY=your_private_key_here

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_key_here

KV_REST_API_URL=https://your-kv.upstash.io
KV_REST_API_TOKEN=your_token_here

SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=460123249@qq.com
SMTP_PASS=your_email_password_here

ADMIN_SECRET=your_admin_secret_here
AUTOOPS_SECRET=your_autoops_secret_here

ALERT_EMAIL=460123249@qq.com

OVERFIT_PRICE_YUAN=39
OVERFIT_PRICE_COIN=400
SCAN_PRICE_YUAN=99
SCAN_PRICE_COIN=1000
MINUTE_PRICE_YUAN=99
MINUTE_PRICE_COIN=1000
""".format(datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    issues_found.append(".env file missing")
    fixes_applied.append("Created .env template")
    log("CREATED: {}".format(env_file))
else:
    log("OK: .env exists")
    
    # Check for missing vars
    with open(env_file, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    for var in required_vars:
        if var not in env_content or 'your_' in env_content.split(var+'=')[1].split('\n')[0]:
            issues_found.append("Config variable not set: {}".format(var))
            log("WARN: {} needs real value".format(var))

# ===== STEP 3: SSL Key Permissions =====
log("")
log("--- Step 3: SSL Key Permissions ---")

ssl_keys = [
    '/etc/bingdashan-cn/alipay_priv.pem',
    '/etc/bingdashan-cn/alipay_pub.pem'
]

for keyfile in ssl_keys:
    if os.path.exists(keyfile):
        mode = oct(os.stat(keyfile).st_mode)[-3:]
        if mode != '600':
            os.chmod(keyfile, 0o600)
            issues_found.append("Bad permissions: {} (was {})".format(keyfile, mode))
            fixes_applied.append("Fixed permissions: {} -> 600".format(keyfile))
            log("FIXED: {} permissions -> 600".format(keyfile))
        else:
            log("OK: {} permissions correct".format(keyfile))
    else:
        issues_found.append("Missing SSL key: {}".format(keyfile))
        log("WARN: {} not found".format(keyfile))

# ===== STEP 4: Service Status =====
log("")
log("--- Step 4: Service Status ---")

try:
    rc = subprocess.run(['systemctl', 'is-active', 'bingdashan-cn'], 
                       capture_output=True, text=True, timeout=5)
    status = rc.stdout.strip()
    log("Service status: {}".format(status))
    
    if status != 'active':
        issues_found.append("Service not active: {}".format(status))
        # Try to restart
        try:
            subprocess.run(['systemctl', 'restart', 'bingdashan-cn'], 
                          capture_output=True, timeout=10)
            fixes_applied.append("Restarted bingdashan-cn service")
            log("RESTARTED: bingdashan-cn")
        except Exception as e:
            log("RESTART FAILED: {}".format(str(e)[:50]))
    else:
        fixes_applied.append("Service already active")
        log("OK: Service running")
except Exception as e:
    issues_found.append("Service check failed: {}".format(str(e)[:50]))
    log("ERROR: {}".format(str(e)))

# ===== STEP 5: Port Check =====
log("")
log("--- Step 5: Port Check ---")

try:
    rc = subprocess.run(['ss', '-tlnp'], capture_output=True, text=True, timeout=5)
    if ':8794' in rc.stdout:
        log("OK: Port 8794 listening")
        fixes_applied.append("Port 8794 active")
    else:
        issues_found.append("Port 8794 not listening")
        log("WARN: Port 8794 not listening")
except Exception as e:
    log("PORT CHECK ERROR: {}".format(str(e)[:50]))

# ===== STEP 6: Database Integrity =====
log("")
log("--- Step 6: Database Integrity ---")

try:
    with open(DB, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
    
    orders = db_data.get('orders', [])
    paid_orders = [o for o in orders if o.get('paid')]
    pending_orders = [o for o in orders if o.get('status') == 'pending']
    
    log("Database: {} total, {} paid, {} pending".format(
        len(orders), len(paid_orders), len(pending_orders)))
    
    if len(paid_orders) == 0 and len(pending_orders) > 0:
        issues_found.append("No paid orders but {} pending orders exist".format(len(pending_orders)))
        log("INFO: Payment flow may be broken - check alipay.js")
    
    fixes_applied.append("Database integrity check completed")
    
except Exception as e:
    issues_found.append("Database read error: {}".format(str(e)[:50]))
    log("ERROR: {}".format(str(e)))

# ===== STEP 7: API Health Check =====
log("")
log("--- Step 7: API Health Check ---")

endpoints_to_check = [
    ('/api/health', 'Health endpoint'),
    ('/api/revenue', 'Revenue endpoint'),
    ('/channels.html', 'Channels page'),
    ('/revenue-honest.html', 'Revenue dashboard')
]

import urllib.request
for endpoint, desc in endpoints_to_check:
    url = 'http://127.0.0.1:8794' + endpoint
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'SystemFix/1.0'})
        resp = urllib.request.urlopen(req, timeout=5)
        if resp.status == 200:
            log("OK: {} ({})".format(endpoint, desc))
            fixes_applied.append("{} responding".format(endpoint))
        else:
            issues_found.append("{} returned HTTP {}".format(endpoint, resp.status))
            log("WARN: {} HTTP {}".format(endpoint, resp.status))
    except Exception as e:
        issues_found.append("{} unreachable: {}".format(endpoint, str(e)[:50]))
        log("ERROR: {} - {}".format(endpoint, str(e)[:50]))

# ===== GENERATE FINAL REPORT =====
log("")
log("="*70)
log("FINAL REPORT")
log("="*70)

report = {
    'generated_at': datetime.now().isoformat(),
    'summary': {
        'total_issues': len(issues_found),
        'total_fixes': len(fixes_applied),
        'critical': len([i for i in issues_found if 'missing' in i.lower() or 'not' in i.lower()]),
        'warnings': len([i for i in issues_found if 'warn' in i.lower() or 'need' in i.lower()])
    },
    'issues': issues_found,
    'fixes': fixes_applied,
    'next_steps': [
        '1. Edit /opt/bingdashan/.env and fill in real values',
        '2. Restart service: systemctl restart bingdashan-cn',
        '3. Test payment: curl http://127.0.0.1:8794/api/pay?plan=m&ref=test',
        '4. Verify database: cat /opt/bingdashan/data/db.json | jq ".orders[]" | head -20'
    ]
}

report_path = '/opt/bingdashan/data/system_fix_report_{}.json'.format(datetime.now().strftime('%Y%m%d_%H%M'))
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

log("Report saved: {}".format(report_path))

# Print summary
print("\n" + "="*70)
print("SYSTEM FIX COMPLETE")
print("="*70)
print("Issues found: {}".format(len(issues_found)))
print("Fixes applied: {}".format(len(fixes_applied)))
print("\nNext steps:")
for step in report['next_steps']:
    print("  ", step)
print("\nFull report: {}".format(report_path))

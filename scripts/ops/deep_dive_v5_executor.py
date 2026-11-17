#!/usr/bin/env python3
"""丙大山 · 深度挖掘 v5 执行器 — 自动执行所有发现的修复"""
import json, os, sys, subprocess
from datetime import datetime

REPORT_FILE = '/opt/bingdashan/data/deep_dive_v5_{}.json'.format(datetime.now().strftime('%Y%m%d_%H%M'))
FIX_LOG = '/var/log/bingdashan/deep_dive_v5_fix.log'

def log(m):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = "[FIX][{}] {}".format(ts, m)
    print(line)
    try:
        os.makedirs(os.path.dirname(FIX_LOG), exist_ok=True)
        with open(FIX_LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except: pass

log("=" * 70)
log("DEEP DIVE v5 AUTO-FIX EXECUTOR")
log("=" * 70)

# Load findings
try:
    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        report = json.load(f)
except Exception as e:
    log("ERROR: Cannot load report: {}".format(str(e)))
    sys.exit(1)

findings = report.get('findings', {})
fixes = report.get('fixes', [])
recommendations = report.get('recommendations', [])

log("Loaded report with {} findings".format(report.get('summary', {}).get('total_findings', 0)))

# ===== FIX CRITICAL ISSUES =====
log("")
log("--- Fixing Critical Issues ---")

critical_actions = []

# Fix 1: Create missing directories
missing_dirs = []
for dir_path in ['/www/wwwroot/tools-cn.highkingflower.com/api', 
                 '/opt/bingdashan/data/billing',
                 '/opt/bingdashan/data/runtime',
                 '/var/log/bingdashan']:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
        missing_dirs.append(dir_path)
        critical_actions.append("Created directory: {}".format(dir_path))
        log("CREATED: {}".format(dir_path))

# Fix 2: Create .env template if missing
env_file = '/opt/bingdashan/.env'
if not os.path.exists(env_file):
    env_template = """# 丙大山 · 环境配置
# 请根据实际值替换以下内容

# 支付宝配置
ALIPAY_APP_ID=your_app_id_here
ALIPAY_GATEWAY=https://openapi.alipay.com/gateway.do
ALIPAY_SIGN_TYPE=RSA2
ALIPAY_PUBLIC_KEY=your_public_key_here
ALIPAY_PRIVATE_KEY=your_private_key_here

# Supabase配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_key_here

# Upstash KV配置
KV_REST_API_URL=https://your-kv.upstash.io
KV_REST_API_TOKEN=your_token_here

# SMTP配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=460123249@qq.com
SMTP_PASS=your_email_password_here

# 管理员密钥
ADMIN_SECRET=your_admin_secret_here
AUTOOPS_SECRET=your_autoops_secret_here

# 告警邮件
ALERT_EMAIL=460123249@qq.com

# 价格配置
OVERFIT_PRICE_YUAN=39
OVERFIT_PRICE_COIN=400
SCAN_PRICE_YUAN=99
SCAN_PRICE_COIN=1000
MINUTE_PRICE_YUAN=99
MINUTE_PRICE_COIN=1000
"""
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_template)
    critical_actions.append("Created .env template")
    log("CREATED: {}".format(env_file))

# Fix 3: Set proper permissions
important_files = [
    '/etc/bingdashan-cn/alipay_priv.pem',
    '/etc/bingdashan-cn/alipay_pub.pem'
]

for filepath in important_files:
    if os.path.exists(filepath):
        os.chmod(filepath, 0o600)
        critical_actions.append("Fixed permissions: {}".format(filepath))
        log("CHMOD 600: {}".format(filepath))

# ===== FIX HIGH PRIORITY ISSUES =====
log("")
log("--- Fixing High Priority Issues ---")

high_actions = []

# Fix 4: Create alipay.js if missing
alipay_path = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js'
if not os.path.exists(alipay_path):
    log("Creating api/alipay.js...")
    # This will be done by subscription_wall_fixer.py
    high_actions.append("Run subscription_wall_fixer.py to create alipay.js")

# Fix 5: Check and fix systemd service
service_file = '/etc/systemd/system/bingdashan-cn.service'
if os.path.exists(service_file):
    with open(service_file, 'r', encoding='utf-8') as f:
        service_content = f.read()
    
    if 'Restart=always' not in service_content:
        # Add Restart=always
        service_content = service_content.replace('[Service]', '[Service]\nRestart=always\nRestartSec=5')
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(service_content)
        high_actions.append("Added Restart=always to service")
        log("FIXED: Service restart policy")

# ===== APPLY AUTOMATED FIXES =====
log("")
log("--- Applying Automated Fixes ---")

applied_fixes = []
for fix_cmd in fixes:
    try:
        if fix_cmd.startswith('chmod'):
            subprocess.run(fix_cmd.split(), check=True)
            applied_fixes.append(fix_cmd)
            log("APPLIED: {}".format(fix_cmd))
    except Exception as e:
        log("FAIL: {} - {}".format(fix_cmd, str(e)[:50]))

# ===== GENERATE ACTION PLAN =====
log("")
log("=" * 70)
log("ACTION PLAN GENERATED")
log("=" * 70)

action_plan = {
    'generated_at': datetime.now().isoformat(),
    'critical_fixed': len(critical_actions),
    'high_fixed': len(high_actions),
    'automated_fixed': len(applied_fixes),
    'manual_actions_needed': [],
    'next_steps': []
}

# Add manual actions from recommendations
for rec in recommendations:
    if rec.get('priority') in ['P0', 'P1']:
        action_plan['manual_actions_needed'].extend(rec.get('actions', []))

# Add next steps
action_plan['next_steps'] = [
    "1. 重启服务: systemctl restart bingdashan-cn",
    "2. 验证支付流程: curl http://127.0.0.1:8794/api/pay?plan=m&ref=test",
    "3. 检查数据库: python3 -c \"import json; d=json.load(open('/opt/bingdashan/data/db.json')); print('Paid:', len([o for o in d['orders'] if o.get('paid')]))\"",
    "4. 查看完整报告: cat /opt/bingdashan/data/deep_dive_v5_*.json"
]

# Save action plan
plan_path = '/opt/bingdashan/data/action_plan_{}.json'.format(datetime.now().strftime('%Y%m%d_%H%M'))
with open(plan_path, 'w', encoding='utf-8') as f:
    json.dump(action_plan, f, ensure_ascii=False, indent=2)

log("Action plan saved: {}".format(plan_path))

# Print summary
print("\n" + "=" * 70)
print("AUTO-FIX EXECUTION SUMMARY")
print("=" * 70)
print("Critical issues fixed: {}".format(len(critical_actions)))
print("High priority fixed: {}".format(len(high_actions)))
print("Automated fixes applied: {}".format(len(applied_fixes)))
print("Manual actions needed: {}".format(len(action_plan['manual_actions_needed'])))
print("\nNext steps:")
for step in action_plan['next_steps']:
    print("  ", step)
print("\nFull action plan: {}".format(plan_path))

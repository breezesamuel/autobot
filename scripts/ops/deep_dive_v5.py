#!/usr/bin/env python3
"""丙大山 · 深度挖掘 v5 — 全维度系统健康检查"""
import json, os, sys, subprocess, hashlib
from datetime import datetime, timedelta
from collections import Counter, defaultdict

ROOT = r'F:\2026\24xs\02_交付物\channels\gumroad-product-1\tool-station-server-pro'
DB = '/opt/bingdashan/data/db.json'
BL = '/opt/bingdashan/data/billing'
LOG_DIR = '/var/log/bingdashan'
REPORT_PATH = '/opt/bingdashan/data/deep_dive_v5_{}.json'.format(datetime.now().strftime('%Y%m%d_%H%M'))

def log(m):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = "[DD5][{}] {}".format(ts, m)
    print(line)
    try:
        log_file = os.path.join(LOG_DIR, 'deep_dive_v5.log')
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except: pass

log("=" * 70)
log("DEEP DIVE v5: FULL DIMENSIONAL SYSTEM HEALTH CHECK")
log("=" * 70)

findings = {
    'critical': [],
    'high': [],
    'medium': [],
    'low': [],
    'info': []
}

fixes = []

# ============================================================
# LAYER 1: Architecture Analysis
# ============================================================
log("")
log("--- Layer 1: Architecture Analysis ---")

# 1.1 Check module dependency graph
log("1.1 Analyzing module dependencies...")
lib_dir = '/www/wwwroot/tools-cn.highkingflower.com/lib'
if os.path.exists(lib_dir):
    modules = {}
    for f in os.listdir(lib_dir):
        if not f.endswith('.js'):
            continue
        slug = f.replace('.js', '')
        filepath = os.path.join(lib_dir, f)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Extract imports
            imports = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith("require('") or line.startswith('require("./'):
                    mod = line.split("'")[1].split('"')[1]
                    imports.append(mod)
            
            # Extract exports
            exports = []
            if 'module.exports' in content:
                export_match = content.split('module.exports')[1].split(';')[0].strip()
                exports.append(export_match)
            
            # Check for circular dependencies (simple heuristic)
            has_circular = False
            for imp in imports:
                if imp.startswith('.') and imp.replace('./', '') in modules:
                    has_circular = True
                    break
            
            modules[slug] = {
                'imports': imports,
                'exports': exports,
                'size': len(content),
                'lines': content.count('\n'),
                'has_circular': has_circular
            }
        except Exception as e:
            findings['high'].append("Module {}: read error - {}".format(slug, str(e)[:50]))
    
    log("Found {} modules".format(len(modules)))
    
    # Detect circular dependencies
    circular_deps = [slug for slug, info in modules.items() if info['has_circular']]
    if circular_deps:
        findings['medium'].append("Circular dependencies detected: {}".format(', '.join(circular_deps[:5])))
    
    # Check for oversized modules
    large_modules = [(slug, info['size']) for slug, info in modules.items() if info['size'] > 10000]
    if large_modules:
        findings['low'].append("Large modules (>10KB): {}".format(', '.join('{}/{}KB'.format(s, size//1024) for s, size in large_modules[:5])))
    
    # Check for missing required functions
    required_funcs = ['onRequest', 'hasStore', 'okRef', 'complianceFooter']
    for slug, info in modules.items():
        filepath = os.path.join(lib_dir, slug + '.js')
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            for func in required_funcs:
                if func not in content:
                    findings['high'].append("Module {} missing required function: {}".format(slug, func))
        except:
            pass
else:
    findings['critical'].append("lib/ directory not found at {}".format(lib_dir))

# 1.2 Check API route coverage
log("1.2 Checking API route coverage...")
api_dir = '/www/wwwroot/tools-cn.highkingflower.com/api'
routes_configured = []
routes_missing = []

if os.path.exists(api_dir):
    alipay_js = os.path.join(api_dir, 'alipay.js')
    if os.path.exists(alipay_js):
        with open(alipay_js, 'r', encoding='utf-8') as f:
            alipay_content = f.read()
        
        # Check for all expected routes
        for slug in ['overfitcheck', 'whitebox', 'papercombo', 'quantcompute', 'quantannual', 
                     'scan_api', 'minute_klines', 'reportexport', 'strategyapi', 'marketdata']:
            if '/api/' + slug in alipay_content:
                routes_configured.append(slug)
            else:
                routes_missing.append(slug)
        
        log("Configured routes: {}/{}".format(len(routes_configured), len(routes_configured) + len(routes_missing)))
        if routes_missing:
            findings['high'].append("Missing API routes: {}".format(', '.join(routes_missing[:5])))
    else:
        findings['critical'].append("api/alipay.js not found")
else:
    findings['critical'].append("api/ directory not found")

# ============================================================
# LAYER 2: Database Integrity
# ============================================================
log("")
log("--- Layer 2: Database Integrity ---")

try:
    with open(DB, 'r', encoding='utf-8') as f:
        db_data = json.load(f)
    
    orders = db_data.get('orders', [])
    visitors = db_data.get('visitors', [])
    leads = db_data.get('leads', [])
    
    log("Database stats: {} orders, {} visitors, {} leads".format(len(orders), len(visitors), len(leads)))
    
    # 2.1 Check for orphaned orders
    log("2.1 Checking for orphaned orders...")
    ref_set = set(str(v.get('visitor') or v.get('ip', '')) for v in visitors)
    orphaned_orders = []
    for o in orders:
        ref = str(o.get('ref', ''))
        if ref and ref not in ref_set and ref != 'None':
            # Check if it's a test order
            if o.get('status') == 'void_test':
                continue
            orphaned_orders.append({
                'ref': ref,
                'id': o.get('id', '')[:12],
                'status': o.get('status', ''),
                'amount': o.get('amount', 0)
            })
    
    if orphaned_orders:
        findings['medium'].append("Orphaned orders (no visitor record): {} found".format(len(orphaned_orders)))
        for o in orphaned_orders[:3]:
            log("  Orphaned: ref={}, status={}, amount={}".format(o['ref'], o['status'], o['amount']))
    
    # 2.2 Check payment consistency
    log("2.2 Checking payment consistency...")
    paid_orders = [o for o in orders if o.get('paid') and float(o.get('amount', 0) or 0) > 5]
    pending_orders = [o for o in orders if o.get('status') == 'pending']
    
    log("Paid orders: {}, Pending orders: {}".format(len(paid_orders), len(pending_orders)))
    
    # Check for orders without gateway
    no_gateway = [o for o in paid_orders if not o.get('gateway')]
    if no_gateway:
        findings['high'].append("Paid orders without gateway: {} found".format(len(no_gateway)))
    
    # Check for orders without out_trade_no
    no_trade_no = [o for o in paid_orders if not o.get('out_trade_no')]
    if no_trade_no:
        findings['high'].append("Paid orders without trade number: {} found".format(len(no_trade_no)))
    
    # 2.3 Check billing ledger consistency
    log("2.3 Checking billing ledger consistency...")
    for ledger_file in ['outreach_ledger.json', 'corporate_899.json']:
        ledger_path = os.path.join(BL, ledger_file)
        if os.path.exists(ledger_path):
            try:
                with open(ledger_path, 'r', encoding='utf-8') as f:
                    ledger_data = json.load(f)
                
                items = ledger_data if isinstance(ledger_data, list) else ledger_data.get('items', ledger_data.get('orders', []))
                
                # Check for duplicate order IDs
                order_ids = [str(i.get('order_id', i.get('id', ''))) for i in items if i.get('order_id') or i.get('id')]
                id_counts = Counter(order_ids)
                duplicates = [(oid, cnt) for oid, cnt in id_counts.items() if cnt > 1 and oid]
                
                if duplicates:
                    findings['high'].append("{}: {} duplicate order IDs".format(ledger_file, len(duplicates)))
                
                # Check for invalid amounts
                invalid_amounts = [i for i in items if float(i.get('collect', i.get('amount', 0) or 0) or 0) < 0]
                if invalid_amounts:
                    findings['medium'].append("{}: {} items with negative amounts".format(ledger_file, len(invalid_amounts)))
                    
            except Exception as e:
                findings['high'].append("{}: parse error - {}".format(ledger_file, str(e)[:60]))
        else:
            findings['medium'].append("Billing ledger missing: {}".format(ledger_file))
    
    # 2.4 Check for stale data
    log("2.4 Checking for stale data...")
    one_week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    stale_orders = [o for o in orders if o.get('created_at', o.get('createdAt', '')) < one_week_ago 
                    and o.get('status') in ('pending', 'void_test')]
    
    if len(stale_orders) > 10:
        findings['low'].append("Stale orders (>7 days): {} found".format(len(stale_orders)))
    
except Exception as e:
    findings['critical'].append("Database read error: {}".format(str(e)))

# ============================================================
# LAYER 3: Configuration Audit
# ============================================================
log("")
log("--- Layer 3: Configuration Audit ---")

# 3.1 Check environment variables
log("3.1 Auditing environment variables...")
env_file = '/opt/bingdashan/.env'
required_env = {
    'ALIPAY_APP_ID': '支付宝APPID',
    'ALIPAY_PRIVATE_KEY': '支付宝私钥',
    'ALIPAY_PUBLIC_KEY': '支付宝公钥',
    'SUPABASE_URL': 'Supabase URL',
    'SUPABASE_KEY': 'Supabase Key',
    'SMTP_USER': 'SMTP用户名',
    'SMTP_PASS': 'SMTP密码'
}

missing_env = []
for env_var, desc in required_env.items():
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
        if env_var not in env_content:
            missing_env.append(env_var)
            findings['high'].append("Missing env var: {} ({})".format(env_var, desc))
    else:
        missing_env.append(env_var)
        findings['critical'].append(".env file not found at {}".format(env_file))

# 3.2 Check SSL certificates
log("3.2 Checking SSL certificates...")
ssl_files = [
    '/etc/bingdashan-cn/alipay_priv.pem',
    '/etc/bingdashan-cn/alipay_pub.pem'
]

for ssl_file in ssl_files:
    if os.path.exists(ssl_file):
        # Check permissions
        stat = os.stat(ssl_file)
        mode = oct(stat.st_mode)[-3:]
        if mode != '600':
            findings['medium'].append("{}: incorrect permissions ({}). Should be 600".format(ssl_file, mode))
            fixes.append("chmod 600 {}".format(ssl_file))
    else:
        findings['high'].append("SSL certificate missing: {}".format(ssl_file))

# 3.3 Check service configuration
log("3.3 Checking service configuration...")
service_file = '/etc/systemd/system/bingdashan-cn.service'
if os.path.exists(service_file):
    with open(service_file, 'r', encoding='utf-8') as f:
        service_content = f.read()
    
    # Check for proper restart policy
    if 'Restart=always' not in service_content:
        findings['medium'].append("Service missing Restart=always directive")
    
    # Check for proper working directory
    if 'WorkingDirectory=' not in service_content:
        findings['low'].append("Service missing WorkingDirectory directive")
else:
    findings['high'].append("Systemd service file not found")

# ============================================================
# LAYER 4: Performance Analysis
# ============================================================
log("")
log("--- Layer 4: Performance Analysis ---")

# 4.1 Check disk usage
log("4.1 Checking disk usage...")
try:
    rc = subprocess.run(['df', '-h', '/'], capture_output=True, text=True, timeout=5)
    if rc.returncode == 0:
        lines = rc.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            use_percent = parts[4].replace('%', '')
            if int(use_percent) > 90:
                findings['critical'].append("Disk usage critical: {}%".format(use_percent))
            elif int(use_percent) > 80:
                findings['high'].append("Disk usage high: {}%".format(use_percent))
            else:
                log("Disk usage: {}%".format(use_percent))
except Exception as e:
    findings['medium'].append("Disk check failed: {}".format(str(e)[:50]))

# 4.2 Check memory usage
log("4.2 Checking memory usage...")
try:
    rc = subprocess.run(['free', '-h'], capture_output=True, text=True, timeout=5)
    if rc.returncode == 0:
        lines = rc.stdout.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            mem_used = parts[2]
            mem_total = parts[1]
            log("Memory: {}/{}".format(mem_used, mem_total))
except Exception as e:
    log("Memory check failed: {}".format(str(e)[:50]))

# 4.3 Check log sizes
log("4.3 Checking log sizes...")
log_sizes = {}
if os.path.exists(LOG_DIR):
    for f in os.listdir(LOG_DIR):
        if f.endswith('.log'):
            filepath = os.path.join(LOG_DIR, f)
            size = os.path.getsize(filepath)
            log_sizes[f] = size
            if size > 50 * 1024 * 1024:  # 50MB
                findings['medium'].append("Large log file: {} ({}MB)".format(f, size // (1024*1024)))

# 4.4 Check backup status
log("4.4 Checking backup status...")
backup_dir = '/opt/bingdashan/backups'
if os.path.exists(backup_dir):
    backups = os.listdir(backup_dir)
    log("Backup count: {}".format(len(backups)))
    if len(backups) == 0:
        findings['high'].append("No backups found")
    else:
        # Check latest backup age
        latest_backup = max(backups)
        latest_path = os.path.join(backup_dir, latest_backup)
        backup_age_hours = (datetime.now().timestamp() - os.path.getmtime(latest_path)) / 3600
        if backup_age_hours > 24:
            findings['medium'].append("Latest backup is {} hours old".format(int(backup_age_hours)))
else:
    findings['high'].append("Backup directory not found")

# ============================================================
# LAYER 5: Security Analysis
# ============================================================
log("")
log("--- Layer 5: Security Analysis ---")

# 5.1 Check for hardcoded secrets
log("5.1 Scanning for hardcoded secrets...")
secret_patterns = [
    r'password\s*=\s*["\'][^"\']+["\']',
    r'secret\s*=\s*["\'][^"\']+["\']',
    r'api_key\s*=\s*["\'][^"\']+["\']',
    r'PRIVATE_KEY\s*=\s*["\'][^"\']+["\']'
]

hardcoded_secrets = []
for root, dirs, files in os.walk('/www/wwwroot/tools-cn.highkingflower.com'):
    for file in files:
        if file.endswith('.js') and not file.startswith('_'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        hardcoded_secrets.append({
                            'file': filepath,
                            'pattern': pattern,
                            'matches': len(matches)
                        })
            except:
                pass

if hardcoded_secrets:
    findings['critical'].append("Hardcoded secrets found: {} occurrences in {} files".format(
        sum(s['matches'] for s in hardcoded_secrets), len(hardcoded_secrets)))
    for hs in hardcoded_secrets[:3]:
        log("  {}: {} matches".format(hs['file'].split('/')[-1], hs['matches']))

# 5.2 Check input validation
log("5.2 Checking input validation...")
weak_validation = []
for f in os.listdir(lib_dir) if os.path.exists(lib_dir) else []:
    if f.endswith('.js') and not f.startswith('_'):
        filepath = os.path.join(lib_dir, f)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            # Check if uses okRef for ref validation
            if 'okRef(ref)' not in content and 'String(ref' not in content:
                weak_validation.append(f.replace('.js', ''))
        except:
            pass

if weak_validation:
    findings['medium'].append("Modules with weak input validation: {}".format(', '.join(weak_validation[:5])))

# 5.3 Check error handling
log("5.3 Checking error handling...")
poor_error_handling = []
for f in os.listdir(lib_dir) if os.path.exists(lib_dir) else []:
    if f.endswith('.js') and not f.startswith('_'):
        filepath = os.path.join(lib_dir, f)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            # Check for bare catch blocks
            if re.search(r'catch\s*\(\s*e\s*\)\s*\{[^}]*\}', content):
                poor_error_handling.append(f.replace('.js', ''))
        except:
            pass

if poor_error_handling:
    findings['low'].append("Modules with poor error handling: {}".format(', '.join(poor_error_handling[:5])))

# ============================================================
# LAYER 6: Business Logic Analysis
# ============================================================
log("")
log("--- Layer 6: Business Logic Analysis ---")

# 6.1 Check pricing consistency
log("6.1 Checking pricing consistency...")
pricing_issues = []
expected_prices = {
    'overfitcheck': {'yuan': 39, 'coin': 400},
    'scan_api': {'yuan': 99, 'coin': 1000},
    'minute_klines': {'yuan': 99, 'coin': 1000}
}

for slug, expected in expected_prices.items():
    filepath = os.path.join(lib_dir, '{}.js'.format(slug))
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Extract actual prices
            yuan_match = re.search(r'PRICE_YUAN.*?(\d+)', content)
            coin_match = re.search(r'PRICE_COIN.*?(\d+)', content)
            
            if yuan_match:
                actual_yuan = int(yuan_match.group(1))
                if actual_yuan != expected['yuan']:
                    pricing_issues.append("{}: expected ¥{}, got ¥{}".format(slug, expected['yuan'], actual_yuan))
            
            if coin_match:
                actual_coin = int(coin_match.group(1))
                if actual_coin != expected['coin']:
                    pricing_issues.append("{}: expected {} coins, got {}".format(slug, expected['coin'], actual_coin))
        except:
            pass

if pricing_issues:
    findings['medium'].append("Pricing inconsistencies: {}".format('; '.join(pricing_issues[:3])))

# 6.2 Check refund logic
log("6.2 Checking refund/cancellation logic...")
refund_logic_found = False
for f in os.listdir(lib_dir) if os.path.exists(lib_dir) else []:
    if f.endswith('.js'):
        filepath = os.path.join(lib_dir, f)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            if 'refund' in content.lower() or 'cancel' in content.lower():
                refund_logic_found = True
                break
        except:
            pass

if not refund_logic_found:
    findings['low'].append("No refund/cancellation logic found in any module")

# 6.3 Check audit logging
log("6.3 Checking audit logging...")
audit_logging = []
for f in os.listdir(lib_dir) if os.path.exists(lib_dir) else []:
    if f.endswith('.js'):
        filepath = os.path.join(lib_dir, f)
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            if 'log(' in content or 'console.log' in content:
                audit_logging.append(f.replace('.js', ''))
        except:
            pass

if len(audit_logging) < 10:
    findings['medium'].append("Only {} modules have audit logging".format(len(audit_logging)))

# ============================================================
# GENERATE REPORT
# ============================================================
log("")
log("=" * 70)
log("GENERATING FINAL REPORT")
log("=" * 70)

summary = {
    'total_findings': sum(len(v) for v in findings.values()),
    'critical': len(findings['critical']),
    'high': len(findings['high']),
    'medium': len(findings['medium']),
    'low': len(findings['low']),
    'info': len(findings['info']),
    'total_fixes': len(fixes)
}

report = {
    'generated_at': datetime.now().isoformat(),
    'summary': summary,
    'findings': findings,
    'fixes': fixes,
    'recommendations': []
}

# Generate recommendations based on findings
if findings['critical']:
    report['recommendations'].append({
        'priority': 'P0',
        'title': '立即修复Critical问题',
        'actions': findings['critical'][:5]
    })

if findings['high']:
    report['recommendations'].append({
        'priority': 'P1',
        'title': '本周内修复High问题',
        'actions': findings['high'][:5]
    })

if not any('alipay.js' in f for f in findings.get('critical', []) + findings.get('high', [])):
    report['recommendations'].append({
        'priority': 'P0',
        'title': '创建缺失的支付网关',
        'actions': ['运行 subscription_wall_fixer.py 自动创建 api/alipay.js']
    })

if missing_env:
    report['recommendations'].append({
        'priority': 'P0',
        'title': '补充缺失的环境变量',
        'actions': ['编辑 /opt/bingdashan/.env 填入缺失的配置项']
    })

# Save report
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
    f.write('\n')

log("Report saved: {}".format(REPORT_PATH))
log("=== Deep Dive v5 Complete ===")

# Print summary
print("\n" + "=" * 70)
print("DEEP DIVE v5 COMPLETE")
print("=" * 70)
print("Total findings: {}".format(summary['total_findings']))
print("  Critical: {}".format(summary['critical']))
print("  High: {}".format(summary['high']))
print("  Medium: {}".format(summary['medium']))
print("  Low: {}".format(summary['low']))
print("Fixes available: {}".format(summary['total_fixes']))
print("Report: {}".format(REPORT_PATH))

#!/usr/bin/env python3
"""丙大山 · 本地深度诊断 — 分析所有本地文件，生成执行脚本"""
import json, os, sys, re
from datetime import datetime
from pathlib import Path

# 本地仓库路径
LOCAL_ROOT = r'F:\2026\24xs\02_交付物\channels\gumroad-product-1\tool-station-server-pro'
OUTPUT_DIR = r'F:\2026\第三轮\diagnostic_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

log_lines = []
def log(m):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = "[LOCAL][{}] {}".format(ts, m)
    print(line)
    log_lines.append(line)

log("=" * 70)
log("LOCAL DEEP DIAGNOSTIC v5")
log("=" * 70)

findings = {
    'critical': [],
    'high': [],
    'medium': [],
    'low': []
}

fixes = []

# ===== CHECK 1: Module Analysis =====
log("")
log("--- Check 1: Module Security Analysis ---")

lib_dir = os.path.join(LOCAL_ROOT, 'lib')
if os.path.exists(lib_dir):
    js_files = [f for f in os.listdir(lib_dir) if f.endswith('.js') and not f.startswith('_')]
    log("Found {} modules in lib/".format(len(js_files)))
    
    module_analysis = []
    for js_file in js_files:
        filepath = os.path.join(lib_dir, js_file)
        slug = js_file.replace('.js', '')
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            
            # Check required security functions
            if 'hasStore()' not in content:
                issues.append('missing_hasStore')
            if 'okRef(ref)' not in content and 'okRef(ref)' not in content:
                issues.append('missing_okRef')
            if 'ADMIN_SECRET' not in content:
                issues.append('missing_ADMIN_SECRET')
            if 'complianceFooter' not in content:
                issues.append('missing_complianceFooter')
            
            # Check quota validation
            if "'run'" in content or "action === 'run'" in content:
                if 'quota <= 0' not in content and 'need_payment' not in content:
                    issues.append('missing_quota_check')
            
            # Check subscription expiry
            if 'quantannual' in slug or 'subscription' in slug.lower():
                if 'active_until' not in content:
                    issues.append('missing_expiry_check')
            
            module_analysis.append({
                'slug': slug,
                'issues': issues,
                'size': len(content),
                'lines': content.count('\n')
            })
            
            if issues:
                findings['high'].append("{}: {}".format(slug, ', '.join(issues)))
                log("  ISSUE: {} - {}".format(slug, ', '.join(issues)))
            else:
                log("  OK: {}".format(slug))
                
        except Exception as e:
            findings['medium'].append("{}: read error - {}".format(slug, str(e)[:50]))
            log("  ERROR: {} - {}".format(slug, str(e)))
    
    # Save module analysis
    with open(os.path.join(OUTPUT_DIR, 'module_analysis.json'), 'w', encoding='utf-8') as f:
        json.dump(module_analysis, f, ensure_ascii=False, indent=2)
else:
    findings['critical'].append("lib/ directory not found at {}".format(lib_dir))
    log("FAIL: lib/ directory not found")

# ===== CHECK 2: API Routes =====
log("")
log("--- Check 2: API Route Coverage ---")

api_dir = os.path.join(LOCAL_ROOT, 'api')
if os.path.exists(api_dir):
    api_files = os.listdir(api_dir)
    log("API files: {}".format(', '.join(api_files)))
    
    alipay_js = os.path.join(api_dir, 'alipay.js')
    if os.path.exists(alipay_js):
        with open(alipay_js, 'r', encoding='utf-8') as f:
            alipay_content = f.read()
        
        # Check routes
        expected_routes = ['overfitcheck', 'whitebox', 'papercombo', 'quantcompute', 'quantannual', 
                          'scan_api', 'minute_klines', 'reportexport', 'strategyapi', 'marketdata']
        
        missing_routes = []
        for route in expected_routes:
            if '/api/' + route not in alipay_content:
                missing_routes.append(route)
        
        if missing_routes:
            findings['high'].append("Missing routes in alipay.js: {}".format(', '.join(missing_routes)))
            log("MISSING ROUTES: {}".format(', '.join(missing_routes)))
        else:
            log("OK: All routes configured")
    else:
        findings['critical'].append("api/alipay.js not found")
        log("CRITICAL: alipay.js missing")
else:
    findings['critical'].append("api/ directory not found")
    log("CRITICAL: api/ directory not found")

# ===== CHECK 3: Pricing Consistency =====
log("")
log("--- Check 3: Pricing Consistency ---")

expected_prices = {
    'overfitcheck': {'yuan': 39, 'coin': 400},
    'scan_api': {'yuan': 99, 'coin': 1000},
    'minute_klines': {'yuan': 99, 'coin': 1000},
    'whitebox': {'yuan': 199, 'coin': 2000},
    'quantannual': {'yuan': 3990, 'coin': 40000}
}

pricing_issues = []
for slug, expected in expected_prices.items():
    filepath = os.path.join(lib_dir, '{}.js'.format(slug)) if os.path.exists(lib_dir) else None
    if filepath and os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
                    
        except Exception as e:
            findings['medium'].append("{}: pricing check failed - {}".format(slug, str(e)[:50]))

if pricing_issues:
    findings['medium'].extend(pricing_issues)
    for issue in pricing_issues:
        log("PRICING: {}".format(issue))
else:
    log("OK: All prices consistent")

# ===== CHECK 4: Vulnerability Patterns =====
log("")
log("--- Check 4: Vulnerability Pattern Scan ---")

vulnerability_patterns = {
    'hardcoded_password': r'password\s*=\s*["\'][^"\']+["\']',
    'hardcoded_secret': r'secret\s*=\s*["\'][^"\']+["\']',
    'unsafe_eval': r'eval\s*\(',
    'sql_injection': r'(SELECT|INSERT|UPDATE|DELETE)\s+.*(?:FROM|INTO|SET|WHERE)',
    'path_traversal': r'\.\.[\\/]'
}

vuln_count = 0
for pattern_name, pattern in vulnerability_patterns.items():
    count = 0
    for root, dirs, files in os.walk(LOCAL_ROOT):
        # Skip node_modules and .git
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'QuantDinger']]
        for file in files:
            if file.endswith('.js') and not file.startswith('_'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    count += len(matches)
                except:
                    pass
    if count > 0:
        vuln_count += count
        findings['high'].append("Pattern '{}' found {} times".format(pattern_name, count))
        log("VULN: {} - {} occurrences".format(pattern_name, count))

if vuln_count == 0:
    log("OK: No vulnerability patterns found")

# ===== GENERATE FIX SCRIPT =====
log("")
log("--- Generating Fix Script ---")

fix_script = '''#!/bin/bash
# 丙大山 · 深度挖掘修复脚本 (一键执行)
# 生成时间: {timestamp}

set -e

echo "=== 丙大山 · 深度挖掘修复 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色定义
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

# Step 1: 创建必要目录
echo "📁 Step 1: 创建必要目录..."
mkdir -p /www/wwwroot/tools-cn.highkingflower.com/api
mkdir -p /opt/bingdashan/data/{billing,runtime,backups,outreach_autogen}
mkdir -p /var/log/bingdashan
echo -e "${{GREEN}}✅ 目录创建完成${{NC}}"
echo ""

# Step 2: 检查并创建.env模板
echo "🔧 Step 2: 检查环境配置..."
if [ ! -f /opt/bingdashan/.env ]; then
    echo -e "${{YELLOW}}⚠️  .env不存在，创建模板...${{NC}}"
    cat > /opt/bingdashan/.env << 'ENVEOF'
# 支付宝配置 (必须填入真实值)
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
ENVEOF
    echo -e "${{GREEN}}✅ .env模板已创建${{NC}}"
    echo -e "${{YELLOW}}⚠️  请编辑 /opt/bingdashan/.env 填入真实配置${{NC}}"
else
    echo -e "${{GREEN}}✅ .env已存在${{NC}}"
fi
echo ""

# Step 3: 检查SSL密钥权限
echo "🔐 Step 3: 检查SSL密钥权限..."
for keyfile in /etc/bingdashan-cn/alipay_priv.pem /etc/bingdashan-cn/alipay_pub.pem; do
    if [ -f "$keyfile" ]; then
        current_perms=$(stat -c %a "$keyfile" 2>/dev/null || stat -f %Lp "$keyfile" 2>/dev/null)
        if [ "$current_perms" != "600" ]; then
            chmod 600 "$keyfile"
            echo -e "${{YELLOW}}修复权限: $keyfile -> 600${{NC}}"
        else
            echo -e "${{GREEN}}权限正确: $keyfile${{NC}}"
        fi
    fi
done
echo ""

# Step 4: 重启服务
echo "🚀 Step 4: 重启服务..."
systemctl daemon-reload
systemctl restart bingdashan-cn
sleep 2
if systemctl is-active --quiet bingdashan-cn; then
    echo -e "${{GREEN}}✅ 服务运行正常${{NC}}"
else
    echo -e "${{RED}}❌ 服务启动失败，检查日志:${{NC}}"
    journalctl -u bingdashan-cn --no-pager -n 20
fi
echo ""

# Step 5: 健康检查
echo "🏥 Step 5: 健康检查..."
curl -s http://127.0.0.1:8794/api/health | jq '.' 2>/dev/null || echo "健康检查端点不可用"
echo ""

# Step 6: 支付测试
echo "💳 Step 6: 支付流程测试..."
TEST_REF="diag_test_$(date +%s)"
curl -s "http://127.0.0.1:8794/api/pay?plan=m&ref=$TEST_REF" | jq '.' 2>/dev/null || echo "支付端点测试失败 (可能需要先配置支付宝)"
echo ""

echo "=========================================="
echo "✅ 修复脚本执行完成"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 检查 /opt/bingdashan/data/deep_dive_v5_*.json 查看详细诊断结果"
echo "2. 确认 .env 中填入了真实的支付宝配置"
echo "3. 测试实际支付流程"
'''

# Replace placeholder with timestamp
fix_script = fix_script.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'))

fix_script_path = os.path.join(OUTPUT_DIR, 'deep_dive_fix.sh')
with open(fix_script_path, 'w', encoding='utf-8') as f:
    f.write(fix_script)

log("FIX SCRIPT SAVED: {}".format(fix_script_path))

# ===== GENERATE SUMMARY REPORT =====
log("")
log("--- Generating Summary Report ---")

total_findings = sum(len(v) for v in findings.values())
summary_report = """# 丙大山 · 深度挖掘 v5 本地诊断报告
> 生成时间: {}
> 模式: 本地静态分析 (等待服务器恢复后执行)

---

## 📊 诊断摘要

| 级别 | 数量 | 状态 |
|------|------|------|
""".format(datetime.now().strftime('%Y-%m-%d %H:%M'))

summary_report += "| 🔴 Critical | {} | {} |\n".format(
    len(findings['critical']), 
    '✅ 无' if not findings['critical'] else '❌ 需立即修复'
)
summary_report += "| 🟠 High | {} | {} |\n".format(
    len(findings['high']),
    '✅ 无' if not findings['high'] else '❌ 本周修复'
)
summary_report += "| 🟡 Medium | {} | 本月修复 |\n".format(len(findings['medium']))
summary_report += "| 🟢 Low | {} | 可选优化 |\n".format(len(findings['low']))
summary_report += "| **总计** | **{}** | |\n".format(total_findings)

summary_report += """
---

## 🔍 详细发现

"""

if findings['critical']:
    summary_report += "### 🔴 Critical (必须立即修复)\n\n"
    for i, issue in enumerate(findings['critical'], 1):
        summary_report += "{}. {}\n".format(i, issue)
    summary_report += "\n"

if findings['high']:
    summary_report += "### 🟠 High (本周内修复)\n\n"
    for i, issue in enumerate(findings['high'], 1):
        summary_report += "{}. {}\n".format(i, issue)
    summary_report += "\n"

if findings['medium']:
    summary_report += "### 🟡 Medium (本月修复)\n\n"
    for i, issue in enumerate(findings['medium'], 1):
        summary_report += "{}. {}\n".format(i, issue)
    summary_report += "\n"

if findings['low']:
    summary_report += "### 🟢 Low (可选优化)\n\n"
    for i, issue in enumerate(findings['low'], 1):
        summary_report += "{}. {}\n".format(i, issue)
    summary_report += "\n"

summary_report += """
---

## ⚡ 一键修复命令

当SSH恢复后，按顺序执行:

```bash
# 1. 上传修复脚本
scp diagnostic_output/deep_dive_fix.sh aliyun:/tmp/
ssh aliyun "bash /tmp/deep_dive_fix.sh"

# 2. 运行Python诊断 (查看详细信息)
ssh aliyun "python3 /opt/bingdashan/scripts/ops/deep_dive_v5.py"

# 3. 运行自动修复
ssh aliyun "python3 /opt/bingdashan/scripts/ops/deep_dive_v5_executor.py"

# 4. 填入支付宝配置
ssh aliyun "nano /opt/bingdashan/.env"
# 填入: ALIPAY_APP_ID, ALIPAY_PRIVATE_KEY, etc.

# 5. 验证支付流程
ssh aliyun "curl 'http://127.0.0.1:8794/api/pay?plan=m&ref=test_verify'"
```

---

## 📦 生成的文件清单

| 文件 | 位置 | 用途 |
|------|------|------|
| deep_dive_v5.py | scripts/ops/ | 核心诊断引擎 |
| deep_dive_v5_executor.py | scripts/ops/ | 自动修复执行器 |
| payment_full_fix.py | scripts/ops/ | 支付网关修复 |
| subscription_wall_fixer.py | scripts/ops/ | 订阅墙加固 |
| vulnerability_scanner.py | scripts/ops/ | 漏洞扫描 |
| deep_dive_fix.sh | {} | 一键修复脚本 |
| module_analysis.json | {} | 模块分析报告 |

---

## 💡 核心认知

```
深度挖掘的目标 = 发现问题 → 修复问题 → 验证结果
而不是催客户付钱 (那是产品运营的事)
```

**修复后的预期**:
- ✅ 所有模块都有完整的安全检查
- ✅ 未付费用户无法访问付费功能
- ✅ 支付网关正常工作
- ✅ 系统安全无漏洞

---

> **下一步**: 等待服务器SSH恢复，然后执行上述命令。
""".format(OUTPUT_DIR, OUTPUT_DIR)

report_path = os.path.join(OUTPUT_DIR, 'local_diagnostic_report.md')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(summary_report)

log("REPORT SAVED: {}".format(report_path))

# Print final summary
print("\n" + "=" * 70)
print("LOCAL DIAGNOSTIC COMPLETE")
print("=" * 70)
print("Total findings: {}".format(total_findings))
print("  Critical: {}".format(len(findings['critical'])))
print("  High: {}".format(len(findings['high'])))
print("  Medium: {}".format(len(findings['medium'])))
print("  Low: {}".format(len(findings['low'])))
print("\nGenerated files:")
print("  - {}".format(fix_script_path))
print("  - {}".format(report_path))
print("  - {}/module_analysis.json".format(OUTPUT_DIR))
print("\nNext steps:")
print("  1. Wait for SSH connection to recover")
print("  2. Upload and execute the fix script")
print("  3. Fill in real Alipay configuration")
print("  4. Test payment flow")

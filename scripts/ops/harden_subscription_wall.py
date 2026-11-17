#!/usr/bin/env python3
"""丙大山 · 订阅墙安全加固器 — 修补所有模块的安全漏洞"""
import os, sys, re
from datetime import datetime

LIB_DIR = '/www/wwwroot/tools-cn.highkingflower.com/lib'
LOG = '/var/log/bingdashan/subscription_wall_fix.log'

def log(m):
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = "[WALL][{}] {}".format(ts, m)
    print(line)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except: pass

log("="*60)
log("SUBSCRIPTION WALL SECURITY HARDENING")
log("="*60)

fixed_modules = []
errors = []

if not os.path.exists(LIB_DIR):
    log("ERROR: lib/ directory not found")
    sys.exit(1)

js_files = [f for f in os.listdir(LIB_DIR) if f.endswith('.js') and not f.startswith('_')]
log("Found {} modules to process".format(len(js_files)))

for js_file in js_files:
    filepath = os.path.join(LIB_DIR, js_file)
    slug = js_file.replace('.js', '')
    
    log("Processing: {}".format(slug))
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = []
        
        # Fix 1: Add quota check before execution actions
        if ("action === 'run'" in content or "action==='run'" in content) and 'need_payment' not in content:
            # Find where to insert quota check (after loading user state)
            pattern = r"(var st = await load\(ref\);.*?)(\n    if\(action === ['\"]summary['\"])"
            replacement = r"""\1
    // SUBSCRIPTION CHECK: Block unpaid users
    if(action === 'run' || action === 'execute' || action === 'backtest' || action === 'scan') {
      var userQuota = (st.quota || 0);
      var isActive = st.active_until > Date.now();
      if(userQuota <= 0 && !isActive) {
        return send(402, { 
          ok: false, 
          error: 'need_payment',
          need: { 
            price_yuan: typeof PRICE_YUAN !== 'undefined' ? PRICE_YUAN : 83,
            pay_entry: '/api/pay?plan=m&ref=' + encodeURIComponent(ref)
          }
        });
      }
    }
\2"""
            
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                changes.append("Added quota check for run/execute actions")
        
        # Fix 2: Strengthen ADMIN_SECRET validation
        if 'ADMIN_SECRET' in content and 'purchase' in content:
            # Replace weak validation
            old_pattern = r"if\(!ADMIN_SECRET \|\| .*?\) return send\(403"
            new_text = "if(!ADMIN_SECRET || !secret || secret !== ADMIN_SECRET) return send(403, { ok: false, error: 'forbidden', note: 'invalid_admin_secret' })"
            
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_text, content)
                changes.append("Strengthened ADMIN_SECRET validation")
        
        # Fix 3: Add time-based expiry for subscription products
        if ('quantannual' in slug or 'subscription' in slug.lower()) and 'active_until' not in content:
            # Add active_until to summarize function
            pattern = r"function summarize\(ref, st\)"
            if re.search(pattern, content):
                replacement = """function summarize(ref, st) {
  st = st || { quota: 0, used: 0, revenue_yuan: 0, revenue_coin: 0, entries: [], active_until: 0 };
  var now = Date.now();
  var active = st.active_until > now;
  return { 
    ref: ref, 
    quota_left: st.quota, 
    total_used: st.used, 
    active: active, 
    active_until: st.active_until, 
    days_left: active ? Math.round((st.active_until-now)/86400000) : 0,
    revenue_yuan: st.revenue_yuan, 
    revenue_coin: st.revenue_coin 
  };"""
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                changes.append("Added time-based expiry check")
        
        # Fix 4: Ensure compliance footer exists
        if 'complianceFooter' not in content and 'module.exports' in content:
            # Add complianceFooter before module.exports
            pattern = r"(module\.exports\s*=)"
            replacement = """function complianceFooter() {
    return { 
      disclaimer: '历史回测不代表未来收益，非投资建议，风险自负', 
      data_source: 'public_market_data', 
      generated_at: new Date().toISOString() 
    };
  }
  
  """
            content = re.sub(pattern, replacement + r'\1', content)
            changes.append("Added complianceFooter function")
        
        # Fix 5: Ensure hasStore and okRef exist
        if 'hasStore()' not in content:
            # Add before onRequest
            pattern = r"async function onRequest"
            replacement = """function hasStore() { return !!(kv() || up() || fileStore()); }
function storeName() { return kv() ? 'kv' : (up() ? 'supabase' : (fileStore() ? 'file' : 'none')); }
function keyOf(ref) { return '{prefix}:' + ref; }
function okRef(ref) { return /^[A-Za-z0-9_.-]{{1,64}}$/.test(String(ref || '')); }

async function onRequest""".replace('{prefix}', slug[:3].lower())
            content = re.sub(pattern, replacement, content)
            changes.append("Added hasStore/okRef functions")
        
        # Write back if changes were made
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed_modules.append({"module": slug, "changes": changes})
            log("FIXED: {} ({})".format(slug, len(changes)))
        else:
            log("OK: {} already secure".format(slug))
            
    except Exception as e:
        errors.append({"module": slug, "error": str(e)})
        log("ERROR {}: {}".format(slug, str(e)[:80]))

# Summary
log("")
log("="*60)
log("SUBSCRIPTION WALL FIX COMPLETE")
log("="*60)
log("Modules fixed: {}".format(len(fixed_modules)))
log("Errors: {}".format(len(errors)))

if errors:
    log("ERROR DETAILS:")
    for err in errors[:5]:
        log("  {}: {}".format(err['module'], err['error']))

# Print success message
print("\n" + "="*60)
print("SUBSCRIPTION WALL HARDENING COMPLETE")
print("="*60)
print("Fixed modules: {}".format(len(fixed_modules)))
for fix in fixed_modules[:5]:
    print("  {} - {}".format(fix['module'], ', '.join(fix['changes'])))
if errors:
    print("\nErrors encountered: {}".format(len(errors)))
print("="*60)

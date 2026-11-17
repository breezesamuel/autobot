#!/usr/bin/env python3
"""丙大山 · 全量自检 + 主动修复器 v2 (兼容 python3.6)"""
import json, os, sys, subprocess
from datetime import datetime
try: from collections import Counter
except: pass  # py3.6 ok

BL='/opt/bingdashan/data/billing'
ROOT='/www/wwwroot/tools-cn.highkingflower.com'
LOG='/var/log/bingdashan/diagnostic.log'

def log(msg):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[{}] {}".format(ts, msg); print(line); 
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

def run(cmd, timeout=10):
    """py3.6 compat: no capture_output"""
    try:
        r=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return r.returncode, r.stdout.decode('utf-8','ignore'), r.stderr.decode('utf-8','ignore')
    except Exception as e:
        return -1, '', str(e)[:120]

log("=== 全量自检 start ===")
issues=[]; fixes=[]

# 1. CN .js 语法检查
log("1/6 syntax check")
for f in os.listdir(ROOT):
    if not f.endswith('.js'): continue
    p=os.path.join(ROOT, f)
    rc,out,err = run(['node','--check',p])
    if rc!=0:
        issues.append("SYNTAX_ERROR:{}: {}{}".format(f, out[:100], err[:100]))
log("  done: {} issues so far".format(len(issues)))

# 2. 服务+端口
log("2/6 services")
for svc in ['bingdashan-cn','bd-revenue-watch.timer']:
    rc,o,e = run(['systemctl','is-active',svc])
    log("  {} : {} (rc={})".format(svc, o.strip(), rc))
rc,o,e=run(['ss','-tlnp'])
port_ok=':8794' in o
log("  port 8794: {}".format('OK' if port_ok else 'FAIL'))
if not port_ok: issues.append("PORT_8794_DOWN")

# 3. HTTP endpoints
log("3/6 http health")
endpoints=[
    ('CN /api/revenue','http://127.0.0.1:8794/api/revenue'),
    ('CN /revenue-honest','http://127.0.0.1:8794/revenue-honest.html'),
    ('CN /channels','http://127.0.0.1:8794/channels.html'),
    ('Vercel /api/revenue','https://tools.highkingflower.com/api/revenue'),
]
try:
    import urllib.request
    for label,url in endpoints:
        try:
            req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            resp=urllib.request.urlopen(req, timeout=15)
            code=resp.status
            body=resp.read(300).decode('utf-8','ignore')
            ok=200<=code<400 and len(body)>100
            log("  {}: HTTP{} ({}) {}".format(label, code, len(body), 'OK' if ok else 'BAD'))
            if not ok: issues.append("HTTP_BAD:{}:{}:{}".format(label, code, body[:80]))
        except Exception as ex:
            issues.append("HTTP_FAIL:{}:{}".format(label, str(ex)[:80]))
            log("  {}: FAIL {}".format(label, ex))
except ImportError:
    log("  urllib not available, skip http checks")

# 4. db.json idempotency
log("4/6 orders dedup")
try:
    d=json.load(open('/opt/bingdashan/data/db.json'))
    orders=d.get('orders',[])
    paid=[o for o in orders if o.get('paid') is True]
    c=Counter()
    for o in paid:
        k=str(o.get('out_trade_no','') or '')
        if k: c[k]+=1
    dups=[k for k,v in c.items() if v>1]
    log("  total_orders={} paid={} dup_notify_keys={}".format(len(orders), len(paid), len(dups)))
    if dups:
        issues.append("DUPLICATE_NOTIFY:keys={}".format(str(dups)[:100]))
        fixes.append("REVIEW_DUPLICATES:{}".format(len(dups)))
except Exception as e:
    issues.append("DB_READ_FAIL:{}".format(str(e)[:80]))

# 5. timer last run
log("5/6 timer last run")
last=None
try:
    lines=open(LOG, 'r', encoding='utf-8', errors='ignore').readlines()[-50:]
    for ln in reversed(lines):
        if '=== reconcile' in ln or '=== 全量自检' in ln:
            last=ln.strip()[:60]; break
    log("  last: {}".format(last or 'never'))
    if not last: issues.append("NEVER_RUN")
except: pass

# 6. file perms
log("6/6 perms")
for path in ['/etc/bingdashan-cn/alipay_priv.pem']:
    try:
        st=os.stat(path)
        mode=oct(st.st_mode)[-3:]
        log("  {}: mode={}".format(path, mode))
        if mode != '600':
            issues.append("BAD_PERM:{}:{}".format(path, mode))
            subprocess.call(['chmod','600',path])
            fixes.append("FIXED_PERM:{}:600".format(path))
            log("  fixed to 600")
    except: pass

log("=== 全量自检 done: {} issues, {} fixes applied ===".format(len(issues), len(fixes)))
if issues:
    log("ISSUES:")
    for i in issues: log("  - " + i)
sys.exit(0 if not issues else 1)

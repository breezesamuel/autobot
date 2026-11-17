#!/usr/bin/env python3
"""Code quality scan for C7~C12 modules + alipay.js route coverage"""
import json, os, sys, subprocess
from datetime import datetime

ROOT='F:/2026/24xs/02_交付物/channels/gumroad-product-1/tool-station-server-pro'
CHS=['reportexport','strategyapi','marketdata','strategyhosting','overfitcheck','whitebox','papercombo','quantcompute','quantannual']
LOG='/var/log/bingdashan/code_scan.log'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[SCAN][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Code Quality Scan start ===")
issues=[]
for ch in CHS:
    lib=os.path.join(ROOT, 'lib', '{}.js'.format(ch))
    if not os.path.exists(lib):
        issues.append("{}: lib/{}.js missing".format(ch,ch))
        continue
    # syntax check
    r=subprocess.run(['node','--check',lib], capture_output=True, text=True)
    if r.returncode!=0:
        issues.append("{}: SYNTAX_ERROR: {}{}".format(ch, r.stdout[:100], r.stderr[:100]))
    else:
        log("  {} syntax OK".format(ch))
    # check exports (onRequest must be exported)
    src=open(lib,'r',encoding='utf-8').read()
    checks={
        'module.exports': 'exports onRequest',
        'ADMIN_SECRET':'auth gate',
        'hasStore()': 'store check',
        'okRef(ref)':'ref validation',
        'complianceFooter':'disclaimer',
    }
    for kw,label in checks.items():
        if kw not in src:
            issues.append("{}: missing '{}' ({})".format(ch,kw,label))
        else:
            log("  {} has {}".format(ch,label))
# also check alipay.js route coverage for all C7-C12
alipay=os.path.join(ROOT,'api','alipay.js')
if os.path.exists(alipay):
    al_src=open(alipay,'r',encoding='utf-8').read()
    for ch in ['overfitcheck','whitebox','papercombo','quantcompute','quantannual']:
        if '/api/'+ch not in al_src:
            issues.append("alipay.js: missing route /api/{}".format(ch))
        else:
            log("  alipay.js has /api/{}".format(ch))
# check vercel.json rewrites
vc_path=os.path.join(ROOT,'vercel.json')
if os.path.exists(vc_path):
    try:
        vc=json.load(open(vc_path,'r'))
        srcs=[r.get('source','') for r in vc.get('rewrites',[])]
        for ch in ['overfitcheck','whitebox','papercombo','quantcompute','quantannual']:
            pat='/api/'+ch
            if not any(pat in s for s in srcs):
                issues.append("vercel.json: missing rewrite for {}".format(ch))
            else:
                log("  vercel.json has rewrite for {}".format(ch))
    except Exception as e:
        issues.append("vercel.json parse error: {}".format(e))
log("=== scan done: issues={} ===".format(len(issues)))
if issues:
    for i in issues: log("  - " + i)
sys.exit(0 if not issues else 1)

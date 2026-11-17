#!/usr/bin/env python3
"""Code quality scan v2 (runs ON CN server, not local path)"""
import json, os, sys, subprocess
from datetime import datetime

ROOT='/www/wwwroot/tools-cn.highkingflower.com'
CHS=['reportexport','strategyapi','marketdata','strategyhosting','overfitcheck','whitebox','papercombo','quantcompute','quantannual']
LOG='/var/log/bingdashan/code_scan.log'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[SCAN][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Code Quality Scan v2 (on CN) ===")
issues=[]
for ch in CHS:
    lib=os.path.join(ROOT, 'lib', '{}.js'.format(ch))
    if not os.path.exists(lib):
        issues.append("{}: lib/{}.js missing".format(ch,ch))
        continue
    rc=subprocess.call(['node','--check',lib], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if rc!=0:
        issues.append("{}: SYNTAX_ERROR".format(ch))
    else:
        log("  {} syntax OK".format(ch))
    src=open(lib,'r',encoding='utf-8').read()
    checks={'module.exports':'exports onRequest','ADMIN_SECRET':'auth gate','hasStore()':'store check','okRef(ref)':'ref validation','complianceFooter':'disclaimer'}
    for kw,label in checks.items():
        if kw not in src:
            issues.append("{}: missing {}".format(ch,label))
log("=== scan done: issues={} ===".format(len(issues)))
if issues:
    for i in issues: log("  - " + i)
sys.exit(0 if not issues else 1)

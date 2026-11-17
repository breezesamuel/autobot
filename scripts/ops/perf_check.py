#!/usr/bin/env python3
"""丙大山 · 自动回测健康检查 + 性能优化 (定时自检引擎)"""
import json, os, sys, subprocess, time
from datetime import datetime

LOG='/var/log/bingdashan/perf_check.log'
ROOT='/www/wwwroot/tools-cn.highkingflower.com'
BL='/opt/bingdashan/data/billing'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[PERF][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Performance Check start ===")

# 1. 检查CN进程数/内存/CPU压力
try:
    r=subprocess.run(['ps','aux'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    lines=r.stdout.strip().split('\n')
    proc_count=len([l for l in lines if 'node' in l or 'python' in l])
    log("  process count: {}".format(proc_count))
except Exception as e:
    log("WARN ps check: {}".format(e))

# 2. 检查 Node.js 端口绑定
r2=subprocess.run(['ss','-tlnp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
if ':8794' in r2.stdout:
    log("  port 8794 OK")
else:
    log("CRITICAL: port 8794 NOT listening!")

# 3. 关键 API 响应时间测试
endpoints=[
    ('health','http://127.0.0.1:8794/api/revenue'),
    ('collection_page','http://127.0.0.1:8794/revenue-collection.html'),
    ('honest_page','http://127.0.0.1:8794/revenue-honest.html'),
]
for name,url in endpoints:
    try:
        t0=time.time()
        import urllib.request
        req=urllib.request.Request(url, headers={'User-Agent':'BingDashan-PerfCheck/1.0'})
        resp=urllib.request.urlopen(req, timeout=10)
        dt=(time.time()-t0)*1000
        size=len(resp.read())
        log("  {} {}ms {}B".format(name, int(dt), size))
    except Exception as e:
        log("ERROR {}: {}".format(name, str(e)[:60]))

# 4. 检查关键文件完整性
checks=[
    ('engine_v7.py','/opt/bingdashan/scripts/ops/engine_v7.py'),
    ('auto_outreach.py','/opt/bingdashan/scripts/ops/auto_outreach.py'),
    ('visitor_insight.py','/opt/bingdashan/scripts/ops/visitor_insight.py'),
    ('lead_outreach.py','/opt/bingdashan/scripts/ops/lead_outreach.py'),
    ('alipay.js',os.path.join(ROOT,'api','alipay.js')),
    ('channels.html',os.path.join(ROOT,'channels.html')),
]
for label,path in checks:
    exists=os.path.exists(path)
    sz=os.path.getsize(path) if exists else 0
    status="OK {}B".format(sz) if exists else "MISSING"
    log("  {} : {}".format(label, status))
    if not exists:
        log("  WARNING: {} missing!".format(label))

# 5. 检查台账文件可读性
for fn in ['outreach_ledger.json','corporate_899.json']:
    p=os.path.join(BL,fn)
    try:
        d=json.load(open(p,'r',encoding='utf-8'))
        cnt=len(d) if isinstance(d,list) else len(d.get('items',d.get('orders',[])))
        log("  {} : OK {} records".format(fn,cnt))
    except Exception as e:
        log("  {} ERR: {}".format(fn,str(e)[:60]))

# 6. 磁盘空间详细
try:
    r3=subprocess.run(['df','-h','/'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    for ln in r3.stdout.strip().split('\n')[1:]:
        parts=ln.split()
        if len(parts)>=5:
            log("  disk: total={} used={} avail={} use%={}".format(parts[1],parts[2],parts[3],parts[4]))
except: pass

log("=== Performance Check done ===")
print("PERF_CHECK_DONE")

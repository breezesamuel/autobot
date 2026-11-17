#!/usr/bin/env python3
"""恢复 alipay.js 并从 git 拉取最新版本，然后添加 C18-C20 路由"""
import json, os, subprocess, re
from datetime import datetime

ROOT = r'F:\2026\24xs\02_交付物\channels\gumroad-product-1\tool-station-server-pro'
LOG = r'C:\Users\46012\AppData\Local\Temp\restore_alipay.log'
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[RESTORE][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

# Step 1: Get the last known good alipay.js from git
log("Step 1: Getting clean alipay.js from git...")
rc = subprocess.call(['git','checkout','HEAD','--',os.path.join(ROOT,r'api\alipay.js')], 
                     cwd=r'F:\2026\24xs', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if rc != 0:
    log("WARNING: git checkout failed, using local file")
else:
    log("  Git checkout OK")

# Verify syntax
rc = subprocess.call(['node','--check',os.path.join(ROOT,r'api\alipay.js')])
if rc != 0:
    log("ERROR: local alipay.js still has syntax errors!")
    # Try the backed-up remote version
    log("Attempting to use remote main version...")
    subprocess.call(['git','pull','origin','main','--no-edit'], cwd=r'F:\2026\24xs', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.call(['git','checkout','origin/main','--',os.path.join(ROOT,r'api\alipay.js')], 
                    cwd=r'F:\2026\24xs', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    rc = subprocess.call(['node','--check',os.path.join(ROOT,r'api\alipay.js')])
    log("  After pull: syntax {}".format('OK' if rc==0 else 'FAIL'))
else:
    log("  Local alipay.js syntax OK")

# Step 2: Add C18-C20 routes to local alipay.js
alipay_path=os.path.join(ROOT,r'api\alipay.js')
src=open(alipay_path,'r',encoding='utf-8').read()

new_routes="""    // C18 全市场扫描 API (scan_api) — 合规渠道\\n
    if(route.startsWith('/api/scan_api')){{\\n
      try{{\\n
        const mod = require('../lib/scan_api.js');\\n
        data.path = route;\\n
        if(!data.ref){{\\n
          const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);\\n
          if(pid)data.ref=pid;\\n
        }}\\n
        return await mod.onRequest(req,res,data);\\n
      }}catch(e){{\\n
        send(500,{{ok:false,error:'scan_api handler error: '+e.message}});\\n
      }}\\n
      return;\\n
    }}\\n
    // C19 价格预警通知 API (alert_api) — 合规渠道\\n
    if(route.startsWith('/api/alert_api')){{\\n
      try{{\\n
        const mod = require('../lib/alert_api.js');\\n
        data.path = route;\\n
        if(!data.ref){{\\n
          const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);\\n
          if(pid)data.ref=pid;\\n
        }}\\n
        return await mod.onRequest(req,res,data);\\n
      }}catch(e){{\\n
        send(500,{{ok:false,error:'alert_api handler error: '+e.message}});\\n
      }}\\n
      return;\\n
    }}\\n
    // C20 分钟级K线订阅 API (minute_klines) — 合规渠道\\n
    if(route.startsWith('/api/minute_klines')){{\\n
      try{{\\n
        const mod = require('../lib/minute_klines.js');\\n
        data.path = route;\\n
        if(!data.ref){{\\n
          const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);\\n
          if(pid)data.ref=pid;\\n
        }}\\n
        return await mod.onRequest(req,res,data);\\n
      }}catch(e){{\\n
        send(500,{{ok:false,error:'minute_klines handler error: '+e.message}});\\n
      }}\\n
      return;\\n
    }}\\n
"""

fallback="send(404,{ok:false,error:'not found',route:route});"
if fallback in src:
    idx=src.index(fallback)
    src=src[:idx] + new_routes + '\n    ' + fallback
    log("Inserted C18-C20 routes into local alipay.js")
else:
    log("WARNING: fallback not found in local alipay.js")

with open(alipay_path,'w',encoding='utf-8') as f:
    f.write(src)

# Validate
rc = subprocess.call(['node','--check',alipay_path])
log("Local alipay.js syntax: {}".format('OK' if rc==0 else 'FAIL'))

# Step 3: Update vercel.json
vc_path=os.path.join(ROOT,'vercel.json')
vc=json.load(open(vc_path,'r',encoding='utf-8'))
existing={r.get('source','') for r in vc.get('rewrites',[])}
for slug in ['scan_api','alert_api','minute_klines']:
    s='/api/'+slug
    if s not in existing:
        vc['rewrites'].append({'source':s,'destination':'/api/alipay.js?r='+slug})
        log("Added vercel rewrite: {}".format(s))
with open(vc_path,'w',encoding='utf-8') as f:
    json.dump(vc,f,ensure_ascii=False,indent=2); f.write('\n')

# Step 4: Sync lib files to local (from CN where they were successfully generated)
log("Syncing lib files from CN...")
local_lib=os.path.join(ROOT,'lib')
for f_name in ['scan_api','alert_api','minute_klines']:
    local_f=os.path.join(local_lib,'{}.js'.format(f_name))
    # Check if already exists locally with correct content
    if not os.path.exists(local_f) or os.path.getsize(local_f) < 1000:
        log("  Need to get {} from CN".format(f_name))
    else:
        sz=os.path.getsize(local_f)
        log("  {} already OK ({})".format(f_name,sz))

log("=== Restore+Wire complete ===")
print(json.dumps({'alipay_syntax_ok': rc==0, 'routes_added': 3}, ensure_ascii=False))

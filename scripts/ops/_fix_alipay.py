#!/usr/bin/env python3
"""Fix: 把 alipay.js 里的字面量 \\n 替换成真实换行，然后重新插入 C18-C20 路由"""
import re

path = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js'
src = open(path, 'r', encoding='utf-8').read()

# First: fix any literal \n in the source (from previous bad insertion)
# These appear as backslash-n in the actual file content
# Replace literal '\n' (two chars: backslash + n) with actual newline
src = src.replace('\\n', '\n')

# Check if routes already exist
for slug in ['scan_api', 'alert_api', 'minute_klines']:
    if "route.startsWith('/api/" + slug + "')" in src:
        print("Route for {} already exists, skipping".format(slug))

# Build the route insertion block with REAL newlines
new_block = """    // C18 全市场扫描 API — 合规渠道
    if(route.startsWith('/api/scan_api')){
      try{
        const mod = require('../lib/scan_api.js');
        data.path = route;
        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}
        return await mod.onRequest(req,res,data);
      }catch(e){send(500,{ok:false,error:'scan_api handler error: '+e.message});}
      return;
    }
    // C19 价格预警通知 API — 合规渠道
    if(route.startsWith('/api/alert_api')){
      try{
        const mod = require('../lib/alert_api.js');
        data.path = route;
        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}
        return await mod.onRequest(req,res,data);
      }catch(e){send(500,{ok:false,error:'alert_api handler error: '+e.message});}
      return;
    }
    // C20 分钟级K线订阅 API — 合规渠道
    if(route.startsWith('/api/minute_klines')){
      try{
        const mod = require('../lib/minute_klines.js');
        data.path = route;
        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}
        return await mod.onRequest(req,res,data);
      }catch(e){send(500,{ok:false,error:'minute_klines handler error: '+e.message});}
      return;
    }
"""

target = "send(404,{ok:false,error:'not found',route:route});"
if target in src:
    idx = src.index(target)
    # Check if we already have these routes
    if "/api/scan_api" not in src and "/api/alert_api" not in src and "/api/minute_klines" not in src:
        src = src[:idx] + new_block + '\n    ' + target
        print("Inserted 3 new routes before 404 fallback")
    else:
        print("Routes already present, just fixing newline issue")
else:
    print("ERROR: could not find fallback")
    import sys; sys.exit(1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
print("Written {} bytes".format(len(src)))

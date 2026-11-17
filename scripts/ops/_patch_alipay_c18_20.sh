#!/usr/bin/env bash
# 在 CN 的 alipay.js 里添加 C18/C19/C20 路由
set -euo pipefail
ALIPAY=/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js
TMP=/tmp/patch_alipay.py

cat > $TMP <<'PY'
import sys, re

path = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js'
src = open(path, 'r', encoding='utf-8').read()

NEW_ROUTES = '''    // C18 全市场扫描 API (scan_api) — 合规渠道\\n
    if(route.startsWith('/api/scan_api')){\\n
      try{\\n
        const mod = require('../lib/scan_api.js');\\n
        data.path = route;\\n
        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}\\n
        return await mod.onRequest(req,res,data);\\n
      }catch(e){send(500,{ok:false,error:'scan_api handler error: '+e.message});}\\n
      return;\\n
    }\\n
    // C19 价格预警通知 API (alert_api) — 合规渠道\\n
    if(route.startsWith('/api/alert_api')){\\n
      try{\\n
        const mod = require('../lib/alert_api.js');\\n
        data.path = route;\\n
        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}\\n
        return await mod.onRequest(req,res,data);\\n
      }catch(e){send(500,{ok:false,error:'alert_api handler error: '+e.message});}\\n
      return;\\n
    }\\n
    // C20 分钟级K线订阅 API (minute_klines) — 合规渠道\\n
    if(route.startsWith('/api/minute_klines')){\\n
      try{\\n
        const mod = require('../lib/minute_klines.js');\\n
        data.path = route;\\n
        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}\\n
        return await mod.onRequest(req,res,data);\\n
      }catch(e){send(500,{ok:false,error:'minute_klines handler error: '+e.message});}\\n
      return;\\n
    }\\n
'''

# Insert before the final send(404 fallback
target = "send(404,{ok:false,error:'not found',route:route});"
if target in src:
    idx = src.index(target)
    src = src[:idx] + NEW_ROUTES + '\n    ' + target
    log_msg = "Inserted {} routes".format(3)
else:
    # Find last occurrence
    matches = [m.start() for m in re.finditer(r"send\(404,", src)]
    if matches:
        idx = matches[-1]
        src = src[:idx] + NEW_ROUTES + '\n    ' + src[idx:]
        log_msg = "Inserted {} routes (alt)".format(3)
    else:
        print("ERROR: could not find fallback"); sys.exit(1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)
print(log_msg)
PY

python3 $TMP
echo "alipay.js patched"

# Also patch vercel.json
VC=/www/wwwroot/tools-cn.highkingflower.com/vercel.json
python3 - <<'PY2'
import json
vc=json.load(open('/www/wwwroot/tools-cn.highkingflower.com/vercel.json','r'))
existing={r.get('source','') for r in vc.get('rewrites',[])}
added=[]
for slug in ['scan_api','alert_api','minute_klines']:
    s='/api/'+slug
    if s not in existing:
        vc['rewrites'].append({'source':s,'destination':'/api/alipay.js?r='+slug})
        added.append(s)
with open('/www/wwwroot/tools-cn.highkingflower.com/vercel.json','w') as f:
    json.dump(vc,f,ensure_ascii=False,indent=2);f.write('\n')
print("vercel.json: added {}".format(added))
PY2

echo ""
echo "=== Verify ==="
node --check /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js && echo "alipay.js syntax OK"
systemctl restart bingdashan-cn && sleep 3
echo "service: $(systemctl is-active bingdashan-cn)"
echo ""
echo "=== API Test ==="
for slug in scan_api alert_api minute_klines; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=test_xyz")
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK price=¥'+str(d.get('price_yuan','?')) if d.get('ok') else 'FAIL:'+str(d.get('error','')))" 2>/dev/null || echo ERR)
  echo "  /api/$slug -> $ok"
done
echo ""
echo "Done"

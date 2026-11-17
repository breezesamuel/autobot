#!/usr/bin/env bash
set -euo pipefail
python3 /tmp/_fix.py 2>&1
echo ""
node --check /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js && echo "alipay.js syntax OK" || echo "FAIL"
systemctl restart bingdashan-cn && sleep 3
echo "service: $(systemctl is-active bingdashan-cn)"
echo ""
echo "=== API Tests ==="
for slug in scan_api alert_api minute_klines; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=test_xyz")
  python3 -c "
import json,sys
d=json.loads('$r')
if d.get('ok'): print('  /api/$slug -> OK price=¥'+str(d.get('price_yuan','?')))
else: print('  /api/$slug -> FAIL: '+str(d.get('error','unknown')))
" 2>/dev/null || echo "  /api/$slug -> ERR (parse failed)"
done
echo ""
echo "Done"

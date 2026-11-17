#!/usr/bin/env bash
set -euo pipefail
echo "=== Deploy C18-C20 to CN ==="
B=/www/wwwroot/tools-cn.highkingflower.com
cp /tmp/gen_modules.sh 2>/dev/null || true
scp -q "F:/2026/24xs/02_交付物/channels/gumroad-product-1/tool-station-server-pro/api/alipay.js" "$B/api/alipay.js" && echo "  alipay.js synced"
scp -q "F:/2026/24xs/02_交付物/channels/gumroad-product-1/tool-station-server-pro/vercel.json" "$B/vercel.json" && echo "  vercel.json synced"
scp -q "F:/2026/24xs/02_交付物/channels/gumroad-product-1/tool-station-server-pro/channels.html" "$B/channels.html" && echo "  channels.html synced"
scp -q "F:/2026/24xs/02_交付物/channels/gumroad-product-1/tool-station-server-pro/lib/scan_api.js" "$B/lib/scan_api.js" && echo "  scan_api.js synced"
scp -q "F:/2026/24xs/02_交付物/channels/gumroad-product-1/tool-station-server-pro/lib/alert_api.js" "$B/lib/alert_api.js" && echo "  alert_api.js synced"
scp -q "F:/2026/24xs/02_交付物/channels/gumroad-product-1/tool-station-server-pro/lib/minute_klines.js" "$B/lib/minute_klines.js" && echo "  minute_klines.js synced"
echo ""
echo "=== Restart + Test ==="
systemctl restart bingdashan-cn && sleep 3
node --check $B/api/alipay.js && echo "  alipay.js syntax OK"
for slug in scan_api alert_api minute_klines; do
  node --check $B/lib/$slug.js && echo "  $slug.js syntax OK"
done
echo ""
echo "=== API Tests ==="
for slug in scan_api alert_api minute_klines; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=test_c18")
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else 'FAIL:'+str(d.get('error','')))" 2>/dev/null || echo ERR)
  price=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('¥'+str(d.get('price_yuan','?')))" 2>/dev/null || echo '?')
  echo "  /api/$slug -> $ok $price"
done
echo ""
echo "=== Final Status ==="
tail -3 /var/log/bingdashan/engine.log
systemctl list-timers --all 2>/dev/null | grep "bd-engine" | head -1

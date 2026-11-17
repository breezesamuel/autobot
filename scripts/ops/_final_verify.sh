#!/usr/bin/env bash
set -euo pipefail
ALIPAY=/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js
echo "=== Alipay.js check ==="
node --check $ALIPAY && echo "SYNTAX OK" || echo "SYNTAX FAIL"
systemctl restart bingdashan-cn && sleep 3
echo "service: $(systemctl is-active bingdashan-cn)"
echo ""
echo "=== C7 (overfitcheck) still works ==="
curl -s "http://127.0.0.1:8794/api/overfitcheck?action=rate&ref=t" | python3 -c "import json,sys;d=json.load(sys.stdin);print('C7:', 'OK' if d.get('ok') else 'FAIL', 'price=', d.get('price_yuan','?'))" 2>/dev/null || echo "C7 ERR"
echo ""
echo "=== C18 scan_api ==="
curl -s "http://127.0.0.1:8794/api/scan_api?action=rate&ref=t" | head -c 120
echo ""
echo "=== C19 alert_api ==="
curl -s "http://127.0.0.1:8794/api/alert_api?action=rate&ref=t" | head -c 120
echo ""
echo "=== C20 minute_klines ==="
curl -s "http://127.0.0.1:8794/api/minute_klines?action=rate&ref=t" | head -c 120
echo ""
echo ""
echo "=== Engine log tail ==="
tail -3 /var/log/bingdashan/engine.log
echo ""
echo "=== Timer status ==="
systemctl list-timers --all 2>/dev/null | grep "bd-engine" | head -1
echo "done"

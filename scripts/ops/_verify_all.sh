#!/usr/bin/env bash
set -euo pipefail
systemctl restart bingdashan-cn && sleep 3
echo "service: $(systemctl is-active bingdashan-cn)"
echo ""
for slug in reportexport strategyapi marketdata strategyhosting overfitcheck whitebox papercombo quantcompute quantannual; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=t")
  echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('  $slug:', 'OK' if d.get('ok') else 'FAIL', '| price=', d.get('price_yuan','?'))";
done
echo ""
echo "=== C18-C20 ==="
for slug in scan_api alert_api minute_klines; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=t")
  echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('  $slug:', 'OK' if d.get('ok') else 'FAIL: '+str(d.get('error','')), '| price=', d.get('price_yuan','?'))";
done
echo ""
tail -2 /var/log/bingdashan/engine.log
systemctl list-timers --all 2>/dev/null | grep bd-engine | head -1

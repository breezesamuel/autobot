#!/usr/bin/env bash
set -euo pipefail
systemctl restart bingdashan-cn && sleep 3
echo "service: $(systemctl is-active bingdashan-cn)"
echo ""
for slug in scan_api alert_api minute_klines overfitcheck reportexport; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=t")
  python3 -c "import json,sys;d=json.load(sys.stdin);print('  $slug -> price=¥'+str(d.get('price_yuan','?'))+' ok='+str(d.get('ok')))" <<< "$r" 2>/dev/null || echo "  $slug -> ERR"
done
echo ""
echo "=== Engine log ==="
tail -5 /var/log/bingdashan/engine.log
echo ""
echo "=== Timer next ==="
systemctl list-timers --all 2>/dev/null | grep bd-engine | head -1

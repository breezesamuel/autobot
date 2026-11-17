#!/usr/bin/env bash
# 验证 C18-C20 全部上线
set -euo pipefail
echo "=== Syntax Check ==="
for f in scan_api alert_api minute_klines; do
  node --check /www/wwwroot/tools-cn.highkingflower.com/lib/$f.js && echo "  $f.js OK" || echo "  $f.js FAIL"
done
echo ""
echo "=== Restart Service ==="
systemctl restart bingdashan-cn && sleep 2
echo "  service: $(systemctl is-active bingdashan-cn)"
echo ""
echo "=== API Rate Test ==="
for slug in scan_api alert_api minute_klines; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=test_c18")
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else 'FAIL')" 2>/dev/null || echo ERR)
  price=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('¥'+str(d.get('price_yuan','?')))" 2>/dev/null || echo '?')
  echo "  /api/$slug -> $ok $price"
done
echo ""
echo "=== Engine Log Tail ==="
tail -3 /var/log/bingdashan/engine.log
echo ""
echo "=== Timer Status ==="
systemctl list-timers --all 2>/dev/null | grep "bd-engine" | head -1

#!/usr/bin/env bash
set -euo pipefail
echo "=== Restart + C13-C17 API test ==="
systemctl restart bingdashan-cn && sleep 3
node --check /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js && echo "syntax OK"
for slug in alternative_data backtest_history co_brand_product custom_indicators custom_integration; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=test_xxx")
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('ok'),'end=')" 2>/dev/null || echo ERR)
  price=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('¥'+str(d.get('price_yuan','?')))" 2>/dev/null || echo '?')
  echo "  /api/$slug -> $ok $price"
done
echo ""
echo "=== Engine status ==="
tail -3 /var/log/bingdashan/engine.log
echo ""
echo "=== Timer status ==="
systemctl list-timers --all 2>/dev/null | grep "bd-engine" | head -1

#!/usr/bin/env bash
# 最终验证：所有 C3-C20 渠道都在线
set -euo pipefail
echo "=== 最终全量验证 ==="
systemctl is-active bingdashan-cn
node --check /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js && echo "alipay.js OK"
for slug in reportexport strategyapi marketdata strategyhosting overfitcheck whitebox papercombo quantcompute quantannual scan_api alert_api minute_klines; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=test_final")
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK price=¥'+str(d.get('price_yuan','?')))" 2>/dev/null || echo "ERR")
  echo "  $slug -> $ok"
done
echo ""
echo "=== Engine status ==="
tail -2 /var/log/bingdashan/engine.log
echo ""
echo "=== Timer next run ==="
systemctl list-timers --all 2>/dev/null | grep bd-engine | head -1
echo "=== ALL DONE ==="

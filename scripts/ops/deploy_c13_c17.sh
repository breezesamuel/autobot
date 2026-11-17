#!/usr/bin/env bash
# 把 C13-C17 部署到 CN + Vercel + 最终验证
set -euo pipefail
echo "=== 部署 C13-C17 到 CN ==="
B="/www/wwwroot/tools-cn.highkingflower.com"
for f in lib/alternative_data.js lib/backtest_history.js lib/co_brand_product.js lib/custom_indicators.js lib/custom_integration.js api/alipay.js vercel.json channels.html; do
  scp -q "F:/2026/24xs/02_交付物/channels/gumroad-product-1/tool-station-server-pro/$f" "aliyun:$B/$f" 2>/dev/null && echo "  synced $f" || echo "  skip $f"
done
echo ""
echo "=== 语法校验 + 重启 ==="
node --check "$B/lib/alternative_data.js" && node --check "$B/lib/backtest_history.js" && node --check "$B/lib/co_brand_product.js" && node --check "$B/lib/custom_indicators.js" && node --check "$B/lib/custom_integration.js" && node --check "$B/api/alipay.js" && echo "  syntax OK"
systemctl restart bingdashan-cn && sleep 2
echo "  service: $(systemctl is-active bingdashan-cn)"
echo ""
echo "=== C13-C17 API 测试 ==="
for slug in alternative_data backtest_history co_brand_product custom_indicators custom_integration; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=test_c13")
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else 'FAIL')" 2>/dev/null || echo "ERR")
  price=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('¥'+str(d.get('price_yuan','?')))" 2>/dev/null || echo "?")
  echo "  /api/$slug -> $ok $price"
done
echo ""
echo "=== Vercel deploy ==="
cd "F:/2026/24xs/02_交付物/channels/gumroad-product-1/tool-station-server-pro"
vercel deploy --prod --project bingdashan-pain-tools --scope solmount --yes 2>&1 | grep -E "Production|ready|error" | head -3 || echo "(deploy skipped or error)"
echo ""
echo "=== 最终状态 ==="
ssh aliyun "systemctl list-timers --all 2>/dev/null | grep 'bd-engine'" 2>&1 | head -3
ssh aliyun "tail -3 /var/log/bingdashan/engine.log" 2>&1
echo "done"

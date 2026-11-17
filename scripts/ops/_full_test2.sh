#!/usr/bin/env bash
set -euo pipefail
echo "=== 全量渠道验收测试 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "服务: $(systemctl is-active bingdashan-cn)"
echo "模块数: $(ls /www/wwwroot/tools-cn.highkingflower.com/lib/*.js 2>/dev/null | wc -l)"
echo "alipay.js: $(wc -c < /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js) bytes"
echo ""

# Get all slugs
slugs=$(grep -oP "route\.startsWith\('/api/\K[^']+" /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js 2>/dev/null | sort -u)
count=$(echo "$slugs" | wc -l)
echo "路由总数: $count"
echo ""

pass=0; fail=0
for slug in $slugs; do
  r=$(curl -s --max-time 5 "http://127.0.0.1:8794/api/$slug?action=rate&ref=t" 2>/dev/null || echo '{"ok":false}')
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else 'FAIL')" 2>/dev/null || echo ERR)
  price=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('¥'+str(d.get('price_yuan','?')))" 2>/dev/null || echo '?')
  if [ "$ok" = "OK" ]; then pass=$((pass+1)); else fail=$((fail+1)); fi
done
echo "通过: $pass | 失败: $fail | 总计: $count"
echo ""

# High-value samples
echo "=== 高价值通道 ==="
for slug in rl_trader ml_backtest tick_data onchain_data whale_tracker lstm_forecast paper_trade_live monte_carlo genetic_optimizer bayesian_optimization portfolio_builder risk_parity attribution excel_report powerpoint_deck pdf_professional; do
  r=$(curl -s --max-time 5 "http://127.0.0.1:8794/api/$slug?action=rate&ref=t" 2>/dev/null || echo '{}')
  price=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('¥'+str(d.get('price_yuan','?')))" 2>/dev/null || echo '?')
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else 'FAIL')" 2>/dev/null || echo ERR)
  echo "  $slug: $ok $price"
done
echo ""
echo "=== Timer ==="
systemctl list-timers --all 2>/dev/null | grep "bd-engine" | head -1
echo "DONE"

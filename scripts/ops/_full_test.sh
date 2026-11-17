#!/usr/bin/env bash
# Final comprehensive test of all channels
set -euo pipefail
echo "=============================================="
echo "丙大山 · 全量渠道验收测试"
echo "生成时间: $(date '+%Y-%m-%d %H:%M:%S CST')"
echo "=============================================="
echo ""

echo "=== 服务状态 ==="
echo "bingdashan-cn: $(systemctl is-active bingdashan-cn)"
echo "磁盘: $(df -h / | tail -1 | awk '{print $5}') 使用率"
echo ""

echo "=== 模块统计 ==="
echo "lib/*.js 数量: $(ls /www/wwwroot/tools-cn.highkingflower.com/lib/*.js 2>/dev/null | wc -l)"
echo "alipay.js 大小: $(wc -c < /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js) bytes"
echo "vercel.json rewrites: $(python3 -c 'import json;d=json.load(open("/www/wwwroot/tools-cn.highkingflower.com/vercel.json"));print(len(d.get("rewrites",[])))'" 2>/dev/null || echo '?')"
echo ""

echo "=== 全部渠道健康检查 (按价格分组) ==="
# Get all slugs from alipay.js
slugs=$(grep -oP "route\.startsWith\('/api/\K[^']+" /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js 2>/dev/null | sort -u)
echo "发现 ${#slugs[@]} 个路由"
echo ""

pass=0; fail=0; total=0
for slug in $slugs; do
  total=$((total+1))
  r=$(curl -s --max-time 5 "http://127.0.0.1:8794/api/$slug?action=rate&ref=test_xxx" 2>/dev/null || echo '{"ok":false}')
  ok=$(echo "$r" | python3 -c "import json,sys; print('OK' if json.load(sys.stdin).get('ok') else 'FAIL')" 2>/dev/null || echo "ERR")
  price=$(echo "$r" | python3 -c "import json,sys; print('¥'+str(json.load(sys.stdin).get('price_yuan','?')))" 2>/dev/null || echo '?')
  if [ "$ok" = "OK" ]; then
    pass=$((pass+1))
    printf "  ✅ %-30s %s\n" "$slug" "$price"
  else
    fail=$((fail+1))
    printf "  ❌ %-30s %s\n" "$slug" "$price"
  fi
done

echo ""
echo "=============================================="
echo "通过: $pass/$total | 失败: $fail"
echo "=============================================="
echo ""
echo "=== 高价值通道抽样测试 ==="
for slug in rl_trader ml_backtest tick_data onchain_data whale_tracker lstm_forecast paper_trade_live monte_carlo genetic_optimizer bayesian_optimization portfolio_builder risk_parity; do
  r=$(curl -s --max-time 5 "http://127.0.0.1:8794/api/$slug?action=rate&ref=t" 2>/dev/null || echo '{}')
  price=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('¥'+str(d.get('price_yuan','?')))" 2>/dev/null || echo '?')
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else 'FAIL')" 2>/dev/null || echo 'ERR')
  echo "  $slug: $ok $price"
done
echo ""
echo "=== Timer 状态 ==="
systemctl list-timers --all 2>/dev/null | grep -E "bd-engine|bd-revenue|bd-perf|bd-trial" | head -4
echo ""
echo "DONE"

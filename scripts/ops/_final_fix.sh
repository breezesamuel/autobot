#!/usr/bin/env bash
set -euo pipefail
echo "=== Fix timers + Final verification ==="
# Enable all timers
for t in bd-engine-hourly bd-revenue-watch bd-perf-backup bd-trial-winback bd-manual8-watch bd-pay-email-watch; do
  systemctl enable --now ${t}.timer 2>/dev/null && echo "  enabled $t" || echo "  $t skip"
done
sleep 2
echo ""
echo "=== Timer status ==="
systemctl list-timers --all 2>/dev/null | grep -E "bd-|bingdashan" | head -8
echo ""
echo "=== Service status ==="
for s in bingdashan-cn bd-engine-hourly bd-revenue-watch bd-perf-backup; do
  echo "  $s: $(systemctl is-active $s 2>/dev/null || echo unknown)"
done
echo ""
echo "=== API smoke test (sample 10 channels) ==="
for slug in overfitcheck whitebox papercombo quantcompute quantannual scan_api alert_api minute_klines rl_trader ml_backtest tick_data onchain_data whale_tracker lstm_forecast; do
  r=$(curl -s --max-time 5 "http://127.0.0.1:8794/api/$slug?action=rate&ref=t" 2>/dev/null || echo '{}')
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else 'FAIL')" 2>/dev/null || echo ERR)
  price=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('¥'+str(d.get('price_yuan','?')))" 2>/dev/null || echo '?')
  echo "  $slug -> $ok $price"
done
echo ""
echo "=== Final stats ==="
echo "Modules: $(ls /www/wwwroot/tools-cn.highkingflower.com/lib/*.js 2>/dev/null | wc -l)"
echo "Routes: $(grep -c \"route.startsWith('/api/\" /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js 2>/dev/null || echo 0)"
echo "Pending: $(python3 -c "import json;d=json.load(open('/opt/bingdashan/data/billing/outreach_ledger.json'));items=d if isinstance(d,list) else d.get('items',[]);p=[x for x in items if x.get('status') not in ('paid','collected','done','verified')];print(len(p),'orders')" 2>/dev/null)"
echo "Server time: $(date '+%Y-%m-%d %H:%M:%S CST')"
echo "=== DONE ==="

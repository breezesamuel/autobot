#!/usr/bin/env bash
set -euo pipefail
echo "=== 1. 跑一次真实对账 ==="
python3 /opt/bingdashan/scripts/reconcile_and_refresh.py 2>&1 | tail -20
echo ""
echo "=== 2. ops.log 最新 10 行 ==="
tail -10 /var/log/bingdashan/ops.log 2>/dev/null || echo "(无 log)"
echo ""
echo "=== 3. revenue-honest.html 当前现金数字 ==="
curl -s http://127.0.0.1:8794/revenue-honest.html | grep -oE '¥[0-9]+' | head -3 || echo "(解析失败)"
echo ""
echo "=== 4. 当前 db.json paid=true 订单数 ==="
python3 -c "import json; d=json.load(open('/opt/bingdashan/data/db.json')); orders=d.get('orders',[]); paid=[o for o in orders if o.get('paid')]; print('total_orders={} paid={} real_yuan={}'.format(len(orders), len(paid), sum(float(o.get('amount',0) or 0) for o in paid)))"
echo "done"

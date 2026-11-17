#!/usr/bin/env bash
# 最终端到端验证脚本 — 一次性检查所有关键组件
echo "=========================================="
echo "丙大山 · 24h 全自动系统 最终验证 (15:30 CST)"
echo "=========================================="
echo ""
echo "=== 1. Timer 状态 ==="
systemctl list-timers --all 2>/dev/null | grep -E "bd-engine|bd-revenue|bd-trial|bd-manual|bd-pay|bd-perf" | head -6
echo ""
echo "=== 2. Service 状态 ==="
for svc in bingdashan-cn bd-engine-hourly bd-revenue-watch bd-trial-winback bd-manual8-watch bd-pay-email-watch bd-perf-backup; do
  status=$(systemctl is-active $svc 2>/dev/null || echo "inactive")
  echo "  $svc: $status"
done
echo ""
echo "=== 3. HTTP 健康检查 ==="
for url in "http://127.0.0.1:8794/api/revenue" "http://127.0.0.1:8794/revenue-honest.html" "http://127.0.0.1:8794/revenue-collection.html"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
  echo "  $url -> HTTP $code"
done
echo ""
echo "=== 4. 真实营收数据 ==="
python3 -c "
import json, sys
try:
    d=json.load(open('/opt/bingdashan/data/db.json'))
    orders=d.get('orders',[])
    paid=[o for o in orders if o.get('paid') and float(o.get('amount',0) or 0)>5]
    print('  db.json total_orders={} paid_real_orders={}'.format(len(orders),len(paid)))
    print('  real_cash=¥{}'.format(sum(float(o.get('amount',0) or 0) for o in paid)))
except Exception as e: print('  ERR:',e)
bl='/opt/bingdashan/data/billing'
import os
for fn in ['outreach_ledger.json','corporate_899.json']:
    p=os.path.join(bl,fn)
    if os.path.exists(p):
        data=json.load(open(p))
        items=data if isinstance(data,list) else data.get('items',data.get('orders',[]))
        pending=[x for x in items if x.get('status') not in ('paid','collected','done','verified','approved')]
        amt=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in pending)
        print('  {} pending={}单 ¥{}'.format(fn,len(pending),int(amt)))
"
echo ""
echo "=== 5. 引擎最后运行日志 ==="
tail -3 /var/log/bingdashan/engine.log 2>/dev/null || echo "  (no engine log)"
echo ""
echo "=== 6. 磁盘空间 ==="
df -h / | tail -1 | awk '{print "  total="$2" used="$3" avail="$4" use%="$5}'
echo ""
echo "=== 7. 备份目录 ==="
ls -la /opt/bingdashan/backups/ 2>/dev/null | tail -5 || echo "  (no backups yet)"
echo ""
echo "=== 验证完成 ==="

#!/usr/bin/env bash
# 全量拉 CN 里 7 条 pending 订单 + 6 条 paid (找出来, 定位文件)
echo "=== 定位哪些文件含 pending / paid 订单 ==="
grep -rlE '"status":"?pending"?' /var/lib/bingdashan-cn 2>/dev/null
echo "--- paid 所在文件 ---"
grep -rlE '"status":"?paid"?' /var/lib/bingdashan-cn 2>/dev/null
echo ""
echo "=== 每个含 pending 的文件: 打印关键字段 ==="
for f in $(grep -rlE '"status":"?pending"?' /var/lib/bingdashan-cn 2>/dev/null); do
  echo "FILE: $f"
  cat "$f" 2>/dev/null | tr ',' '\n' | grep -iE '"(out_trade_no|ref|status|amount|plan|slug|created_at|subject|trade_status)"' | head -12
  echo "---"
done
echo "=== paid 订单汇总 ==="
for f in $(grep -rlE '"status":"?paid"?' /var/lib/bingdashan-cn 2>/dev/null); do
  echo "FILE: $f"
  cat "$f" 2>/dev/null | tr ',' '\n' | grep -iE '"(out_trade_no|ref|amount|plan|slug)"' | head -8
  echo "---"
done
echo "done"

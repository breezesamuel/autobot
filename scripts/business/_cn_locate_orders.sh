#!/usr/bin/env bash
# 工具站 CN 订单实际存储位置: file store 的 bds_order_ 文件 + 各账本
echo "=== 1. CN file store 根目录 (找 .env 里 fileStore 配置) ==="
grep -iE 'FILE_STORE|BDS_FILE|STORE_DIR|DATA_DIR' /etc/bingdashan-cn.env 2>/dev/null | head -5
echo "=== 2. /var/lib/bingdashan-cn 全量文件 (找 bds_order / orders_by_ref) ==="
find /var/lib/bingdashan-cn -type f 2>/dev/null | grep -iE 'bds_order|order' | head -20
echo "--- 该目录文件总数 ---"
find /var/lib/bingdashan-cn -type f 2>/dev/null | wc -l
echo "=== 3. 站点目录内是否有数据文件 ==="
find /www/wwwroot/tools-cn.highkingflower.com -maxdepth 2 -type f \( -name '*.json' -o -name 'bds_*' \) 2>/dev/null | grep -viE 'node_modules|package|\.git|arcade/|a_logic' | head -20
echo "=== 4. 各渠道账本条数 (bounty/cashback 等) ==="
for d in bounty cashback bandwidth writerewards charity recovery; do
  n=$(find /var/lib/bingdashan-cn/$d -type f 2>/dev/null | wc -l)
  echo "  $d: $n 文件"
done
echo "=== 5. 找 'paid' 状态的订单记录 (扫所有 json) ==="
grep -rlE '"status":"?paid"?' /var/lib/bingdashan-cn 2>/dev/null | head -20
echo "done"

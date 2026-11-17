#!/usr/bin/env bash
# 查 CN 连的 Supabase/Upstash (订单真身所在) + 直接查云端 bds_orders 待付单
echo "=== 1. CN 云端存储配置 (Supabase / Upstash) ==="
grep -iE 'SUPABASE_URL|SUPABASE_KEY|UPSTASH|KV_REST|REACT_APP|BDS_' /etc/bingdashan-cn.env 2>/dev/null | sed 's/=.*KEY.*/=***REDACTED***/i' | head -10
echo "=== 2. 工具站 storeKind: CN 现在用哪种存储? ==="
curl -sk "https://tools-cn.highkingflower.com/api/config" --max-time 20 | grep -oE '"store":"[a-z]+"' | head -1
echo "=== 3. 直接从 CN API 查待付/已付订单 (走 alipay.js 的 order 端点) ==="
# alipay.js 有 /api/order?out_trade_no= 和 /api/entitle; 找列订单的端点
grep -nE "route==='/api/(order|orders|entitle|pay)|action==*(order|pending|list)" /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js 2>/dev/null | head -8
echo "=== 4. 各 ref 的订单索引 (orders_by_ref_*) — file store 有就列 ==="
find /var/lib/bingdashan-cn -iname 'orders_by_ref_*' 2>/dev/null | head
echo "=== 5. 扫全部 CN 文件里的订单状态分布 ==="
grep -rhoE '"status":"?paid"?' /var/lib/bingdashan-cn 2>/dev/null | sort | uniq -c
grep -rhoE '"status":"?pending"?' /var/lib/bingdashan-cn 2>/dev/null | sort | uniq -c
echo "done"

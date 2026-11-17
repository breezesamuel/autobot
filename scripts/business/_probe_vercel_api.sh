#!/usr/bin/env bash
# A2: 探 Vercel 主站 API, 找能列订单/待付的端点
B="https://tools.highkingflower.com/api"
echo "=== 1. 探 alipay.js 相关订单端点 ==="
for e in "order" "entitle" "config" "orders?ref=probe" "bds_orders?status=pending"; do
  printf "  /api/%-28s " "$e"
  code=$(curl -sk "$B/$e" --max-time 20 -o /tmp/_probe.json -w "%{http_code}" 2>/dev/null)
  echo "HTTP $code"
  head -c 160 /tmp/_probe.json 2>/dev/null; echo
done
echo ""
echo "=== 2. 找 Vercel 有没有 'list orders' 端点 (看 alipay.js 路由名) ==="
# 拉 alipay.js 的路由声明 (若 Vercel 站点能访问源, 用 /api 目录; 否则从已知 route 名推)
for e in "pay?plan=trial&ref=probe&slug=p&amount=1" ; do
  printf "  /api/%-40s " "$e"
  code=$(curl -sk "$B/$e" --max-time 20 -o /tmp/_probe2.json -w "%{http_code}" 2>/dev/null)
  echo "HTTP $code"
  grep -oE 'out_trade_no[":=]+[A-Za-z0-9_]+|action="submit"|bntBtn' /tmp/_probe2.json 2>/dev/null | head -2
done
echo ""
echo "=== 3. /api/entitle (权益/订单查询) 带 ref 探 ==="
for ref in "" "probe"; do
  printf "  /api/entitle?ref=%-12s " "$ref"
  code=$(curl -sk "$B/entitle?ref=$ref" --max-time 20 -o /tmp/_e.json -w "%{http_code}" 2>/dev/null)
  echo "HTTP $code"; head -c 200 /tmp/_e.json 2>/dev/null; echo
done
echo "done"

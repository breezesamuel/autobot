#!/usr/bin/env bash
# 找 Vercel 站的 Upstash 配置 + 探 'orders_by_ref' 索引, 定位 9 单待付的 ref 列表
echo "=== 1. Vercel 站点的 Upstash KV 是否可读 (经 /api/config 的 store) ==="
curl -sk "https://tools.highkingflower.com/api/config" --max-time 20 | grep -oE '"store":"[a-z]+"' | head -1
echo "=== 2. 本地 24xs 仓库里的 Upstash/Supabase 配置 (Vercel 用的) ==="
grep -rhoE "UPSTASH[^ ]*|KV_REST_API[^ ]*|bds_order|orders_by_ref" /www/wwwroot/tools-cn.highkingflower.com/.env* 2>/dev/null | head
# 从本地 24xs (Vercel 部署源) 找
find /www/wwwroot -maxdepth 4 -name '.env*' 2>/dev/null | head -5
echo "=== 3. 日报数据来源: 找 '9 待付' 的统计脚本 (CN 有 autoops.js) ==="
grep -nE "pending|待付|orders.*length|funnel|revenue" /www/wwwroot/tools-cn.highkingflower.com/api/autoops.js 2>/dev/null | head -15
echo "=== 4. CN autoops ?a=loop 直接拉 (它统计全漏斗含待付) ==="
# 找 autoops 端点 + 是否需要 secret
curl -sk "https://tools-cn.highkingflower.com/api/autoops.js?a=loop" --max-time 20 | head -c 400; echo
curl -sk "https://tools-cn.highkingflower.com/api/autoops?a=loop" --max-time 20 | head -c 400; echo
echo "done"

#!/usr/bin/env bash
# 用 autoops ?a=loop (带 secret) 拉全量订单漏斗 (pending/paid 都在里面)
echo "=== 1. 找 autoops 的 secret 存法 (CN 环境变量) ==="
grep -iE "AUTOOPS|OPS_SECRET|SECRET_KEY|_SECRET" /etc/bingdashan-cn.env 2>/dev/null | sed -E 's/=(.{0,4}).*/=\1.../' | head
echo "=== 2. autoops.js 怎么取 secret + 路由 ==="
grep -nE "k=|secret|SECRET|forbidden|a=loop|a=stats|route===" /www/wwwroot/tools-cn.highkingflower.com/api/autoops.js 2>/dev/null | head -15
echo "=== 3. autoops 端点实际怎么被路由 (site_cn_server 预读) ==="
grep -nE "autoops|a=loop|/api/autoops" /www/wwwroot/tools-cn.highkingflower.com/site_cn_server.mjs 2>/dev/null | head -8
echo "done"

#!/usr/bin/env bash
# 找"丙大山工具站"(Alipay) 的订单存储 —— 之前 6 已付/9 待付 的订单在这
echo "=== 1. CN 工具站目录 ==="
ls -d /www/wwwroot/tools-cn.highkingflower.com 2>/dev/null
echo "=== 2. 订单存储: bds_order 表 / 文件? ==="
# 之前 SOP 提到 bds_order 订单表 (Alipay 轨) + 各渠道账本 (bounty/cashback 等)
echo "--- 2a. 找 bds_order 相关数据文件 (file store) ---"
find /var/lib/bingdashan-cn -maxdepth 2 -iname '*order*' 2>/dev/null | head -10
find /www/wwwroot/tools-cn.highkingflower.com -maxdepth 3 -iname '*order*' 2>/dev/null | grep -vE 'node_modules|\.git' | head -10
echo "--- 2b. 各渠道账本目录 ---"
ls -1 /var/lib/bingdashan-cn/ 2>/dev/null | head -30
echo "=== 3. 有没有 PostgreSQL (订单表可能在这) ==="
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Status}}' 2>/dev/null | grep -iE 'postgres|quant' | head -5 || echo "  无 docker postgres 容器"
pg_isready 2>/dev/null && echo "  本地 postgres running" || echo "  本地无 pg_isready"
echo "=== 4. 工具站怎么存订单? 看 alipay.js 的订单持久化 ==="
grep -nE "bds_order|orders?\[|dbSet\('order|kvSet\('order|orders\.push|orderStore" /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js 2>/dev/null | head -10
echo "done"

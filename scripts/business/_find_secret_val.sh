#!/usr/bin/env bash
echo "=== 1. autoops.js 的 env() 怎么取值 (文件? 进程env?) ==="
sed -n '340,360p' /www/wwwroot/tools-cn.highkingflower.com/api/autoops.js 2>/dev/null
echo "=== 2. AUTOOPS_SECRET 存在哪 (全机搜) ==="
grep -rns "AUTOOPS_SECRET" /etc 2>/dev/null | head -5
grep -rns "AUTOOPS_SECRET" /www/wwwroot/tools-cn.highkingflower.com/.env* 2>/dev/null | sed -E 's/=(.{0,4}).*/=\1.../' | head
find /www/wwwroot/tools-cn.highkingflower.com -maxdepth 2 -name '*.env*' 2>/dev/null | head
echo "=== 3. systemd unit 是否注入 AUTOOPS_SECRET ==="
systemctl cat bingdashan-cn 2>/dev/null | grep -iE "AUTOOPS|Environment" | head
echo "done"

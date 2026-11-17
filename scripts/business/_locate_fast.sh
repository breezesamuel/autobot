#!/usr/bin/env bash
# 定位 Upstash 密钥存放 (快速版, 只查关键路径)
echo "=== 工具站 alipay.js 读 KV 的 env 字段名 ==="
grep -oE "get\('[A-Z_]+'\)" /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js 2>/dev/null | grep -iE "kv|upstash|rest" | sort -u
echo ""
echo "=== CN env 里 KV/UPSTASH 相关 (只列键名, 不打印值) ==="
grep -oE "^[A-Z_]*(KV|UPSTASH|REST)[A-Z_]*=" /etc/bingdashan-cn.env 2>/dev/null | head
echo "done"

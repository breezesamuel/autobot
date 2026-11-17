#!/usr/bin/env bash
# 摸清 Upstash/Vercel 密钥的存放位置 (不打印明文值, 只定位)
echo "=== 1. 本地 24xs 仓库 (Vercel 部署源) 里的 KV 配置 ==="
grep -rlnE "KV_REST_API_URL|UPSTASH|KV_REST_API_TOKEN" /www/wwwroot 2>/dev/null | grep -v node_modules | head
echo "--- .env / .env.example 类文件 ---"
find /www/wwwroot -maxdepth 4 \( -name '.env*' -o -name 'vercel.json' \) 2>/dev/null | grep -vE 'node_modules|\.git' | head -10
echo ""
echo "=== 2. 24xs 仓库本地 (F 盘, 你机器上) 的 Vercel 项目 secrets ==="
echo "   (Vercel secrets 存在 Vercel 云端, 本地通常只有 .env.example 占位)"
echo ""
echo "=== 3. 工具站 alipay.js 读 KV 的 env 名 (确认字段) ==="
grep -oE "get\('(KV_REST_API_[A-Z]+|UPSTASH[A-Z_]*)'\)" /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js 2>/dev/null | sort -u
echo "done"

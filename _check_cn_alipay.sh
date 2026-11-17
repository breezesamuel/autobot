#!/usr/bin/env bash
# 查 CN 现有支付宝密钥位置 + APPID, 跟新密钥 (app_pub SPKI=fe575fe2...) 比对
echo "=== 1. CN 现有支付宝密钥文件位置 ==="
ls -la /etc/bingdashan-cn/ 2>/dev/null | grep -i "alipay\|pay" 
find /etc -name "*alipay*" -o -name "*_pub.pem" 2>/dev/null | head -8
echo ""
echo "=== 2. CN 现有密钥 SPKI 指纹 (对比 app_pub=fe575fe26446f8fc) ==="
for f in /etc/bingdashan-cn/alipay_pub.pem /etc/bingdashan-cn/ALIPAY_PUB_KEY; do
  if [ -f "$f" ]; then
    node -e 'const fs=require("fs"),crypto=require("crypto");const p=fs.readFileSync(process.argv[1],"utf8");console.log("  '+process.argv[1]+' SPKI-SHA256:",crypto.createHash("sha256").update(Buffer.from(p.replace(/-----[^-]+-----|\s+/g,""),"base64")).digest("hex").slice(0,32))' "$f" 2>/dev/null
  fi
done
echo ""
echo "=== 3. CN 现有 APPID + 支付宝公钥配置 (在 .env / 代码里) ==="
grep -i "ALIPAY_APP_ID\|alipay_app_id\|ALIPAY_PUB\|alipay_pub\|支付宝公钥" /etc/bingdashan-cn.env 2>/dev/null | head -6
grep -rho "ALIPAY_APP_ID=[0-9]*" /opt/bingdashan/*.env /opt/bingdashan/.env* /www/wwwroot/tools-cn.highkingflower.com/*.env 2>/dev/null | sort -u | head -4
echo "done"

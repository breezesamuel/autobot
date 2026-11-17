#!/usr/bin/env bash
# 比对: 这套新密钥 vs CN 现有 alipay_priv.pem 是否同一套 (只算公钥指纹, 不泄私钥)
D="C:\\Users\\46012\\Documents\\支付宝开放平台密钥工具"
echo "=== 新密钥 公钥完整 SHA256 指纹 ==="
node -e '
const fs=require("fs"),crypto=require("crypto");
function cleanKey(raw){ let m=raw.match(/MI[A-Za-z0-9+/=]{20,}/g); return m?m.join(""):""; }
const appPub=cleanKey(fs.readFileSync(process.argv[1],"utf8"));
const aliPub=cleanKey(fs.readFileSync(process.argv[2],"utf8"));
console.log("  应用公钥 SPKI-SHA256:", crypto.createHash("sha256").update(Buffer.from(appPub,"base64")).digest("hex").slice(0,32));
console.log("  支付宝公钥 SPKI-SHA256:", crypto.createHash("sha256").update(Buffer.from(aliPub,"base64")).digest("hex").slice(0,32));
' "$D\\应用公钥RSA2048.txt" "$D\\支付宝公钥.txt"

echo ""
echo "=== CN 现有密钥 公钥完整 SHA256 指纹 (对比是否同一套) ==="
node -e '
const fs=require("fs"),crypto=require("crypto");
// CN 现有 alipay_pub.pem (PEM 头格式), 读公钥 SPKI
const pub=fs.readFileSync("/etc/bingdashan-cn/alipay_pub.pem","utf8");
console.log("  CN 应用公钥 SPKI-SHA256:", crypto.createHash("sha256").update(Buffer.from(pub.replace(/-----[^-]+-----|\s+/g,""),"base64")).digest("hex").slice(0,32));
' 2>/dev/null || echo "  CN 公钥读取失败 (可能没在 /etc/bingdashan-cn/)"

echo ""
echo "=== CN 现有 .env 的 APPID / 支付宝公钥配置 ==="
grep -o "ALIPAY_APP_ID=[0-9]*\|ALIPAY_PUB[^\n]*\|ALIPAY_GATEWAY[^\n]*" /etc/bingdashan-cn.env 2>/dev/null | head -5
echo "done"

#!/usr/bin/env bash
# 核对 3 把支付宝密钥 与 CN 现在用的 alipay_priv/pub.pem 是否一致 (只比对指纹, 不打印私钥明文)
D="C:\Users\46012\Documents\支付宝开放平台密钥工具"
PUB="$D\应用公钥RSA2048.txt"
PRIV="$D\应用私钥RSA2048-敏感数据，请妥善保管.txt"
ALIPAY_PUB="$D\支付宝公钥.txt"
echo "=== 本地 3 把密钥 指纹 (SHA256, 前16位, 只算指纹不泄密) ==="
for f in "$PUB" "$PRIV" "$ALIPAY_PUB"; do
  if [ -f "$f" ]; then
    fp=$(python -c "import hashlib,sys;print(hashlib.sha256(open('$f','rb').read().strip()).hexdigest()[:16])" 2>/dev/null)
    lines=$(wc -l < "$f")
    echo "  $(basename "$f"): len指纹=$fp · 行数=$lines"
  else
    echo "  缺: $f"
  fi
done
echo ""
echo "=== 确认私钥是 PKCS8/OPENSSL 格式 (CN openssl 能直接用) ==="
head -c 60 "$PRIV" 2>/dev/null | tr -d '\r'
echo ""
echo "=== 确认应用公钥/支付宝公钥是裸公钥还是 X509 ==="
head -c 40 "$PUB" 2>/dev/null; echo " <- 应用公钥开头"
head -c 40 "$ALIPAY_PUB" 2>/dev/null; echo " <- 支付宝公钥开头"
echo done

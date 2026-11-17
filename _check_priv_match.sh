#!/usr/bin/env bash
# 最终比对: CN 现有 alipay_priv.pem 派生公钥 vs 新密钥 app_pub.txt (fe575fe2...)
echo "=== CN 现有 alipay_priv.pem (1708B, PEM头) 的 SHA256 + 派生公钥指纹 ==="
# 文件原始哈希
python3 -c "import hashlib;print('  priv.pem 文件 SHA256:',hashlib.sha256(open('/etc/bingdashan-cn/alipay_priv.pem','rb').read().strip()).hexdigest()[:32])"
# 派生公钥 SPKI 哈希 (openssl 可读 CN 的 PEM 头格式)
openssl pkey -in /etc/bingdashan-cn/alipay_priv.pem -pubout 2>/dev/null | python3 -c "import hashlib,sys;print('  priv.pem 派生公钥 SHA256:',hashlib.sha256(sys.stdin.read().strip()).hexdigest()[:32])"
echo ""
echo "=== 新密钥 app_pub.txt (你的应用公钥) 派生的 SPKI 哈希 ==="
echo "  (本地算过: app_pub SPKI-SHA256 = fe575fe26446f8fc4e3a7afb0d263769)"
echo ""
echo "=== CN 现有 alipay_pub.pem 的 SPKI 哈希 (上面已得 79cbaf53 = 新 alipay_pub, 同一把) ==="
echo "=== 结论需要: CN priv.pem 派生公钥 == 新 app_pub(fe575fe2)? ==="
# 让 CN 直接算 app_pub 的哈希需要新密钥内容, 改在 CN 上把新 app_pub 临时放进来比
echo "done"

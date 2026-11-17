#!/usr/bin/env bash
echo "=== CN 现有 alipay_priv.pem 派生公钥 SHA256 (openssl, CN 上算) ==="
openssl pkey -in /etc/bingdashan-cn/alipay_priv.pem -pubout 2>/dev/null | python3 -c "import hashlib,sys;print('  CN priv.pem 派生公钥 SHA256:',hashlib.sha256(sys.stdin.read().strip()).hexdigest()[:32])"
echo "  目标比对值 (新私钥派生公钥): fe575fe26446f8fc4e3a7afb0d263769"
echo "done"

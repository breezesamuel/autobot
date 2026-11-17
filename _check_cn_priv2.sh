#!/usr/bin/env bash
echo "=== CN 现有 alipay_priv.pem 派生公钥 指纹 ==="
# openssl 派生公钥 PEM, 再算 SHA256 (去掉头尾和换行, 对 DER 部分哈希)
openssl pkey -in /etc/bingdashan-cn/alipay_priv.pem -pubout 2>/dev/null | sed 's/---.*---//g' | tr -d '[:space:]' > /tmp/_pub_b64.txt
python3 -c "import base64,hashlib;print('  CN priv.pem 派生公钥 SHA256:',hashlib.sha256(base64.b64decode(open('/tmp/_pub_b64.txt').read())).hexdigest()[:32])"
echo "  目标 (新私钥派生公钥): fe575fe26446f8fc4e3a7afb0d263769"
echo "=== CN 现有 alipay_pub.pem 文件 指纹 (之前=79cbaf53) ==="
sed 's/---.*---//g' /etc/bingdashan-cn/alipay_pub.pem 2>/dev/null | tr -d '[:space:]' > /tmp/_pub2_b64.txt
python3 -c "import base64,hashlib;print('  CN alipay_pub.pem SHA256:',hashlib.sha256(base64.b64decode(open('/tmp/_pub2_b64.txt').read())).hexdigest()[:32])"
echo "done"

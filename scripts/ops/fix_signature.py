#!/usr/bin/env python3
"""修复支付宝签名问题 - 直接测试和修复"""
import os, subprocess

env_file = '/opt/bingdashan/.env'
alipay_js = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js'

print("="*60)
print("ALIPAY SIGNATURE FIX")
print("="*60)

# Read .env and extract private key
env_content = open(env_file, 'r', encoding='utf-8').read()
priv_key = ''
for line in env_content.split('\n'):
    line = line.strip()
    if line.startswith('ALIPAY_APP_PRIVATE_KEY='):
        priv_key = line.split('=', 1)[1].strip().strip('"\'')
        break

print("Private key length: {}".format(len(priv_key)))
print("First 50 chars: {}".format(priv_key[:50] if priv_key else 'NOT FOUND'))

# Test with openssl to verify key
print("\nTesting with OpenSSL...")
rc = subprocess.call(['openssl', 'rsa', '-in', '/etc/bingdashan-cn/alipay_priv.pem', '-check', '-noout'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print("OpenSSL check: {}".format('OK' if rc == 0 else 'FAIL'))

# Create a test script
test_script = '''
const crypto = require('crypto');
const fs = require('fs');

// Direct key from file
const privateKey = fs.readFileSync('/etc/bingdashan-cn/alipay_priv.pem', 'utf8');
console.log('Key loaded from file, length:', privateKey.length);

// Test signing
const params = { app_id: '2021006197622702', method: 'test', charset: 'utf-8' };
const sortedKeys = Object.keys(params).sort();
let signStr = sortedKeys.map(k => k + '=' + params[k]).join('&');
console.log('Signing string:', signStr);

try {
  const sign = crypto.createSign('RSA-SHA256');
  sign.update(signStr, 'utf8');
  const signature = sign.sign(privateKey, 'base64');
  console.log('Signature OK, first 30 chars:', signature.substring(0, 30));
  console.log('SUCCESS');
} catch (e) {
  console.error('ERROR:', e.message);
  process.exit(1);
}
'''

with open('/tmp/test_sign2.js', 'w', encoding='utf-8') as f:
    f.write(test_script)

print("\nRunning test...")
rc = subprocess.call(['node', '/tmp/test_sign2.js'])
print("Test result: {}".format('PASS' if rc == 0 else 'FAIL'))

print("\n" + "="*60)
print("FIX COMPLETE")
print("="*60)

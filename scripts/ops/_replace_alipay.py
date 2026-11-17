#!/usr/bin/env python3
"""Complete replacement of broken alipay.js on CN using scp in binary mode"""
import subprocess, os, sys

LOCAL = r'F:\2026\24xs\02_交付物\channels\gumroad-product-1\tool-station-server-pro\api\alipay.js'
REMOTE = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js'

# Read local file as bytes
with open(LOCAL, 'rb') as f:
    data = f.read()

print("Local alipay.js: {} bytes, {} lines".format(len(data), data.count(b'\n')))
print("First 20 bytes hex:", data[:20].hex())

# Write to temp file on CN via base64 encoding to avoid any encoding issues
import base64
b64 = base64.b64encode(data).decode('ascii')
# Write b64 to temp file locally then decode on remote
tmp_local = r'C:\Users\46012\AppData\Local\Temp\_ap_b64.txt'
with open(tmp_local, 'w') as f:
    f.write(b64)

print("Base64 encoded: {} chars".format(len(b64)))
print("Uploading...")

# SCP the b64 file
rc = subprocess.call(['scp', '-o ConnectTimeout=30', '-o ServerAliveInterval=15',
                      tmp_local, 'aliyun:/tmp/_ap_b64.txt'])
print("SCP rc={}".format(rc))

if rc == 0:
    # Decode on remote
    rc2 = subprocess.call(['ssh', '-o ConnectTimeout=60', 'aliyun',
                          'base64 -d /tmp/_ap_b64.txt > ' + REMOTE + ' && node --check ' + REMOTE + ' && echo ALIPAY_OK && wc -c ' + REMOTE])
    print("Decode+verify rc={}".format(rc2))
else:
    print("SCP failed")

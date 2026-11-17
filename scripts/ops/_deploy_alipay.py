#!/usr/bin/env python3
"""Binary-safe deploy of alipay.js to CN via base64"""
import subprocess, os, base64, sys

LOCAL = r'F:\2026\24xs\02_交付物\channels\gumroad-product-1\tool-station-server-pro\api\alipay.js'
REMOTE_PATH = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js'
TMP_B64 = r'C:\Users\46012\AppData\Local\Temp\_ap_b64.txt'
TMP_DECODED = r'C:\Users\46012\AppData\Local\Temp\_ap_decoded.js'

# Read and encode
data = open(LOCAL, 'rb').read()
b64 = base64.b64encode(data).decode('ascii')
open(TMP_B64, 'w').write(b64)
print("Encoded {} bytes -> {} b64 chars".format(len(data), len(b64)))

# SCP b64 to CN
r1 = subprocess.call(['scp', '-o ConnectTimeout=30', '-o ServerAliveInterval=15',
                      TMP_B64, 'aliyun:/tmp/_ap_b64.txt'])
print("SCP rc={}".format(r1))
if r1 != 0:
    sys.exit(1)

# Decode on CN and verify
cmd = ('base64 -d /tmp/_ap_b64.txt > {} && node --check {} && echo ALIPAY_DEPLOYED_OK && '
       'wc -c {}'.format(REMOTE_PATH, REMOTE_PATH, REMOTE_PATH))
r2 = subprocess.call(['ssh', '-o ConnectTimeout=60', 'aliyun', cmd])
print("Deploy rc={}".format(r2))

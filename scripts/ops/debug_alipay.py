#!/usr/bin/env python3
"""调试支付宝签名问题"""
import json, os, sys

env_file = '/opt/bingdashan/.env'
log_file = '/var/log/bingdashan/alipay_debug.log'

def log(m):
    ts = __import__('datetime').datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line = "[DEBUG][{}] {}".format(ts, m)
    print(line)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

log("="*60)
log("ALIPAY SIGNATURE DEBUG")
log("="*60)

# Load env
env = {}
with open(env_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"\'')

log("Loaded {} env vars".format(len(env)))
log("ALIPAY_APP_ID: {}".format(env.get('ALIPAY_APP_ID', 'NOT SET')))
log("ALIPAY_APP_PRIVATE_KEY length: {}".format(len(env.get('ALIPAY_APP_PRIVATE_KEY', ''))))
log("ALIPAY_GATEWAY: {}".format(env.get('ALIPAY_GATEWAY', 'NOT SET')))

# Check if private key has newlines
priv_key = env.get('ALIPAY_APP_PRIVATE_KEY', '')
if '\n' in priv_key:
    log("WARNING: Private key contains newlines!")
    # Remove newlines
    priv_key_clean = priv_key.replace('\n', '').replace('\r', '')
    log("Cleaned private key length: {}".format(len(priv_key_clean)))
else:
    log("Private key format OK (no newlines)")

# Test signature
import subprocess
test_js = '''
const crypto = require('crypto');
const fs = require('fs');

// Load env
const env = {};
const content = fs.readFileSync('/opt/bingdashan/.env', 'utf-8');
content.split('\\n').forEach(line => {
  line = line.trim();
  if (!line || line.startsWith('#')) return;
  const eqIndex = line.indexOf('=');
  if (eqIndex > 0) {
    const k = line.substring(0, eqIndex).trim();
    let v = line.substring(eqIndex + 1).trim();
    if ((v.startsWith('"'"'"') && v.endsWith('"'"'"')) || (v.startsWith('"'"'"') && v.endsWith('"'"'"'))) {
      v = v.substring(1, v.length - 1);
    }
    env[k] = v;
  }
});

console.error('APP_ID:', env.ALIPAY_APP_ID);
console.error('KEY_LENGTH:', env.ALIPAY_APP_PRIVATE_KEY ? env.ALIPAY_APP_PRIVATE_KEY.length : 0);

const privateKey = env.ALIPAY_APP_PRIVATE_KEY || '';
if (!privateKey) {
  console.error('ERROR: No private key');
  process.exit(1);
}

// Test signing
const params = { app_id: env.ALIPAY_APP_ID, method: 'test', charset: 'utf-8' };
const sortedKeys = Object.keys(params).sort();
let signStr = sortedKeys.map(k => k + '=' + params[k]).join('&');
console.error('SIGN_STR:', signStr);

try {
  const sign = crypto.createSign('RSA-SHA256');
  sign.update(signStr, 'utf8');
  const signature = sign.sign(privateKey, 'base64');
  console.error('SIGNATURE_OK:', signature.substring(0, 20) + '...');
  console.log('SUCCESS');
} catch (e) {
  console.error('SIGN_ERROR:', e.message);
  process.exit(1);
}
'''

with open('/tmp/test_sign.js', 'w', encoding='utf-8') as f:
    f.write(test_js)

rc = subprocess.call(['node', '/tmp/test_sign.js'], 
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.STDOUT)

log("Node test exit code: {}".format(rc))

# Check database
log("")
log("Checking database...")
db_path = '/opt/bingdashan/data/db.json'
if os.path.exists(db_path):
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    orders = db.get('orders', [])
    paid = [o for o in orders if o.get('paid')]
    pending = [o for o in orders if o.get('status') == 'pending']
    log("Total orders: {}".format(len(orders)))
    log("Paid: {}".format(len(paid)))
    log("Pending: {}".format(len(pending)))
else:
    log("DB file not found")

log("")
log("="*60)
log("DEBUG COMPLETE")
log("="*60)

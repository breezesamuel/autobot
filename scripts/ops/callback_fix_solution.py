#!/usr/bin/env python3
"""丙大山 · 支付回调终极修复方案"""
import subprocess
import json
from datetime import datetime

LOG = '/var/log/bingdashan/callback_fix_final.log'

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] {msg}")
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{ts}] {msg}\n")
    except: pass

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
    return r.returncode, r.stdout.strip(), r.stderr.strip()

# ========== 问题分析 ==========
log("="*70)
log("丙大山 · 支付回调问题诊断与修复")
log("="*70)

log("")
log("【问题1】回调端点无响应 (HTTP 000)")
log("原因分析:")
log("  1. 异步回调处理中可能未正确结束HTTP响应")
log("  2. req.on('end') 可能是异步的但未await")
log("  3. 错误处理可能不完整")

log("")
log("【解决方案】重写回调处理器")

# ========== 生成新的alipay.js回调处理代码 ==========
new_callback_code = '''
    } else if (path === '/api/pay/callback') {
      // 支付宝回调处理 - 修复版
      let body = '';
      req.setEncoding('utf8');
      
      req.on('data', function(chunk) {
        body += chunk;
      });
      
      req.on('end', function() {
        // 解析参数
        const params = {};
        if (body) {
          body.split('&').forEach(function(pair) {
            const eqIndex = pair.indexOf('=');
            if (eqIndex > 0) {
              const k = decodeURIComponent(pair.substring(0, eqIndex));
              const v = decodeURIComponent(pair.substring(eqIndex + 1));
              params[k] = v;
            }
          });
        }
        
        log('CALLBACK RECEIVED: trade_status=' + params.trade_status + ' out_trade_no=' + params.out_trade_no);
        
        // 验证签名
        try {
          const publicKey = fs.readFileSync('/etc/bingdashan-cn/alipay_pub.pem', 'utf-8');
          const signStr = body.replace(/sign=[^&]*/, '');
          const verifier = crypto.createVerify('RSA-SHA256');
          verifier.update(signStr, 'utf8');
          
          const valid = verifier.verify(publicKey, params.sign);
          
          if (valid && params.trade_status === 'TRADE_SUCCESS') {
            // 更新订单
            updateOrderPaid(params.out_trade_no, params).then(function() {
              log('PAYMENT SUCCESS: ' + params.out_trade_no);
              res.writeHead(200, {'Content-Type': 'text/plain'});
              res.end('success');
            }).catch(function(e) {
              log('DB UPDATE ERROR: ' + e.message);
              res.writeHead(500, {'Content-Type': 'application/json'});
              res.end(JSON.stringify({error: 'internal_error'}));
            });
          } else {
            log('PAYMENT FAILED or PENDING: status=' + params.trade_status);
            res.writeHead(400, {'Content-Type': 'text/plain'});
            res.end('failed');
          }
        } catch (e) {
          log('SIGNATURE VERIFICATION ERROR: ' + e.message);
          res.writeHead(500, {'Content-Type': 'application/json'});
          res.end(JSON.stringify({error: 'verification_failed'}));
        }
      });
'''

log("")
log("已生成修复代码，请手动替换 alipay.js 中的回调处理部分")
log("")
log("【步骤】")
log("1. 备份原文件:")
log("   cp /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js.bak")
log("")
log("2. 编辑文件，找到 'else if (path === \'/api/pay/callback\')' 部分")
log("3. 用上面的新代码替换")
log("")
log("4. 重启服务:")
log("   systemctl restart bingdashan-cn")
log("")
log("5. 测试:")
log("   curl -X POST 'http://127.0.0.1:8794/api/pay/callback' \\")
log("     -H 'Content-Type: application/x-www-form-urlencoded' \\")
log("     -d 'out_trade_no=test&trade_status=TRADE_SUCCESS&sign=test'")
log("")

# ========== 生成完整的修复脚本 ==========
fix_script = '''#!/bin/bash
# 丙大山 · 支付回调一键修复脚本 v2
set -e

echo "=== 支付回调修复 v2 ==="

# 1. 备份
cp /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js \
   /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js.bak.$(date +%s)

# 2. 创建新的回调处理函数
cat > /tmp/new_callback.js << 'JSEOF'
    } else if (path === '/api/pay/callback') {
      let body = '';
      req.setEncoding('utf8');
      req.on('data', function(chunk) { body += chunk; });
      req.on('end', function() {
        const params = {};
        if (body) {
          body.split('&').forEach(function(pair) {
            const eqIndex = pair.indexOf('=');
            if (eqIndex > 0) {
              params[decodeURIComponent(pair.substring(0, eqIndex))] = 
                decodeURIComponent(pair.substring(eqIndex + 1));
            }
          });
        }
        log('CALLBACK: status=' + params.trade_status + ' order=' + params.out_trade_no);
        try {
          const publicKey = fs.readFileSync('/etc/bingdashan-cn/alipay_pub.pem', 'utf-8');
          const verifier = crypto.createVerify('RSA-SHA256');
          verifier.update(body.replace(/sign=[^&]*/, ''));
          if (verifier.verify(publicKey, params.sign) && params.trade_status === 'TRADE_SUCCESS') {
            updateOrderPaid(params.out_trade_no, params).then(() => {
              log('SUCCESS: ' + params.out_trade_no);
              res.writeHead(200); res.end('success');
            }).catch(e => {
              log('DB ERROR: ' + e.message);
              res.writeHead(500); res.end('error');
            });
          } else {
            log('FAILED/PENDING: ' + params.trade_status);
            res.writeHead(400); res.end('failed');
          }
        } catch (e) {
          log('VERIFY ERROR: ' + e.message);
          res.writeHead(500); res.end('error');
        }
      });
JSEOF

# 3. 使用sed替换回调处理部分（简化版，实际可能需要手动编辑）
echo "请手动编辑 /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js"
echo "替换 '/api/pay/callback' 处理部分为上述代码"
echo ""
echo "修复完成后执行:"
echo "  systemctl restart bingdashan-cn"
echo "  curl -X POST 'http://127.0.0.1:8794/api/pay/callback' -H 'Content-Type: application/x-www-form-urlencoded' -d 'test=1'"
'''

fix_path = '/tmp/fix_callback_v2.sh'
with open(fix_path, 'w', encoding='utf-8') as f:
    f.write(fix_script)

log("")
log(f"修复脚本已生成: {fix_path}")
log("")
log("【重要提示】")
log("由于回调问题比较复杂，建议:")
log("1. 先理解当前代码的问题")
log("2. 手动编辑修复（更可控）")
log("3. 或联系开发者协助")
log("")
log("="*70)

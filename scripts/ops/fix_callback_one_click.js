const fs = require('fs');
const path = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js';

// 读取原文件
let content = fs.readFileSync(path, 'utf8');

// 原始回调处理代码（有问题的版本）
const oldCallback = `    } else if (path === '/api/pay/callback') {
      let body = '';
      req.on('data', chunk => body += chunk.toString());
      req.on('end', async () => {
        const params = {};
        body.split('&').forEach(pair => {
          const [k, v] = pair.split('=');
          params[decodeURIComponent(k)] = decodeURIComponent(v || '');
        });
        
        try {
          const publicKey = fs.readFileSync('/etc/bingdashan-cn/alipay_pub.pem', 'utf-8');
          const verifier = crypto.createVerify('RSA-SHA256');
          verifier.update(body.replace(/sign=[^&]*/, ''));
          
          if (verifier.verify(publicKey, params.sign) && params.trade_status === 'TRADE_SUCCESS') {
            await updateOrderPaid(params.out_trade_no, params);
            res.writeHead(200); res.end('success');
          } else {
            res.writeHead(400); res.end('failed');
          }
        } catch (e) {
          res.writeHead(500); res.end('error');
        }
      });`;

// 修复后的回调处理代码
const newCallback = `    } else if (path === '/api/pay/callback') {
      let body = '';
      req.setEncoding('utf8');
      req.on('data', function(chunk) { body += chunk; });
      req.on('end', function() {
        const params = {};
        if (body) {
          body.split('&').forEach(function(pair) {
            const eq = pair.indexOf('=');
            if (eq > 0) {
              params[decodeURIComponent(pair.substring(0, eq))] = 
                decodeURIComponent(pair.substring(eq + 1));
            }
          });
        }
        
        log('CALLBACK: status=' + params.trade_status + ' order=' + params.out_trade_no);
        
        try {
          const publicKey = fs.readFileSync('/etc/bingdashan-cn/alipay_pub.pem', 'utf-8');
          const verifier = crypto.createVerify('RSA-SHA256');
          verifier.update(body.replace(/sign=[^&]*/, ''));
          
          const valid = verifier.verify(publicKey, params.sign);
          
          if (valid && params.trade_status === 'TRADE_SUCCESS') {
            updateOrderPaid(params.out_trade_no, params)
              .then(function() {
                log('SUCCESS: ' + params.out_trade_no);
                res.writeHead(200, {'Content-Type': 'text/plain'});
                res.end('success');
              })
              .catch(function(e) {
                log('DB ERROR: ' + e.message);
                res.writeHead(500, {'Content-Type': 'application/json'});
                res.end(JSON.stringify({error: 'internal_error'}));
              });
          } else {
            log('PENDING/FAIL: status=' + params.trade_status);
            res.writeHead(400, {'Content-Type': 'text/plain'});
            res.end('failed');
          }
        } catch (e) {
          log('VERIFY ERROR: ' + e.message);
          res.writeHead(500, {'Content-Type': 'application/json'});
          res.end(JSON.stringify({error: 'verification_failed'}));
        }
      });`;

// 检查是否包含要替换的代码
if (content.includes(oldCallback)) {
  // 替换代码
  content = content.replace(oldCallback, newCallback);
  
  // 备份原文件
  const backupPath = path + '.bak.' + Date.now();
  fs.copyFileSync(path, backupPath);
  console.log('✅ 已备份原文件到: ' + backupPath);
  
  // 写入新文件
  fs.writeFileSync(path, content, 'utf8');
  console.log('✅ 已修复回调处理代码');
  console.log('');
  console.log('📝 修复内容:');
  console.log('   - 使用同步的req.on事件处理器');
  console.log('   - 添加log记录便于调试');
  console.log('   - 确保HTTP响应一定会发送');
  console.log('   - 改进错误处理和参数解析');
  console.log('');
  console.log('🚀 下一步:');
  console.log('   1. systemctl restart bingdashan-cn');
  console.log('   2. curl -X POST "http://127.0.0.1:8794/api/pay/callback" -H "Content-Type: application/x-www-form-urlencoded" -d "out_trade_no=test&trade_status=TRADE_SUCCESS&sign=dummy"');
  console.log('');
} else {
  console.log('❌ 未找到需要替换的代码段');
  console.log('可能已经修复过，或者代码格式不同');
  console.log('');
  console.log('请手动检查文件:', path);
  console.log('查找 "else if (path === \'/api/pay/callback\')" 部分');
}

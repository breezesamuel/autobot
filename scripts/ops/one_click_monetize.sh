#!/bin/bash
# 丙大山 · 一键修复支付回调 + 启动变现流程
set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              丙大山 · 一键变现启动脚本                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: 检查服务状态
echo "【Step 1】检查服务状态..."
systemctl is-active bingdashan-cn && echo "✅ 服务运行中" || echo "❌ 服务未运行"
echo ""

# Step 2: 检查当前营收状态
echo "【Step 2】检查营收状态..."
grep 'cash=' /var/log/bingdashan/engine.log | tail -1
echo ""

# Step 3: 备份并修复回调代码
echo "【Step 3】修复支付宝回调代码..."
BACKUP_FILE="/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js.bak.$(date +%s)"
cp /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js "$BACKUP_FILE"
echo "✅ 已备份到: $BACKUP_FILE"
echo ""
echo "📝 请手动编辑以下文件:"
echo "   nano /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js"
echo ""
echo "   找到第166-200行的回调处理代码，替换为:"
echo "   ===================================================="
echo "   } else if (path === '/api/pay/callback') {"
echo "     let body = '';"
echo "     req.setEncoding('utf8');"
echo "     req.on('data', function(chunk) { body += chunk; });"
echo "     req.on('end', function() {"
echo "       const params = {};"
echo "       if (body) {"
echo "         body.split('&').forEach(function(pair) {"
echo "           const eq = pair.indexOf('=');"
echo "           if (eq > 0) {"
echo "             params[decodeURIComponent(pair.substring(0, eq))] ="
echo "               decodeURIComponent(pair.substring(eq + 1));"
echo "           }"
echo "         });"
echo "       }"
echo "       log('CALLBACK: ' + params.trade_status + ' ' + params.out_trade_no);"
echo "       try {"
echo "         const publicKey = fs.readFileSync('/etc/bingdashan-cn/alipay_pub.pem', 'utf-8');"
echo "         const verifier = crypto.createVerify('RSA-SHA256');"
echo "         verifier.update(body.replace(/sign=[^&]*/, ''));"
echo "         if (verifier.verify(publicKey, params.sign) && params.trade_status === 'TRADE_SUCCESS') {"
echo "           updateOrderPaid(params.out_trade_no, params).then(function() {"
echo "             log('SUCCESS: ' + params.out_trade_no);"
echo "             res.writeHead(200); res.end('success');"
echo "           }).catch(function(e) {"
echo "             log('DB ERROR: ' + e.message);"
echo "             res.writeHead(500); res.end('error');"
echo "           });"
echo "         } else {"
echo "           log('PENDING: ' + params.trade_status);"
echo "           res.writeHead(400); res.end('failed');"
echo "         }"
echo "       } catch (e) {"
echo "         log('VERIFY ERROR: ' + e.message);"
echo "         res.writeHead(500); res.end('error');"
echo "       }"
echo "     });"
echo "   }"
echo "   ===================================================="
echo ""

# Step 4: 重启服务（修复后执行）
echo "【Step 4】修复完成后重启服务:"
echo "   systemctl restart bingdashan-cn"
echo "   curl -s -X POST 'http://127.0.0.1:8794/api/pay/callback' \\ -H 'Content-Type: application/x-www-form-urlencoded' \\ -d 'out_trade_no=test&trade_status=TRADE_SUCCESS&sign=dummy'"
echo ""

# Step 5: 显示催款消息
echo "【Step 5】催款消息（复制发送到微信/QQ）:"
echo "=================================================="
cat /opt/bingdashan/data/outreach_messages.txt 2>/dev/null | head -100 || echo "消息文件不存在，请先运行生成脚本"
echo ""

# Step 6: 显示高价值线索
echo "【Step 6】高价值线索TOP10:"
echo "=================================================="
node -e "
const store = require('/opt/bingdashan/core/store');
const db = store.read();
const leads = db.leads || [];
const top10 = leads.filter(l => l.signal >= 70).sort((a,b) => b.signal - a.signal).slice(0,10);
top10.forEach((l, i) => console.log(\`\${i+1}. \${l.name.padEnd(45)} 信号=\${l.signal} ⭐\${l.stars||0} [\${l.stage}]\`));
" 2>/dev/null || echo "无法读取leads数据"
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    执行清单                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "□ 1. 编辑 alipay.js 修复回调代码（30分钟）"
echo "□ 2. 重启服务: systemctl restart bingdashan-cn"
echo "□ 3. 测试回调端点"
echo "□ 4. 发送13条催款消息（10分钟）"
echo "□ 5. 联系TOP5高价值线索（20分钟）"
echo ""
echo "💰 预期收入:"
echo "   - Pending转化: ¥700-1000"
echo "   - 线索转化: ¥67-250/月"
echo "   - 合计首月: ¥800-1250"
echo ""

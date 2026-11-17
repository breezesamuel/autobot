#!/bin/bash
# 丙大山 · 一键深度修复脚本
# 生成时间: 2026-11-15
# 用途: SSH恢复后一键执行所有修复

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║     丙大山 · 深度挖掘 v5 一键修复                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1: 创建目录结构
echo -e "${BLUE}[1/7]${NC} 创建必要目录..."
mkdir -p /www/wwwroot/tools-cn.highkingflower.com/api
mkdir -p /opt/bingdashan/data/{billing,runtime,backups,outreach_autogen}
mkdir -p /var/log/bingdashan
echo -e "${GREEN}✅ 目录创建完成${NC}"
echo ""

# Step 2: 检查并创建.env
echo -e "${BLUE}[2/7]${NC} 检查环境配置..."
if [ ! -f /opt/bingdashan/.env ]; then
    echo -e "${YELLOW}⚠️  .env不存在，创建模板...${NC}"
    cat > /opt/bingdashan/.env << 'ENVEOF'
# ===== 丙大山 · 支付宝配置 (必须填入真实值) =====
ALIPAY_APP_ID=your_app_id_here
ALIPAY_GATEWAY=https://openapi.alipay.com/gateway.do
ALIPAY_SIGN_TYPE=RSA2
ALIPAY_PUBLIC_KEY=your_public_key_here
ALIPAY_PRIVATE_KEY=your_private_key_here

# ===== Supabase配置 =====
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_key_here

# ===== Upstash KV配置 =====
KV_REST_API_URL=https://your-kv.upstash.io
KV_REST_API_TOKEN=your_token_here

# ===== SMTP配置 =====
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=460123249@qq.com
SMTP_PASS=your_email_password_here

# ===== 管理员密钥 =====
ADMIN_SECRET=your_admin_secret_here
AUTOOPS_SECRET=your_autoops_secret_here

# ===== 告警邮件 =====
ALERT_EMAIL=460123249@qq.com

# ===== 价格配置 =====
OVERFIT_PRICE_YUAN=39
OVERFIT_PRICE_COIN=400
SCAN_PRICE_YUAN=99
SCAN_PRICE_COIN=1000
MINUTE_PRICE_YUAN=99
MINUTE_PRICE_COIN=1000
ENVEOF
    echo -e "${GREEN}✅ .env模板已创建${NC}"
    echo -e "${YELLOW}⚠️  请编辑 /opt/bingdashan/.env 填入真实配置!${NC}"
else
    echo -e "${GREEN}✅ .env已存在${NC}"
fi
echo ""

# Step 3: 修复SSL密钥权限
echo -e "${BLUE}[3/7]${NC} 修复SSL密钥权限..."
for keyfile in /etc/bingdashan-cn/alipay_priv.pem /etc/bingdashan-cn/alipay_pub.pem; do
    if [ -f "$keyfile" ]; then
        current_perms=$(stat -c %a "$keyfile" 2>/dev/null || stat -f %Lp "$keyfile" 2>/dev/null)
        if [ "$current_perms" != "600" ]; then
            chmod 600 "$keyfile"
            echo -e "${YELLOW}  修复权限: $keyfile ($current_perms -> 600)${NC}"
        else
            echo -e "${GREEN}  ✅ 权限正确: $keyfile${NC}"
        fi
    else
        echo -e "${YELLOW}  ⚠️  文件不存在: $keyfile${NC}"
    fi
done
echo ""

# Step 4: 创建支付网关 (如果缺失)
echo -e "${BLUE}[4/7]${NC} 创建支付网关..."
if [ ! -f /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js ]; then
    echo "Creating api/alipay.js..."
    cat > /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js << 'JSEOF'
'use strict';
// Alipay Payment Gateway — 丙大山
const crypto = require('crypto');
const fs = require('fs');

function loadEnv() {
  const env = {};
  try {
    const content = fs.readFileSync('/opt/bingdashan/.env', 'utf-8');
    content.split('\n').forEach(line => {
      const match = line.match(/^([A-Z_]+)=(.*)$/);
      if (match) {
        env[match[1]] = match[2].trim().replace(/^[\"']|[\"']$/g, '');
      }
    });
  } catch (e) { console.error('[ALIPAY] Env load error:', e.message); }
  return env;
}

const env = loadEnv();
const PLAN_AMOUNTS = { t: 1, m: 83, p: 199, q: 269, v: 399, y: 899 };

function generateOrderId() {
  return 'bd_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function signRequest(params) {
  const privateKey = env.ALIPAY_PRIVATE_KEY || '';
  if (!privateKey) { console.error('[ALIPAY] Missing PRIVATE_KEY'); return null; }
  const sortedKeys = Object.keys(params).sort();
  let signStr = sortedKeys.map(k => k + '=' + params[k]).join('&');
  try {
    const sign = crypto.createSign('RSA-SHA256');
    sign.update(signStr, 'utf8');
    return sign.sign(privateKey, 'base64');
  } catch (e) { console.error('[ALIPAY] Sign error:', e.message); return null; }
}

function saveOrderToDB(order) {
  try {
    const dbPath = '/opt/bingdashan/data/db.json';
    let data = { orders: [] };
    if (fs.existsSync(dbPath)) data = JSON.parse(fs.readFileSync(dbPath, 'utf-8'));
    data.orders.push(order);
    fs.writeFileSync(dbPath, JSON.stringify(data, null, 2));
  } catch (e) { console.error('[ALIPAY] DB save error:', e.message); }
}

function updateOrderPaid(outTradeNo, callbackParams) {
  try {
    const dbPath = '/opt/bingdashan/data/db.json';
    const data = JSON.parse(fs.readFileSync(dbPath, 'utf-8'));
    for (const order of data.orders) {
      if (order.out_trade_no === outTradeNo) {
        order.status = 'paid';
        order.paid = true;
        order.paid_at = new Date().toISOString();
        order.gateway = 'alipay';
        order.trade_no = callbackParams.trade_no;
        break;
      }
    }
    fs.writeFileSync(dbPath, JSON.stringify(data, null, 2));
  } catch (e) { console.error('[ALIPAY] DB update error:', e.message); }
}

module.exports = {
  onRequest(req, res) {
    const url = new URL(req.url, 'http://localhost:8794');
    const path = url.pathname;
    
    if (path === '/api/pay') {
      const plan = url.searchParams.get('plan') || 'm';
      const ref = url.searchParams.get('ref') || 'anonymous';
      const amount = PLAN_AMOUNTS[plan] || 83;
      const orderId = generateOrderId();
      
      const params = {
        app_id: env.ALIPAY_APP_ID,
        method: 'alipay.trade.page.pay',
        charset: 'utf-8',
        sign_type: 'RSA2',
        timestamp: new Date().toISOString(),
        version: '1.0',
        notify_url: 'https://tools-cn.highkingflower.com/api/pay/callback',
        return_url: 'https://tools.highkingflower.com/channels.html?ref=' + encodeURIComponent(ref),
        out_trade_no: orderId,
        total_amount: amount.toString(),
        subject: '丙大山-' + plan + '-' + ref,
        product_code: 'FAST_INSTANT_TRADE_PAY'
      };
      
      const sign = signRequest(params);
      if (!sign) {
        res.writeHead(500, {'Content-Type': 'application/json'});
        res.end(JSON.stringify({ error: 'signature_failed' }));
        return;
      }
      params.sign = sign;
      
      const queryString = Object.keys(params).sort()
        .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k]))
        .join('&');
      
      const payUrl = (env.ALIPAY_GATEWAY || 'https://openapi.alipay.com/gateway.do') + '?' + queryString;
      
      saveOrderToDB({
        id: orderId, createdAt: Date.now(), visitor: 'ip:' + ref,
        plan, amount, currency: 'CNY', months: plan==='y'?12:plan==='q'?3:plan==='v'?6:1,
        status: 'pending', ref, slug: 'tool', gateway: 'alipay',
        out_trade_no: orderId, pay_url: payUrl
      });
      
      res.writeHead(200, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({ ok: true, orderId, amount, plan, ref, payUrl, expireAt: Date.now() + 7200000 }));
      
    } else if (path === '/api/pay/callback') {
      let body = '';
      req.on('data', chunk => body += chunk.toString());
      req.on('end', () => {
        const params = {};
        body.split('&').forEach(pair => { const [k,v] = pair.split('='); params[decodeURIComponent(k)] = decodeURIComponent(v||''); });
        
        try {
          const publicKey = fs.readFileSync('/etc/bingdashan-cn/alipay_pub.pem', 'utf-8');
          const verifier = crypto.createVerify('RSA-SHA256');
          verifier.update(body.replace(/sign=[^&]*/, ''));
          
          if (verifier.verify(publicKey, params.sign) && params.trade_status === 'TRADE_SUCCESS') {
            updateOrderPaid(params.out_trade_no, params);
            res.writeHead(200); res.end('success');
          } else {
            res.writeHead(400); res.end('failed');
          }
        } catch (e) { res.writeHead(500); res.end('error'); }
      });
      
    } else if (path === '/api/health') {
      res.writeHead(200, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({ ok: true, service: 'bingdashan-pay', timestamp: Date.now() }));
      
    } else {
      res.writeHead(404, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({ error: 'not found', path }));
    }
  }
};
JSEOF
    echo -e "${GREEN}✅ alipay.js 已创建${NC}"
else
    echo -e "${GREEN}✅ alipay.js 已存在${NC}"
fi
echo ""

# Step 5: 重启服务
echo -e "${BLUE}[5/7]${NC} 重启服务..."
systemctl daemon-reload
systemctl restart bingdashan-cn
sleep 2

if systemctl is-active --quiet bingdashan-cn; then
    echo -e "${GREEN}✅ 服务运行正常${NC}"
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo "查看日志: journalctl -u bingdashan-cn --no-pager -n 20"
fi
echo ""

# Step 6: 健康检查
echo -e "${BLUE}[6/7]${NC} 健康检查..."
HEALTH=$(curl -s http://127.0.0.1:8794/api/health 2>/dev/null || echo '{"error":"unavailable"}')
echo "Health: $HEALTH"
echo ""

# Step 7: 支付测试
echo -e "${BLUE}[7/7]${NC} 支付流程测试..."
TEST_REF="fix_test_$(date +%s)"
PAY_TEST=$(curl -s "http://127.0.0.1:8794/api/pay?plan=m&ref=$TEST_REF" 2>/dev/null || echo '{"error":"endpoint_unreachable"}')
echo "Pay test: $PAY_TEST"
echo ""

# 完成
echo "╔════════════════════════════════════════════════════════╗"
echo "║                     修复完成                           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "下一步操作:"
echo "  1. 编辑 /opt/bingdashan/.env 填入真实的支付宝配置"
echo "  2. 重新运行本脚本完成最终配置"
echo "  3. 测试实际支付流程"
echo ""
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"

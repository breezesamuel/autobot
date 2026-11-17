'use strict';
// 丙大山 Alipay Payment Gateway - Final Version
const crypto = require('crypto');
const fs = require('fs');

// Load environment variables
function loadEnv() {
  const env = {};
  try {
    const content = fs.readFileSync('/opt/bingdashan/.env', 'utf-8');
    content.split('\n').forEach(line => {
      line = line.trim();
      if (!line || line.startsWith('#')) return;
      const eqIndex = line.indexOf('=');
      if (eqIndex > 0) {
        const key = line.substring(0, eqIndex).trim();
        let value = line.substring(eqIndex + 1).trim();
        if ((value.startsWith('"') && value.endsWith('"')) || 
            (value.startsWith("'") && value.endsWith("'"))) {
          value = value.substring(1, value.length - 1);
        }
        env[key] = value;
      }
    });
  } catch (e) {
    console.error('[ALIPAY] Env error:', e.message);
  }
  return env;
}

const env = loadEnv();

// Plan amounts
const PLAN_AMOUNTS = { t: 1, m: 83, p: 199, q: 269, v: 399, y: 899 };

// Generate order ID
function generateOrderId() {
  return 'bd_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Logger
function log(msg) {
  const ts = new Date().toISOString().replace('T', ' ').slice(0, 19);
  const line = '[ALIPAY][' + ts + '] ' + msg;
  console.log(line);
  try { fs.appendFileSync('/var/log/bingdashan/engine.log', line + '\n'); } catch(e) {}
}

// Sign request using PEM file directly
function signRequest(params) {
  try {
    // Read private key from PEM file
    const privateKey = fs.readFileSync('/etc/bingdashan-cn/alipay_priv.pem', 'utf8');
    
    if (!privateKey || privateKey.length < 100) {
      log('ERROR: Private key file empty or missing');
      return null;
    }
    
    // Sort params
    const sortedKeys = Object.keys(params).sort();
    const signStr = sortedKeys.map(k => k + '=' + params[k]).join('&');
    
    const sign = crypto.createSign('RSA-SHA256');
    sign.update(signStr, 'utf8');
    return sign.sign(privateKey, 'base64');
  } catch (e) {
    log('SIGN ERROR: ' + e.message);
    return null;
  }
}

// Save order to DB
async function saveOrderToDB(order) {
  try {
    const dbPath = '/opt/bingdashan/data/db.json';
    let data = { orders: [] };
    if (fs.existsSync(dbPath)) {
      data = JSON.parse(fs.readFileSync(dbPath, 'utf-8'));
    }
    data.orders.push(order);
    fs.writeFileSync(dbPath, JSON.stringify(data, null, 2));
    log('ORDER SAVED: ' + order.id);
  } catch (e) {
    log('DB SAVE ERROR: ' + e.message);
  }
}

// Update order to paid
async function updateOrderPaid(outTradeNo, callbackParams) {
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
        log('ORDER PAID: ' + outTradeNo + ' ref=' + order.ref);
        break;
      }
    }
    fs.writeFileSync(dbPath, JSON.stringify(data, null, 2));
    log('DATABASE UPDATED');
  } catch (e) {
    log('DB UPDATE ERROR: ' + e.message);
  }
}

// Main handler
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
        subject: 'BingDashan-' + plan + '-' + ref,
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
        plan, amount, currency: 'CNY',
        months: plan==='y'?12:plan==='q'?3:plan==='v'?6:1,
        status: 'pending', ref, slug: 'tool', gateway: 'alipay',
        out_trade_no: orderId, pay_url: payUrl
      });
      
      res.writeHead(200, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({
        ok: true, orderId, amount, plan, ref, payUrl,
        expireAt: Date.now() + 7200000
      }));
      
    } else if (path === '/api/pay/callback') {
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

log('ALIPAY.JS LOADED - Reading key from PEM file');

// 丙大山 · Alipay Payment Gateway
// Auto-generated on: 2026-11-15

const crypto = require('crypto');
const fs = require('fs');

// Load environment config
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
  } catch (e) {
    console.error('[ALIPAY] Failed to load .env:', e.message);
  }
  return env;
}

const env = loadEnv();

// Plan to amount mapping
const PLAN_AMOUNTS = {
  t: 1,    // trial
  m: 83,   // monthly
  p: 199,  // pro
  q: 269,  // quarterly
  v: 399,  // VIP
  y: 899   // annual
};

// Generate unique order ID
function generateOrderId() {
  return 'bd_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function log(msg) {
  const ts = new Date().toISOString().replace('T', ' ').slice(0, 19);
  const line = '[ALIPAY][' + ts + '] ' + msg;
  console.log(line);
  try {
    fs.appendFileSync('/var/log/bingdashan/engine.log', line + '\n');
  } catch (e) {}
}

// Sign request with RSA2
function signRequest(params) {
  const privateKey = env.ALIPAY_PRIVATE_KEY || '';
  if (!privateKey) {
    log('ERROR: ALIPAY_PRIVATE_KEY not configured');
    return null;
  }
  
  // Sort parameters
  const sortedKeys = Object.keys(params).sort();
  let signStr = sortedKeys.map(k => k + '=' + params[k]).join('&');
  
  try {
    const sign = crypto.createSign('RSA-SHA256');
    sign.update(signStr, 'utf8');
    return sign.sign(privateKey, 'base64');
  } catch (e) {
    log('SIGN ERROR: ' + e.message);
    return null;
  }
}

// Save order to database
async function saveOrderToDB(order) {
  try {
    const dbPath = '/opt/bingdashan/data/db.json';
    let data = { orders: [] };
    
    if (fs.existsSync(dbPath)) {
      const content = fs.readFileSync(dbPath, 'utf-8');
      data = JSON.parse(content);
    }
    
    data.orders.push(order);
    fs.writeFileSync(dbPath, JSON.stringify(data, null, 2));
    log('ORDER SAVED: ' + order.id);
  } catch (e) {
    log('DB SAVE ERROR: ' + e.message);
  }
}

// Update order to paid status
async function updateOrderPaid(outTradeNo, callbackParams) {
  try {
    const dbPath = '/opt/bingdashan/data/db.json';
    const content = fs.readFileSync(dbPath, 'utf-8');
    const data = JSON.parse(content);
    
    let updated = false;
    for (const order of data.orders) {
      if (order.out_trade_no === outTradeNo) {
        order.status = 'paid';
        order.paid = true;
        order.paid_at = new Date().toISOString();
        order.gateway = 'alipay';
        order.trade_no = callbackParams.trade_no;
        updated = true;
        log('ORDER PAID: ' + outTradeNo + ' ref=' + order.ref + ' amount=' + order.amount);
        break;
      }
    }
    
    if (updated) {
      fs.writeFileSync(dbPath, JSON.stringify(data, null, 2));
      log('DATABASE UPDATED successfully');
    } else {
      log('WARNING: Order not found: ' + outTradeNo);
    }
  } catch (e) {
    log('DB UPDATE ERROR: ' + e.message);
  }
}

// Handle payment request
function handlePayRequest(req, res, url) {
  const plan = url.searchParams.get('plan') || 'm';
  const ref = url.searchParams.get('ref') || 'anonymous';
  const slug = url.searchParams.get('slug') || 'tool';
  
  const amount = PLAN_AMOUNTS[plan] || 83;
  const orderId = generateOrderId();
  const now = new Date().toISOString();
  
  // Prepare Alipay parameters
  const params = {
    app_id: env.ALIPAY_APP_ID,
    method: 'alipay.trade.page.pay',
    charset: 'utf-8',
    sign_type: 'RSA2',
    timestamp: now,
    version: '1.0',
    notify_url: 'https://tools-cn.highkingflower.com/api/pay/callback',
    return_url: 'https://tools.highkingflower.com/channels.html?ref=' + encodeURIComponent(ref),
    out_trade_no: orderId,
    total_amount: amount.toString(),
    subject: ' BingDashan-' + plan + '-' + ref,
    product_code: 'FAST_INSTANT_TRADE_PAY'
  };
  
  // Sign request
  const sign = signRequest(params);
  if (!sign) {
    log('SIGNATURE FAILED - check ALIPAY_PRIVATE_KEY');
    res.writeHead(500, {'Content-Type': 'application/json'});
    res.end(JSON.stringify({ error: 'signature_generation_failed' }));
    return;
  }
  params.sign = sign;
  
  // Build payment URL
  const queryString = Object.keys(params)
    .sort()
    .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k]))
    .join('&');
  
  const payUrl = (env.ALIPAY_GATEWAY || 'https://openapi.alipay.com/gateway.do') + '?' + queryString;
  
  // Save order to database
  saveOrderToDB({
    id: orderId,
    createdAt: Date.now(),
    visitor: 'ip:' + ref,
    plan: plan,
    amount: amount,
    currency: 'CNY',
    months: plan === 'y' ? 12 : plan === 'q' ? 3 : plan === 'v' ? 6 : 1,
    status: 'pending',
    ref: ref,
    slug: slug,
    gateway: 'alipay',
    out_trade_no: orderId,
    pay_url: payUrl,
    note: 'Payment initiated via alipay.js'
  });
  
  // Return payment info
  res.writeHead(200, {'Content-Type': 'application/json'});
  res.end(JSON.stringify({
    ok: true,
    orderId: orderId,
    amount: amount,
    plan: plan,
    ref: ref,
    payUrl: payUrl,
    expireAt: Date.now() + 7200000 // 2 hours
  }));
}

// Handle Alipay callback
function handlePayCallback(req, res) {
  let body = '';
  req.on('data', chunk => { body += chunk.toString(); });
  req.on('end', async () => {
    try {
      // Parse callback parameters
      const params = {};
      body.split('&').forEach(pair => {
        const [k, v] = pair.split('=');
        params[decodeURIComponent(k)] = decodeURIComponent(v || '');
      });
      
      log('CALLBACK RECEIVED: trade_status=' + params.trade_status + ' out_trade_no=' + params.out_trade_no);
      
      // Verify signature
      const publicKey = fs.readFileSync('/etc/bingdashan-cn/alipay_pub.pem', 'utf-8');
      const verifier = crypto.createVerify('RSA-SHA256');
      verifier.update(body.replace(/sign=[^&]*/, ''));
      
      const valid = verifier.verify(publicKey, params.sign);
      
      if (valid && params.trade_status === 'TRADE_SUCCESS') {
        // Update order to paid
        await updateOrderPaid(params.out_trade_no, params);
        
        log('PAYMENT SUCCESS: ' + params.out_trade_no);
        
        res.writeHead(200);
        res.end('success');
      } else {
        log('PAYMENT FAILED or PENDING: ' + params.out_trade_no + ' status=' + params.trade_status);
        res.writeHead(400);
        res.end('failed');
      }
    } catch (e) {
      log('CALLBACK ERROR: ' + e.message);
      res.writeHead(500);
      res.end('error');
    }
  });
}

// Main export
module.exports = {
  onRequest(req, res) {
    const url = new URL(req.url, 'http://localhost:8794');
    const pathname = url.pathname;
    
    log('REQUEST: ' + pathname + ' ' + req.method);
    
    if (pathname === '/api/pay') {
      handlePayRequest(req, res, url);
    } else if (pathname === '/api/pay/callback') {
      handlePayCallback(req, res);
    } else if (pathname === '/api/health') {
      res.writeHead(200, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({ 
        ok: true, 
        service: 'bingdashan-pay', 
        timestamp: Date.now(),
        config: {
          alipay_configured: !!env.ALIPAY_APP_ID,
          gateway: env.ALIPAY_GATEWAY || 'not_set'
        }
      }));
    } else {
      res.writeHead(404, {'Content-Type': 'application/json'});
      res.end(JSON.stringify({ error: 'not found', path: pathname }));
    }
  }
};

log('ALIPAY.JS MODULE LOADED SUCCESSFULLY');

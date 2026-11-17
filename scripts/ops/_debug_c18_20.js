const fs = require('fs');
const path = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js';
const src = fs.readFileSync(path, 'utf8');

// Find where scan_api route is
const lines = src.split('\n');
for (let i = 0; i < lines.length; i++) {
  if (lines[i].includes('scan_api') || lines[i].includes('alert_api') || lines[i].includes('minute_klines')) {
    console.log('Line ' + (i+1) + ': ' + lines[i].trim().slice(0, 80));
  }
}

// Check if lib files exist
for (const mod of ['scan_api', 'alert_api', 'minute_klines']) {
  const libPath = '/www/wwwroot/tools-cn.highkingflower.com/lib/' + mod + '.js';
  const exists = fs.existsSync(libPath);
  const size = exists ? fs.statSync(libPath).size : 0;
  console.log(mod + '.js: exists=' + exists + ' size=' + size);
}

// Test requiring the modules
console.log('\n=== Module require test ===');
try {
  const m1 = require('/www/wwwroot/tools-cn.highkingflower.com/lib/scan_api.js');
  console.log('scan_api.js requires OK, has onRequest:', typeof m1.onRequest);
} catch(e) { console.log('scan_api require ERR:', e.message.slice(0, 80)); }

try {
  const m2 = require('/www/wwwroot/tools-cn.highkingflower.com/lib/alert_api.js');
  console.log('alert_api.js requires OK, has onRequest:', typeof m2.onRequest);
} catch(e) { console.log('alert_api require ERR:', e.message.slice(0, 80)); }

try {
  const m3 = require('/www/wwwroot/tools-cn.highkingflower.com/lib/minute_klines.js');
  console.log('minute_klines.js requires OK, has onRequest:', typeof m3.onRequest);
} catch(e) { console.log('minute_klines require ERR:', e.message.slice(0, 80)); }

const fs = require('fs');
const path = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js';
const src = fs.readFileSync(path, 'utf8');
const lines = src.split('\n');

// Find the route parsing section
console.log('=== Route parsing logic ===');
for (let i = 0; i < Math.min(30, lines.length); i++) {
  if (lines[i].includes('route') || lines[i].includes('pathname') || lines[i].includes('searchParams')) {
    console.log((i+1) + ': ' + lines[i]);
  }
}

console.log('\n=== Around scan_api route (line 1745-1780) ===');
for (let i = 1744; i < Math.min(1780, lines.length); i++) {
  console.log((i+1) + ': ' + lines[i]);
}

// Test the actual routing by simulating a request
console.log('\n=== Simulating route parse for /api/scan_api ===');
const testUrl = '/api/scan_api?action=rate&ref=test';
const u = new URL(testUrl, 'http://x');
let route = u.searchParams.get('r') || u.pathname;
route = '/' + String(route).replace(/^\/+/, '').replace(/^api\//, '');
if (route.indexOf('/api/') !== 0) route = '/api' + route;
console.log('Input:', testUrl);
console.log('Parsed route:', route);
console.log('Starts with /api/scan_api:', route.startsWith('/api/scan_api'));

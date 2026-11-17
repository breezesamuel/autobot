const fs = require('fs');
const src = fs.readFileSync('/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js', 'utf8');
// Find lines with "route=" assignment
const lines = src.split('\n');
for (let i = 0; i < lines.length; i++) {
  const l = lines[i];
  if (l.includes("let route=") || l.includes("const route=") || l.includes("route=u")) {
    console.log((i+1) + ': ' + l.trim().slice(0,120));
  }
  if (l.includes("route.indexOf") || l.includes("route==='") || l.includes("route==='/api")) {
    console.log((i+1) + ': ' + l.trim().slice(0,120));
  }
}
// Show lines 465-490 (where routing starts)
console.log('\n=== Lines 465-495 ===');
for (let i = 464; i < 495 && i < lines.length; i++) {
  console.log((i+1) + ': ' + lines[i]);
}
// Show lines around scan_api to see what's before it
console.log('\n=== Lines 1730-1750 ===');
for (let i = 1729; i < 1750 && i < lines.length; i++) {
  console.log((i+1) + ': ' + lines[i]);
}

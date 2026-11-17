const fs=require('fs');
const src=fs.readFileSync('/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js','utf8');
const lines=src.split('\n');
// Find ALL if(route==='/api/... blocks and their line numbers
console.log('=== All route checks ===');
for(let i=0;i<lines.length;i++){
  const l=lines[i].trim();
  if(l.startsWith("if(route==='")){
    console.log((i+1)+': '+l.slice(0,80));
  }
}
// Check: is scan_api BEFORE or AFTER the 404 fallback?
const targetLine=lines.findIndex(l=>l.includes("send(404,{ok:false,error:'not found'"));
const scanLine=lines.findIndex(l=>l.includes("route.startsWith('/api/scan_api')"));
console.log('\n404 fallback at line:', targetLine+1);
console.log('scan_api route at line:', scanLine+1);
console.log('scan_api BEFORE 404?', scanLine < targetLine);
// Show context around scan_api
console.log('\n=== Context around scan_api (line '+(scanLine)+') ===');
for(let i=Math.max(0,scanLine-3);i<Math.min(lines.length,scanLine+15);i++){
  console.log((i+1)+': '+lines[i]);
}
// Also show what comes right BEFORE the scan_api block
console.log('\n=== Lines just before scan_api ===');
for(let i=Math.max(0,scanLine-15);i<scanLine;i++){
  console.log((i+1)+': '+lines[i]);
}

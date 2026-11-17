const fs=require('fs');
const path=require('path');
const LIB='/www/wwwroot/tools-cn.highkingflower.com/lib';
console.log('=== Fix remaining prices ===');

// C8 whitebox -> ¥199/seat
{
  const p=path.join(LIB,'whitebox.js');
  let s=fs.readFileSync(p,'utf8');
  s=s.replace(/\? v : \d+;/g,(m)=>{
    // Only replace the yuan default (39->199) and coin default (400->2000)
    // Find position relative to PRICE_YUAN vs PRICE_COIN
    return m; // skip, handle below
  });
  // More precise: replace the specific defaults
  s=s.replace(/PRICE_YUAN = \(function\(\)\{\s*var v = parseFloat\(process\.env\.WB_SEAT_YUAN\);\s*return \(isFinite\(v\) && v > 0\) \? v : \d+/,'PRICE_YUAN = (function(){ var v = parseFloat(process.env.WB_SEAT_YUAN); return (isFinite(v) && v > 0) ? v : 199');
  s=s.replace(/PRICE_COIN = \(function\(\)\{\s*var v = parseFloat\(process\.env\.WB_SEAT_COIN\);\s*return \(isFinite\(v\) && v > 0\) \? v : \d+/,'PRICE_COIN = (function(){ var v = parseFloat(process.env.WB_SEAT_COIN); return (isFinite(v) && v > 0) ? v : 2000');
  fs.writeFileSync(p,s);
  try{require('child_process').execSync('node --check "'+p+'"',{stdio:['pipe','pipe','pipe']});console.log('whitebox.js: OK');}catch(e){console.log('whitebox FAIL:',e.message.slice(0,60));}
}

// C12 quantannual -> ¥399 month / ¥3990 year (the rate endpoint shows the month price)
{
  const p=path.join(LIB,'quantannual.js');
  let s=fs.readFileSync(p,'utf8');
  // The quantannual module has MONTH/YEAR prices, let's check what's there
  const matches=s.match(/PRICE_MONTH_YUAN.*?\? v : (\d+)/g);
  if(matches){
    console.log('quantannual month prices found:',matches);
    // Replace any wrong defaults
    s=s.replace(/PRICE_MONTH_YUAN.*?\? v : \d+/g,'PRICE_MONTH_YUAN = (function(){ var v = parseFloat(process.env.QA_MONTH_YUAN); return (isFinite(v) && v > 0) ? v : 399; }()) ;');
    s=s.replace(/PRICE_YEAR_YUAN.*?\? v : \d+/g,'PRICE_YEAR_YUAN = (function(){ var v = parseFloat(process.env.QA_YEAR_YUAN); return (isFinite(v) && v > 0) ? v : 3990; }()) ;');
    s=s.replace(/PRICE_MONTH_COIN.*?\? v : \d+/g,'PRICE_MONTH_COIN = (function(){ var v = parseFloat(process.env.QA_MONTH_COIN); return (isFinite(v) && v > 0) ? v : 4000; }()) ;');
    s=s.replace(/PRICE_YEAR_COIN.*?\? v : \d+/g,'PRICE_YEAR_COIN = (function(){ var v = parseFloat(process.env.QA_YEAR_COIN); return (isFinite(v) && v > 0) ? v : 39900; }()) ;');
  }
  fs.writeFileSync(p,s);
  try{require('child_process').execSync('node --check "'+p+'"',{stdio:['pipe','pipe','pipe']});console.log('quantannual.js: OK');}catch(e){console.log('quantannual FAIL:',e.message.slice(0,60));}
}

console.log('\n=== Verify fixed channels ===');
const {execSync}=require('child_process');
for(const slug of ['whitebox','quantannual','rl_trader','ml_backtest','scan_api','alert_api']){
  try{
    const r=execSync(`curl -s "http://127.0.0.1:8794/api/${slug}?action=rate&ref=t"`,{encoding:'utf8',timeout:5000});
    const d=JSON.parse(r);
    console.log(`${slug}: ok=${d.ok} price_yuan=${d.price_yuan}`);
  }catch(e){console.log(`${slug}: ERR`);}
}
console.log('\nDone');

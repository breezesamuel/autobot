const fs=require('fs');
const path=require('path');
const LIB='/www/wwwroot/tools-cn.highkingflower.com/lib';

const configs=[
  {name:'scan_api',     yuan:99,  coin:1000},
  {name:'alert_api',    yuan:29,  coin:300},
  {name:'minute_klines',yuan:99,  coin:1000},
];

for(const cfg of configs){
  const p=path.join(LIB,cfg.name+'.js');
  let src=fs.readFileSync(p,'utf8');
  
  // Fix PRICE_YUAN default
  src=src.replace(
    /PRICE_YUAN = \(function\(\)\{\s*var v = parseFloat\(process\.env\.[^)]+\);\s*return \(isFinite\(v\) && v > 0\) \? v : \d+;[\s\S]*?\}\)\(\);/,
    `PRICE_YUAN = (function(){ var v = parseFloat(process.env.${cfg.name.toUpperCase().replace(/_API$/,'')}_PRICE_YUAN); return (isFinite(v) && v > 0) ? v : ${cfg.yuan}; }()) ;`
  );
  
  // Fix PRICE_COIN default
  src=src.replace(
    /PRICE_COIN = \(function\(\)\{\s*var v = parseFloat\(process\.env\.[^)]+\);\s*return \(isFinite\(v\) && v > 0\) \? v : \d+;[\s\S]*?\}\)\(\);/,
    `PRICE_COIN = (function(){ var v = parseFloat(process.env.${cfg.name.toUpperCase().replace(/_API$/,'')}_PRICE_COIN); return (isFinite(v) && v > 0) ? v : ${cfg.coin}; }()) ;`
  );
  
  // Also fix the note text
  src=src.replace(/note: '付费过拟合检测[^\']*/,'note: \''+cfg.name+' API (币或¥)');
  
  fs.writeFileSync(p,src,'utf8');
  
  // Verify
  try{require('child_process').execSync('node --check "'+p+'"',{stdio:['pipe','pipe','pipe']});
    console.log(cfg.name+': fixed + syntax OK');
  }catch(e){console.log(cfg.name+': FIX FAILED '+e.message.slice(0,80));}
}

// Now test
console.log('\n=== Test ===');
for(const slug of ['scan_api','alert_api','minute_klines']){
  try{
    const r=require('child_process').execSync(`curl -s "http://127.0.0.1:8794/api/${slug}?action=rate&ref=t"`,{encoding:'utf8',timeout:5000});
    const d=JSON.parse(r);
    console.log(slug+': ok='+d.ok+' price_yuan='+d.price_yuan+' note='+String(d.note||'').slice(0,30));
  }catch(e){console.log(slug+': ERR '+e.message.slice(0,60));}
}

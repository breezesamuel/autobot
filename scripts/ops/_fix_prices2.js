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
  
  // Find and replace the PRICE_YUAN line directly
  // Pattern: return (isFinite(v) && v > 0) ? v : NUM;
  const yMatch=src.match(/\? v : (\d+);[\s\S]*?\}\)\(\);/);
  if(yMatch){
    const oldNum=yMatch[1];
    src=src.replace(`? v : ${oldNum};`,`? v : ${cfg.yuan};`);
    console.log(cfg.name+': PRICE_YUAN '+oldNum+' -> '+cfg.yuan);
  }else{
    console.log(cfg.name+': PRICE_YUAN pattern NOT found, trying alternate...');
    // Fallback: simple numeric replace
    src=src.replace(/return \(isFinite\(v\) && v > 0\) \? v : \d+/g,
      `return (isFinite(v) && v > 0) ? v : ${cfg.yuan}`);
  }
  
  // Same for PRICE_COIN
  const cMatch=src.match(/PRICE_COIN.*?\? v : (\d+)/);
  if(cMatch){
    const oldCoin=cMatch[1];
    src=src.replace(`? v : ${oldCoin}`,`? v : ${cfg.coin}`);
    console.log(cfg.name+': PRICE_COIN '+oldCoin+' -> '+cfg.coin);
  }
  
  fs.writeFileSync(p,src,'utf8');
}

// Quick test
console.log('\n=== Test ===');
for(const slug of ['scan_api','alert_api','minute_klines','overfitcheck']){
  try{
    const r=require('child_process').execSync(`curl -s "http://127.0.0.1:8794/api/${slug}?action=rate&ref=t"`,{encoding:'utf8',timeout:5000});
    const d=JSON.parse(r);
    console.log(slug+': ok='+d.ok+' price_yuan='+d.price_yuan);
  }catch(e){console.log(slug+': ERR');}
}

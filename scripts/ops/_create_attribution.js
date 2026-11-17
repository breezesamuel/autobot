const fs=require('fs');
const path=require('path');
const LIB='/www/wwwroot/tools-cn.highkingflower.com/lib';
// Create attribution module (was missed due to name typo)
const tpl=fs.readFileSync(path.join(LIB,'overfitcheck.js'),'utf8');
let src=tpl.replace(/overfitcheck/g,'attribution').replace(/Overfitcheck/g,'Attribution')
  .replace(/ofc:/g,'at:').replace(/overfitcheck_kv/g,'attribution_kv')
  .replace(/'overfitcheck'/g,"'attribution'").replace(/'OF'/g,"'AT'")
  .replace(/process\.env\.OFIT_PRICE_YUAN/g,'process.env.ATTRIBUTION_PRICE_YUAN')
  .replace(/process\.env\.OFIT_PRICE_COIN/g,'process.env.ATTRIBUTION_PRICE_COIN')
  .replace(/\? v : 39;/,'? v : 49;').replace(/\? v : 400;/,'? v : 490;')
  .replace(/付费过拟合检测/,'收益归因分析API:Brinson三步拆解收益来源,¥49买5次');
fs.writeFileSync(path.join(LIB,'attribution.js'),src,'utf8');
console.log('Created attribution.js:',fs.statSync(path.join(LIB,'attribution.js')).size,'bytes');
try{require('child_process').execSync('node --check "'+path.join(LIB,'attribution.js')+'"',{stdio:['pipe','pipe','pipe']});console.log('syntax OK');}catch(e){console.log('FAIL:',e.message.slice(0,60));}

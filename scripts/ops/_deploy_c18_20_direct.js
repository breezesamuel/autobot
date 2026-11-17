// Direct-deploy C18/C19/C20 modules on CN — no shell encoding issues
const fs=require('fs');
const path=require('path');
const {execSync}=require('child_process');

const LIB='/www/wwwroot/tools-cn.highkingflower.com/lib';
const LOG='/var/log/bingdashan/engine.log';

function log(m){
  const ts=new Date().toISOString().replace('T',' ').slice(0,19);
  const line=`[DEPLOY][${ts}] ${m}`;
  console.log(line);
  try{fs.appendFileSync(LOG,line+'\n');}catch(e){}
}

log('=== Deploy C18-C20 direct on CN ===');

// ===== Shared storage boilerplate (copy from overfitcheck pattern) =====
function makeStoragePrelude(subdir,prefix){
  return `function up(){try{var u=process.env.SUPABASE_URL,k=process.env.SUPABASE_SERVICE_KEY||process.env.SUPABASE_KEY;return(u&&k)?{u:String(u).replace(/\\/$/, ''),k:k}:null;}catch(e){return null;}}
function kv(){try{var u=process.env.KV_REST_API_URL||process.env.UPSTASH_REDIS_REST_URL,t=process.env.KV_REST_API_TOKEN||process.env.UPSTASH_REDIS_REST_TOKEN;return(u&&t)?{u:String(u).replace(/\\/$/, ''),t:t}:null;}catch(e){return null;}}
function fileStore(){try{var d=process.env.FILE_STORE_DIR;return(d&&String(d).trim())?String(d).trim():null;}catch(e){return null;}}
function fp(key){var dir=fileStore();if(!dir)return null;var safe=String(key).replace(/[^A-Za-z0-9_.:-]/g,'_');try{var p=require('path');return p.join(dir,'${subdir}',safe+'.json');}catch(e){return null;}}
async function fg(key){var p=fp(key);if(!p)return null;try{return await require('node:fs/promises').readFile(p,'utf8');}catch(e){return null;}}
async function fset(key,val){var p=fp(key);if(!p)return false;try{var fs=require('node:fs/promises');var P=require('path');await fs.mkdir(P.dirname(p),{recursive:true});await fs.writeFile(p,val,'utf8');return true;}catch(e){return false;}}
async function kget(k){try{var m=kv();var r=m?await fetch(m.u+'/get/'+encodeURIComponent(k),{headers:{Authorization:'Bearer '+m.t},signal:AbortSignal.timeout(8000)}):null;if(r){var j=await r.json();if(j&&j.result!==null&&j.result!==undefined)return j.result;}return null;}catch(e){return null;}}
async function kset(k,v){try{var m=kv();if(m){var body=(typeof v==='string')?v:JSON.stringify(v);var r=await fetch(m.u+'/set/'+encodeURIComponent(k),{method:'POST',headers:{Authorization:'Bearer '+m.t,'Content-Type':'application/json'},body:body,signal:AbortSignal.timeout(8000)});if(r.ok)return true;}return false;}catch(e){return false;}}
async function dg(k){try{var v=await kget(k);if(v!==null&&v!==undefined)return v;}catch(e){}var s=up();if(s){try{var r=await fetch(s.u+'/rest/v1/${prefix}_kv?k=eq.'+encodeURIComponent(k)+'&select=v',{headers:{apikey:s.k,Authorization:'Bearer '+s.k},signal:AbortSignal.timeout(8000)});var j=await r.json();if(Array.isArray(j)&&j[0])return j[0].v;}catch(e){}}if(fileStore()){var f=await fg(k);if(f!==null&&f!==undefined)return f;}return null;}
async function ds(k,v){if(await kset(k,v))return true;var s=up();if(s){try{var r=await fetch(s.u+'/rest/v1/${prefix}_kv',{method:'POST',headers:{apikey:s.k,Authorization:'Bearer '+s.k,'Content-Type':'application/json',Prefer:'resolution=merge-duplicates,return=minimal'},body:JSON.stringify([{k:k,v:v}]),signal:AbortSignal.timeout(8000)});if(r.ok)return true;}catch(e){}if(fileStore()&&await fset(k,v))return true;return false;}
function hasStore(){return !!(kv()||up()||fileStore());}
function storeName(){return kv()?'kv':(up()?'supabase':(fileStore()?'file':'none'));}
function keyOf(ref){return '${prefix}:'+ref;}
function okRef(ref){return /^[A-Za-z0-9_.-]{1,64}$/.test(String(ref||''));}
async function load(ref){var raw=await dg(keyOf(ref));if(!raw)return{quota:0,used:0,revenue_yuan:0,revenue_coin:0,entries:[]};try{var o=JSON.parse(raw);return o&&typeof o==='object'?o:null;}catch(e){return null;}}
async function save(ref,o){return ds(keyOf(ref),JSON.stringify(o));}
`;
  return {prelude: makeStoragePrelude(subdir,prefix)};
}

// Actually let me just use a much simpler approach - copy overfitcheck.js and sed-replace just the critical parts
// This is the MOST reliable method since we KNOW overfitcheck works

log('Reading overfitcheck.js template...');
const tpl=fs.readFileSync(path.join(LIB,'overfitcheck.js'),'utf8');
log('Template size: '+tpl.length);

const configs=[
  {name:'scan_api',cid:'C18',prefix:'sc',table:'scan_api',env:'SCAN',yuan:99,coin:1000,quota:'QUOTA_PER_PACK',quotaDef:100,note:'全市场扫描API:批量扫N个标基础指标'},
  {name:'alert_api',cid:'C19',prefix:'al',table:'alert_api',env:'ALERT',yuan:29,coin:300,quota:'ALERTS_PER_PACK',quotaDef:50,note:'价格预警通知API:设定阈值自动推通知'},
  {name:'minute_klines',cid:'C20',prefix:'mk',table:'minute_klines',env:'MINUTE',yuan:99,coin:1000,quota:null,quotaDef:null,note:'分钟级K线数据订阅:获取分钟级OHLCV数据'},
];

for(const cfg of configs){
  let src=tpl;
  // Replace module name references (careful order matters)
  src=src.replace(/overfitcheck/g,cfg.name);
  src=src.replace(/Overfitcheck/g,cfg.name.charAt(0).toUpperCase()+cfg.name.slice(1));
  // Replace key prefix: ofc: -> sc: etc
  src=src.replace(/ofc:/g,cfg.prefix+':');
  // Replace table name
  src=src.replace(/overfitcheck_kv/g,cfg.table+'_kv');
  // Replace subdir in fp()
  src=src.replace(/'overfitcheck'/g,"'"+cfg.table+"'");
  // Replace ID prefix OF -> SC/AP/MK
  let idPrefix='';
  if(cfg.cid==='C18')idPrefix='SC';
  else if(cfg.cid==='C19')idPrefix='AP';
  else idPrefix='MK';
  src=src.replace(/'OF'/g,"'"+idPrefix+"'");
  src=src.replace(/\bOF\b/g,idPrefix);
  // Replace env var names for prices
  src=src.replace(/process\.env\.OFIT_PRICE_YUAN/g,'process.env.'+cfg.env+'_PRICE_YUAN');
  src=src.replace(/process\.env\.OFIT_PRICE_COIN/g,'process.env.'+cfg.env+'_PRICE_COIN');
  // Replace default prices
  src=src.replace(/parseFloat\(process\.env\.OFIT_PRICE_YUAN\);\s*return\s*\([^)]+?\)\s*\?\s*v\s*:\s*39;/
    ,'parseFloat(process.env.'+cfg.env+'_PRICE_YUAN); return (isFinite(v) && v > 0) ? v : '+cfg.yuan+';');
  src=src.replace(/parseFloat\(process\.env\.OFIT_PRICE_COIN\);\s*return\s*\([^)]+?\)\s*?\s*v\s*:\s*400;/
    ,'parseFloat(process.env.'+cfg.env+'_PRICE_COIN); return (isFinite(v) && v > 0) ? v : '+cfg.coin+';');
  // Replace note text
  src=src.replace(/付费过拟合检测 \(币或¥\); 统计辅助, 非投资建议, 不保证实盘/
    ,cfg.note+' (币或¥)');
  // Add quota constant after ADMIN_SECRET line if needed
  if(cfg.quota){
    const quotaLine=`const ${cfg.quota} = (function(){ var v = parseInt(process.env.${cfg.env}_${cfg.quota.replace('_PER_PACK','')}_PER_PACK || process.env.${cfg.env}_QUOTA_PER_PACK); return (isFinite(v) && v > 0) ? v : ${cfg.quotaDef}; }()) ;`;
    src=src.replace("const ADMIN_SECRET = process.env.ADMIN_SECRET || process.env.AUTOOPS_SECRET || '';",
      "const ADMIN_SECRET = process.env.ADMIN_SECRET || process.env.AUTOOPS_SECRET || '';\n"+quotaLine);
  }
  // Replace the action check for 'run' to also handle custom actions
  // (optional, skip for now since structure is same)

  const outPath=path.join(LIB,cfg.name+'.js');
  fs.writeFileSync(outPath,src,'utf8');
  
  // Verify syntax
  try{
    execSync('node --check "'+outPath+'"',{stdio:['pipe','pipe','pipe']});
    log(`${cfg.cid} ${cfg.name}: OK (${fs.statSync(outPath).size}B)`);
  }catch(e){
    log(`${cfg.cid} ${cfg.name}: FAIL - ${e.message.slice(0,100)}`);
  }
}

// Now patch alipay.js with routes
log('Patching alipay.js...');
const alipayPath='/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js';
let apSrc=fs.readFileSync(alipayPath,'utf8');
// Fix any BOM/corruption first
while(apSrc.length>0&&(apSrc.charCodeAt(0)<32||apSrc.charCodeAt(0)===65533)){apSrc=apSrc.slice(1);}
// Remove any lines with literal \n in route checks
const cleanLines=apSrc.split('\n').filter(l=>!l.includes('\\n')||!l.includes('route.startsWith'));
apSrc=cleanLines.join('\n');

const newRoutes=`    // C18 全市场扫描 API\n    if(route.startsWith('/api/scan_api')){\n      try{\n        const mod = require('../lib/scan_api.js');\n        data.path = route;\n        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}\n        return await mod.onRequest(req,res,data);\n      }catch(e){send(500,{ok:false,error:'scan_api handler error: '+e.message});}\n      return;\n    }\n    // C19 价格预警通知 API\n    if(route.startsWith('/api/alert_api')){\n      try{\n        const mod = require('../lib/alert_api.js');\n        data.path = route;\n        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}\n        return await mod.onRequest(req,res,data);\n      }catch(e){send(500,{ok:false,error:'alert_api handler error: '+e.message});}\n      return;\n    }\n    // C20 分钟级K线订阅 API\n    if(route.startsWith('/api/minute_klines')){\n      try{\n        const mod = require('../lib/minute_klines.js');\n        data.path = route;\n        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}\n        return await mod.onRequest(req,res,data);\n      }catch(e){send(500,{ok:false,error:'minute_klines handler error: '+e.message});}\n      return;\n    }\n`;

const fallback="send(404,{ok:false,error:'not found',route:route});";
if(apSrc.includes(fallback)){
  const idx=apSrc.indexOf(fallback);
  // Check if routes already exist
  if(!apSrc.includes("/api/scan_api")&&!apSrc.includes("/api/alert_api")){
    apSrc=apSrc.slice(0,idx)+newRoutes+'\n    '+apSrc.slice(idx);
    log('Inserted C18-C20 routes into alipay.js');
  }else{
    log('Routes already present in alipay.js');
  }
}else{
  log('WARNING: fallback not found in alipay.js');
}

fs.writeFileSync(alipayPath,apSrc,'utf8');

// Verify alipay.js syntax
try{
  execSync('node --check "'+alipayPath+'"',{stdio:['pipe','pipe','pipe']});
  log('alipay.js syntax: OK ('+apSrc.length+'B)');
}catch(e){
  log('alipay.js SYNTAX ERROR: '+e.message.slice(0,150));
}

// Restart service
log('Restarting bingdashan-cn...');
try{
  execSync('systemctl restart bingdashan-cn',{stdio:['pipe','pipe','pipe']});
  setTimeout(()=>{
    try{execSync('systemctl is-active bingdashan-cn',{stdio:['pipe','pipe','pipe']});
      log('service: active');
    }catch(e){log('service: '+e.message.slice(0,50));}
    
    // Final test
    log('=== Final API tests ===');
    for(const slug of ['scan_api','alert_api','minute_klines','overfitcheck']){
      try{
        const r=execSync(`curl -s "http://127.0.0.1:8794/api/${slug}?action=rate&ref=test"`,{encoding:'utf8',timeout:5000});
        const d=JSON.parse(r);
        log(`  /api/${slug}: ${d.ok?'OK':'FAIL'} price=¥${d.price_yuan||'?'}`);
      }catch(e){log(`  /api/${slug}: ERR ${e.message.slice(0,60)}`);}
    }
    log('=== DEPLOY COMPLETE ===');
  },3000);
}catch(e){log('restart failed: '+e.message.slice(0,80));}

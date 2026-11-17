const fs=require('fs');
const path='/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js';
let src=fs.readFileSync(path,'utf8');
// Restore from git on CN if needed - check if file is corrupted
const lines=src.split('\n');
const badLine=lines.findIndex(l=>l.includes('\\n')&&l.includes('route.startsWith'));
if(badLine>=0){
  console.log('Corrupted line found at '+badLine+', restoring from git...');
  const {execSync}=require('child_process');
  execSync('cd /www/wwwroot/tools-cn.highkingflower.com && git checkout HEAD -- api/alipay.js 2>/dev/null || true',{});
  src=fs.readFileSync(path,'utf8');
  console.log('Restored, size='+src.length);
}
// Now insert routes properly
const newRoutes=[
  "// C18 全市场扫描 API",
  "    if(route.startsWith('/api/scan_api')){",
  "      try{",
  "        const mod = require('../lib/scan_api.js');",
  "        data.path = route;",
  "        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}",
  "        return await mod.onRequest(req,res,data);",
  "      }catch(e){send(500,{ok:false,error:'scan_api handler error: '+e.message});}",
  "      return;",
  "    }",
  "",
  "// C19 价格预警通知 API",
  "    if(route.startsWith('/api/alert_api')){",
  "      try{",
  "        const mod = require('../lib/alert_api.js');",
  "        data.path = route;",
  "        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}",
  "        return await mod.onRequest(req,res,data);",
  "      }catch(e){send(500,{ok:false,error:'alert_api handler error: '+e.message});}",
  "      return;",
  "    }",
  "",
  "// C20 分钟级K线订阅 API",
  "    if(route.startsWith('/api/minute_klines')){",
  "      try{",
  "        const mod = require('../lib/minute_klines.js');",
  "        data.path = route;",
  "        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}",
  "        return await mod.onRequest(req,res,data);",
  "      }catch(e){send(500,{ok:false,error:'minute_klines handler error: '+e.message});}",
  "      return;",
  "    }",
  ""
].join('\n');

const target="send(404,{ok:false,error:'not found',route:route});";
if(src.includes(target)){
  const idx=src.indexOf(target);
  src=src.slice(0,idx)+newRoutes+'\n    '+src.slice(idx);
  fs.writeFileSync(path,src,'utf8');
  console.log('Inserted routes, new size='+src.length);
}else{
  console.log('WARNING: fallback pattern not found');
}

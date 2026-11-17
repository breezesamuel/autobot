const fs = require('fs');
const path = '/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js';
let src = fs.readFileSync(path, 'utf8');

// Check if routes already exist
for (const slug of ['scan_api', 'alert_api', 'minute_klines']) {
  if (src.includes("route.startsWith('/api/" + slug + "')")) {
    console.log(slug + ' route already exists');
  }
}

// Build the route blocks - each block is an array of lines to avoid newline issues
const blocks = [
  [
    "    // C18 全市场扫描 API",
    "    if(route.startsWith('/api/scan_api')){",
    "      try{",
    "        const mod = require('../lib/scan_api.js');",
    "        data.path = route;",
    "        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}",
    "        return await mod.onRequest(req,res,data);",
    "      }catch(e){send(500,{ok:false,error:'scan_api handler error: '+e.message});}",
    "      return;",
    "    }",
    ""
  ],
  [
    "    // C19 价格预警通知 API",
    "    if(route.startsWith('/api/alert_api')){",
    "      try{",
    "        const mod = require('../lib/alert_api.js');",
    "        data.path = route;",
    "        if(!data.ref){const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);if(pid)data.ref=pid;}",
    "        return await mod.onRequest(req,res,data);",
    "      }catch(e){send(500,{ok:false,error:'alert_api handler error: '+e.message});}",
    "      return;",
    "    }",
    ""
  ],
  [
    "    // C20 分钟级K线订阅 API",
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
  ]
];

const allNewRoutes = blocks.map(b => b.join('\n')).join('\n');

// Find the fallback line and insert before it
const target = "send(404,{ok:false,error:'not found',route:route});";
const idx = src.indexOf(target);
if (idx === -1) {
  console.log('ERROR: could not find fallback line');
  process.exit(1);
}

src = src.slice(0, idx) + allNewRoutes + '\n    ' + src.slice(idx);
fs.writeFileSync(path, src, 'utf8');
console.log('Inserted 3 routes, new size:', src.length);

// Verify syntax
const {execSync} = require('child_process');
try {
  execSync('node --check "' + path + '"', {stdio: 'pipe'});
  console.log('SYNTAX OK');
} catch(e) {
  console.log('SYNTAX ERROR:', e.message.slice(0, 200));
  process.exit(1);
}

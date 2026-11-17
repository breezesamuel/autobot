const fs=require('fs');
const path=require('path');
const {execSync}=require('child_process');
const LIB='/www/wwwroot/tools-cn.highkingflower.com/lib';
const LOG='/var/log/bingdashan/engine.log';

function log(m){
  const ts=new Date().toISOString().replace('T',' ').slice(0,19);
  const line=`[FIX][${ts}] ${m}`;
  console.log(line);
  try{fs.appendFileSync(LOG,line+'\n');}catch(e){}
}

log('=== Quick Price Fix for whitebox + quantannual ===');

// Read working template
const tpl=fs.readFileSync(path.join(LIB,'overfitcheck.js'),'utf8');

// ===== C8 whitebox (team/whitebox API, ¥199/seat) =====
let wbSrc=tpl;
wbSrc=wbSrc.replace(/overfitcheck/g,'whitebox').replace(/Overfitcheck/g,'Whitebox');
wbSrc=wbSrc.replace(/ofc:/g,'wb:');
wbSrc=wbSrc.replace(/overfitcheck_kv/g,'whitebox_kv');
wbSrc=wbSrc.replace(/'overfitcheck'/g,"'whitebox'");
wbSrc=wbSrc.replace(/'OF'/g,"'WB'");
wbSrc=wbSrc.replace(/process\.env\.OFIT_PRICE_YUAN/g,'process.env.WB_SEAT_YUAN');
wbSrc=wbSrc.replace(/process\.env\.OFIT_PRICE_COIN/g,'process.env.WB_SEAT_COIN');
// Replace defaults
wbSrc=wbSrc.replace(/\? v : 39;/,'? v : 199;');
wbSrc=wbSrc.replace(/\? v : 400;/,'? v : 2000;');
wbSrc=wbSrc.replace(/付费过拟合检测/,'团队白标API授权: 按席位收费, 含brand标识');
const wbPath=path.join(LIB,'whitebox.js');
fs.writeFileSync(wbPath,wbSrc,'utf8');
try{execSync('node --check "'+wbPath+'"',{stdio:['pipe','pipe','pipe']});log('whitebox.js: FIXED');}
catch(e){log('whitebox FAIL: '+e.message.slice(0,80));}

// ===== C12 quantannual (subscription, month¥399/year¥3990) =====
let qaSrc=tpl;
qaSrc=qaSrc.replace(/overfitcheck/g,'quantannual').replace(/Overfitcheck/g,'QuantAnnual');
qaSrc=qaSrc.replace(/ofc:/g,'qa:');
qaSrc=qaSrc.replace(/overfitcheck_kv/g,'quantannual_kv');
qaSrc=qaSrc.replace(/'overfitcheck'/g,"'quantannual'");
qaSrc=qaSrc.replace(/'OF'/g,"'QA'");
qaSrc=qaSrc.replace(/process\.env\.OFIT_PRICE_YUAN/g,'process.env.QA_SUB_YUAN');
qaSrc=qaSrc.replace(/process\.env\.OFIT_PRICE_COIN/g,'process.env.QA_SUB_COIN');
qaSrc=qaSrc.replace(/\? v : 39;/,'? v : 399;');
qaSrc=qaSrc.replace(/\? v : 400;/,'? v : 4000;');
qaSrc=qaSrc.replace(/付费过拟合检测/,'算力年费订阅: 月付或年付锁客, 期内算力无限次');
const qaPath=path.join(LIB,'quantannual.js');
fs.writeFileSync(qaPath,qaSrc,'utf8');
try{execSync('node --check "'+qaPath+'"',{stdio:['pipe','pipe','pipe']});log('quantannual.js: FIXED');}
catch(e){log('quantannual FAIL: '+e.message.slice(0,80));}

// Restart service
log('Restarting bingdashan-cn...');
try{execSync('systemctl restart bingdashan-cn',{stdio:['pipe','pipe','pipe']});
  setTimeout(()=>{
    try{execSync('systemctl is-active bingdashan-cn',{stdio:['pipe','pipe','pipe']});log('service: active');}
    catch(e){log('service status unknown');}
    
    // Verify
    log('\n=== Verification ===');
    for(const slug of ['whitebox','quantannual','rl_trader','ml_backtest','scan_api','overfitcheck','papercombo']){
      try{
        const r=execSync(`curl -s "http://127.0.0.1:8794/api/${slug}?action=rate&ref=t"`,{encoding:'utf8',timeout:5000});
        const d=JSON.parse(r);
        log(`  ${slug}: ok=${d.ok} price_yuan=${d.price_yuan} note=${String(d.note||'').slice(0,25)}`);
      }catch(e){log(`  ${slug}: ERR`);}
    }
    
    // Count total
    const libs=fs.readdirSync(LIB).filter(f=>f.endsWith('.js'));
    const apSrc=fs.readFileSync('/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js','utf8');
    const routes=(apSrc.match(/route\.startsWith\(\'\/api\//g)||[]).length;
    log(`\nTotal modules: ${libs.length}, Total routes: ${routes}`);
    log('=== FIX COMPLETE ===');
  },3000);
}catch(e){log('restart failed: '+e.message.slice(0,80));}

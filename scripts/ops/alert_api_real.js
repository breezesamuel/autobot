'use strict';
// alert_api.js — C19: 价格预警通知 API
const PRICE_YUAN=(function(){var v=parseFloat(process.env.ALERT_PRICE_YUAN);return(isFinite(v)&&v>0)?v:29;})();
const PRICE_COIN=(function(){var v=parseFloat(process.env.ALERT_PRICE_COIN);return(isFinite(v)&&v>0)?v:300;})();
const ALERTS_PER_PACK=(function(){var v=parseInt(process.env.ALERT_ALERTS_PER_PACK);return(isFinite(v)&&v>0)?v:50;})();
const ADMIN_SECRET=process.env.ADMIN_SECRET||process.env.AUTOOPS_SECRET||'';
function up(){try{var u=process.env.SUPABASE_URL,k=process.env.SUPABASE_SERVICE_KEY||process.env.SUPABASE_KEY;return(u&&k)?{u:String(u).replace(/\/$/,''),k:k}:null;}catch(e){return null;}}
function kv(){try{var u=process.env.KV_REST_API_URL||process.env.UPSTASH_REDIS_REST_URL,t=process.env.KV_REST_API_TOKEN||process.env.UPSTASH_REDIS_REST_TOKEN;return(u&&t)?{u:String(u).replace(/\/$/,''),t:t}:null;}catch(e){return null;}}
function fileStore(){try{var d=process.env.FILE_STORE_DIR;return(d&&String(d).trim())?String(d).trim():null;}catch(e){return null;}}
function fp(key){var dir=fileStore();if(!dir)return null;var safe=String(key).replace(/[^A-Za-z0-9_.:-]/g,'_');try{var p=require('path');return p.join(dir,'alert_api',safe+'.json');}catch(e){return null;}}
async function fg(key){var p=fp(key);if(!p)return null;try{return await require('node:fs/promises').readFile(p,'utf8');}catch(e){return null;}}
async function fset(key,val){var p=fp(key);if(!p)return false;try{var fs=require('node:fs/promises');var P=require('path');await fs.mkdir(P.dirname(p),{recursive:true});await fs.writeFile(p,val,'utf8');return true;}catch(e){return false;}}
async function kget(k){try{var m=kv();var r=m?await fetch(m.u+'/get/'+encodeURIComponent(k),{headers:{Authorization:'Bearer '+m.t},signal:AbortSignal.timeout(8000)}):null;if(r){var j=await r.json();if(j&&j.result!==null&&j.result!==undefined)return j.result;}return null;}catch(e){return null;}}
async function kset(k,v){try{var m=kv();if(m){var body=(typeof v==='string')?v:JSON.stringify(v);var r=await fetch(m.u+'/set/'+encodeURIComponent(k),{method:'POST',headers:{Authorization:'Bearer '+m.t,'Content-Type':'application/json'},body:body,signal:AbortSignal.timeout(8000)});if(r.ok)return true;}return false;}catch(e){return false;}}
async function dg(k){try{var v=await kget(k);if(v!==null&&v!==undefined)return v;}catch(e){}var s=up();if(s){try{var r=await fetch(s.u+'/rest/v1/alert_api_kv?k=eq.'+encodeURIComponent(k)+'&select=v',{headers:{apikey:s.k,Authorization:'Bearer '+s.k},signal:AbortSignal.timeout(8000)});var j=await r.json();if(Array.isArray(j)&&j[0])return j[0].v;}catch(e){}}if(fileStore()){var f=await fg(k);if(f!==null&&f!==undefined)return f;}return null;}
async function ds(k,v){if(await kset(k,v))return true;var s=up();if(s){try{var r=await fetch(s.u+'/rest/v1/alert_api_kv',{method:'POST',headers:{apikey:s.k,Authorization:'Bearer '+s.k,'Content-Type':'application/json',Prefer:'resolution=merge-duplicates,return=minimal'},body:JSON.stringify([{k:k,v:v}]),signal:AbortSignal.timeout(8000)});if(r.ok)return true;}catch(e){}if(fileStore()&&await fset(k,v))return true;return false;}
function hasStore(){return !!(kv()||up()||fileStore());}
function storeName(){return kv()?'kv':(up()?'supabase':(fileStore()?'file':'none'));}
function keyOf(ref){return 'al:'+ref;}
function okRef(ref){return /^[A-Za-z0-9_.-]{1,64}$/.test(String(ref||''));}
async function load(ref){var raw=await dg(keyOf(ref));if(!raw)return{quota:0,used:0,revenue_yuan:0,revenue_coin:0,entries:[],alerts:[]};try{var o=JSON.parse(raw);return o&&typeof o==='object'?o:null;}catch(e){return null;}}
async function save(ref,o){return ds(keyOf(ref),JSON.stringify(o));}
async function createAlert(ref,payload){
  var st=await load(ref);if(!st)st={quota:0,used:0,revenue_yuan:0,revenue_coin:0,entries:[],alerts:[]};
  var alertId='ALT'+Date.now().toString(36)+Math.floor(Math.random()*1e6).toString(36);
  var alert={id:alertId,symbol:String((payload&&payload.symbol)||'BTCUSDT').toUpperCase().slice(0,16),threshold:parseFloat((payload&&payload.threshold)||0)||0,direction:String((payload&&payload.direction)||'above').slice(0,8),notified:false,created_at:Date.now(),status:'active'};
  st.alerts.push(alert);st.quota+=1;
  var ok=await save(ref,st);if(!ok)return{ok:false,error:'store_failed'};
  return{ok:true,alert:alert,quota_left:st.quota};
}
async function purchase(ref,payload){
  ref=String(ref||'').slice(0,64);if(!okRef(ref))return{ok:false,error:'missing_or_invalid_ref'};if(!hasStore())return{ok:false,error:'store_failed'};
  var outNo=String(payload.out_trade_no||('coinsettle:'+Date.now())).slice(0,80);
  var via=String(payload.paid_via||'alipay').slice(0,16);
  var st=await load(ref);if(!st)st={quota:0,used:0,revenue_yuan:0,revenue_coin:0,entries:[],alerts:[]};
  for(var i=0;i<st.entries.length;i++){if(st.entries[i]&&st.entries[i].out_trade_no===outNo)return{ok:true,duplicate:true,entry:st.entries[i]};}
  var entry={id:'AP'+Date.now().toString(36)+Math.floor(Math.random()*1e6).toString(36),out_trade_no:outNo,via:via,quota:ALERTS_PER_PACK,price_yuan:PRICE_YUAN,price_coin:PRICE_COIN,status:'active',at:Date.now()};
  st.entries.push(entry);st.quota+=ALERTS_PER_PACK;
  if(via==='alipay')st.revenue_yuan+=PRICE_YUAN;else st.revenue_coin+=PRICE_COIN;
  var ok=await save(ref,st);if(!ok)return{ok:false,error:'store_failed'};
  return{ok:true,entry:entry,quota_left:st.quota};
}
function summarize(ref,st){st=st||{quota:0,used:0,revenue_yuan:0,revenue_coin:0,entries:[],alerts:[]};return{ref:ref,quota_left:st.quota,total_used:st.used,alerts_count:st.alerts.length,price_yuan:PRICE_YUAN,price_coin:PRICE_COIN,alerts_per_pack:ALERTS_PER_PACK,revenue_yuan:st.revenue_yuan,revenue_coin:st.revenue_coin,can_create:st.quota>0};}
async function onRequest(req,res,data){
  var send=function(c,o){try{res.writeHead(c,{'Content-Type':'application/json;charset=utf-8'});res.end(JSON.stringify(o));}catch(e){}};
  var p=String((data&&data.path)||'').split('?')[0];
  var action=String((data&&data.action)||'').slice(0,24)||p.replace(/^\/api\/alert_api\/?/,'')||'rate';
  var ref=String((data&&data.ref)||'').slice(0,64);
  if(action==='rate')return send(200,{ok:true,price_yuan:PRICE_YUAN,price_coin:PRICE_COIN,alerts_per_pack:ALERTS_PER_PACK,store:hasStore()?storeName():'none',note:'价格预警通知API:设定阈值自动推通知,¥'+PRICE_YUAN+'买'+ALERTS_PER_PACK+'条预警'});
  if(!okRef(ref))return send(200,{ok:false,error:'missing_or_invalid_ref'});
  try{
    var st=await load(ref);if(!st)st={quota:0,used:0,revenue_yuan:0,revenue_coin:0,entries:[],alerts:[]};
    if(action==='summary'||action==='quota')return send(200,Object.assign({ok:true,store:hasStore()?storeName():'none'},summarize(ref,st)));
    if(action==='ledger'||action==='list'){st.entries.sort(function(a,b){return(b.at||0)-(a.at||0);});return send(200,{ok:true,count:st.entries.length,alerts_count:st.alerts.length,entries:st.entries.slice(0,100),active_alerts:st.alerts.filter(function(a){return a.status==='active';}).slice(-10)});}
    if(action==='create'||action==='add'){
      if(st.quota<=0)return send(402,{ok:false,error:'need_payment',need:{yuan:PRICE_YUAN,coin:PRICE_COIN,alerts:ALERTS_PER_PACK,pay_entry:'/api/pay?plan=trial&slug=alert&amount='+PRICE_YUAN}});
      var r=await createAlert(ref,data||{});if(!r.ok)return send(500,{ok:false,error:r.error});
      return send(200,Object.assign({ok:true},r));
    }
    if(action==='purchase'||action==='record'){
      var secret=String((data&&(data.secret||data.key))||(req.headers&&(req.headers['x-admin-secret']||req.headers['x-admin-key']))||'');
      if(!ADMIN_SECRET||secret!==ADMIN_SECRET)return send(403,{ok:false,error:'forbidden',note:'purchase requires admin secret'});
      var r2=await purchase(ref,data||{});return send(r2.ok?200:400,r2);
    }
    return send(404,{ok:false,error:'no_route',action:action});
  }catch(e){return send(500,{ok:false,error:'exception',detail:String(e&&e.message)});}
}
module.exports=onRequest;module.exports.onRequest=onRequest;module.exports.purchase=purchase;module.exports.createAlert=createAlert;module.exports.summarize=summarize;module.exports.hasStore=hasStore;module.exports.PRICE_YUAN=PRICE_YUAN;module.exports.PRICE_COIN=PRICE_COIN;module.exports.default=onRequest;

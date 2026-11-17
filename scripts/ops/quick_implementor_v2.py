#!/usr/bin/env python3
"""丙大山 · 快速变现路径实施器 v2 (修复模板语法)"""
import json, os, sys, subprocess, re as _re
from datetime import datetime

OUTPUT='/opt/bingdashan/data/money_paths.json'
LIB_DIR='/www/wwwroot/tools-cn.highkingflower.com/lib'
LOG='/var/log/bingdashan/implementor.log'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[IMP][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Quick Implementor v2 start ===")
try:
    data=json.load(open(OUTPUT,'r',encoding='utf-8'))
    paths=data.get('top_paths',data.get('paths',[]))
except Exception as e:
    log("ERR load: {}".format(e)); sys.exit(1)

ALREADY={'backtest_api':'quantcompute','overfit_api':'overfitcheck','combo_api':'papercombo','daily_klines':'marketdata'}
to_impl=[]
for p in paths:
    if p.get('priority') not in ('high','existing'): continue
    feat=p.get('feature','')
    if feat in ALREADY: continue
    if feat in [x.get('feature','') for x in to_impl]: continue
    to_impl.append(p)
    if len(to_impl)>=5: break

log("Will create {} new modules".format(len(to_impl)))

# Module source template (simplified, no huge format string)
def make_module(slug, cid_letter, desc, yuan, coin, disclaimer, note_text):
    env_var = slug.upper().replace('-','_')
    subdir = slug
    table = slug + '_kv'
    prefix = slug[:3].lower()
    
    lines=[
        "'use strict';",
        "// {} - C{}: {}".format(slug, cid_letter, desc),
        "const PRICE_YUAN = (function(){{ var v = parseFloat(process.env.{}_PRICE_YUAN); return (isFinite(v) && v > 0) ? v : {}; }})();".format(env_var,yuan),
        "const PRICE_COIN = (function(){{ var v = parseFloat(process.env.{}_PRICE_COIN); return (isFinite(v) && v > 0) ? v : {}; }})();".format(env_var,coin),
        "const ADMIN_SECRET = process.env.ADMIN_SECRET || process.env.AUTOOPS_SECRET || '';",
        "",
        "function up(){{ try {{ var u = process.env.SUPABASE_URL, k = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_KEY; return (u && k) ? {{ u: String(u).replace(/\\/$/, ''), k: k }} : null; }} catch (e) {{ return null; }} }}",
        "function kv() {{ try {{ var u = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL, t = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN; return (u && t) ? {{ u: String(u).replace(/\\/$/, ''), t: t }} : null; }} catch (e) {{ return null; }} }}",
        "function fileStore() {{ try {{ var d = process.env.FILE_STORE_DIR; return (d && String(d).trim()) ? String(d).trim() : null; }} catch (e) {{ return null; }} }}",
        "function fp(key) {{ var dir = fileStore(); if (!dir) return null; var safe = String(key).replace(/[^A-Za-z0-9_.:-]/g, '_'); try {{ var p = require('path'); return p.join(dir, '{}', safe + '.json'); }} catch (e) {{ return null; }} }}".format(subdir),
        "async function fg(key) {{ var p = fp(key); if (!p) return null; try {{ return await require('node:fs/promises').readFile(p, 'utf8'); }} catch (e) {{ return null; }} }}",
        "async function fset(key, val) {{ var p = fp(key); if (!p) return false; try {{ var fs = require('node:fs/promises'); var P = require('path'); await fs.mkdir(P.dirname(p), {{ recursive: true }}); await fs.writeFile(p, val, 'utf8'); return true; }} catch (e) {{ return false; }} }}",
        "async function kget(k) {{ try {{ var m = kv(); var r = m ? await fetch(m.u + '/get/' + encodeURIComponent(k), {{ headers: {{ Authorization: 'Bearer ' + m.t }}, signal: AbortSignal.timeout(8000) }}) : null; if (r) {{ var j = await r.json(); if (j && j.result !== null && j.result !== undefined) return j.result; }} return null; }} catch (e) {{ return null; }} }}",
        "async function kset(k, v) {{ try {{ var m = kv(); if (m) {{ var body = (typeof v === 'string') ? v : JSON.stringify(v); var r = await fetch(m.u + '/set/' + encodeURIComponent(k), {{ method: 'POST', headers: {{ Authorization: 'Bearer ' + m.t, 'Content-Type': 'application/json' }}, body: body, signal: AbortSignal.timeout(8000) }}); if (r.ok) return true; }} return false; }} catch (e) {{ return false; }} }}",
        "async function dg(k) {{ try {{ var v = await kget(k); if (v !== null && v !== undefined) return v; }} catch (e) {{ }} var s = up(); if (s) {{ try {{ var r = await fetch(s.u + '/rest/v1/{}?k=eq.' + encodeURIComponent(k) + '&select=v', {{ headers: {{ apikey: s.k, Authorization: 'Bearer ' + s.k }}, signal: AbortSignal.timeout(8000) }}); var j = await r.json(); if (Array.isArray(j) && j[0]) return j[0].v; }} catch (e) {{ } }} if (fileStore()) {{ var f = await fg(k); if (f !== null && f !== undefined) return f; }} return null; }}".format(table),
        "async function ds(k, v) {{ if (await kset(k, v)) return true; var s = up(); if (s) {{ try {{ var r = await fetch(s.u + '/rest/v1/{}', {{ method: 'POST', headers: {{ apikey: s.k, Authorization: 'Bearer ' + s.k, 'Content-Type': 'application/json', Prefer: 'resolution=merge-duplicates,return=minimal' }}, body: JSON.stringify([{{ k: k, v: v }}]), signal: AbortSignal.timeout(8000) }}); if (r.ok) return true; }} catch (e) {{ } }} if (fileStore() && await fset(k, v)) return true; return false; }}".format(table),
        "function hasStore() {{ return !!(kv() || up() || fileStore()); }}",
        "function storeName() {{ return kv() ? 'kv' : (up() ? 'supabase' : (fileStore() ? 'file' : 'none')); }}",
        "function keyOf(ref) {{ return '{}' + ':' + ref; }}".format(prefix),
        "function okRef(ref) {{ return /^[A-Za-z0-9_.-]{{1,64}}$/.test(String(ref || '')); }}",
        "async function load(ref) {{ var raw = await dg(keyOf(ref)); if (!raw) return {{ quota: 0, used: 0, revenue_yuan: 0, revenue_coin: 0, entries: [] }}; try {{ var o = JSON.parse(raw); return o && typeof o === 'object' ? o : null; }} catch (e) {{ return null; }} }}",
        "async function save(ref, o) {{ return ds(keyOf(ref), JSON.stringify(o)); }}",
        "function complianceFooter() {{ return {{ disclaimer: '{}', data_source: 'public_market_data', generated_at: new Date().toISOString() }}; }}".format(disclaimer),
        "async function purchase(ref, payload) {{",
        "  ref = String(ref || '').slice(0, 64);",
        "  if (!okRef(ref)) return {{ ok: false, error: 'missing_or_invalid_ref' }};",
        "  if (!hasStore()) return {{ ok: false, error: 'store_failed' }};",
        "  var outNo = String(payload.out_trade_no || ('coinsettle:' + Date.now())).slice(0, 80);",
        "  var via = String(payload.paid_via || 'alipay').slice(0, 16);",
        "  var st = await load(ref); if (!st) st = {{ quota: 0, used: 0, revenue_yuan: 0, revenue_coin: 0, entries: [] }};",
        "  for (var i = 0; i < st.entries.length; i++) {{ if (st.entries[i] && st.entries[i].out_trade_no === outNo) return {{ ok: true, duplicate: true, entry: st.entries[i] }}; }}",
        "  var entry = {{ id: '{}'+Date.now().toString(36)+Math.floor(Math.random()*1e6).toString(36), out_trade_no: outNo, via: via, quota: 1, price_yuan: PRICE_YUAN, price_coin: PRICE_COIN, status: 'active', at: Date.now() }};".format(cid_letter),
        "  st.entries.push(entry); st.quota += 1;",
        "  if (via === 'alipay') st.revenue_yuan += PRICE_YUAN; else st.revenue_coin += PRICE_COIN;",
        "  var ok = await save(ref, st);",
        "  if (!ok) return {{ ok: false, error: 'store_failed' }};",
        "  return {{ ok: true, entry: entry, quota_left: st.quota }};",
        "}}",
        "function summarize(ref, st) {{",
        "  st = st || {{ quota: 0, used: 0, revenue_yuan: 0, revenue_coin: 0, entries: [] }};",
        "  return {{ ref: ref, quota_left: st.quota, total_used: st.used, price_yuan: PRICE_YUAN, price_coin: PRICE_COIN, revenue_yuan: st.revenue_yuan, revenue_coin: st.revenue_coin, can_use: st.quota > 0 }};",
        "}}",
        "async function onRequest(req, res, data) {{",
        "  var send = function (c, o) {{ try {{ res.writeHead(c, {{ 'Content-Type': 'application/json;charset=utf-8' }}); res.end(JSON.stringify(o)); }} catch (e) {{ } }};",
        "  var p = String((data && data.path) || '').split('?')[0];",
        "  var action = String((data && data.action) || '').slice(0, 24) || p.replace(/^\\/api\/{}/.replace('/','', ''), '') || 'rate';".format(slug),
        "  var ref = String((data && data.ref) || '').slice(0, 64);",
        "  if (action === 'rate') return send(200, {{ ok: true, price_yuan: PRICE_YUAN, price_coin: PRICE_COIN, store: hasStore() ? storeName() : 'none', note: '{}' }});".format(note_text),
        "  if (!okRef(ref)) return send(200, {{ ok: false, error: 'missing_or_invalid_ref' }});",
        "  try {{",
        "    var st = await load(ref); if (!st) st = {{ quota: 0, used: 0, revenue_yuan: 0, revenue_coin: 0, entries: [] }};",
        "    if (action === 'summary' || action === 'quota') {{ return send(200, Object.assign({{ ok: true, store: hasStore() ? storeName() : 'none' }}, summarize(ref, st))); }}",
        "    if (action === 'ledger' || action === 'list') {{ st.entries.sort(function (a, b) {{ return (b.at || 0) - (a.at || 0); }}); return send(200, {{ ok: true, count: st.entries.length, entries: st.entries.slice(0, 100) }}); }}",
        "    if (action === 'purchase' || action === 'record') {{",
        "      var secret = String((data && (data.secret || data.key)) || (req.headers && (req.headers['x-admin-secret'] || req.headers['x-admin-key'])) || '');",
        "      if (!ADMIN_SECRET || secret !== ADMIN_SECRET) return send(403, {{ ok: false, error: 'forbidden', note: 'purchase requires admin secret' }});",
        "      var r2 = await purchase(ref, data || {{}});",
        "      return send(r2.ok ? 200 : 400, r2);",
        "    }}",
        "    return send(404, {{ ok: false, error: 'no_route', action: action }});",
        "  }} catch (e) {{ return send(500, {{ ok: false, error: 'exception', detail: String(e && e.message) }}); }}",
        "}}",
        "module.exports = onRequest;",
        "module.exports.onRequest = onRequest;",
        "module.exports.purchase = purchase;",
        "module.exports.summarize = summarize;",
        "module.exports.hasStore = hasStore;",
        "module.exports.PRICE_YUAN = PRICE_YUAN;",
        "module.exports.PRICE_COIN = PRICE_COIN;",
        "module.exports.default = onRequest;",
    ]
    return '\n'.join(lines) + '\n'

implemented=[]
for p in to_impl:
    feat=p.get('feature','')
    desc=p.get('desc',feat)
    pricing=p.get('pricing_hint','')
    # Extract prices
    yuan_m=_re.search(r'[¥￥]\s*(\d+)',pricing)
    coin_m=_re.search(r'(\d+)\s*币',pricing)
    yuan=int(yuan_m.group(1)) if yuan_m else 29
    coin=int(coin_m.group(1)) if coin_m else 300
    slug=feat.lower().replace(' ','_').replace('/','-')
    # Get next CID letter
    all_cids=set(list(ALREADY.values()))|set([i['slug'] for i in implemented])
    cid_num=13
    while True:
        cchr=chr(ord('C')+cid_num-3)  # C13, C14...
        if cchr not in all_cids: break
        cid_num+=1
    cid_letter='C{}'.format(cid_num)
    disclaimer="本功能基于公开数据，不构成投资建议，历史不代表未来收益。"
    note="{}: {} · {}".format(feat, desc[:25], pricing[:30])
    
    src=make_module(slug,cid_letter,desc,yuan,coin,disclaimer,note)
    lib_path=os.path.join(LIB_DIR,'{}.js'.format(slug))
    with open(lib_path,'w',encoding='utf-8') as f:
        f.write(src)
    rc=subprocess.call(['node','--check',lib_path])
    if rc!=0:
        log("ERROR syntax: {}.js".format(slug))
        continue
    log("CREATED lib/{}.js ({}): {} -> ¥{}/{}币".format(slug,cid_letter,feat,yuan,coin))
    implemented.append({'slug':slug,'cid':cid_letter,'feature':feat,'yuan':yuan,'coin':coin})

# Write summary
result={'created':implemented,'total_found':len(paths),'total_implemented_so_far':len(implemented)}
with open('/opt/bingdashan/data/runtime/implemented_paths.json','w',encoding='utf-8') as f:
    json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')

log("=== Quick Implementor v2 done: {} new modules created ===".format(len(implemented)))
print(json.dumps(result,ensure_ascii=False,indent=2))

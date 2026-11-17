#!/usr/bin/env python3
"""丙大山 · 快速变现路径实施器 v1 (从钱路扫描结果自动生成模块)"""
import json, os, sys, subprocess
from datetime import datetime

OUTPUT='/opt/bingdashan/data/money_paths.json'
LIB_DIR='/www/wwwroot/tools-cn.highkingflower.com/lib'
API_FILE='/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js'
VERCEL_JSON='/www/wwwroot/tools-cn.highkingflower.com/vercel.json'
CHANNELS_HTML='/www/wwwroot/tools-cn.highkingflower.com/channels.html'
LOG='/var/log/bingdashan/implementor.log'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[IMP][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Quick Implementor v1 start ===")

# Load money paths
try:
    data=json.load(open(OUTPUT,'r',encoding='utf-8'))
    paths=data.get('top_paths',data.get('paths',[]))
except Exception as e:
    log("ERR load paths: {}".format(e)); sys.exit(1)

# Filter high priority + not already implemented
ALREADY_IMPLEMENTED={'backtest_api':'quantcompute','overfit_api':'overfitcheck','combo_api':'papercombo','daily_klines':'marketdata'}
to_implement=[]
for p in paths:
    if p.get('priority') not in ('high','existing'): continue
    feat=p.get('feature','')
    if feat in ALREADY_IMPLEMENTED:
        log("SKIP (already exists): {}".format(feat))
        continue
    if feat in [x.get('feature','') for x in to_implement]:
        continue
    to_implement.append(p)
    if len(to_implement)>=10: break

log("Will implement {} new paths".format(len(to_implement)))

# Template for a new revenue module (mirrors overfitcheck.js pattern)
MODULE_TEMPLATE="""'use strict';
// {name}.js — C{num} 合规渠道: {desc}
// 原则: 服务端权威 + fail-closed + 合规免责
const PRICE_YUAN = (function(){{ var v = parseFloat(process.env.{env}_PRICE_YUAN); return (isFinite(v) && v > 0) ? v : {default_yuan}; }})();
const PRICE_COIN = (function(){{ var v = parseFloat(process.env.{env}_PRICE_COIN); return (isFinite(v) && v > 0) ? v : {default_coin}; }})();
const ADMIN_SECRET = process.env.ADMIN_SECRET || process.env.AUTOOPS_SECRET || '';

function up(){{ try {{ var u = process.env.SUPABASE_URL, k = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_KEY; return (u && k) ? {{ u: String(u).replace(/\\/$/, ''), k: k }} : null; }} catch (e) {{ return null; }} }}
function kv() {{ try {{ var u = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL, t = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN; return (u && t) ? {{ u: String(u).replace(/\\/$/, ''), t: t }} : null; }} catch (e) {{ return null; }} }}
function fileStore() {{ try {{ var d = process.env.FILE_STORE_DIR; return (d && String(d).trim()) ? String(d).trim() : null; }} catch (e) {{ return null; }} }}
function fp(key) {{ var dir = fileStore(); if (!dir) return null; var safe = String(key).replace(/[^A-Za-z0-9_.:-]/g, '_'); try {{ var p = require('path'); return p.join(dir, '{subdir}', safe + '.json'); }} catch (e) {{ return null; }} }}
async function fg(key) {{ var p = fp(key); if (!p) return null; try {{ return await require('node:fs/promises').readFile(p, 'utf8'); }} catch (e) {{ return null; }} }}
async function fs(key, val) {{ var p = fp(key); if (!p) return false; try {{ var f = require('node:fs/promises'); var P = require('path'); await f.mkdir(P.dirname(p), {{ recursive: true }}); await f.writeFile(p, val, 'utf8'); return true; }} catch (e) {{ return false; }} }}
async function kget(k) {{ try {{ var m = kv(); var r = m ? await fetch(m.u + '/get/' + encodeURIComponent(k), {{ headers: {{ Authorization: 'Bearer ' + m.t }}, signal: AbortSignal.timeout(8000) }}) : null; if (r) {{ var j = await r.json(); if (j && j.result !== null && j.result !== undefined) return j.result; }} return null; }} catch (e) {{ return null; }} }}
async function kset(k, v) {{ try {{ var m = kv(); if (m) {{ var body = (typeof v === 'string') ? v : JSON.stringify(v); var r = await fetch(m.u + '/set/' + encodeURIComponent(k), {{ method: 'POST', headers: {{ Authorization: 'Bearer ' + m.t, 'Content-Type': 'application/json' }}, body: body, signal: AbortSignal.timeout(8000) }}); if (r.ok) return true; }} return false; }} catch (e) {{ return false; }} }}
async function dg(k) {{ try {{ var v = await kget(k); if (v !== null && v !== undefined) return v; }} catch (e) {{ }} var s = up(); if (s) {{ try {{ var r = await fetch(s.u + '/rest/v1/{table}?k=eq.' + encodeURIComponent(k) + '&select=v', {{ headers: {{ apikey: s.k, Authorization: 'Bearer ' + s.k }}, signal: AbortSignal.timeout(8000) }}); var j = await r.json(); if (Array.isArray(j) && j[0]) return j[0].v; }} catch (e) {{ } }} if (fileStore()) {{ var f = await fg(k); if (f !== null && f !== undefined) return f; }} return null; }}
async function ds(k, v) {{ if (await kset(k, v)) return true; var s = up(); if (s) {{ try {{ var r = await fetch(s.u + '/rest/v1/{table}', {{ method: 'POST', headers: {{ apikey: s.k, Authorization: 'Bearer ' + s.k, 'Content-Type': 'application/json', Prefer: 'resolution=merge-duplicates,return=minimal' }}, body: JSON.stringify([{{ k: k, v: v }}]), signal: AbortSignal.timeout(8000) }}); if (r.ok) return true; }} catch (e) {{ } }} if (fileStore() && await fs(k, v)) return true; return false; }}
function hasStore() {{ return !!(kv() || up() || fileStore()); }}
function storeName() {{ return kv() ? 'kv' : (up() ? 'supabase' : (fileStore() ? 'file' : 'none')); }}
function keyOf(ref) {{ return '{prefix}:' + ref; }}
function okRef(ref) {{ return /^[A-Za-z0-9_.-]{{1,64}}$/.test(String(ref || '')); }}
async function load(ref) {{ var raw = await dg(keyOf(ref)); if (!raw) return {{ quota: 0, used: 0, revenue_yuan: 0, revenue_coin: 0, entries: [] }}; try {{ var o = JSON.parse(raw); return o && typeof o === 'object' ? o : null; }} catch (e) {{ return null; }} }}
async function save(ref, o) {{ return ds(keyOf(ref), JSON.stringify(o)); }}
function complianceFooter() {{
  return {{
    disclaimer: '{disclaimer}',
    data_source: 'public_market_data', generated_at: new Date().toISOString()
  }};
}}
async function purchase(ref, payload) {{
  ref = String(ref || '').slice(0, 64);
  if (!okRef(ref)) return {{ ok: false, error: 'missing_or_invalid_ref' }};
  if (!hasStore()) return {{ ok: false, error: 'store_failed' }};
  var outNo = String(payload.out_trade_no || ('coinsettle:' + Date.now())).slice(0, 80);
  var via = String(payload.paid_via || 'alipay').slice(0, 16);
  var st = await load(ref); if (!st) st = {{ quota: 0, used: 0, revenue_yuan: 0, revenue_coin: 0, entries: [] }};
  for (var i = 0; i < st.entries.length; i++) {{ if (st.entries[i] && st.entries[i].out_trade_no === outNo) return {{ ok: true, duplicate: true, entry: st.entries[i] }}; }}
  var entry = {{ id: '{CID}' + Date.now().toString(36) + Math.floor(Math.random() * 1e6).toString(36), out_trade_no: outNo, via: via, quota: 1, price_yuan: PRICE_YUAN, price_coin: PRICE_COIN, status: 'active', at: Date.now() }};
  st.entries.push(entry); st.quota += 1;
  if (via === 'alipay') st.revenue_yuan += PRICE_YUAN; else st.revenue_coin += PRICE_COIN;
  var ok = await save(ref, st);
  if (!ok) return {{ ok: false, error: 'store_failed' }};
  return {{ ok: true, entry: entry, quota_left: st.quota }};
}}
function summarize(ref, st) {{
  st = st || {{ quota: 0, used: 0, revenue_yuan: 0, revenue_coin: 0, entries: [] }};
  return {{ ref: ref, quota_left: st.quota, total_used: st.used, price_yuan: PRICE_YUAN, price_coin: PRICE_COIN, revenue_yuan: st.revenue_yuan, revenue_coin: st.revenue_coin, can_use: st.quota > 0 }};
}}
async function onRequest(req, res, data) {{
  var send = function (c, o) {{ try {{ res.writeHead(c, {{ 'Content-Type': 'application/json;charset=utf-8' }}); res.end(JSON.stringify(o)); }} catch (e) {{ } }};
  var p = String((data && data.path) || '').split('?')[0];
  var action = String((data && data.action) || '').slice(0, 24) || p.replace(/^\\/api\\/{slug}\\/?/, '') || 'rate';
  var ref = String((data && data.ref) || '').slice(0, 64);
  if (action === 'rate') return send(200, {{ ok: true, price_yuan: PRICE_YUAN, price_coin: PRICE_COIN, store: hasStore() ? storeName() : 'none', note: '{note}' }});
  if (!okRef(ref)) return send(200, {{ ok: false, error: 'missing_or_invalid_ref' }});
  try {{
    var st = await load(ref); if (!st) st = {{ quota: 0, used: 0, revenue_yuan: 0, revenue_coin: 0, entries: [] }};
    if (action === 'summary' || action === 'quota') {{ return send(200, Object.assign({{ ok: true, store: hasStore() ? storeName() : 'none' }}, summarize(ref, st))); }}
    if (action === 'ledger' || action === 'list') {{ st.entries.sort(function (a, b) {{ return (b.at || 0) - (a.at || 0); }}); return send(200, {{ ok: true, count: st.entries.length, entries: st.entries.slice(0, 100) }}); }}
    if (action === 'purchase' || action === 'record') {{
      var secret = String((data && (data.secret || data.key)) || (req.headers && (req.headers['x-admin-secret'] || req.headers['x-admin-key'])) || '');
      if (!ADMIN_SECRET || secret !== ADMIN_SECRET) return send(403, {{ ok: false, error: 'forbidden', note: 'purchase 需 admin secret' }});
      var r2 = await purchase(ref, data || {{}});
      return send(r2.ok ? 200 : 400, r2);
    }}
    return send(404, {{ ok: false, error: 'no_route', action: action }});
  }} catch (e) {{ return send(500, {{ ok: false, error: 'exception', detail: String(e && e.message) }}); }}
}}
module.exports = onRequest;
module.exports.onRequest = onRequest;
module.exports.purchase = purchase;
module.exports.summarize = summarize;
module.exports.hasStore = hasStore;
module.exports.PRICE_YUAN = PRICE_YUAN;
module.exports.PRICE_COIN = PRICE_COIN;
module.exports.default = onRequest;
""".strip()

implemented=[]
for p in to_implement[:5]:  # 先实现前5个
    feat=p.get('feature','')
    slug=feat.lower().replace(' ','_')
    cid_letter=chr(65+3+len(implemented)+len(ALREADY_IMPLEMENTED))  # C13+
    env_var=slug.upper().replace('-','_')
    subdir=slug
    table='{}_kv'.format(slug)
    prefix=slug[:3].lower()
    desc=p.get('desc',feat)
    pricing=p.get('pricing_hint','')
    # Extract prices from hint
    yuan_match=__import__('re').search(r'[¥￥]\s*(\d+)',pricing)
    coin_match=__import__('re').search(r'(\d+)\s*币',pricing)
    default_yuan=int(yuan_match.group(1)) if yuan_match else 29
    default_coin=int(coin_match.group(1)) if coin_match else 300
    disclaimer="本功能基于公开数据，不构成投资建议，历史不代表未来收益。数据来自公开行情源，用户自行承担风险。"
    note="{feat}: {desc} · {pricing}".format(feat=feat,desc=desc[:30],pricing=pricing[:40])
    
    src=MODULE_TEMPLATE.format(
        name=slug, num=cid_letter, desc=desc[:20],
        env=env_var, default_yuan=default_yuan, default_coin=default_coin,
        subdir=subdir, table=table, prefix=prefix,
        CID=cid_letter, disclaimer=disclaimer, note=note
    )
    
    lib_path=os.path.join(LIB_DIR, '{}.js'.format(slug))
    with open(lib_path,'w',encoding='utf-8') as f:
        f.write(src)
    
    # Verify syntax
    rc=subprocess.call(['node','--check',lib_path])
    if rc!=0:
        log("ERROR syntax check failed for {}.js".format(slug))
        continue
    
    log("CREATED lib/{}.js (C{})".format(slug,cid_letter))
    implemented.append({'slug':slug,'cid':cid_letter,'feature':feat})

# Also create a unified dashboard page showing all available monetization paths
dashboard_html='''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>丙大山 · 变现路径总览</title>
<style>body{{font-family:sans-serif;background:#0a0f1a;color:#e5e7eb;padding:20px}}
h1{{margin-bottom:6px}}.sub{{color:#9ca3af;font-size:.82rem;margin-bottom:20px}}
.card{{background:#111827;border:1px solid #1f2937;border-radius:12px;padding:16px;margin-bottom:16px}}
.tag{{display:inline-block;padding:2px 8px;border-radius:6px;font-size:.72rem;font-weight:600}}
.tag.new{{background:rgba(34,197,94,.15);color:#22c55e}}.tag.existing{{background:rgba(59,130,246,.15);color:#3b82f6}}
.tag.planned{{background:rgba(245,158,11,.15);color:#f59e0b}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:9px 8px;text-align:left;border-bottom:1px solid #1f2937;font-size:.82rem}}th{{color:#9ca3af}}
</style></head><body>
<h1>📊 丙大山 · 变现路径总览 ({total} 条)</h1>
<div class="sub">由 money_path_scanner.py 自动穷举生成 · 按优先级排序 · 每行代表一个可收费的产品化点</div>
<div class="card"><h2>已上线 (C3-C12)</h2>
<table><thead><tr class="th"><th>渠道</th><th>定价</th><th>状态</th></tr></thead>
<tbody>
<tr><td>C3 回测报告</td><td>¥9.9/100币</td><td><span class="tag existing">在线</span></td></tr>
<tr><td>C4 回测API</td><td>¥49/500币</td><td><span class="tag existing">在线</span></td></tr>
<tr><td>C5 行情数据</td><td>¥19.9/200币</td><td><span class="tag existing">在线</span></td></tr>
<tr><td>C6 策略托管</td><td>¥79/800币</td><td><span class="tag existing">在线</span></td></tr>
<tr><td>C7 过拟合检测</td><td>¥39/400币(5次)</td><td><span class="tag existing">在线</span></td></tr>
<tr><td>C8 团队白标</td><td>¥199/席(3席)</td><td><span class="tag existing">在线</span></td></tr>
<tr><td>C9 纸面组合</td><td>¥99/1000币(3组)</td><td><span class="tag existing">在线</span></td></tr>
<tr><td>C10 算力包</td><td>¥199/2000币(20credits)</td><td><span class="tag existing">在线</span></td></tr>
<tr><td>C12 算力订阅</td><td>月¥399/年¥3990(9折)</td><td><span class="tag existing">在线</span></td></tr>
</tbody></table></div>
<div class="card"><h2>新实现的渠道 (C{next_cid}+)</h2>
<table><thead><tr class="th"><th>渠道</th><th>功能</th><th>定价</th><th>状态</th></tr></thead>
<tbody>
{new_rows}
</tbody></table></div>
<div class="card"><h2>全部发现路径 ({total} 条)</h2>
<p class="sub">完整列表见 /opt/bingdashan/data/money_paths.json</p>
</div>
</body></html>'''.format(total=len(paths), next_cid=chr(65+3+len(ALREADY_IMPLEMENTED)+len(implemented)), new_rows=''.join('<tr><td>{}</td><td>{}</td><td>{}</td><td><span class="tag new">刚创建</span></td></tr>'.format(i['cid'],i['feature'],i.get('pricing_hint','')) for i in implemented)))

dash_path=os.path.join(ROOT,'money-paths.html')
with open(dash_path,'w',encoding='utf-8') as f:
    f.write(dashboard_html)
log("WROTE {} ({})".format(dash_path,len(dashboard_html)))

log("=== Quick Implementor v1 done: created {} new modules ===".format(len(implemented)))
print(json.dumps({'created':implemented,'total_paths':len(paths)},ensure_ascii=False,indent=2))

#!/usr/bin/env python3
"""给 alipay.js 和 vercel.json 添加 C18-C20 路由 (基于已有模式)"""
import json, os, re, subprocess
from datetime import datetime

ROOT = r'F:\2026\24xs\02_交付物\channels\gumroad-product-1\tool-station-server-pro'
LOG = r'C:\Users\46012\AppData\Local\Temp\wire_c18_20.log'
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[WIRE2][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

# New modules to wire
NEW=[
    {'slug':'scan_api','cid':'C18','desc':'全市场扫描'},
    {'slug':'alert_api','cid':'C19','desc':'价格预警通知'},
    {'slug':'minute_klines','cid':'C20','desc':'分钟级K线订阅'},
]

# 1. Patch alipay.js
alipay_path=os.path.join(ROOT,r'api\alipay.js')
src=open(alipay_path,'r',encoding='utf-8').read()

insert=""
for m in NEW:
    insert += """    // {cid} {desc} ({slug}) — 合规渠道\\n
    if(route.startsWith('/api/{slug}')){{\\n
      try{{\\n
        const mod = require('../lib/{slug}.js');\\n
        data.path = route;\\n
        if(!data.ref){{\\n
          const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);\\n
          if(pid)data.ref=pid;\\n
        }}\\n
        return await mod.onRequest(req,res,data);\\n
      }}catch(e){{\\n
        send(500,{{ok:false,error:'{slug} handler error: '+e.message}});\\n
      }}\\n
      return;\\n
    }}\\n
""".format(**m)

# Insert before the final 404 fallback
fallback="send(404,{ok:false,error:'not found',route:route});"
if fallback in src:
    idx = src.index(fallback)
    src = src[:idx] + insert + '\n    ' + fallback
    log("Patched alipay.js with {} routes".format(len(NEW)))
else:
    log("WARNING: could not find fallback pattern")
    # Try alternate
    alt = "send(404,{ok:false,error:"
    matches = [m.start() for m in re.finditer(re.escape('send(404,'), src)]
    if matches:
        idx = matches[-1]
        src = src[:idx] + insert + '\n    ' + src[idx:]
        log("Patched alipay.js (alt) with {} routes".format(len(NEW)))

with open(alipay_path,'w',encoding='utf-8') as f:
    f.write(src)

# 2. Patch vercel.json
vc_path=os.path.join(ROOT,'vercel.json')
vc=json.load(open(vc_path,'r',encoding='utf-8'))
existing={r.get('source','') for r in vc.get('rewrites',[])}
added=[]
for m in NEW:
    s='/api/'+m['slug']
    if s not in existing:
        vc['rewrites'].append({'source':s,'destination':'/api/alipay.js?r='+m['slug']})
        added.append(s)
with open(vc_path,'w',encoding='utf-8') as f:
    json.dump(vc,f,ensure_ascii=False,indent=2); f.write('\n')
log("vercel.json: added {} rewrites: {}".format(len(added), added))

# 3. Validate
log("Validating...")
all_ok=True
for m in NEW:
    rc=subprocess.call(['node','--check',os.path.join(ROOT,'lib',m['slug']+'.js')])
    log("  lib/{}.js: {}".format(m['slug'],'OK' if rc==0 else 'FAIL'))
    if rc!=0: all_ok=False
rc_alipay=subprocess.call(['node','--check',alipay_path])
log("  api/alipay.js: {}".format('OK' if rc_alipay==0 else 'FAIL'))
if rc_alipay!=0: all_ok=False
try:
    json.load(open(vc_path,'r'))
    log("  vercel.json: OK")
except Exception as e:
    log("  vercel.json: ERR {}".format(str(e)[:60]))
    all_ok=False

# 4. Update channels.html - add cards after C12
ch_path=os.path.join(ROOT,'channels.html')
ch_src=open(ch_path,'r',encoding='utf-8').read()
new_cards=""
for m in NEW:
    new_cards += '''
  <!-- {cid} 合规渠道: {desc} -->
  <div class="card">
    <h3>{desc} <span class="tag live">{cid}</span></h3>
    <p class="d"><b>{feat_desc}</b></p>
    <div class="acts">
      <a id="{slug}PayLink" class="cta" href="#">购买</a>
      <button id="{slug}Btn">查询额度</button>
    </div>
    <div class="stat" id="{slug}Stat"></div>
    <div class="note">基于公开数据，不构成投资建议。服务端权威，fail-closed。</div>
  </div>
'''.format(cid=m['cid'],desc=m['desc'],slug=m['slug'],feat_desc=m['desc']+'服务')

if '<h2>为什么可信</h2>' in ch_src:
    ch_src=ch_src.replace('<h2>为什么可信</h2>', new_cards+'\n  <h2>为什么可信</h2>', 1)
    log("channels.html: inserted {} cards".format(len(NEW)))
else:
    log("WARNING: anchor not found in channels.html")

with open(ch_path,'w',encoding='utf-8') as f:
    f.write(ch_src)

# 5. Update channel count
ch_src2=open(ch_path,'r',encoding='utf-8').read()
old1=re.search(r'(\d+)\s*条账本渠道', ch_src2)
old2=re.search(r'(\d+)\s*类付费渠道', ch_src2)
if old1:
    new_count=int(old1.group(1))+len(NEW)
    ch_src2=ch_src2.replace(old1.group(0), '{} 条账本渠道'.format(new_count), 1)
    log("Updated count: {} 条账本".format(new_count))
if old2:
    new_cat=int(old2.group(1))+1
    ch_src2=ch_src2.replace(old2.group(0), '{} 类付费渠道'.format(new_cat), 1)
    log("Updated count: {} 类付费".format(new_cat))
with open(ch_path,'w',encoding='utf-8') as f:
    f.write(ch_src2)

log("=== Wire Up C18-C20 complete ===")
print(json.dumps({'created':[m['cid']+':'+m['slug'] for m in NEW],'count':len(NEW),'all_ok':all_ok},ensure_ascii=False))

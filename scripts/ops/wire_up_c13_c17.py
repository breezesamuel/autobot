#!/usr/bin/env python3
"""给 alipay.js 添加 C13-C17 新路由 + vercel.json rewrite (本地运行)"""
import json, os, sys, subprocess, re as _re
from datetime import datetime

ROOT=r'F:\2026\24xs\02_交付物\channels\gumroad-product-1\tool-station-server-pro'
LOG=r'C:\Users\46012\AppData\Local\Temp\wire_up.log'

os.makedirs(os.path.dirname(LOG), exist_ok=True)
def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[WIRE][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Wire Up C13-C17 (LOCAL) ===")

NEW_MODULES=[
    {'slug':'alternative_data','cid':'C13','desc':'另类数据订阅','price_yuan':499,'price_coin':300},
    {'slug':'backtest_history','cid':'C14','desc':'历史回测存档','price_yuan':19,'price_coin':300},
    {'slug':'co_brand_product','cid':'C15','desc':'联合品牌产品','price_yuan':29,'price_coin':300},
    {'slug':'custom_indicators','cid':'C16','desc':'自定义指标库','price_yuan':49,'price_coin':300},
    {'slug':'custom_integration','cid':'C17','desc':'定制集成开发','price_yuan':2000,'price_coin':20000},
]

# 1. Patch alipay.js
alipay_path=os.path.join(ROOT,r'api\alipay.js')
src=open(alipay_path,'r',encoding='utf-8').read()

insert_block=""
for m in NEW_MODULES:
    insert_block += """    // {cid} {desc} ({slug}) — 合规渠道: 按次付费, 币¥双付\n
    if(route.startsWith('/api/{slug}')){{\n
      try{{\n
        const mod = require('../lib/{slug}.js');\n
        data.path = route;\n
        if(!data.ref){{\n
          const pid = String((req.headers['x-ref']||req.headers['x-user-ref']||'')||'').slice(0,64);\n
          if(pid)data.ref=pid;\n
        }}\n
        return await mod.onRequest(req,res,data);\n
      }}catch(e){{\n
        send(500,{{ok:false,error:'{slug} handler error: '+e.message}});\n
      }}\n
      return;\n
    }}\n
""".format(**m)

fallback=_re.search(r"send\(404,\{ok:false,error:'not found'", src)
if fallback:
    idx=fallback.start()
    src=src[:idx] + insert_block + src[idx:]
    log("Patched alipay.js: inserted {} routes before 404 fallback".format(len(NEW_MODULES)))
else:
    # Find last occurrence of "send(404"
    indices=[m.start() for m in _re.finditer(r"send\(404", src)]
    if indices:
        idx=indices[-1]
        src=src[:idx] + insert_block + src[idx:]
        log("Patched alipay.js (last 404): inserted {} routes".format(len(NEW_MODULES)))
    else:
        log("ERROR: no 404 fallback found in alipay.js")
        sys.exit(1)

with open(alipay_path,'w',encoding='utf-8') as f:
    f.write(src)

# 2. Patch vercel.json
vercel_path=os.path.join(ROOT,'vercel.json')
vc=json.load(open(vercel_path,'r',encoding='utf-8'))
existing=set(r.get('source','') for r in vc.get('rewrites',[]))
added=[]
for m in NEW_MODULES:
    s='/api/'+m['slug']
    if s not in existing:
        vc['rewrites'].append({'source':s,'destination':'/api/alipay.js?r='+m['slug']})
        added.append(s)
with open(vercel_path,'w',encoding='utf-8') as f:
    json.dump(vc,f,ensure_ascii=False,indent=2); f.write('\n')
log("vercel.json: added {} new rewrites: {}".format(len(added), added))

# 3. Validate
log("Validating...")
checks={'alipay.js':alipay_path,'vercel.json':vercel_path}
for m in NEW_MODULES:
    checks['lib/'+m['slug']+'.js']=os.path.join(ROOT,'lib',m['slug']+'.js')
all_ok=True
for name,path in checks.items():
    rc=subprocess.call(['node','--check',path]) if path.endswith('.js') else 0
    if path.endswith('.json'):
        try: json.load(open(path,'r')); rc=0
        except: rc=1
    status='OK' if rc==0 else 'FAIL'
    log("  {}: {}".format(name,status))
    if rc!=0: all_ok=False
if not all_ok:
    log("ERROR: validation failed!")
    sys.exit(1)

# 4. Update channels.html - add cards after C12 card
ch_path=os.path.join(ROOT,'channels.html')
ch_src=open(ch_path,'r',encoding='utf-8').read()
new_cards_html=""
for m in NEW_MODULES:
    new_cards_html += '''
  <!-- {cid} 合规渠道: {desc} -->
  <div class="card">
    <h3>{desc} <span class="tag live">{cid}</span></h3>
    <p class="d"><b>{feat_desc}</b> · <b>¥{price_yuan} / {price_coin}币</b></p>
    <div class="acts">
      <a id="{slug}PayLink" class="cta" href="#">¥{price_yuan} 购买</a>
      <button id="{slug}Btn">查我的额度</button>
    </div>
    <div class="stat" id="{slug}Stat"></div>
    <div class="note">基于公开数据, 不构成投资建议。服务端权威, fail-closed, 不造假。</div>
  </div>
'''.format(cid=m['cid'],desc=m['desc'],slug=m['slug'],feat_desc=m['desc']+'服务',price_yuan=m['price_yuan'],price_coin=m['price_coin'])

if '<h2>为什么可信</h2>' in ch_src:
    ch_src=ch_src.replace('<h2>为什么可信</h2>', new_cards_html+'\n  <h2>为什么可信</h2>', 1)
    log("channels.html: inserted {} new cards".format(len(NEW_MODULES)))
else:
    log("WARNING: could not find anchor in channels.html")

with open(ch_path,'w',encoding='utf-8') as f:
    f.write(ch_src)

# 5. Update trust count
ch_src2=open(ch_path,'r',encoding='utf-8').read()
old_count=_re.search(r'(\d+)\s*条账本渠道', ch_src2)
if old_count:
    new_count=int(old_count.group(1))+len(NEW_MODULES)
    ch_src2=ch_src2.replace(old_count.group(0), '{} 条账本渠道'.format(new_count), 1)
    old_cat=_re.search(r'(\d+) 类付费渠道', ch_src2)
    if old_cat:
        new_cat=int(old_cat.group(1))+1
        ch_src2=ch_src2.replace(old_cat.group(0), '{} 类付费渠道'.format(new_cat), 1)
    log("Updated channel counts: {} 条账本 / {} 类付费".format(new_count, new_cat))
with open(ch_path,'w',encoding='utf-8') as f:
    f.write(ch_src2)

log("=== Wire Up COMPLETE ===")
print(json.dumps({'created':[m['cid']+':'+m['slug'] for m in NEW_MODULES],'count':len(NEW_MODULES)},ensure_ascii=False))

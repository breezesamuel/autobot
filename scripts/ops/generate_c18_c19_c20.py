#!/usr/bin/env python3
"""从 overfitcheck.js 模板生成 C18 scan_api + C19 alert_api + C20 minute_klines (修正版)"""
import os, re, shutil

ROOT = '/www/wwwroot/tools-cn.highkingflower.com'
LIB_DIR = os.path.join(ROOT, 'lib')
LOG = '/var/log/bingdashan/engine.log'

def log(m):
    ts=__import__('datetime').datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[GEN][{}] {}".format(ts,m); print(line)
    try: __import__('open')(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

# Read template from existing working module
template_path = os.path.join(LIB_DIR, 'overfitcheck.js')
src = open(template_path, 'r', encoding='utf-8').read()
log("Template loaded: {} ({} bytes)".format(template_path, len(src)))

configs = [
    {'name': 'scan_api',      'cid': 'C18', 'prefix': 'sc:',  'subdir': 'scan_api',        'table': 'scan_api_kv',  'env_prefix': 'SCAN_',   'price_yuan': 99,  'price_coin': 1000, 'quota_name': 'QUOTA_PER_PACK', 'quota_default': 100,  'action_handler': 'scan'},
    {'name': 'alert_api',     'cid': 'C19', 'prefix': 'al:',  'subdir': 'alert_api',       'table': 'alert_api_kv', 'env_prefix': 'ALERT_',  'price_yuan': 29,  'price_coin': 300,  'quota_name': 'ALERTS_PER_PACK', 'quota_default': 50, 'action_handler': 'create'},
    {'name': 'minute_klines', 'cid': 'C20', 'prefix': 'mk:',  'subdir': 'minute_klines',  'table': 'minute_klines_kv', 'env_prefix': 'MINUTE_', 'price_yuan': 99, 'price_coin': 1000, 'quota_name': None, 'quota_default': None, 'action_handler': 'purchase', 'period_days': 30},
]

import subprocess
created = []
for cfg in configs:
    mod_src = src
    
    # Replace placeholder values
    replacements = {
        'overfitcheck': cfg['name'],
        'ofc': cfg['prefix'],
        'OF': 'OC',  # ID prefix for entries
        'ofc:': cfg['prefix'],
        'Overfitcheck': cfg['name'].replace('_',' ').title(),
        '/api/overfitcheck': '/api/' + cfg['name'],
        'overfitcheck_kv': cfg['table'],
        'overfitcheck/': cfg['subdir'] + '/',
        'PRICE_YUAN': cfg['env_prefix'] + 'PRICE_YUAN',
        'PRICE_COIN': cfg['env_prefix'] + 'PRICE_COIN',
    }
    
    for old, new in replacements.items():
        mod_src = mod_src.replace(old, new)
    
    # Add custom config constants after ADMIN_SECRET line
    if cfg.get('quota_name'):
        quota_const = "const {} = (function(){{ var v = parseInt(process.env.{}) ; return (isFinite(v) && v > 0) ? v : {}; }})();".format(
            cfg['quota_name'], cfg['env_prefix'] + 'QUOTA_PER_PACK', cfg['quota_default'])
    else:
        quota_const = ""
    
    if cfg.get('period_days'):
        period_const = "const PERIOD_DAYS = (function(){{ var v = parseInt(process.env.{}_PERIOD_DAYS); return (isFinite(v) && v > 0) ? v : {}; }})();".format(cfg['env_prefix'], cfg['period_days'])
    else:
        period_const = ""
    
    # Insert quota constant after ADMIN_SECRET line
    admin_line = "const ADMIN_SECRET = process.env.ADMIN_SECRET || process.env.AUTOOPS_SECRET || '';"
    if quota_const or period_const:
        mod_src = mod_src.replace(admin_line, admin_line + '\n' + quota_const + '\n' + period_const, 1)
    
    # Write file
    out_path = os.path.join(LIB_DIR, '{}.js'.format(cfg['name']))
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(mod_src)
    
    # Verify syntax
    rc = subprocess.call(['node', '--check', out_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sz = os.path.getsize(out_path)
    status = 'OK {}B'.format(sz) if rc == 0 else 'FAIL'
    log("{} -> {} ({})".format(cfg['cid'], cfg['name'], status))
    if rc == 0:
        created.append({'cid': cfg['cid'], 'name': cfg['name'], 'yuan': cfg['price_yuan'], 'coin': cfg['price_coin'], 'size': sz})

log("Created {} modules: {}".format(len(created), [c['cid']+':'+c['name'] for c in created]))
print(__import__('json').dumps({'created': created, 'total': len(configs)}, ensure_ascii=False, indent=2))

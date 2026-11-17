#!/usr/bin/env python3
"""丙大山 · 全链路主引擎 v7 (reconcile + payment_alert_ssl + weekly_digest + insight + selfheal)"""
import json, os, sys, time, subprocess, smtplib, glob
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import Counter
import urllib.request

BL='/opt/bingdashan/data/billing'
DB='/opt/bingdashan/data/db.json'
LOG='/var/log/bingdashan/engine.log'
STATE_DIR='/opt/bingdashan/data/runtime'
STATE_FILE=os.path.join(STATE_DIR,'engine_state_v7.json')
SMTP_ENV='/opt/bingdashan/.env'
ALERTS_FILE=os.path.join(STATE_DIR,'alerts_v7.json')

os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[V7][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

def load_state():
    try: return json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {}
    except: return {}
def save_state(s):
    with open(STATE_FILE,'w',encoding='utf-8') as f: json.dump(s,f,ensure_ascii=False,indent=2); f.write('\n')

def get_smtp():
    cfg={'host':'smtp.qq.com','port':465,'user':'460123249@qq.com','pass':'','to':['460123249@qq.com'],'secure':True}
    try:
        env=open(SMTP_ENV,'r',encoding='utf-8').read()
        for ln in env.split('\n'):
            if not ln.strip() or ln.strip().startswith('#'): continue
            kv=ln.split('=',1)
            if len(kv)!=2: continue
            k,v=kv[0].strip(),kv[1].strip().strip('"\'')
            if k=='SMTP_HOST': cfg['host']=v
            elif k=='SMTP_PORT': cfg['port']=int(v)
            elif k=='SMTP_SECURE': cfg['secure']=(v.lower()=='true')
            elif k=='SMTP_USER': cfg['user']=v
            elif k=='SMTP_PASS': cfg['pass']=v
            elif k=='ALERT_EMAIL': cfg['to']=[x.strip() for x in v.split(',')]
    except Exception as e:
        log("WARN smtp: {}".format(str(e)[:60]))
    return cfg

def send_email(to_addrs, subject, html_body):
    cfg=get_smtp()
    if not cfg.get('pass'):
        log("SKIP email: no SMTP_PASS"); return False
    try:
        msg=MIMEMultipart('alternative')
        msg['Subject']=subject; msg['From']=cfg['user']; msg['To']=','.join(to_addrs)
        msg.attach(MIMEText(html_body,'html','utf-8'))
        if cfg.get('secure'):
            srv=smtplib.SMTP_SSL(cfg['host'], cfg['port'], timeout=15)
        else:
            srv=smtplib.SMTP(cfg['host'], cfg['port'], timeout=15)
            srv.starttls()
        srv.login(cfg['user'], cfg['pass'])
        srv.send_message(msg)
        srv.quit()
        log("EMAIL SENT to {} subj={}".format(len(to_addrs), subject[:40]))
        return True
    except Exception as e:
        log("EMAIL FAIL: {}".format(str(e)[:100]))
        return False

FINAL={'paid','collected','done','verified','approved'}
log("=== ENGINE V7 LOOP start ===")

# ===== PHASE 1: Reconcile =====
try:
    d=json.load(open(DB,'r',encoding='utf-8')); orders=d.get('orders',[])
except Exception as e:
    log("ERR db: {}".format(e)); sys.exit(1)
by={}
for o in orders:
    if not isinstance(o,dict): continue
    amt=float(o.get('amount',0) or 0); ref=str(o.get('ref','') or '')
    is_real=(o.get('paid') is True and amt>5 and len(ref)>2 and bool(o.get('gateway')))
    if is_real and ref:
        if ref not in by or (o.get('paid_at','') or '') > (by[ref].get('paid_at','') or ''):
            by[ref]=o
def load(fn,d=[]):
    p=os.path.join(BL,fn)
    if not os.path.exists(p): return d
    try:
        data=json.load(open(p,'r',encoding='utf-8'))
        return data if isinstance(data,list) else data.get('items',data.get('orders',d))
    except: return d
def save(fn,data):
    with open(os.path.join(BL,fn),'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2); f.write('\n')

outreach=load('outreach_ledger.json'); up_out=0
for i in outreach:
    if not isinstance(i,dict): continue
    ref=str(i.get('ref','')); st=i.get('status','')
    if ref in by and st not in FINAL:
        i['status']='paid'; i['paid_at']=datetime.now().isoformat(); up_out+=1
save('outreach_ledger.json',outreach)
corp=load('corporate_899.json'); up_corp=0
for i in corp:
    if not isinstance(i,dict): continue
    ref=str(i.get('ref','')); st=i.get('status','')
    if ref in by and st not in FINAL:
        i['status']='paid'; i['paid_at']=datetime.now().isoformat(); up_corp+=1
save('corporate_899.json',corp)
outreach=load('outreach_ledger.json'); corp=load('corporate_899.json')
po=[x for x in outreach if x.get('status') not in FINAL]
pc=[x for x in corp if x.get('status') not in FINAL]
py=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in po+pc)
ro=[o for o in orders if o.get('paid') is True and float(o.get('amount',0) or 0)>5]
ry=sum(float(o.get('amount',0) or 0) for o in ro)
log("PHASE1 reconcile: out_up={} corp_up={} cash=¥{} pending=¥{}".format(up_out,up_corp,int(ry),int(py)))

# ===== PHASE 2: Payment Alert (SSL SMTP) =====
state=load_state()
last_cash=state.get('last_cash_yuan',0)
new_cash=int(ry)
alerted=False
if new_cash > last_cash and last_cash > 0:
    delta=new_cash-last_cash
    today_str=datetime.now().strftime('%Y-%m-%d %H:%M')
    body='''<!DOCTYPE html><html><body style="font-family:sans-serif;background:#0a0f1a;color:#e5e7eb;padding:20px">
<div style="background:#111827;border-radius:12px;padding:20px;border:1px solid #1f2937">
<h2 style="color:#22c55e;margin-top:0">&#x6536;&#x6B3E;&#x63D0;&#x9192;</h2>
<table style="width:100%%;border-collapse:collapse">
<tr><th style="text-align:left;padding:8px">&#x6307;&#x6807;</th><th style="text-align:right;padding:8px">&#x6570;&#x503C;</th></tr>
<tr><td style="padding:8px;border-bottom:#1f2937 1px solid">&#x65B0;&#x589E;</td><td style="padding:8px;text-align:right;color:#22c55e;font-weight:700">+&#xA5;{}</td></tr>
<tr><td style="padding:8px;border-bottom:#1f2937 1px solid">&#x603B;&#x73B0;&#x91D1;</td><td style="padding:8px;text-align:right;color:#3b82f6">&#xA5;{}</td></tr>
<tr><td style="padding:8px">&#x5F85;&#x6536;</td><td style="padding:8px;text-align:right">&#xA5;{}</td></tr>
</table>
<p style="color:#9ca3af;font-size:.85rem;margin-top:16px">{}</p>
<a href="https://tools-cn.highkingflower.com/revenue-honest.html" style="color:#22c55e">-> &#x67E5;&#x770B;&#x5B8C;&#x6574;&#x770B;&#x677F;</a>
</div></body></html>'''.format(int(delta), int(ry), int(py), today_str)
    sent=send_email(get_smtp()['to'], "[&#x4E59;&#x5927;&#x5C71;] &#x65B0;&#x6536;&#x6B3E; &#xA5;{}".format(int(delta)), body)
    if sent: log("PHASE2 ALERT SENT delta=&#xA5;{}".format(int(delta))); alerted=True
    else: log("PHASE2 ALERT FAILED (check SMTP)")
else:
    log("PHASE2 no new cash (last={}, current={})".format(last_cash, new_cash))
state['last_cash_yuan']=new_cash; state['last_alert_sent']=alerted
save_state(state)

# ===== PHASE 3: Weekly Digest (Monday only) =====
now=datetime.now(); today_s=now.strftime('%Y-%m-%d'); is_monday=(now.weekday()==0)
last_digest=state.get('last_digest_date','')
if last_digest != today_s and is_monday:
    pending_list=[]
    for x in po+pc:
        if isinstance(x,dict):
            pending_list.append({'oid':str(x.get('order_id',''))[:16],'kind':x.get('kind','?'),'amt':int(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0),'status':x.get('status','?'),'note':str(x.get('note',x.get('memo',''))[:50])})
    py_total=sum(p['amt'] for p in pending_list)
    rows='<br>'.join("<tr><td>{}</td><td>{}</td><td style='text-align:right'>&#xA5;{}</td><td>{}</td><td style='max-width:200px'>{}</td></tr>".format(p['oid'],p['kind'],p['amt'],p['status'],p['note']) for p in pending_list[:10])
    digest_html='''<!DOCTYPE html><html><body style="font-family:sans-serif;background:#0a0f1a;color:#e5e7eb;padding:20px">
<div style="background:#111827;border-radius:12px;padding:20px;border:1px solid #1f2937">
<h2 style="color:#f59e0b;margin-top:0">&#x6BCF;&#x5468;&#x8425;&#x6536;&#x5468;&#x62A5; ({})</h2>
<table style="width:100%%;border-collapse:collapse;font-size:.85rem">
<tr><th style="text-align:left;padding:8px">ID</th><th>type</th><th style="text-align:right">amt</th><th>status</th><th>note</th></tr>
{}
</table>
<p style="color:#9ca3af;font-size:.85rem;margin-top:16px">total_pending: &#xA5;{} <a href="https://tools-cn.highkingflower.com/revenue-collection.html" style="color:#22c55e">copy alerts</a></p>
</div></body></html>'''.format(today_s, rows, py_total)
    send_email(get_smtp()['to'], "[&#x4E59;&#x5927;&#x5C71;] WEEKLY {}", today_s, digest_html)
    state['last_digest_date']=today_s
    log("PHASE3 weekly digest sent")
else:
    log("PHASE3 skip digest (mon={} last={} now={})".format(is_monday,last_digest,today_s))

# ===== PHASE 4: Visitor Insight =====
try:
    rc=subprocess.call(['python3','/opt/bingdashan/scripts/ops/visitor_insight.py'], timeout=30)
    log("PHASE4 insight rc={}".format(rc))
except Exception as e:
    log("PHASE4 insight WARN: {}".format(str(e)[:80]))

# ===== PHASE 4b: Lead Outreach (daily) =====
today_s2=datetime.now().strftime('%Y-%m-%d')
last_lead_run=state.get('last_lead_run_date','')
if last_lead_run != today_s2:
    try:
        rc2=subprocess.call(['python3','/opt/bingdashan/scripts/ops/lead_outreach.py'], timeout=30)
        log("PHASE4b lead_outreach rc={}".format(rc2))
    except Exception as e:
        log("PHASE4b lead_outreach WARN: {}".format(str(e)[:80]))
    state['last_lead_run_date']=today_s2
else:
    log("PHASE4b skip lead_outreach (already ran today)")

# ===== PHASE 5: Self-heal =====
svcs=['bingdashan-cn']
for svc in svcs:
    r=subprocess.run(['systemctl','is-active',svc], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if r.stdout.strip()!='active':
        log("HEAL: {} down -> restart".format(svc))
        subprocess.call(['systemctl','restart',svc]); time.sleep(3)
endpoints=['http://127.0.0.1:8794/api/revenue','http://127.0.0.1:8794/revenue-honest.html']
for ep in endpoints:
    try:
        req=urllib.request.Request(ep, headers={'User-Agent':'BingDashan-V7/1.0'})
        resp=urllib.request.urlopen(req, timeout=10)
        if resp.status!=200: log("WARNING {} HTTP{}".format(ep, resp.status))
    except Exception as e:
        log("ERROR {} : {}".format(ep, str(e)[:80]))
try:
    r=subprocess.run(['df','-h','/'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    pct=int(r.stdout.strip().split('\n')[1].split()[4].replace('%',''))
    if pct>90:
        log("HEAL: disk >90%, cleanup!")
        for lp in glob.glob('/var/log/bingdashan/*.log'):
            try:
                if os.path.getsize(lp)>10*1024*1024: os.rename(lp, lp+'.bak')
            except: pass
except: pass
log("PHASE5 health OK (disk={}%".format(pct if 'pct' in dir() else '?') + ')')

all_pending=po+pc; total_py=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in all_pending)
log("=== ENGINE V7 done: cash=¥{} pending=¥{} alerts={} digest={} ===".format(
    int(ry), int(total_py), alerted, state.get('last_digest_date','')))
sys.exit(0)

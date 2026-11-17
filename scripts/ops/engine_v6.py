#!/usr/bin/env python3
"""丙大山 · 收入预警 + 每日自动触达引擎 v6 (payment_alert + daily_digest)"""
import json, os, sys, time, smtplib, subprocess
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

BL='/opt/bingdashan/data/billing'
DB='/opt/bingdashan/data/db.json'
LOG='/var/log/bingdashan/engine.log'
STATE='/opt/bingdashan/data/runtime/engine_v6_state.json'
SMTP_PASS_FILE='/opt/bingdashan/.env'

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[V6][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

def load_state():
    try: return json.load(open(STATE)) if os.path.exists(STATE) else {}
    except: return {}
def save_state(s):
    with open(STATE,'w',encoding='utf-8') as f: json.dump(s,f,ensure_ascii=False,indent=2); f.write('\n')

def get_smtp_config():
    """从 .env 读 SMTP 配置"""
    cfg={'host':'smtp.qq.com','port':587,'user':'supi24@163.com','pass':''}
    try:
        env_content=open(SMTP_PASS_FILE,'r',encoding='utf-8').read()
        for ln in env_content.split('\n'):
            if ln.startswith('SMTP_HOST='): cfg['host']=ln.split('=',1)[1].strip().strip('"\'')
            elif ln.startswith('SMTP_PORT='): cfg['port']=int(ln.split('=',1)[1].strip())
            elif ln.startswith('SMTP_USER='): cfg['user']=ln.split('=',1)[1].strip().strip('"\'')
            elif ln.startswith('SMTP_PASS='): cfg['pass']=ln.split('=',1)[1].strip().strip('"\'')
    except Exception as e:
        log("WARN read smtp config: {}".format(str(e)[:60]))
    return cfg

def send_alert(to_addr, subject, body_html):
    """发送 HTML 邮件告警 (收款/触发)"""
    cfg=get_smtp_config()
    if not cfg.get('pass'):
        log("SKIP alert: no SMTP_PASS configured"); return False
    try:
        msg=MIMEMultipart('alternative')
        msg['Subject']=subject
        msg['From']=cfg['user']
        msg['To']=to_addr
        msg.attach(MIMEText(body_html,'html','utf-8'))
        with smtplib.SMTP(cfg['host'], cfg['port'], timeout=15) as srv:
            srv.starttls()
            srv.login(cfg['user'], cfg['pass'])
            srv.send_message(msg)
        log("ALERT SENT to {} subj={}".format(to_addr, subject[:40]))
        return True
    except Exception as e:
        log("ALERT SEND FAIL to {}: {}".format(to_addr, str(e)[:100]))
        return False

FINAL={'paid','collected','done','verified','approved'}
log("=== ENGINE V6 LOOP start ===")

# ===== PHASE 1: Reconcile (same as v5) =====
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
        return data if isinstance(data,list) else data.get('items', data.get('orders',d))
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

# ===== PHASE 2: Payment Alert (新收的钱立即报警) =====
state=load_state()
last_cash=state.get('last_cash_yuan',0)
new_cash=int(ry)
if new_cash > last_cash and last_cash > 0:
    delta=new_cash - last_cash
    today_paid_count=len([o for o in ro if o.get('paid_at','')[:10]==datetime.now().strftime('%Y-%m-%d')])
    # Build alert email
    from_addr=get_smtp_config()['user']
    to_addrs=[from_addr]  # 发到 owner 自己邮箱
    html_body="""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#0a0f1a;color:#e5e7eb;padding:24px">
<div style="background:#111827;border-radius:12px;padding:20px;border:1px solid #1f2937">
<h2 style="color:#22c55e;margin-top:0">💰 丙大山·实时收款提醒</h2>
<table style="width:100%;border-collapse:collapse">
<tr><th style="text-align:left;padding:8px">指标</th><th style="text-align:right;padding:8px">数值</th></tr>
<tr><td style="padding:8px;border-bottom:#1f2937 1px solid">新增入账</td><td style="padding:8px;text-align:right;color:#22c55e;font-weight:700">+¥{}</td></tr>
<tr><td style="padding:8px;border-bottom:#1f2937 1px solid">今日累计</td><td style="padding:8px;text-align:right;color:#f59e0b">¥{}</td></tr>
<tr><td style="padding:8px;border-bottom:#1f2937 1px solid">总现金</td><td style="padding:8px;text-align:right;color:#3b82f6">¥{}</td></tr>
<tr><td style="padding:8px">待收</td><td style="padding:8px;text-align:right">¥{}</td></tr>
</table>
<p style="color:#9ca3af;font-size:.85rem;margin-top:16px">触发时间: {} · 查看详情: <a href="https://tools-cn.highkingflower.com/revenue-honest.html" style="color:#22c55e">看板</a></p>
</div></body></html>""".format(int(delta), int(ry), int(ry), int(py), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sent=send_alert(to_addrs[0], "[丙大山] 新收款 ¥{}!".format(int(delta)), html_body)
    if sent: log("PHASE2 ALERT SENT: delta=¥{} total=¥{}".format(int(delta), int(ry)))
    else: log("PHASE2 ALERT FAILED (check SMTP)")
else:
    log("PHASE2 no new cash (last={}, current={})".format(last_cash, new_cash))
state['last_cash_yuan']=new_cash
state['last_check_at']=datetime.now().isoformat()
save_state(state)

# ===== PHASE 3: Daily Digest (每周一早上发汇总) =====
now=datetime.now()
last_digest=state.get('last_digest_date','')
today_str=now.strftime('%Y-%m-%d')
if last_digest != today_str:
    # Only run digest on Monday OR first run of the day
    is_monday=(now.weekday()==0)
    if is_monday:
        log("PHASE3 MONDAY DIGEST triggered")
        pending_list=[]
        for x in po+pc:
            if isinstance(x,dict):
                pending_list.append({
                    'oid':str(x.get('order_id',''))[:16],
                    'kind':x.get('kind','?'),
                    'amt':int(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0),
                    'status':x.get('status','?'),
                    'link':str(x.get('pay_link','') or ''),
                    'note':str(x.get('note',x.get('memo',''))[:50])
                })
        pending_yuan=sum(p['amt'] for p in pending_list)
        from_addr=get_smtp_config()['user']
        to_addrs=[from_addr]
        rows='<br>'.join("<tr><td>{}</td><td>{}</td><td style='text-align:right'>¥{}</td><td>{}</td><td style='max-width:200px;word-break:break-all'>{}</td></tr>".format(p['oid'],p['kind'],p['amt'],p['status'],p['note']) for p in pending_list[:10])
        digest_html="""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#0a0f1a;color:#e5e7eb;padding:24px">
<div style="background:#111827;border-radius:12px;padding:20px;border:1px solid #1f2937">
<h2 style="color:#f59e0b;margin-top:0">📊 丙大山 · 每周营收周报 ({})</h2>
<table style="width:100%;border-collapse:collapse;font-size:.85rem">
<tr class="th"><th style="text-align:left;padding:8px">订单ID</th><th style="text-align:left;padding:8px">类型</th><th style="text-align:right;padding:8px">金额</th><th style="text-align:left;padding:8px">状态</th><th style="text-align:left;padding:8px">备注</th></tr>
{}
</table>
<p style="color:#9ca3af;font-size:.85rem;margin-top:16px">本周待收合计: ¥{} · 查看详情: <a href="https://tools-cn.highkingflower.com/revenue-honest.html" style="color:#22c55e">看板</a> · 一键触达: <a href="https://tools-cn.highkingflower.com/revenue-collection.html" style="color:#22c55e">批量复制</a></p>
</div></body></html>""".format(today_str, rows, pending_yuan)
        send_alert(to_addrs[0], "[丙大山] 每周营收周报 {}".format(today_str), digest_html)
        state['last_digest_date']=today_str
        log("PHASE3 weekly digest sent (total pending ¥{})".format(int(pending_yuan)))
    else:
        log("PHASE3 not monday, skip digest (today={}, last={})".format(today_str, last_digest))
state['last_digest_date']=today_str
save_state(state)

# ===== SUMMARY =====
all_pending=po+pc
total_py=sum(float(x.get('collect',0) or x.get('amount',0) or x.get('corporate_amount',0) or 0) for x in all_pending)
log("=== ENGINE V6 done: cash=¥{} pending=¥{} new_alerts={} weekly_sent={} ===".format(
    int(ry), int(total_py), int(new_cash>last_cash and last_cash>0), 
    int(last_digest != today_str and datetime.now().weekday()==0)))
sys.exit(0)

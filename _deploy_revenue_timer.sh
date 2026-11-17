# 定时器: 每 5min 跑一次 _auto_reconcile.sh + _gen_honest_dashboard.py (自动同步台账+刷新看板)
cat > /etc/systemd/system/bd-revenue-watch.timer <<'EOF'
[Unit]
Description=BingDashan Revenue Auto-Reconcile + Dashboard Refresh Timer

[Timer]
OnBootSec=2m
OnUnitActiveSec=5m
AccuracySec=10s
Persistent=true

[Install]
WantedBy=timers.target
EOF
cat > /etc/systemd/system/bd-revenue-watch.service <<'EOF'
[Unit]
Description=BingDashan Revenue Auto-Reconcile + Dashboard Refresh

[Service]
Type=oneshot
WorkingDirectory=/www/wwwroot/tools-cn.highkingflower.com
Environment="FILE_STORE_DIR=/var/lib/bingdashan-cn"
ExecStartPre=/bin/bash -c 'echo "[%{=utc:%Y-%m-%dT%H:%M:%S}] start bd-revenue-watch" >> /var/log/bingdashan/ops.log'
ExecStart=/bin/bash /opt/bingdashan/scripts/ops/reconcile_and_refresh.sh
ExecStartPost=/bin/bash -c 'echo "[%{=utc:%Y-%m-%dT%H:%M:%S}] done bd-revenue-watch" >> /var/log/bingdashan/ops.log'
StandardOutput=append:/var/log/bingdashan/ops.log
StandardError=append:/var/log/bingdashan/ops.log
EOF
# 创建 reconcile script
mkdir -p /opt/bingdashan/scripts/ops /var/log/bingdashan
cat > /opt/bingdashan/scripts/ops/reconcile_and_refresh.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd /opt/bingdashan
# 1. auto-reconcile: db.json paid -> outreach/corp ledger
python3 - <<'PY'
import json,os,sys
from datetime import datetime
bl='/opt/bingdashan/data/billing'
def load(fn):
    try: return json.load(open(os.path.join(bl,fn))) if os.path.exists(os.path.join(bl,fn)) else []
    except: return []
def save(fn,data):
    with open(os.path.join(bl,fn),'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)
db_path='/opt/bingdashan/data/db.json'
try: d=json.load(open(db_path)); orders=d.get('orders',[])
except: orders=[]
paid_by_ref={}
for o in orders:
    if o.get('paid') is True and o.get('ref'): paid_by_ref[str(o['ref'])]=o
outreach=load('outreach_ledger.json')
if isinstance(outreach,dict): outreach=outreach.get('items',[])
updated_out=0
for i in outreach:
    if not isinstance(i,dict):continue
    ref=str(i.get('ref','')); status=i.get('status','')
    if ref in paid_by_ref and status not in ('paid','collected','done','verified'):
        i['status']='paid'; i['paid_at']=datetime.now().isoformat(); updated_out+=1
save('outreach_ledger.json',outreach)
corp=load('corporate_899.json')
if isinstance(corp,dict): corp=corp.get('items',corp.get('orders',[]))
updated_corp=0
for i in corp:
    if not isinstance(i,dict):continue
    ref=str(i.get('ref','')); status=i.get('status','')
    if ref in paid_by_ref and status not in ('paid','collected','done','verified','approved'):
        i['status']='paid'; i['paid_at']=datetime.now().isoformat(); updated_corp+=1
save('corporate_899.json',corp)
pending_out=[x for x in outreach if x.get('status') not in ('paid','collected','done','verified')]
pending_corp=[x for x in corp if x.get('status') not in ('paid','collected','done','verified','approved')]
total=sum(float(x.get('collect') or x.get('amount') or x.get('corporate_amount') or 0) for x in (pending_out+pending_corp))
print("RECONCILE: out_up=%d corp_up=%d pending_yuan=%.0f"%(updated_out,updated_corp,total))
PY
# 2. refresh dashboard
python3 /tmp/_hd3.py 2>/dev/null || true
echo "[reconcile done]"
SH
chmod +x /opt/bingdashan/scripts/ops/reconcile_and_refresh.sh
systemctl daemon-reload && systemctl enable --now bd-revenue-watch.timer 2>/dev/null && echo "TIMER ENABLED" || echo "TIMER SKIP (may need root)"

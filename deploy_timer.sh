#!/bin/bash
# bd-revenue-watch.service
cat > /etc/systemd/system/bd-revenue-watch.service <<'SVC'
[Unit]
Description=BingDashan Revenue Auto-Reconcile + Dashboard Refresh
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/bingdashan
Environment="FILE_STORE_DIR=/var/lib/bingdashan-cn"
ExecStartPre=/usr/bin/mkdir -p /var/log/bingdashan
ExecStartPre=/usr/bin/touch /var/log/bingdashan/ops.log
ExecStart=/usr/bin/python3 /opt/bingdashan/scripts/reconcile_and_refresh.py
StandardOutput=append:/var/log/bingdashan/ops.log
StandardError=append:/var/log/bingdashan/ops.log
SVC
# timer: every 5 minutes
cat > /etc/systemd/system/bd-revenue-watch.timer <<'TMR'
[Unit]
Description=BingDashan Revenue Watch Timer (reconcile + dashboard refresh every 5min)

[Timer]
OnBootSec=2m
OnUnitActiveSec=5m
AccuracySec=10s
Persistent=true

[Install]
WantedBy=timers.target
TMR
# reconcile script in ops/
mkdir -p /opt/bingdashan/scripts
cp /tmp/rc.py /opt/bingdashan/scripts/reconcile_and_refresh.py 2>/dev/null || true
chmod 755 /opt/bingdashan/scripts/reconcile_and_refresh.py
systemctl daemon-reload
systemctl enable --now bd-revenue-watch.timer 2>&1 || echo "[WARN] timer enable failed (check root)"
echo "[OK] bd-revenue-watch deployed"

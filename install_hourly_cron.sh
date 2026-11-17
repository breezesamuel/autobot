#!/usr/bin/env bash
# 部署每小时自动引擎服务
set -euo pipefail
echo "[1/4] Installing bd-engine-hourly service..."
cat > /etc/systemd/system/bd-engine-hourly.service <<'SVC'
[Unit]
Description=BingDashan 24h Revenue Engine v5 (hourly)
After=network.target bingdashan-cn.service

[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/bingdashan
Environment="FILE_STORE_DIR=/var/lib/bingdashan-cn"
ExecStartPre=/bin/mkdir -p /var/log/bingdashan
ExecStart=/usr/bin/python3 /opt/bingdashan/scripts/ops/engine_v3.py
StandardOutput=append:/var/log/bingdashan/ops.log
StandardError=append:/var/log/bingdashan/ops.log
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
SVC

cat > /etc/systemd/system/bd-engine-hourly.timer <<'TMR'
[Unit]
Description=BingDashan Hourly Revenue Engine Timer
[Timer]
OnBootSec=1m
OnUnitActiveSec=1h
AccuracySec=60s
Persistent=true
[Install]
WantedBy=timers.target
TMR

echo "[2/4] Reload systemd + enable timer..."
systemctl daemon-reload
systemctl enable --now bd-engine-hourly.timer
sleep 2

echo "[3/4] Verify timer active..."
timer_status=$(systemctl is-active bd-engine-hourly.timer)
svc_status=$(systemctl is-enabled bd-engine-hourly.timer)
echo "  timer=$timer_status enabled=$svc_status"

echo "[4/4] Test run..."
python3 /opt/bingdashan/scripts/ops/engine_v3.py 2>&1 | tail -8
echo ""
echo "=== INSTALL COMPLETE ==="
echo "Next run: ~1h from now"
echo "Logs: /var/log/bingdashan/engine.log"
echo ""
echo "Available URLs:"
echo "  CN   revenue-collection: http://tools-cn.highkingflower.com/revenue-collection.html"
echo "  CN   revenue-honest:     http://tools-cn.highkingflower.com/revenue-honest.html"
echo "  CN   channels:           http://tools-cn.highkingflower.com/channels.html"
echo "  Vercel:                   https://tools.highkingflower.com/"

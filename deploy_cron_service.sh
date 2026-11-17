[Unit]
Description=BingDashan 24h Revenue Engine (run every hour)

[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/bingdashan
ExecStartPre=/usr/bin/mkdir -p /var/log/bingdashan
ExecStart=/usr/bin/python3 /opt/bingdashan/scripts/ops/cron_main.py
StandardOutput=append:/var/log/bingdashan/ops.log
StandardError=append:/var/log/bingdashan/ops.log

[Install]
WantedBy=multi-user.target

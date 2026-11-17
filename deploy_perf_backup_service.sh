[Unit]
Description=BingDashan Performance Check + Backup (hourly)
After=network.target bingdashan-cn.service

[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/bingdashan
Environment="FILE_STORE_DIR=/var/lib/bingdashan-cn"
ExecStartPre=/bin/mkdir -p /var/log/bingdashan /opt/bingdashan/backups
ExecStart=/usr/bin/python3 /opt/bingdashan/scripts/ops/perf_check.py
ExecStartPost=/usr/bin/python3 /opt/bingdashan/scripts/ops/auto_backup.py
StandardOutput=append:/var/log/bingdashan/ops.log
StandardError=append:/var/log/bingdashan/ops.log
TimeoutStartSec=180

[Install]
WantedBy=multi-user.target

[Unit]
Description=BingDashan 24h Revenue Engine v6 (reconcile + payment alert + weekly digest)
After=network.target bingdashan-cn.service

[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/bingdashan
Environment="FILE_STORE_DIR=/var/lib/bingdashan-cn"
ExecStartPre=/bin/mkdir -p /var/log/bingdashan
ExecStart=/usr/bin/python3 /opt/bingdashan/scripts/ops/engine_v6.py
StandardOutput=append:/var/log/bingdashan/ops.log
StandardError=append:/var/log/bingdashan/ops.log
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target

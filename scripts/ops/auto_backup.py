#!/usr/bin/env python3
"""丙大山 · 数据库备份自动化 (每天一次 + 变更触发)"""
import json, os, sys, shutil
from datetime import datetime
from pathlib import Path

BL='/opt/bingdashan/data'
BACKUP_DIR='/opt/bingdashan/backups'
LOG='/var/log/bingdashan/backup.log'
MAX_BACKUPS=30  # 最多保留30天备份

def log(m):
    ts=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    line="[BACKUP][{}] {}".format(ts,m); print(line)
    try: open(LOG,'a',encoding='utf-8').write(line+'\n')
    except: pass

log("=== Database Backup start ===")
os.makedirs(BACKUP_DIR, exist_ok=True)
ts_str=datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file=os.path.join(BACKUP_DIR,"bingdashan_backup_{}.json".format(ts_str))

try:
    # 备份 db.json
    src=os.path.join(BL,'db.json')
    if os.path.exists(src):
        shutil.copy2(src, backup_file)
        sz=os.path.getsize(backup_file)
        log("backed up db.json -> {} ({})".format(backup_file, sz))
    else:
        log("WARNING: db.json not found at {}".format(src))
    
    # 备份 billing 目录
    billing_bak=os.path.join(BACKUP_DIR,"billing_{}.tar.gz".format(ts_str))
    import subprocess
    rc=subprocess.call(['tar','czf',billing_bak,'-C',BL,'.'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if rc==0 and os.path.exists(billing_bak):
        sz2=os.path.getsize(billing_bak)
        log("backed up billing/ -> {} ({})".format(billing_bak,sz2))
    else:
        log("WARNING: billing backup failed")
    
    # 清理旧备份
    backups=sorted(Path(BACKUP_DIR).glob('*.json'))+sorted(Path(BACKUP_DIR).glob('*.tar.gz'))
    while len(backups)>MAX_BACKUPS:
        old=backups.pop(0)
        old.unlink()
        log("cleaned old backup: {}".format(old.name))
    
    log("=== Database Backup done: {} files in {}".format(len(list(Path(BACKUP_DIR).iterdir())), BACKUP_DIR))
except Exception as e:
    log("BACKUP ERROR: {}".format(str(e)[:120]))

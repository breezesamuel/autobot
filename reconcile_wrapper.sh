#!/bin/bash
# Wrapper: run reconcile script + refresh dashboard
set -euo pipefail
cd /opt/bingdashan
python3 /opt/bingdashan/scripts/reconcile_and_refresh.py 2>&1 | tail -20

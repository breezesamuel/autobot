#!/bin/bash
# BingDashan Auto-Promo System v7 - Complete Deployment Script
export PATH=/root/.local/bin:/usr/local/nodejs/bin:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

echo "=========================================="
echo "BINGDASHAN AUTO PROMO SYSTEM v7"
echo "GitHub Search + Full Automation"
echo "=========================================="

# Check all projects
echo ""
echo "[Project Status]"
for dir in auto-xhs zhihu-automation-skill content-pilot WeMediaCrawler humanized-social-publisher omni-social xhs-auto auto-hongmyungbo claude-trading-skills Y2A-Auto; do
    if [ -d "/opt/$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ✗ $dir MISSING"
    fi
done

echo ""
echo "[Environment]"
echo "  Node.js: $(node --version 2>/dev/null || echo 'not found')"
echo "  Python: $(python3 --version 2>/dev/null || echo 'not found')"
echo "  uv Python: $(/root/.local/bin/uv python list 2>/dev/null | head -1 || echo 'not configured')"
echo "  ffmpeg: $(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3 || echo 'not found')"

echo ""
echo "[Playwright]"
ls /root/.cache/ms-playwright/ 2>/dev/null | wc -l | xargs echo "  Browser installs:"

echo ""
echo "[Business Data]"
python3 << 'PYEOF'
import json
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)
orders = db.get('orders', [])
paid = [o for o in orders if o.get('paid')]
pending = [o for o in orders if not o.get('paid')]
total_pending = sum(o.get('amount', 0) for o in pending)
high_value = len([o for o in pending if o.get('amount', 0) >= 100])
print(f"Total Orders: {len(orders)}")
print(f"Paid: {len(paid)} (RMB{sum(o.get('amount',0) for o in paid):.2f})")
print(f"Pending: {len(pending)} (RMB{total_pending:.2f})")
print(f"High-value Pending: {high_value} orders >= RMB100")
PYEOF

echo ""
echo "=========================================="
echo "QUICK START COMMANDS"
echo "=========================================="
echo ""
echo "# Xiaohongshu (auto-xhs):"
echo "  ssh aliyun && cd /opt/auto-xhs && python3 core/login.py"
echo ""
echo "# Content Pilot GUI:"
echo "  cd /opt/content-pilot && source .venv/bin/activate && content-pilot gui"
echo ""
echo "# Zhihu Hot List:"
echo "  cd /opt/zhihu-automation-skill && node zhihu.js hot-list"
echo ""
echo "# WeMediaCrawler:"
echo "  cd /opt/WeMediaCrawler && /root/.local/bin/uv run python main.py --help"
echo ""
echo "=========================================="
#!/bin/bash
# BingDashan Auto-Promo v8 - Full Deployment Script
export PATH=/root/.local/bin:/usr/local/nodejs/bin:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

echo "=========================================="
echo "BINGDASHAN AUTO PROMO SYSTEM v8.0"
echo "GitHub Deep Search Complete!"
echo "=========================================="
echo ""

# Check all projects
echo "[Project Status]"
count=0
for dir in auto-xhs zhihu-automation-skill content-pilot WeMediaCrawler humanized-social-publisher omni-social xhs-auto auto-hongmyungbo claude-trading-skills Y2A-Auto apify-mcp-server yominpost scrapeio-agent; do
    if [ -d "/opt/$dir" ]; then
        echo "  ✓ $dir"
        count=$((count+1))
    else
        echo "  ✗ $dir MISSING"
    fi
done
echo ""
echo "Total deployed: $count/13 projects"

echo ""
echo "[Environment]"
node --version 2>/dev/null && echo "Node.js OK" || echo "Node.js missing"
python3 --version 2>/dev/null && echo "Python3 OK" || echo "Python3 missing"
/root/.local/bin/uv python list 2>/dev/null | /usr/bin/head -1 || echo "uv Python not found"
ffmpeg -version 2>/dev/null | /usr/bin/head -1 || echo "ffmpeg missing"

echo ""
echo "[Playwright]"
ls /root/.cache/ms-playwright/ 2>/dev/null | /usr/bin/wc -l | xargs echo "Browser versions installed:"

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
echo "# First time setup (one-time QR login):"
echo "  ssh aliyun"
echo "  cd /opt/auto-xhs"
echo "  python3 core/login.py"
echo ""
echo "# Start publishing:"
echo "  python3 core/publish.py --mode semi"
echo ""
echo "# Content Pilot GUI (recommended):"
echo "  cd /opt/content-pilot"
echo "  source .venv/bin/activate"
echo "  content-pilot gui"
echo "  # Then open http://127.0.0.1:8080"
echo ""
echo "# Zhihu hot list:"
echo "  cd /opt/zhihu-automation-skill"
echo "  node zhihu.js hot-list"
echo ""
echo "=========================================="
echo "TARGET: Activate 22 high-value users"
echo "POTENTIAL REVENUE: RMB 19,197"
echo "=========================================="
#!/bin/bash
# 丙大山 · 全自动推广系统状态检查脚本
export PATH=/usr/local/nodejs/bin:/root/.local/bin:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

echo "=========================================="
echo "BINGDASHAN AUTO PROMO SYSTEM - STATUS"
echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

echo ""
echo "[1] Node.js & Python Versions"
node --version 2>/dev/null || echo "Node.js not found"
python3 --version 2>/dev/null || echo "Python3 not found"
/root/.local/bin/uv python list 2>/dev/null | /usr/bin/head -5 || echo "uv not configured"

echo ""
echo "[2] Project Status"
for dir in auto-xhs zhihu-automation-skill WeMediaCrawler humanized-social-publisher; do
    if [ -d "/opt/$dir" ]; then
        echo "  ✓ $dir exists"
    else
        echo "  ✗ $dir MISSING"
    fi
done

echo ""
echo "[3] Browser Engines"
ls /root/.cache/ms-playwright/ 2>/dev/null && echo "  ✓ Playwright browsers installed" || echo "  ✗ No playwright browsers"

echo ""
echo "[4] Business Data"
python3 << 'PYEOF'
import json
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)
orders = db.get('orders', [])
paid = [o for o in orders if o.get('paid')]
pending = [o for o in orders if not o.get('paid')]
print(f"Total Orders: {len(orders)}")
print(f"Paid: {len(paid)} (RMB{sum(o.get('amount',0) for o in paid):.2f})")
print(f"Pending: {len(pending)} (RMB{sum(o.get('amount',0) for o in pending):.2f})")
PYEOF

echo ""
echo "[5] Content Generated"
if [ -d "/tmp/promo_output_v4" ]; then
    ls /tmp/promo_output_v4/*.json 2>/dev/null | while read f; do
        echo "  ✓ $(basename $f)"
    done
else
    echo "  ✗ Content directory missing"
fi

echo ""
echo "=========================================="
echo "NEXT STEPS:"
echo "=========================================="
echo ""
echo "1. Login Xiaohongshu (One-time QR scan):"
echo "   ssh aliyun && cd /opt/auto-xhs && python3 core/login.py"
echo ""
echo "2. First publish (semi-auto mode):"
echo "   python3 core/publish.py --mode semi"
echo ""
echo "3. Check Zhihu hot topics:"
echo "   cd /opt/zhihu-automation-skill && node zhihu.js hot-list"
echo ""
echo "4. View generated content:"
echo "   cat /tmp/promo_output_v4/xiaohongshu_content.json"
echo ""
echo "=========================================="
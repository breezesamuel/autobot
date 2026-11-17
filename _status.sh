#!/bin/bash
export PATH=/usr/local/nodejs/bin:/root/.local/bin:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

echo "=== BingDashan Auto Promo Status ==="
echo ""
echo "[Node.js]" && node --version 2>/dev/null || echo "not found"
echo "[Python3]" && python3 --version 2>/dev/null || echo "not found"
echo "[uv Python]" && /root/.local/bin/uv python list 2>/dev/null | /usr/bin/head -3 || echo "not found"
echo ""
echo "[Projects]"
for d in auto-xhs zhihu-automation-skill WeMediaCrawler humanized-social-publisher; do
    [ -d "/opt/$d" ] && echo "  OK: $d" || echo "  MISSING: $d"
done
echo ""
echo "[Playwright]"
[ -d "/root/.cache/ms-playwright" ] && echo "  OK: browsers installed" || echo "  MISSING"
echo ""
echo "[Data]"
python3 -c "import json; db=json.load(open('/opt/bingdashan/data/db.json')); orders=db['orders']; paid=[o for o in orders if o.get('paid')]; pending=[o for o in orders if not o.get('paid')]; print(f'Orders:{len(orders)} Paid:{len(paid)} Pending:{len(pending)}')"
echo ""
echo "[Content]"
[ -d "/tmp/promo_output_v4" ] && ls /tmp/promo_output_v4/ 2>/dev/null || echo "not generated"
echo ""
echo "NEXT:"
echo "1. ssh aliyun && cd /opt/auto-xhs && python3 core/login.py"
echo "2. python3 core/publish.py --mode semi"
echo "3. cd /opt/zhihu-automation-skill && node zhihu.js hot-list"
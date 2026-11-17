#!/bin/bash
# BingDashan Auto-Promo Final System Configuration
export PATH=/root/.local/bin:/usr/local/nodejs/bin:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

echo "=========================================="
echo "BINGDASHAN AUTO PROMO SYSTEM - FINAL SETUP"
echo "=========================================="
echo ""

# Create content directory structure
mkdir -p /opt/bingdashan/content/{xiaohongshu,zhihu,github,twitter}
mkdir -p /opt/bingdashan/logs

# Copy generated content
cp /tmp/promo_output_v4/*.json /opt/bingdashan/content/ 2>/dev/null || true

# Create main automation script
cat > /opt/bingdashan/run_promo.sh << 'PROMOSCRIPT'
#!/bin/bash
export PATH=/root/.local/bin:/usr/local/nodejs/bin:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin
cd /opt/bingdashan

echo "=== BingDashan Auto Promo Runner ==="
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"

# Check data
python3 << 'PYCHECK'
import json
with open('/opt/bingdashan/data/db.json') as f:
    db = json.load(f)
orders = db['orders']
paid = [o for o in orders if o.get('paid')]
pending = [o for o in orders if not o.get('paid')]
print(f"Orders: {len(orders)} | Paid: {len(paid)} (¥{sum(o.get('amount',0) for o in paid):.2f}) | Pending: {len(pending)} (¥{sum(o.get('amount',0) for o in pending):.2f})")
PYCHECK

echo ""
echo "Available Automation:"
echo "  1. Xiaohongshu: cd /opt/auto-xhs && python3 core/publish.py --mode semi"
echo "  2. Zhihu: cd /opt/zhihu-automation-skill && node zhihu.js hot-list"
echo "  3. Content Pilot: cd /opt/content-pilot && source .venv/bin/activate && content-pilot gui"
echo "  4. WeMediaCrawler: cd /opt/WeMediaCrawler && uv run python main.py --help"
echo ""
echo "Quick Actions:"
echo "  ssh aliyun && cd /opt/auto-xhs && python3 core/login.py  # Login"
echo "  ssh aliyun && cd /opt/auto-xhs && python3 core/publish.py --mode semi  # Publish"
echo ""
echo "=========================================="
PROMOSCRIPT

chmod +x /opt/bingdashan/run_promo.sh

# Create cron job setup
cat > /opt/bingdashan/cron_setup.sh << 'CRONSCRIPT'
#!/bin/bash
# Add to crontab: crontab -e
# Add this line:
# */30 * * * * /opt/bingdashan/run_promo.sh >> /var/log/bingdashan_promo.log 2>&1
echo "Cron setup instructions:"
echo "1. Run: crontab -e"
echo "2. Add: */30 * * * * /opt/bingdashan/run_promo.sh >> /var/log/bingdashan_promo.log 2>&1"
echo "3. Save and exit"
CRONSCRIPT

chmod +x /opt/bingdashan/cron_setup.sh

# Summary
echo "✓ Content directory created: /opt/bingdashan/content/"
echo "✓ Main runner script created: /opt/bingdashan/run_promo.sh"
echo "✓ Cron setup script created: /opt/bingdashan/cron_setup.sh"
echo ""
echo "All systems ready!"
echo "Run: /opt/bingdashan/run_promo.sh"
echo "=========================================="
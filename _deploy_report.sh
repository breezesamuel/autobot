#!/bin/sh
# 完整的部署检查脚本
export PATH=/usr/local/nodejs/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

echo "=========================================="
echo "丙大山 · 自动化推广系统 - 完整状态报告"
echo "=========================================="

echo ""
echo "[系统信息]"
hostname
uname -a

echo ""
echo "[Node.js]"
node --version
npm --version

echo ""
echo "[Python]"
python3 --version 2>/dev/null || echo "Python3 not found"

echo ""
echo "[ffmpeg]"
ffmpeg -version 2>/dev/null | /usr/bin/head -1 || echo "ffmpeg not installed"

echo ""
echo "[Playwright]"
ls /root/.cache/ms-playwright/ 2>/dev/null || echo "no playwright cache"
ls /opt/auto-xhs/node_modules/playwright 2>/dev/null && echo "playwright installed" || echo "playwright not in auto-xhs"
ls /opt/zhihu-automation-skill/node_modules/playwright 2>/dev/null && echo "zhihu playwright installed" || echo "zhihu no playwright"

echo ""
echo "[项目目录]"
ls -la /opt/auto-xhs/ 2>/dev/null | /usr/bin/wc -l
ls -la /opt/zhihu-automation-skill/ 2>/dev/null | /usr/bin/wc -l
ls -la /opt/auto-hongmyungbo/ 2>/dev/null | /usr/bin/wc -l

echo ""
echo "[配置文件]"
test -f /opt/auto-xhs/config.yaml && echo "auto-xhs config: OK" || echo "auto-xhs config: MISSING"
test -f /opt/zhihu-automation-skill/.env && echo "zhihu env: OK" || echo "zhihu env: MISSING"

echo ""
echo "[业务数据]"
python3 - << 'PYEOF'
import json
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)
orders = db.get('orders', [])
paid = [o for o in orders if o.get('paid')]
pending = [o for o in orders if not o.get('paid')]
print(f"总订单: {len(orders)}")
print(f"已支付: {len(paid)} (¥{sum(o.get('amount',0) for o in paid):.2f})")
print(f"待支付: {len(pending)} (¥{sum(o.get('amount',0) for o in pending):.2f})")
PYEOF

echo ""
echo "[服务状态]"
curl -s http://127.0.0.1:8794/api/health 2>/dev/null || echo "服务未运行"

echo ""
echo "=========================================="
echo "下一步操作指南"
echo "=========================================="
echo ""
echo "【小红书自动化】"
echo "  cd /opt/auto-xhs"
echo "  python3 core/pick_topic.py          # AI选题"
echo "  python3 core/write_script.py         # 生成脚本"  
echo "  python3 core/make_video.py           # 制作视频"
echo "  python3 core/publish.py --mode semi  # 半自动发布"
echo ""
echo "【知乎自动化】"
echo "  cd /opt/zhihu-automation-skill"
echo "  node zhihu.js setup                  # 扫码登录"
echo "  node zhihu.js hot-list               # 查看热榜"
echo "  node zhihu.js search '量化回测'      # 搜索问题"
echo "  node zhihu.js answer <问题ID>        # 回答问题"
echo ""
echo "【内容生成】"
echo "  python3 /tmp/generate_content.py     # 生成所有平台文案"
echo ""
echo "=========================================="

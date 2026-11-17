#!/bin/bash
# 自动化推广系统部署脚本
export PATH=/usr/local/nodejs/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

echo "=========================================="
echo "丙大山 · 自动化推广系统部署"
echo "=========================================="

# 检查Node.js
echo ""
echo "[1/6] 检查Node.js环境..."
node --version
npm --version

# 检查auto-xhs
echo ""
echo "[2/6] 检查auto-xhs..."
cd /opt/auto-xhs
if [ -d "node_modules/playwright" ]; then
    echo "✓ playwright已安装"
else
    echo "✗ playwright未安装，正在安装..."
    npm install playwright 2>&1
fi

# 检查zhihu-automation
echo ""
echo "[3/6] 检查知乎自动化..."
cd /opt/zhihu-automation-skill
if [ -f ".env" ]; then
    echo "✓ 知乎账号已配置"
else
    echo "⚠ 知乎账号未配置，需要运行: node zhihu.js setup"
fi

# 检查ffmpeg
echo ""
echo "[4/6] 检查ffmpeg..."
if command -v ffmpeg &>/dev/null; then
    echo "✓ ffmpeg已安装: $(ffmpeg -version | /usr/bin/head -1)"
else
    echo "✗ ffmpeg未安装（视频功能需要）"
fi

# 检查数据库
echo ""
echo "[5/6] 检查业务数据..."
python3 << 'PYEOF'
import json
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)
orders = db.get('orders', [])
paid = [o for o in orders if o.get('paid')]
pending = [o for o in orders if not o.get('paid')]
print(f"总订单: {len(orders)} | 已支付: {len(paid)} (¥{sum(o.get('amount',0) for o in paid):.2f})")
print(f"待支付: {len(pending)} (¥{sum(o.get('amount',0) for o in pending):.2f})")
PYEOF

# 生成推广内容
echo ""
echo "[6/6] 生成推广内容..."
python3 /tmp/generate_content.py 2>/dev/null || python3 /opt/bingdashan/scripts/ops/generate_promo.py 2>/dev/null || echo "⚠ 内容生成脚本需要手动运行"

echo ""
echo "=========================================="
echo "部署完成！下一步操作："
echo "=========================================="
echo ""
echo "【小红书发布】"
echo "  cd /opt/auto-xhs"
echo "  python3 core/login.py        # 扫码登录"
echo "  python3 core/publish.py --mode semi  # 半自动发布"
echo ""
echo "【知乎回答】"
echo "  cd /opt/zhihu-automation-skill"
echo "  node zhihu.js setup          # 首次配置"
echo "  node zhihu.js hot-list       # 查看热榜"
echo "  node zhihu.js answer --help  # 回答问题"
echo ""
echo "【查看状态】"
echo "  curl http://127.0.0.1:8794/api/health"
echo "=========================================="
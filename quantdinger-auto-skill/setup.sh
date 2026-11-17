#!/bin/bash
# quantdinger-auto-skill 安装 & 快速启动脚本

set -e
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="$PROJECT_ROOT/quantdinger-auto-skill"

echo "=== QuantDinger Auto-Skill Setup ==="
echo "Project: $PROJECT_ROOT"
echo "Skill:   $SKILL_DIR"
echo ""

# ── Step 1: Python 环境检查 ─────────────────────────────────────────────────────
echo "[1/5] 检查 Python 环境..."
python3 --version || python --version
pip install playwright 2>/dev/null || echo "  (playwright optional, use system browser tools for now)"

# ── Step 2: 密钥配置 ────────────────────────────────────────────────────────────
ENV_FILE="$SKILL_DIR/.env.example"
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'EOF'
# 邮件通知（丙大山运营邮箱）
SMTP_USER=your@qq.com
SMTP_PASS=your_smtp_password_or_auth_code

# 企业微信机器人 Webhook（收款/提交结果推送）
WECHAT_WORK_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY

# GitHub Token（用于 GitHub API 和 make.fun repo 操作）
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# make.fun Solana 私钥路径（JSON 格式）
MAKEFUN_KEYPAIR=/path/to/makefun-keypair.json

# QuantDinger MCP Token（连接交易系统）
QUANTDINGER_AGENT_TOKEN=qd_agent_xxx
QUANTDINGER_BASE_URL=http://localhost:8888
EOF
    echo "  ✓ .env.example created — copy to .env and fill in real values"
fi

# ── Step 3: 运行测试套件 ────────────────────────────────────────────────────────
echo ""
echo "[3/5] 运行测试套件..."
cd "$SKILL_DIR"
python test_all.py

# ── Step 4: 生成收款消息包（演示） ─────────────────────────────────────────────
echo ""
echo "[4/5] 生成收款消息包（演示，billing_dir 需指向实际服务器路径）..."
SERVER_BILLING="/opt/bingdashan/data/billing"
if [ -d "$SERVER_BILLING" ]; then
    ssh aliyun "python3 $SKILL_DIR/main.py billing --billing-dir $SERVER_BILLING" \
        || echo "  ⚠ SSH to aliyun failed, skipping live billing scan"
else
    echo "  ℹ Billing dir not found at $SERVER_BILLING — skip live scan"
fi

# ── Step 5: CLI 帮助 ───────────────────────────────────────────────────────────
echo ""
echo "[5/5] CLI 命令速查:"
echo "  python main.py health                          # 系统健康检查"
echo "  python main.py billing --billing-dir <path>    # 生成收款消息包"
echo "  python main.py makefun --action quota          # 查看 make.fun quota"
echo "  python main.py github --action repos           # 列出 GitHub repos"
echo "  python main.py fiverr --action generate        # 生成所有 Fiverr Gig 文案"
echo "  python main.py workflow                        # 执行自动收款工作流"
echo ""
echo "=== Setup complete! ==="

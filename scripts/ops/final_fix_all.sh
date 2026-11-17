#!/bin/bash
# 丙大山 · 完整修复脚本 (一键执行版)
# 生成时间: 2026-11-15
# 用途: SSH恢复后直接运行此脚本完成所有修复

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    丙大山 · 系统修复                          ║"
echo "║                   Depth Mining v5 Final Fix                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1: 检查Python3
echo -e "${BLUE}[1/8]${NC} 检查Python3..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3未安装${NC}"
    exit 1
fi
PYTHON=$(command -v python3)
echo -e "${GREEN}✅ Python3: $($PYTHON --version)${NC}"
echo ""

# Step 2: 创建目录结构
echo -e "${BLUE}[2/8]${NC} 创建必要目录..."
mkdir -p /www/wwwroot/tools-cn.highkingflower.com/api
mkdir -p /www/wwwroot/tools-cn.highkingflower.com/lib
mkdir -p /opt/bingdashan/data/{billing,runtime,backups,outreach_autogen}
mkdir -p /var/log/bingdashan
echo -e "${GREEN}✅ 目录创建完成${NC}"
echo ""

# Step 3: 检查并创建.env
echo -e "${BLUE}[3/8]${NC} 检查环境配置..."
ENV_FILE="/opt/bingdashan/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  .env不存在，创建模板...${NC}"
    cat > "$ENV_FILE" << 'ENVEOF'
# 丙大山 · 环境配置 (必须填入真实值)
ALIPAY_APP_ID=your_app_id_here
ALIPAY_GATEWAY=https://openapi.alipay.com/gateway.do
ALIPAY_SIGN_TYPE=RSA2
ALIPAY_PUBLIC_KEY=your_public_key_here
ALIPAY_PRIVATE_KEY=your_private_key_here

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_key_here

KV_REST_API_URL=https://your-kv.upstash.io
KV_REST_API_TOKEN=your_token_here

SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=460123249@qq.com
SMTP_PASS=your_email_password_here

ADMIN_SECRET=your_admin_secret_here
AUTOOPS_SECRET=your_autoops_secret_here

ALERT_EMAIL=460123249@qq.com

OVERFIT_PRICE_YUAN=39
OVERFIT_PRICE_COIN=400
SCAN_PRICE_YUAN=99
SCAN_PRICE_COIN=1000
MINUTE_PRICE_YUAN=99
MINUTE_PRICE_COIN=1000
ENVEOF
    echo -e "${GREEN}✅ .env模板已创建${NC}"
    echo -e "${YELLOW}⚠️  请编辑 $ENV_FILE 填入真实配置!${NC}"
else
    echo -e "${GREEN}✅ .env已存在${NC}"
fi
echo ""

# Step 4: 修复SSL密钥权限
echo -e "${BLUE}[4/8]${NC} 修复SSL密钥权限..."
for keyfile in /etc/bingdashan-cn/alipay_priv.pem /etc/bingdashan-cn/alipay_pub.pem; do
    if [ -f "$keyfile" ]; then
        chmod 600 "$keyfile"
        echo -e "${GREEN}✅ $keyfile (${NC}600${GREEN})${NC}"
    else
        echo -e "${YELLOW}⚠️  文件不存在: $keyfile${NC}"
    fi
done
echo ""

# Step 5: 检查支付网关
echo -e "${BLUE}[5/8]${NC} 检查支付网关..."
ALIPAY_JS="/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js"
if [ ! -f "$ALIPAY_JS" ]; then
    echo -e "${YELLOW}⚠️  alipay.js不存在，需要创建...${NC}"
    echo -e "${YELLOW}   请运行: python3 /opt/bingdashan/scripts/ops/create_alipay_js.py${NC}"
else
    echo -e "${GREEN}✅ alipay.js已存在${NC}"
fi
echo ""

# Step 6: 检查模块安全
echo -e "${BLUE}[6/8]${NC} 检查模块安全..."
LIB_DIR="/www/wwwroot/tools-cn.highkingflower.com/lib"
if [ -d "$LIB_DIR" ]; then
    MODULE_COUNT=$(ls -1 "$LIB_DIR"/*.js 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ 找到 $MODULE_COUNT 个模块${NC}"
    echo -e "${YELLOW}   请运行: python3 /opt/bingdashan/scripts/ops/harden_subscription_wall.py${NC}"
else
    echo -e "${YELLOW}⚠️  lib目录不存在${NC}"
fi
echo ""

# Step 7: 重启服务
echo -e "${BLUE}[7/8]${NC} 重启服务..."
systemctl daemon-reload 2>/dev/null
systemctl restart bingdashan-cn 2>/dev/null
sleep 2
if systemctl is-active --quiet bingdashan-cn; then
    echo -e "${GREEN}✅ 服务运行正常${NC}"
else
    echo -e "${YELLOW}⚠️  服务启动可能有问题，检查日志:${NC}"
    journalctl -u bingdashan-cn --no-pager -n 10 2>/dev/null || echo "无法获取日志"
fi
echo ""

# Step 8: 健康检查
echo -e "${BLUE}[8/8]${NC} 健康检查..."
HEALTH=$(curl -s http://127.0.0.1:8794/api/health 2>/dev/null || echo '{"error":"unavailable"}')
echo "Health: $HEALTH"
echo ""

# 完成
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                     修复完成                                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "下一步操作:"
echo "  1. 编辑 /opt/bingdashan/.env 填入真实配置"
echo "  2. 运行: python3 /opt/bingdashan/scripts/ops/create_alipay_js.py"
echo "  3. 运行: python3 /opt/bingdashan/scripts/ops/harden_subscription_wall.py"
echo "  4. 测试支付: curl 'http://127.0.0.1:8794/api/pay?plan=m&ref=test'"
echo ""
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"

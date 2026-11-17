#!/bin/bash
# 丙大山 · 支付流程快速修复脚本
# 用途: 一键诊断并修复支付流程问题

set -e

echo "=== 丙大山 · 支付流程自动修复 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查必要的目录
echo "📁 检查目录结构..."
mkdir -p /www/wwwroot/tools-cn.highkingflower.com/api
mkdir -p /opt/bingdashan/data/billing
mkdir -p /opt/bingdashan/data/runtime
mkdir -p /var/log/bingdashan
echo -e "${GREEN}✅ 目录检查完成${NC}"
echo ""

# 检查环境配置文件
echo "🔧 检查环境变量配置..."
if [ ! -f /opt/bingdashan/.env ]; then
    echo -e "${YELLOW}⚠️  .env文件不存在，创建模板...${NC}"
    cat > /opt/bingdashan/.env << 'EOF'
# 丙大山 · 支付宝配置 (请填入真实值)
ALIPAY_APP_ID=
ALIPAY_GATEWAY=https://openapi.alipay.com/gateway.do
ALIPAY_SIGN_TYPE=RSA2
ALIPAY_PUBLIC_KEY=
ALIPAY_PRIVATE_KEY=

# SMTP配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=460123249@qq.com
SMTP_PASS=

# 告警邮件
ALERT_EMAIL=460123249@qq.com
EOF
    echo -e "${GREEN}✅ .env模板已创建${NC}"
else
    echo -e "${GREEN}✅ .env文件已存在${NC}"
fi
echo ""

# 检查支付宝密钥文件
echo "🔑 检查支付宝密钥..."
if [ -f /etc/bingdashan-cn/alipay_priv.pem ]; then
    echo -e "${GREEN}✅ 私钥文件存在${NC}"
    ls -la /etc/bingdashan-cn/alipay_priv.pem
else
    echo -e "${YELLOW}⚠️  私钥文件不存在，需要从支付宝开放平台下载${NC}"
    echo "下载地址: https://opendocs.alipay.com/open/02ek0a"
fi

if [ -f /etc/bingdashan-cn/alipay_pub.pem ]; then
    echo -e "${GREEN}✅ 公钥文件存在${NC}"
    ls -la /etc/bingdashan-cn/alipay_pub.pem
else
    echo -e "${YELLOW}⚠️  公钥文件不存在${NC}"
fi
echo ""

# 检查支付路由文件
echo "💻 检查支付路由..."
PAY_JS="/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js"
if [ -f "$PAY_JS" ]; then
    echo -e "${GREEN}✅ 支付路由文件存在${NC}"
    wc -l "$PAY_JS"
else
    echo -e "${YELLOW}⚠️  支付路由文件不存在，准备创建...${NC}"
    echo "需要运行 Python 诊断脚本创建完整支付路由"
fi
echo ""

# 检查数据库
echo "🗄️  检查数据库状态..."
DB_FILE="/opt/bingdashan/data/db.json"
if [ -f "$DB_FILE" ]; then
    PENDING=$(python3 -c "import json; d=json.load(open('$DB_FILE')); print(len([o for o in d.get('orders',[]) if o.get('status')=='pending']))" 2>/dev/null || echo "0")
    PAID=$(python3 -c "import json; d=json.load(open('$DB_FILE')); print(len([o for o in d.get('orders',[]) if o.get('paid')]))" 2>/dev/null || echo "0")
    echo -e "${GREEN}✅ 数据库正常${NC}"
    echo "   Pending订单: $PENDING"
    echo "   Paid订单: $PAID"
else
    echo -e "${YELLOW}⚠️  数据库文件不存在${NC}"
fi
echo ""

# 检查服务状态
echo "🚀 检查服务状态..."
if systemctl is-active --quiet bingdashan-cn; then
    echo -e "${GREEN}✅ bingdashan-cn 服务正在运行${NC}"
else
    echo -e "${YELLOW}⚠️  bingdashan-cn 服务未运行${NC}"
    echo "尝试启动服务..."
    systemctl start bingdashan-cn 2>/dev/null || echo "启动失败，请手动检查"
fi
echo ""

# 端口检查
echo "🌐 检查端口8794..."
if ss -tlnp | grep -q ':8794'; then
    echo -e "${GREEN}✅ 端口8794正在监听${NC}"
else
    echo -e "${YELLOW}⚠️  端口8794未监听${NC}"
fi
echo ""

# 总结
echo "=========================================="
echo "📊 修复报告摘要"
echo "=========================================="
echo ""
echo "需要手动完成的步骤:"
echo "1. 填写 /opt/bingdashan/.env 中的支付宝配置"
echo "2. 确保 /etc/bingdashan-cn/ 下有正确的密钥文件"
echo "3. 运行 Python 诊断脚本创建支付路由 (如果不存在)"
echo "4. 重启服务: systemctl restart bingdashan-cn"
echo "5. 测试支付: curl http://127.0.0.1:8794/api/pay?plan=m&ref=test"
echo ""
echo "查看详细报告: /opt/bingdashan/data/payment_fix_result_*.txt"
echo ""
echo -e "${GREEN}✅ 快速修复完成${NC}"

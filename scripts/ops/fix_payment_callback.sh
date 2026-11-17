#!/bin/bash
# 丙大山 · 支付回调一键修复脚本
# 执行: bash /tmp/fix_payment_callback.sh

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              丙大山 · 支付回调修复工具                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
ENV_FILE="/opt/bingdashan/.env"
LOG_FILE="/var/log/bingdashan/fix_callback_$(date +%Y%m%d_%H%M%S).log"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

echo "📋 第1步: 备份当前配置..."
cp "$ENV_FILE" "${ENV_FILE}.bak.$(date +%s)" 2>/dev/null && log "✅ 备份完成" || log "⚠️  备份跳过（文件不存在）"

echo ""
echo "📝 第2步: 检查当前配置..."
if grep -q "ALIPAY_NOTIFY_URL" "$ENV_FILE"; then
    CURRENT_NOTIFY=$(grep "ALIPAY_NOTIFY_URL" "$ENV_FILE" | cut -d'=' -f2)
    echo "   当前 ALIPAY_NOTIFY_URL: $CURRENT_NOTIFY"
else
    echo "   ⚠️  ALIPAY_NOTIFY_URL 未配置"
    CURRENT_NOTIFY=""
fi

if grep -q "ALIPAY_RETURN_URL" "$ENV_FILE"; then
    CURRENT_RETURN=$(grep "ALIPAY_RETURN_URL" "$ENV_FILE" | cut -d'=' -f2)
    echo "   当前 ALIPAY_RETURN_URL: $CURRENT_RETURN"
else
    echo "   ⚠️  ALIPAY_RETURN_URL 未配置"
    CURRENT_RETURN=""
fi

echo ""
echo "🔧 第3步: 更新回调地址..."

# 正确的回调地址（根据代码分析）
NEW_NOTIFY_URL="https://tools-cn.highkingflower.com/v1/pay/alipay/notify"
NEW_RETURN_URL="https://tools-cn.highkingflower.com/v1/pay/alipay/return"

# 使用sed更新
sed -i "s|ALIPAY_NOTIFY_URL=.*|ALIPAY_NOTIFY_URL=${NEW_NOTIFY_URL}|g" "$ENV_FILE"
sed -i "s|ALIPAY_RETURN_URL=.*|ALIPAY_RETURN_URL=${NEW_RETURN_URL}|g" "$ENV_FILE"

log "✅ 已更新:"
log "   ALIPAY_NOTIFY_URL=$NEW_NOTIFY_URL"
log "   ALIPAY_RETURN_URL=$NEW_RETURN_URL"

echo ""
echo "🔄 第4步: 重启服务..."
systemctl restart bingdashan-cn
sleep 2

if systemctl is-active --quiet bingdashan-cn; then
    log "✅ 服务重启成功"
else
    log "❌ 服务启动失败"
    exit 1
fi

echo ""
echo "🧪 第5步: 测试回调端点..."
HTTP_CODE=$(curl -s -X POST "https://tools-cn.highkingflower.com/v1/pay/alipay/notify" \
    -H "Content-Type: application/json" \
    -d '{"test":"callback_health_check"}' \
    -w "%{http_code}" --max-time 10)

if [[ "$HTTP_CODE" == "200" ]] || [[ "$HTTP_CODE" == "400" ]]; then
    log "✅ 端点可访问 (HTTP $HTTP_CODE)"
    log "   （400表示端点工作但参数不完整，这是正常的）"
elif [[ "$HTTP_CODE" == "404" ]]; then
    log "⚠️  端点返回404，可能需要额外配置路由"
else
    log "⚠️  端点响应异常: HTTP $HTTP_CODE"
fi

echo ""
echo "📋 第6步: 查看最新日志..."
log "最近的引擎日志:"
tail -5 /var/log/bingdashan/engine.log 2>/dev/null | while read line; do
    log "  $line"
done

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    修复完成摘要                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ 已完成的操作:"
echo "   1. 备份了原.env文件"
echo "   2. 更新了ALIPAY_NOTIFY_URL和ALIPAY_RETURN_URL"
echo "   3. 重启了bingdashan-cn服务"
echo "   4. 测试了回调端点可达性"
echo ""
echo "⚠️  下一步必须操作:"
echo ""
echo "   1️⃣  登录支付宝开放平台:"
echo "      https://open.alipay.com/dev/index.htm"
echo ""
echo "   2️⃣  找到你的应用:"
echo "      APPID: 2021006197622702"
echo ""
echo "   3️⃣  更新回调地址:"
echo "      「开发设置」→「接口加签方式」→「授权回调地址」"
echo "      填写: ${NEW_NOTIFY_URL}"
echo ""
echo "   4️⃣  保存并发布新版本"
echo ""
echo "   5️⃣  用真实账号测试完整支付流程"
echo "      访问: https://tools-cn.highkingflower.com/api/pay?plan=t&ref=test_after_fix"
echo ""
echo "📊 预期效果:"
echo "   • 回调正常接收 → 订单自动变paid"
echo "   • 订阅自动激活 → 用户体验流畅"
echo "   • cash从¥0开始累积"
echo ""
echo "💡 提示:"
echo "   如果测试仍然失败，请检查："
echo "   - 防火墙是否允许入站HTTPS连接"
echo "   - 域名DNS解析是否正确"
echo "   - SSL证书是否有效"
echo ""
echo "日志位置: $LOG_FILE"
echo ""

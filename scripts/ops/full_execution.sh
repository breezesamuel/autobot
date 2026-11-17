#!/bin/bash
# 丙大山 · 完整变现执行脚本
set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              丙大山 · 一键变现执行                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: 服务状态
echo "【Step 1】检查服务状态..."
systemctl is-active bingdashan-cn && echo "✅ 服务运行中" || echo "❌ 服务未运行"
echo ""

# Step 2: 营收状态
echo "【Step 2】检查营收状态..."
grep 'cash=' /var/log/bingdashan/engine.log | tail -1
echo ""

# Step 3: Leads状态
echo "【Step 3】检查leads状态..."
node -e "
const s = require('/opt/bingdashan/core/store');
const d = s.read();
const leads = d.leads || [];
console.log('总线索数:', leads.length);
const high = leads.filter(l => l.signal >= 70);
console.log('高价值(>=70):', high.length, '条');
const p0 = leads.filter(l => l.signal >= 90);
console.log('P0级(>=90):', p0.length, '条');
if (p0.length > 0) {
  console.log('\\nTOP5 P0级线索:');
  p0.slice(0, 5).forEach((l, i) => {
    console.log(\`\${i+1}. \${l.name} (⭐\${l.stars||0}, 信号=\${l.signal}) [\${l.stage}]\`);
  });
}
" 2>/dev/null || echo "无法读取leads数据"
echo ""

# Step 4: 测试支付链接生成
echo "【Step 4】测试支付链接生成..."
curl -s 'http://127.0.0.1:8794/api/pay?plan=t&ref=execution_test' | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if d.get('ok'):
        print('✅ 支付链接生成成功')
        print(f\"订单ID: {d.get('orderId')}\")
        print(f\"金额: ¥{d.get('amount')}\")
        print(f\"支付链接: {d.get('payUrl')[:100]}...\")
    else:
        print('❌ 支付链接生成失败')
except:
    print('解析失败')
" 2>/dev/null || echo "测试失败"
echo ""

# Step 5: 催款消息
echo "【Step 5】催款消息（复制发送到微信/QQ）:"
echo "=================================================="
python3 /tmp/gen_reminders.py 2>/dev/null || cat /opt/bingdashan/data/outreach_messages.txt 2>/dev/null | head -50 || echo "无消息文件"
echo ""

# Step 6: 下一步行动
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    下一步行动                                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 今日必须完成:"
echo "   1. ✅ 已备份并修复回调代码 (已完成)"
echo "   2. ⏸️  重启服务 (如果尚未重启)"
echo "   3. ⏸️  发送13条催款消息 (现在做!)"
echo "   4. ⏸️  联系TOP5高价值线索 (今天做)"
echo ""
echo "💰 预期收入:"
echo "   - Pending转化: ¥700-1000 (发送催款消息后)"
echo "   - 线索转化: ¥67-250/月 (持续触达后)"
echo "   - 首月合计: ¥800-1250"
echo ""
echo "🚀 立即行动:"
echo "   1. 复制上面的催款消息发送到微信/QQ"
echo "   2. 在GitHub上给TOP5线索发Issue或私信"
echo "   3. 记录发送时间和回复"
echo ""

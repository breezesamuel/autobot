#!/bin/bash
# 丙大山 · 线索跟进流程自动化脚本
set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              丙大山 · 线索跟进自动化流程                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: 显示当前状态
echo "【Step 1】检查线索状态..."
python3 /tmp/dash.py 2>/dev/null || echo "仪表盘不可用，使用备用方式..."

# Step 2: 生成触达消息
echo ""
echo "【Step 2】生成个性化触达消息..."
cat > /tmp/generate_messages.js << 'JSEOF'
const store = require('/opt/bingdashan/core/store');
const fs = require('fs');

async function main() {
  const db = store.read();
  const leads = db.leads || [];
  
  // 筛选高价值线索
  const highValue = leads.filter(l => l.signal >= 70)
    .sort((a, b) => b.signal - a.signal)
    .slice(0, 20);
  
  const messages = [];
  
  for (const lead of highValue) {
    const stars = lead.stars || 0;
    const name = lead.name || '';
    const company = name.split('/')[0];
    const signal = lead.signal || 0;
    
    let message = '';
    
    if (stars >= 10000) {
      message = `Hi ${company},\n\n看到你的${name}项目，⭐${stars}真的很棒！我们也在做AI量化回测工具（丙大山），首周只要¥1体验。\n\n如果感兴趣可以试试：https://tools-cn.highkingflower.com/api/pay?plan=t&ref=${encodeURIComponent(name)}\n\n祝项目越来越火！`;
    } else if (stars >= 1000) {
      message = `Hello! 👋\n\n发现你的${name}项目，star ${stars}很棒！\n\n我们在做一个AI辅助量化回测工具，能自动检测过拟合、生成完整报告。可能对你们的项目有帮助。\n\n欢迎交流：https://tools-cn.highkingflower.com`;
    } else {
      message = `Hey ${company}!\n\n刚看到${name}，很有创意！\n\n分享一个我们的AI量化工具，可能对你们的研究有用。首周¥1体验：https://tools-cn.highkingflower.com/api/pay?plan=t\n\n保持联系！🚀`;
    }
    
    messages.push({
      repo: name,
      company: company,
      stars: stars,
      signal: signal,
      message: message,
      priority: signal >= 90 ? 'P0' : signal >= 80 ? 'P1' : 'P2'
    });
  }
  
  // 保存到文件
  fs.writeFileSync('/tmp/outreach_messages.json', JSON.stringify(messages, null, 2));
  
  console.log(`✅ 生成了 ${messages.length} 条个性化触达消息`);
  console.log(`   P0级: ${messages.filter(m => m.priority === 'P0').length}条`);
  console.log(`   P1级: ${messages.filter(m => m.priority === 'P1').length}条`);
  console.log(`   P2级: ${messages.filter(m => m.priority === 'P2').length}条`);
  console.log(`\n💾 已保存到: /tmp/outreach_messages.json`);
}

main().catch(e => console.error('错误:', e.message));
JSEOF

node /tmp/generate_messages.js

# Step 3: 显示TOP5消息
echo ""
echo "【Step 3】TOP5触达消息预览:"
python3 << 'PYEOF'
import json
try:
    with open('/tmp/outreach_messages.json', 'r') as f:
        messages = json.load(f)
    
    for i, m in enumerate(messages[:5], 1):
        print(f"\n{'='*70}")
        print(f"【{m['priority']}】#{i} {m['repo']}")
        print(f"公司: {m['company']} | ⭐{m['stars']} | 信号: {m['signal']}")
        print(f"{'='*70}")
        print(m['message'])
except Exception as e:
    print(f"Error: {e}")
PYEOF

# Step 4: 创建一键发送脚本
echo ""
echo "【Step 4】创建发送脚本..."
cat > /tmp/send_messages.sh << 'SHEOF'
#!/bin/bash
# 一键发送所有触达消息
MESSAGES_FILE="/tmp/outreach_messages.json"

if [ ! -f "$MESSAGES_FILE" ]; then
    echo "❌ 找不到消息文件"
    exit 1
fi

echo "📧 准备发送消息..."
echo ""

python3 << 'PYEOF'
import json

with open('/tmp/outreach_messages.json', 'r') as f:
    messages = json.load(f)

print(f"共 {len(messages)} 条消息待发送:\n")

for i, m in enumerate(messages, 1):
    print(f"【{m['priority']}】#{i} {m['repo']}")
    print(f"目标: {m['company']}")
    print(f"消息:")
    print(m['message'])
    print("-" * 70)
PYEOF

echo ""
echo "💡 提示：复制上述消息到GitHub Issue/PR评论/私信发送"
SHEOF

chmod +x /tmp/send_messages.sh
echo "✅ 发送脚本已创建: /tmp/send_messages.sh"

# Step 5: 设置定时任务
echo ""
echo "【Step 5】设置定时获客任务..."
(crontab -l 2>/dev/null | grep -v "activate_leadgen") | crontab -
(crontab -l 2>/dev/null; echo "0 9 * * * node /tmp/activate_leadgen.js >> /var/log/bingdashan/leadgen.log 2>&1") | crontab -
echo "✅ 已设置每天9点自动补充线索"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    流程完成                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 下一步行动:"
echo "   1. 运行 bash /tmp/send_messages.sh 查看消息"
echo "   2. 复制P0级消息到GitHub私信/Issue"
echo "   3. 跟踪回复并标记转化状态"
echo "   4. 每天运行 node /tmp/activate_leadgen.js 补充新线索"
echo ""

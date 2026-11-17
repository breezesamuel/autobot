#!/bin/bash
# 丙大山 · 线索变现完整流程

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              丙大山 · 线索变现自动化流程                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: 检查当前状态
echo "【Step 1】检查leads状态..."
python3 << 'PYEOF'
import json
try:
    d=json.load(open('/opt/bingdashan/data/db.json'))
    leads=d.get('leads',[])
    print(f'总线索数: {len(leads)}')
    
    stages={}
    for l in leads:
        s=l.get('stage','?')
        stages[s]=stages.get(s,0)+1
    print(f'阶段分布: {json.dumps(stages, ensure_ascii=False)}')
    
    high=[l for l in leads if l.get('signal',0)>=70]
    p0=[l for l in leads if l.get('signal',0)>=90]
    print(f'\n高价值(≥70): {len(high)}条')
    print(f'P0级(≥90): {len(p0)}条')
except Exception as e:
    print(f'Error: {e}')
PYEOF

# Step 2: 生成触达消息
echo ""
echo "【Step 2】生成个性化触达消息..."
node /tmp/gen_msg_final.js

# Step 3: 显示消息
echo ""
echo "【Step 3】TOP5触达消息预览:"
python3 << 'PYEOF'
import json
try:
    with open('/tmp/outreach_messages.json', 'r') as f:
        msgs = json.load(f)
    
    for i, m in enumerate(msgs[:5], 1):
        print(f"\n{'='*60}")
        print(f"【{m['priority']}】#{i} {m['repo']}")
        print(f"Stars: {m['stars']} | 信号: {m['signal']}")
        print(f"{'='*60}")
        print(m['message'])
except Exception as e:
    print(f"Error: {e}")
PYEOF

# Step 4: 设置定时任务
echo ""
echo "【Step 4】设置定时获客任务..."
(crontab -l 2>/dev/null | grep -v "activate_leadgen") | crontab -
echo "0 9 * * * node /tmp/activate_v2.js >> /var/log/bingdashan/leadgen.log 2>&1" | crontab -
echo "✅ 已设置每天9点自动补充线索"

# Step 5: 总结
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    流程完成                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 下一步行动:"
echo "   1. 复制上述消息到GitHub Issue/私信发送"
echo "   2. 跟踪回复并标记转化状态"
echo "   3. 每天运行: node /tmp/activate_v2.js"
echo "   4. 每周检查: python3 /tmp/dash.py"
echo ""
echo "💡 提示: P0级线索（信号≥90）优先触达，转化率最高！"
echo ""

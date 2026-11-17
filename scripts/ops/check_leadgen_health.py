import json
from datetime import datetime

def main():
    print("="*70)
    print("丙大山 · 自动获客系统状态报告")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 读取数据
    try:
        with open('/opt/bingdashan/data/db.json', 'r') as f:
            db = json.load(f)
    except Exception as e:
        print(f"❌ 无法读取db.json: {e}")
        return 1
    
    leads = db.get('leads', [])
    print(f"\n📊 Leads总数: {len(leads)}")
    
    # 按阶段统计
    stages = {}
    for l in leads:
        s = l.get('stage', 'unknown')
        stages[s] = stages.get(s, 0) + 1
    
    print("\n📈 阶段分布:")
    for stage, count in sorted(stages.items(), key=lambda x: -x[1]):
        bar = '█' * min(count, 30)
        print(f"  {stage:10s}: {count:3d} {bar}")
    
    # 信号分统计
    signals = [l.get('signal', 0) for l in leads]
    if signals:
        avg_signal = sum(signals) / len(signals)
        high_count = len([s for s in signals if s >= 80])
        med_count = len([s for s in signals if 60 <= s < 80])
        low_count = len([s for s in signals if s < 60])
        
        print(f"\n🎯 线索质量分析:")
        print(f"  平均信号分: {avg_signal:.1f}")
        print(f"  高价值(≥80): {high_count}条")
        print(f"  中价值(60-80): {med_count}条")
        print(f"  低价值(<60): {low_count}条")
    
    # TOP线索
    print(f"\n🔥 TOP10高价值线索:")
    high_leads = sorted(leads, key=lambda x: x.get('signal', 0), reverse=True)[:10]
    for i, l in enumerate(high_leads, 1):
        name = l.get('name', '?')[:40]
        stars = l.get('stars', 0)
        signal = l.get('signal', 0)
        stage = l.get('stage', '?')
        print(f"  {i:2d}. {name:40s} 信号={signal:3d} ⭐{stars:5d} [{stage}]")
    
    # 收入预估
    print(f"\n💰 收入预估:")
    conv_rate = 0.05
    arpu = 167
    high_value = len([l for l in leads if l.get('signal', 0) >= 66])
    expected_customers = high_value * conv_rate
    monthly_revenue = expected_customers * arpu
    
    print(f"  高价值线索(≥66): {high_value}条")
    print(f"  预期转化客户: {expected_customers:.1f}人")
    print(f"  预期月收入: ¥{monthly_revenue:.0f}")
    print(f"  预期年收入: ¥{monthly_revenue*12:.0f}")
    
    # 建议行动
    print(f"\n✅ 建议行动:")
    if high_value > 0:
        print(f"  1. 优先联系 {high_value} 条高价值线索的开发者")
        print(f"  2. 对signal≥80的线索立即私信/Issue互动")
        print(f"  3. 配置GitHub Token提升获客效率")
        print(f"  4. 设置每日定时补充新线索")
    else:
        print("  1. 运行 node /tmp/add_high_value_leads.js 补充线索")
        print("  2. 配置GITHUB_TOKEN环境变量")
    
    print("\n" + "="*70)
    return 0

if __name__ == '__main__':
    exit(main())

import json
from datetime import datetime

def main():
    print("="*70)
    print("丙大山 · 实时线索追踪仪表盘")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        with open('/opt/bingdashan/data/db.json', 'r') as f:
            db = json.load(f)
    except Exception as e:
        print(f"❌ 无法读取数据: {e}")
        return 1
    
    leads = db.get('leads', [])
    total = len(leads)
    
    print(f"\n📊 总体状态:")
    print(f"   总线索数: {total}")
    
    # 按信号分统计
    high = len([l for l in leads if l.get('signal', 0) >= 70])
    p0 = len([l for l in leads if l.get('signal', 0) >= 90])
    
    print(f"   高价值(≥70): {high}条 ({high/total*100:.1f}%)")
    print(f"   P0级(≥90): {p0}条 ({p0/total*100:.1f}%)")
    
    # 按阶段统计
    stages = {}
    for l in leads:
        s = l.get('stage', '?')
        stages[s] = stages.get(s, 0) + 1
    
    print(f"\n📈 阶段分布:")
    for stage, count in sorted(stages.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        bar = '█' * int(pct / 5)
        print(f"   {stage:10s}: {count:3d} ({pct:5.1f}%) {bar}")
    
    # 收入预估
    conv_rate = 0.05
    arpu = 167
    expected_customers = high * conv_rate
    monthly_revenue = expected_customers * arpu
    
    print(f"\n💰 收入预测:")
    print(f"   预期转化客户: {expected_customers:.1f}人")
    print(f"   预期月收入: ¥{monthly_revenue:.0f}")
    print(f"   预期年收入: ¥{monthly_revenue*12:.0f}")
    
    # TOP10列表
    print(f"\n🔥 TOP10高价值线索:")
    top10 = sorted([l for l in leads if l.get('signal', 0) >= 70], 
                   key=lambda x: x.get('signal', 0), reverse=True)[:10]
    
    for i, l in enumerate(top10, 1):
        name = l.get('name', '?')[:45]
        stars = l.get('stars', 0)
        signal = l.get('signal', 0)
        stage = l.get('stage', '?')
        print(f"   {i:2d}. {name:45s} 信号={signal:3d} ⭐{stars:6d} [{stage}]")
    
    # 建议行动
    print(f"\n✅ 建议行动:")
    if p0 > 0:
        print(f"   1. 🔥 立即联系 {p0} 条P0级线索（信号≥90）")
    if high > p0:
        print(f"   2. 📞 本周内触达 {high-p0} 条高价值线索")
    print(f"   3. 🔄 每天运行补充新线索")
    print(f"   4. 📊 每周检查转化率并优化")
    
    print("\n" + "="*70)
    return 0

if __name__ == '__main__':
    exit(main())

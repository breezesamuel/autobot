import json
from datetime import datetime

# 读取数据库
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)

print("="*70)
print("丙大山 · 订单数据深度分析")
print("="*70)

# 分析orders
orders = db.get('orders', [])
print(f"\n📊 订单总数: {len(orders)}")

if len(orders) > 0:
    # 按状态统计
    paid_orders = [o for o in orders if o.get('paid') == True or o.get('status') == 'paid']
    pending_orders = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]
    
    print(f"已支付: {len(paid_orders)} 笔")
    print(f"待支付: {len(pending_orders)} 笔")
    
    # 计算金额
    total_paid = sum(o.get('amount', 0) for o in paid_orders)
    total_pending = sum(o.get('amount', 0) for o in pending_orders)
    
    print(f"\n💰 已收金额: ¥{total_paid:.2f}")
    print(f"💰 待收金额: ¥{total_pending:.2f}")
    print(f"💰 总金额:   ¥{total_paid + total_pending:.2f}")
    
    # 显示待支付订单详情
    if pending_orders:
        print(f"\n📋 待支付订单详情 (前20条):")
        for i, o in enumerate(pending_orders[:20], 1):
            order_id = o.get('id', 'N/A')
            amount = o.get('amount', 0)
            plan = o.get('plan', 'N/A')
            ref = o.get('ref', '')
            created = o.get('createdAt', 0)
            dt = datetime.fromtimestamp(created/1000).strftime('%Y-%m-%d %H:%M') if created else 'N/A'
            print(f"  {i:2d}. {str(order_id)[:20]:20s} ¥{amount:6.2f} {str(plan):10s} {dt}")
        
        if len(pending_orders) > 20:
            print(f"  ... 还有 {len(pending_orders) - 20} 条")

# 分析revenue
revenues = db.get('revenue', [])
print(f"\n📈 营收记录: {len(revenues)} 条")
if revenues:
    total_revenue = sum(r.get('amt', r.get('amount', 0)) for r in revenues if r.get('settled') == True)
    print(f"已结算营收: ¥{total_revenue:.2f}")

# 分析leads
leads = db.get('leads', [])
print(f"\n🎯 Leads数据: {len(leads)} 条")
if leads:
    high_value = [l for l in leads if l.get('signal', 0) >= 70]
    p0 = [l for l in leads if l.get('signal', 0) >= 90]
    print(f"高价值(≥70): {len(high_value)} 条")
    print(f"P0级(≥90): {len(p0)} 条")
    
    # 检查email字段
    with_email = [l for l in leads if l.get('email')]
    print(f"有邮箱: {len(with_email)} 条")

print("\n" + "="*70)

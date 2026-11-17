import json
from datetime import datetime

# 读取数据库
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)

orders = db.get('orders', [])
paid = [o for o in orders if o.get('paid') == True or o.get('status') == 'paid']
pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]

print("="*70)
print(f"丙大山 · 实时收入状态")
print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
print()
print(f"📊 订单统计:")
print(f"   总订单数: {len(orders)}")
print(f"   ✅ 已支付: {len(paid)} 笔")
print(f"   ⏳ 待支付: {len(pending)} 笔")
print()
print(f"💰 金额统计:")
total_paid = sum(o.get('amount', 0) for o in paid)
total_pending = sum(o.get('amount', 0) for o in pending)
print(f"   已收金额: ¥{total_paid:.2f}")
print(f"   待收金额: ¥{total_pending:.2f}")
print(f"   总金额:   ¥{total_paid + total_pending:.2f}")
print()
print("="*70)

if len(paid) > 0:
    print("✅ 已支付订单详情:")
    for i, o in enumerate(paid[:10], 1):
        order_id = o.get('id', '')
        amount = o.get('amount', 0)
        plan = o.get('plan', 't')
        created = o.get('createdAt', 0)
        dt = datetime.fromtimestamp(created/1000).strftime('%m-%d %H:%M') if created else '?'
        print(f"   {i}. {order_id[:20]:20s} ¥{amount:6.2f} {dt}")
    
    if len(paid) > 10:
        print(f"   ... 还有 {len(paid) - 10} 条")
else:
    print("⚠️ 暂无已支付订单")

print()
print("="*70)
print("📋 高价值待支付订单（优先处理）:")
print("="*70)
pending_sorted = sorted(pending, key=lambda x: x.get('amount', 0), reverse=True)
for i, o in enumerate(pending_sorted[:10], 1):
    order_id = o.get('id', '')
    amount = o.get('amount', 0)
    plan = o.get('plan', 't')
    pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref="
    print(f"{i:2d}. ¥{amount:6.2f} | {order_id} | {pay_url}")

print()
print("="*70)
print("🔧 建议操作:")
print("   1. 复制上面的付款链接，发送到客户微信/QQ")
print("   2. 在网站添加促销Banner吸引新访客")
print("   3. 在社交媒体发布推广文案")
print("="*70)

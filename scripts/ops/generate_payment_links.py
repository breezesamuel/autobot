import json
from datetime import datetime

# 读取数据库
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)

orders = db.get('orders', [])
pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]

print("="*70)
print(f"丙大山 · 待收款订单 ({len(pending)}笔，总计¥{sum(o.get('amount',0) for o in pending):,.2f})")
print("="*70)

# 按金额分组统计
by_amount = {}
for o in pending:
    amt = o.get('amount', 0)
    by_amount[amt] = by_amount.get(amt, 0) + 1

print("\n💰 按金额分布:")
for amt in sorted(by_amount.keys(), reverse=True):
    count = by_amount[amt]
    total = amt * count
    print(f"  ¥{amt:6.2f} × {count:3d}笔 = ¥{total:8.2f}")

# 按plan分组
by_plan = {}
for o in pending:
    plan = o.get('plan', 'unknown')
    by_plan[plan] = by_plan.get(plan, 0) + 1

print("\n📦 按套餐分布:")
plan_names = {'t': '首7天体验', 'm': '基础月卡', 'q': '季度卡', 'y': '年卡', 'p': 'Pro版', 'v': 'VIP', 's': '至尊'}
for plan, count in sorted(by_plan.items(), key=lambda x: -x[1]):
    name = plan_names.get(plan, plan)
    amt = next((o.get('amount', 0) for o in pending if o.get('plan') == plan), 0)
    total = amt * count
    print(f"  {name}({plan}): {count:3d}笔 × ¥{amt:.2f} = ¥{total:8.2f}")

# 生成催款消息（前50条）
print("\n📧 催款消息预览（前20条）:")
print("="*70)

for i, o in enumerate(pending[:20], 1):
    order_id = o.get('id', 'N/A')
    amount = o.get('amount', 0)
    plan = o.get('plan', 't')
    ref = o.get('ref', '')
    
    pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
    
    print(f"\n【订单 #{i}】¥{amount:.2f}")
    print(f"订单ID: {order_id}")
    print(f"付款链接: {pay_url}")
    print(f"消息: 【丙大山·支付提醒】您的订单{order_id}已开通。付款链接: {pay_url} 金额:¥{amount:.2f}。首周仅需¥1体验！注意:回测是历史数据，不代表未来收益；非投资建议，风险自负。")
    print("-"*70)

print(f"\n💡 提示: 共{len(pending)}笔待支付订单，总金额¥{sum(o.get('amount',0) for o in pending):,.2f}")
print("   以上是前20条，如需全部请运行完整脚本")

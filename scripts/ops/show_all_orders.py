import json

# 读取数据库
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)

orders = db.get('orders', [])
pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]

print("="*80)
print(f"丙大山 · 待收款订单汇总")
print(f"总订单数: {len(orders)}")
print(f"已支付: {len(orders) - len(pending)} 笔")
print(f"待支付: {len(pending)} 笔")
print(f"待收金额: ¥{sum(o.get('amount', 0) for o in pending):,.2f}")
print("="*80)
print()

# 按金额排序
pending_sorted = sorted(pending, key=lambda x: x.get('amount', 0), reverse=True)

# 分组统计
by_plan = {}
for o in pending:
    plan = o.get('plan', 'unknown')
    by_plan[plan] = by_plan.get(plan, 0) + 1

print("📊 按套餐分布:")
plan_names = {'t': '体验', 'm': '月卡', 'q': '季卡', 'y': '年卡', 'p': 'Pro', 'v': 'VIP', 's': '至尊'}
for plan, count in sorted(by_plan.items(), key=lambda x: -x[1]):
    name = plan_names.get(plan, plan)
    amt = next((o.get('amount', 0) for o in pending if o.get('plan') == plan), 0)
    total = amt * count
    print(f"  {name}({plan}): {count:3d}笔 × ¥{amt:.2f} = ¥{total:8.2f}")

print()
print("="*80)
print("📋 全部订单列表（按金额降序）:")
print("="*80)

for i, o in enumerate(pending_sorted, 1):
    order_id = o.get('id', '')
    amount = o.get('amount', 0)
    plan = o.get('plan', 't')
    ref = o.get('ref', '')
    pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
    
    plan_name = plan_names.get(plan, plan)
    
    print(f"{i:3d}. {order_id} | ¥{amount:6.2f} | {plan_name:4s} | {pay_url}")

print()
print("="*80)
print(f"💰 总计: {len(pending)}笔订单，¥{sum(o.get('amount', 0) for o in pending):,.2f}")
print("="*80)

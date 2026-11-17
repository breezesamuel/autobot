import json

# 读取数据库
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)

orders = db.get('orders', [])
pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]
high_value = [o for o in pending if o.get('amount', 0) >= 100]

print("# 🔥 高价值订单催款消息（优先发送）\n")

for i, o in enumerate(high_value[:20], 1):
    order_id = o.get('id', '')
    amount = o.get('amount', 0)
    plan = o.get('plan', 't')
    ref = o.get('ref', '')
    pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
    
    message = f"【丙大山·支付提醒】您的订单{order_id}已开通。付款链接: {pay_url} 金额:¥{amount:.2f}。年付立省¥289，立即开通全部功能！注意:回测是历史数据，不代表未来收益；非投资建议，风险自负。"
    
    print(f"## 订单 #{i}: ¥{amount:.2f}")
    print(f"**订单ID:** {order_id}")
    print(f"**付款链接:** {pay_url}")
    print(f"**催款消息:**")
    print(message)
    print()

print("---")
print(f"\n💰 总计: {len(high_value)}个高价值订单，¥{sum(o.get('amount',0) for o in high_value):,.2f}")
import json
from datetime import datetime

# 读取数据库
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)

orders = db.get('orders', [])
pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]

print("="*70)
print("丙大山 · 全部150笔待收款订单")
print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"总金额: ¥{sum(o.get('amount',0) for o in pending):,.2f}")
print("="*70)
print()

# 生成CSV格式（方便导入Excel）
print("【CSV格式 - 复制到Excel】")
print("订单ID,金额,套餐,付款链接,消息")
for o in pending:
    order_id = o.get('id', '')
    amount = o.get('amount', 0)
    plan = o.get('plan', 't')
    ref = o.get('ref', '')
    pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
    message = f"【丙大山·支付提醒】您的订单{order_id}已开通。付款链接: {pay_url} 金额:¥{amount:.2f}。"
    print(f"{order_id},{amount:.2f},{plan},{pay_url},{message}")

print()
print("="*70)
print("【纯文本消息 - 复制到微信/QQ】")
print("="*70)
print()

for i, o in enumerate(pending, 1):
    order_id = o.get('id', '')
    amount = o.get('amount', 0)
    plan = o.get('plan', 't')
    ref = o.get('ref', '')
    pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
    
    message = f"""【丙大山·支付提醒】

您的订单 {order_id} 已开通。
付款链接: {pay_url}
金额: ¥{amount:.2f}

功能亮点:
• AI自动检测过拟合
• 一键生成完整回测报告
• 支持126个专业技能

首周仅需¥1体验！

注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。"""
    
    print(f"{'='*70}")
    print(f"【订单 #{i}/{len(pending)}】金额: ¥{amount:.2f}")
    print(f"{'='*70}")
    print(message)
    print()

print("="*70)
print(f"总计: {len(pending)}笔订单，¥{sum(o.get('amount',0) for o in pending):,.2f}")
print("="*70)

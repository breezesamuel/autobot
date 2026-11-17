#!/usr/bin/env python3
"""丙大山 · 150笔待收款订单完整列表 - 可直接复制发送"""
import json
from datetime import datetime

# 读取数据库
with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)

orders = db.get('orders', [])
pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]

print("="*80)
print("丙大山 · 全部150笔待收款订单")
print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"总订单数: {len(pending)} 笔")
print(f"总金额: ¥{sum(o.get('amount',0) for o in pending):,.2f}")
print("="*80)
print()

# 按金额排序（优先处理高价值订单）
pending_sorted = sorted(pending, key=lambda x: x.get('amount', 0), reverse=True)

print("🔥 【高价值订单优先】(¥100以上)")
print("-"*80)
high_value = [o for o in pending_sorted if o.get('amount', 0) >= 100]
for i, o in enumerate(high_value[:30], 1):
    order_id = o.get('id', '')
    amount = o.get('amount', 0)
    plan = o.get('plan', 't')
    ref = o.get('ref', '')
    pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
    
    print(f"\n【#{i}】¥{amount:.2f} | 订单: {order_id}")
    print(f"链接: {pay_url}")
    print(f"消息: 【丙大山·支付提醒】您的订单{order_id}已开通。付款链接: {pay_url} 金额:¥{amount:.2f}")

print("\n\n" + "="*80)
print("📋 【全部订单列表】(共{}笔)".format(len(pending)))
print("="*80)

for i, o in enumerate(pending_sorted, 1):
    order_id = o.get('id', '')
    amount = o.get('amount', 0)
    plan = o.get('plan', 't')
    ref = o.get('ref', '')
    pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
    
    # 套餐名称映射
    plan_names = {'t': '体验', 'm': '月卡', 'q': '季卡', 'y': '年卡', 'p': 'Pro', 'v': 'VIP', 's': '至尊'}
    plan_name = plan_names.get(plan, plan)
    
    print(f"{i:3d}. {order_id} | ¥{amount:6.2f} | {plan_name} | {pay_url}")

print("\n" + "="*80)
print(f"💰 总计: {len(pending)}笔订单，¥{sum(o.get('amount',0) for o in pending):,.2f}")
print("="*80)

# 保存CSV文件
csv_file = '/tmp/pending_orders.csv'
with open(csv_file, 'w', encoding='utf-8') as f:
    f.write("序号,订单ID,金额,套餐,付款链接,消息\n")
    for i, o in enumerate(pending_sorted, 1):
        order_id = o.get('id', '')
        amount = o.get('amount', 0)
        plan = o.get('plan', 't')
        ref = o.get('ref', '')
        pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
        message = f"【丙大山·支付提醒】您的订单{order_id}已开通。付款链接: {pay_url} 金额:¥{amount:.2f}"
        f.write(f"{i},{order_id},{amount:.2f},{plan},{pay_url},\"{message}\"\n")

print(f"\n💾 CSV文件已保存: {csv_file}")
print("   可用Excel打开，批量发送到微信/QQ/邮件")

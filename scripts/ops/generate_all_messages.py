#!/usr/bin/env python3
"""丙大山 · 一键生成全部催款消息"""
import json

def main():
    try:
        with open('/opt/bingdashan/data/db.json', 'r') as f:
            db = json.load(f)
    except Exception as e:
        print(f"❌ 无法读取数据库: {e}")
        return 1
    
    orders = db.get('orders', [])
    pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]
    
    print("="*80)
    print(f"丙大山 · 待收款订单催款消息")
    print(f"总数: {len(pending)}笔，总金额: ¥{sum(o.get('amount', 0) for o in pending):,.2f}")
    print("="*80)
    print()
    
    # 按金额排序（优先处理高价值）
    pending_sorted = sorted(pending, key=lambda x: x.get('amount', 0), reverse=True)
    
    plan_names = {'t': '体验', 'm': '月卡', 'q': '季卡', 'y': '年卡', 'p': 'Pro', 'v': 'VIP', 's': '至尊'}
    
    for i, o in enumerate(pending_sorted, 1):
        order_id = o.get('id', '')
        amount = o.get('amount', 0)
        plan = o.get('plan', 't')
        ref = o.get('ref', '')
        pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
        plan_name = plan_names.get(plan, plan)
        
        # 生成催款消息
        message = f"""【丙大山·支付提醒】

您的订单 {order_id} 已开通。
付款链接: {pay_url}
金额: ¥{amount:.2f}（{plan_name}）

功能亮点:
• AI自动检测过拟合
• 一键生成完整回测报告  
• 支持126个专业技能
• 7种Agent编排架构

首周仅需¥1体验！

注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。"""
        
        print(f"{'='*80}")
        print(f"【订单 #{i}/{len(pending)}】金额: ¥{amount:.2f} | {plan_name}")
        print(f"订单ID: {order_id}")
        print(f"{'='*80}")
        print(message)
        print()
    
    print("="*80)
    print(f"💾 共生成 {len(pending)} 条催款消息")
    print(f"💰 总金额: ¥{sum(o.get('amount', 0) for o in pending):,.2f}")
    print("="*80)
    
    # 保存到文件
    output_file = '/tmp/all_payment_messages.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, o in enumerate(pending_sorted, 1):
            order_id = o.get('id', '')
            amount = o.get('amount', 0)
            plan = o.get('plan', 't')
            ref = o.get('ref', '')
            pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&slug=tool&ref={ref}"
            plan_name = plan_names.get(plan, plan)
            
            message = f"""【丙大山·支付提醒】

您的订单 {order_id} 已开通。
付款链接: {pay_url}
金额: ¥{amount:.2f}（{plan_name}）

功能亮点:
• AI自动检测过拟合
• 一键生成完整回测报告  
• 支持126个专业技能
• 7种Agent编排架构

首周仅需¥1体验！

注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。"""
            
            f.write(f"{'='*80}\n")
            f.write(f"【订单 #{i}/{len(pending)}】金额: ¥{amount:.2f} | {plan_name}\n")
            f.write(f"订单ID: {order_id}\n")
            f.write(f"{'='*80}\n")
            f.write(message)
            f.write("\n\n")
    
    print(f"\n💾 完整消息已保存到: {output_file}")
    print("   可使用: cat /tmp/all_payment_messages.txt 查看")

if __name__ == '__main__':
    exit(main())

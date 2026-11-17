#!/usr/bin/env python3
"""丙大山 · 催款消息生成器 - 直接可发送版本"""
import json
from datetime import datetime

def main():
    print("="*70)
    print("丙大山 · 待发送催款消息（直接复制到微信/QQ）")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 读取外联消息
    try:
        with open('/opt/bingdashan/data/outreach_messages.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割每条消息
        messages = content.split('---')[1:]  # 跳过标题部分
        
        print(f"\n共 {len(messages)} 条催款消息\n")
        
        for i, msg in enumerate(messages[:13], 1):  # 只显示前13条
            # 清理格式
            clean_msg = msg.strip().replace('\n>', '\n').replace('> ', '')
            
            print(f"{'='*70}")
            print(f"【消息 #{i}】")
            print(f"{'='*70}")
            print(clean_msg)
            print()
            
    except FileNotFoundError:
        print("❌ 找不到消息文件，尝试从数据库生成...")
        
        # 尝试从订单数据生成
        try:
            d = json.load(open('/opt/bingdashan/data/db.json'))
            orders = d.get('orders', [])
            pending = [o for o in orders if not o.get('paid', False)]
            
            print(f"\n找到 {len(pending)} 个待付款订单\n")
            
            for i, order in enumerate(pending[:13], 1):
                amount = order.get('amount', 0)
                plan = order.get('plan', 'unknown')
                ref = order.get('ref', '')
                
                pay_url = f"https://tools-cn.highkingflower.com/api/pay?plan={plan}&ref={ref}"
                
                message = f"""【丙大山·支付提醒】

您的订单已生成，金额: ¥{amount}
付款链接: {pay_url}

功能亮点:
• AI自动检测过拟合
• 一键生成完整回测报告
• 支持126个专业技能

首周仅需¥1体验！

注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。"""
                
                print(f"{'='*70}")
                print(f"【消息 #{i}】金额: ¥{amount}")
                print(f"{'='*70}")
                print(message)
                print()
                
        except Exception as e:
            print(f"❌ 无法生成消息: {e}")
    
    print("="*70)
    print("💡 使用说明:")
    print("   1. 复制每条消息")
    print("   2. 发送到对应客户的微信/QQ")
    print("   3. 记录发送时间和回复")
    print("="*70)

if __name__ == '__main__':
    main()

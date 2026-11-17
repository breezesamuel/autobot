#!/usr/bin/env python3
"""丙大山 · 待发送催款消息 - 可直接复制版"""
import json
from datetime import datetime

def main():
    # 催款消息数据
    orders = [
        {"id": "mvgevdw6xm1av", "amount": 500, "plan": "proY", "ref": "mvgeerdl"},
        {"id": "mvi21kh7wvntq", "amount": 500, "plan": "proY", "ref": "ao7n"},
        {"id": "mvi221uqrxqob", "amount": 299, "plan": "team", "ref": "ao7n"},
        {"id": "mvp9kl8kl6uag", "amount": 150, "plan": "pro3", "ref": "aob0"},
        {"id": "mvut742rctwkh", "amount": 60, "plan": "pro", "ref": "aodm"},
        {"id": "mvgetaxc4pezq", "amount": 60, "plan": "pro", "ref": "mvgeerdl"},
        {"id": "mvut5w4ezvp9n", "amount": 1, "plan": "trial", "ref": "aodm"},
        {"id": "mvz2eultgsbh4", "amount": 1, "plan": "trial", "ref": "aofl"},
    ]
    
    print("="*70)
    print("丙大山 · 待发送催款消息（直接复制到微信/QQ）")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总订单数: {len(orders)} 条")
    print(f"总金额: ¥{sum(o['amount'] for o in orders)}")
    print("="*70)
    print()
    
    for i, order in enumerate(orders, 1):
        url = f"https://tools-cn.highkingflower.com/api/pay?plan={order['plan']}&slug=tool&ref={order['ref']}"
        
        message = f"""【丙大山·支付提醒】

您的订单 {order['id']} 已开通。
付款链接: {url}
金额: ¥{order['amount']}

功能亮点:
• AI自动检测过拟合
• 一键生成完整回测报告  
• 支持126个专业技能

首周仅需¥1体验！

注意: 回测是历史数据，不代表未来收益；非投资建议，风险自负。"""
        
        print(f"{'='*70}")
        print(f"【消息 #{i}】金额: ¥{order['amount']} | 订单ID: {order['id']}")
        print(f"{'='*70}")
        print(message)
        print()
    
    print("="*70)
    print("💡 使用说明:")
    print("   1. 复制每条消息")
    print("   2. 发送到对应客户的微信/QQ/短信")
    print("   3. 记录发送时间和回复状态")
    print("   4. 追踪转化结果")
    print("="*70)

if __name__ == '__main__':
    main()

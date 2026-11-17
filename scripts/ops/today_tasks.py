import json

try:
    with open('/opt/bingdashan/data/db.json', 'r') as f:
        db = json.load(f)
    
    orders = db.get('orders', [])
    pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]
    high_value = [o for o in pending if o.get('amount', 0) >= 100]
    
    total = sum(o.get('amount', 0) for o in pending)
    
    print('='*70)
    print('丙大山 今日推广任务清单')
    print('='*70)
    print()
    print(f'Pending orders: {len(pending)}')
    print(f'High value (>=100): {len(high_value)}')
    print(f'Total pending amount: {total:,.2f}')
    print()
    print('Tasks for today:')
    print('-'*70)
    print('1. Twitter Post 1 (09:00) - 功能介绍')
    print('   内容: 做了量化交易3年，踩过最大的坑不是选错因子...')
    print()
    print('2. Twitter Post 2 (12:00) - 定价透明')
    print('   内容: 说实话的定价：首周¥1/月卡¥99/年卡¥899...')
    print()
    print('3. GitHub Issue Reply (14:00)')
    print('   Issue #7: https://github.com/guiguesaxel-lab/AI-INVESTOR-OS/issues/7')
    print('   Issue #35: https://github.com/Emposes/ai-encyclopedia/issues/35')
    print()
    print('4. WeChat Moment (20:00)')
    print('   内容: 做了3年量化交易，终于做出了一款能自动检测过拟合的AI回测工具...')
    print()
    print('5. Follow up high-value orders (16:00)')
    print(f'   Count: {len(high_value[:10])} orders to follow up')
    print('-'*70)
    print()
    print('High-value orders to follow up:')
    for i, o in enumerate(high_value[:10], 1):
        oid = o.get('id', '')
        amt = o.get('amount', 0)
        print(f'  {i}. {oid}: ¥{amt}')
    print()
    print('='*70)
    print('建议执行顺序:')
    print('  早上: 发Twitter + 检查Banner')
    print('  中午: 回复GitHub Issue')
    print('  下午: 跟进高价值订单')
    print('  晚上: 发布朋友圈')
    print('='*70)
except Exception as e:
    print(f'Error: {e}')

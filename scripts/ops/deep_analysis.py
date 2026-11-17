import json
from datetime import datetime, timedelta

try:
    with open('/opt/bingdashan/data/db.json', 'r') as f:
        db = json.load(f)
    
    orders = db.get('orders', [])
    pending = [o for o in orders if not (o.get('paid') == True or o.get('status') == 'paid')]
    
    print('='*70)
    print('丙大山 · 订单深度分析')
    print('='*70)
    print()
    
    # 按时间分组
    by_date = {}
    for o in pending:
        ts = o.get('createdAt', 0)
        if ts:
            dt = datetime.fromtimestamp(ts/1000)
            date_key = dt.strftime('%Y-%m-%d')
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append(o)
    
    print('📅 按日期分布:')
    for date, items in sorted(by_date.items(), reverse=True)[:10]:
        total = sum(o.get('amount', 0) for o in items)
        print(f'  {date}: {len(items)}笔, ¥{total:.2f}')
    
    print()
    
    # 按plan分组
    by_plan = {}
    for o in pending:
        plan = o.get('plan', 'unknown')
        if plan not in by_plan:
            by_plan[plan] = []
        by_plan[plan].append(o)
    
    print('📦 按套餐分布:')
    plan_names = {'t': '体验', 'm': '月卡', 'q': '季卡', 'y': '年卡', 'p': 'Pro', 'v': 'VIP'}
    for plan, items in sorted(by_plan.items(), key=lambda x: -sum(o.get('amount',0) for o in x[1])):
        name = plan_names.get(plan, plan)
        count = len(items)
        total = sum(o.get('amount', 0) for o in items)
        print(f'  {name}({plan}): {count}笔, ¥{total:.2f}')
    
    print()
    
    # 检查最早和最晚的订单
    if pending:
        earliest = min(pending, key=lambda x: x.get('createdAt', 999999999999))
        latest = max(pending, key=lambda x: x.get('createdAt', 0))
        
        print('⏰ 时间范围:')
        earliest_dt = datetime.fromtimestamp(earliest.get('createdAt', 0)/1000)
        latest_dt = datetime.fromtimestamp(latest.get('createdAt', 0)/1000)
        print(f'  最早订单: {earliest_dt} ({earliest.get("id", "")})')
        print(f'  最新订单: {latest_dt} ({latest.get("id", "")})')
        print(f'  间隔天数: {(latest_dt - earliest_dt).days}')
    
    print()
    print('='*70)
    print(f'总计: {len(pending)}笔待支付, ¥{sum(o.get("amount", 0) for o in pending):,.2f}')
    print('='*70)
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

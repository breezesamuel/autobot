import json
import os
from datetime import datetime

CONFIG = {
    'project_name': 'BingDashan',
    'website': 'https://tools-cn.highkingflower.com',
    'db_path': '/opt/bingdashan/data/db.json',
    'output_dir': '/opt/bingdashan/promo_output',
}

def load_db():
    try:
        with open(CONFIG['db_path'], 'r') as f:
            return json.load(f)
    except Exception as e:
        print('Error loading db:', e)
        return None

def get_stats(db):
    orders = db.get('orders', [])
    paid = [o for o in orders if o.get('paid')]
    pending = [o for o in orders if not o.get('paid')]
    total_paid = sum(o.get('amount', 0) for o in paid)
    total_pending = sum(o.get('amount', 0) for o in pending)
    now = datetime.now()
    today_start = int(now.replace(hour=0,minute=0,second=0,microsecond=0).timestamp() * 1000)
    today_paid = [o for o in paid if o.get('createdAt', 0) >= today_start]
    today_revenue = sum(o.get('amount', 0) for o in today_paid)
    return {
        'total_orders': len(orders),
        'paid_count': len(paid),
        'pending_count': len(pending),
        'total_paid_amount': total_paid,
        'total_pending_amount': total_pending,
        'today_new': len([o for o in orders if o.get('createdAt', 0) >= today_start]),
        'today_paid': len(today_paid),
        'today_revenue': today_revenue,
        'high_value_pending': len([o for o in pending if o.get('amount', 0) >= 100]),
    }

def main():
    print('='*60)
    print('BingDashan Auto Promo System v3')
    print('='*60)
    
    db = load_db()
    if not db:
        print('Failed to load database')
        return 1
    
    stats = get_stats(db)
    print("Total Orders:", stats['total_orders'])
    print("Paid:", stats['paid_count'], "(RMB" + str(stats['total_paid_amount']) + ")")
    print("Pending:", stats['pending_count'], "(RMB" + str(stats['total_pending_amount']) + ")")
    print("Today New:", stats['today_new'], "Paid:", stats['today_paid'], "Rev: RMB" + str(stats['today_revenue']))
    print("High-value pending:", stats['high_value_pending'], "orders")
    
    os.makedirs(CONFIG['output_dir'], exist_ok=True)
    
    with open(CONFIG['output_dir'] + '/stats.json', 'w') as f:
        json.dump({'stats': stats, 'timestamp': datetime.now().isoformat()}, f, indent=2)
    
    print("")
    print("Stats saved to", CONFIG['output_dir'] + "/stats.json")
    print('='*60)
    return 0

if __name__ == '__main__':
    main()

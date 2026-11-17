import json
from datetime import datetime
import time

DB_PATH = '/opt/bingdashan/data/db.json'

def get_stats():
    try:
        with open(DB_PATH, 'r') as f:
            db = json.load(f)
        
        orders = db.get('orders', [])
        paid = [o for o in orders if o.get('paid') == True]
        pending = [o for o in orders if not o.get('paid') == True]
        
        total_paid = sum(o.get('amount', 0) for o in paid)
        total_pending = sum(o.get('amount', 0) for o in pending)
        
        now = datetime.now()
        today_start = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
        
        today_orders = [o for o in orders if o.get('createdAt', 0) >= today_start]
        today_paid = [o for o in today_orders if o.get('paid') == True]
        today_revenue = sum(o.get('amount', 0) for o in today_paid)
        
        return {
            'total': len(orders),
            'paid': len(paid),
            'pending': len(pending),
            'paid_amount': total_paid,
            'pending_amount': total_pending,
            'today_new': len(today_orders),
            'today_paid': len(today_paid),
            'today_revenue': today_revenue,
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    stats = get_stats()
    
    print("="*70)
    print('BingDashan Payment Monitor')
    print("="*70)
    print(f"Time: {stats['timestamp']}")
    print(f"Total Orders: {stats['total']}")
    print(f"Paid: {stats['paid']} (RMB{stats['paid_amount']:.2f})")
    print(f"Pending: {stats['pending']} (RMB{stats['pending_amount']:.2f})")
    print(f"Today New: {stats['today_new']}, Paid: {stats['today_paid']}, Rev: RMB{stats['today_revenue']:.2f}")
    print("="*70)
    
    if stats.get('error'):
        print(f"Error: {stats['error']}")

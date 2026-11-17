import json
from datetime import datetime

with open('/opt/bingdashan/data/db.json', 'r') as f:
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

print('='*70)
print('BingDashan Payment Monitor')
print('Time:', now.strftime('%Y-%m-%d %H:%M:%S'))
print('='*70)
print('Total Orders:', len(orders))
print('Paid:', len(paid), '(RMB' + str(total_paid) + ')')
print('Pending:', len(pending), '(RMB' + str(total_pending) + ')')
print('Today New:', len(today_orders))
print('Today Paid:', len(today_paid), '(RMB' + str(today_revenue) + ')')
print('='*70)

if today_paid:
    print('\\nToday Payments:')
    for o in today_paid:
        print('  OK', o.get('id', ''), ':', o.get('amount', 0))

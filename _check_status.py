import json
from datetime import datetime

with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)

orders = db.get('orders', [])
paid = [o for o in orders if o.get('paid') == True]
pending = [o for o in orders if not o.get('paid') == True]

total_paid = sum(o.get('amount', 0) for o in paid)
total_pending = sum(o.get('amount', 0) for o in pending)

print('='*70)
print('BingDashan Payment Status')
print('='*70)
print(f'Total Orders: {len(orders)}')
print(f'Paid: {len(paid)} (RMB{total_paid:.2f})')
print(f'Pending: {len(pending)} (RMB{total_pending:.2f})')
print('='*70)

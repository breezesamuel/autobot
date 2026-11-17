import json, os
from datetime import datetime

with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)

orders = db.get('orders', [])
paid = [o for o in orders if o.get('paid')]
pending = [o for o in orders if not o.get('paid')]
total_paid = sum(o.get('amount', 0) for o in paid)
total_pending = sum(o.get('amount', 0) for o in pending)
now = datetime.now()
today_start = int(now.replace(hour=0,minute=0,second=0,microsecond=0).timestamp() * 1000)
today_paid = [o for o in paid if o.get('createdAt', 0) >= today_start]
today_revenue = sum(o.get('amount', 0) for o in today_paid)

print('='*60)
print('BingDashan Payment Status')
print('='*60)
print(f"Total Orders: {len(orders)}")
print(f"Paid: {len(paid)} (RMB{total_paid:.2f})")
print(f"Pending: {len(pending)} (RMB{total_pending:.2f})")
print(f"Today New: {len([o for o in orders if o.get('createdAt',0)>=today_start])}")
print(f"Today Paid: {len(today_paid)} (RMB{today_revenue:.2f})")
print(f"High-value Pending: {len([o for o in pending if o.get('amount',0)>=100])} orders")
print('='*60)

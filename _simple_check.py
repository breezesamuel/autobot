import json
from datetime import datetime

with open('/opt/bingdashan/data/db.json', 'r') as f:
    db = json.load(f)

orders = db.get('orders', [])
paid = [o for o in orders if o.get('paid') == True]
pending = [o for o in orders if not o.get('paid') == True]

print('Total:', len(orders))
print('Paid:', len(paid), 'Pending:', len(pending))
print('Paid amount: RMB' + str(sum(o.get('amount', 0) for o in paid)))
print('Pending amount: RMB' + str(sum(o.get('amount', 0) for o in pending)))

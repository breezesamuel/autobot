#!/usr/bin/env python3
import json
from datetime import datetime, timedelta

try:
    with open('/opt/bingdashan/data/db.json', 'r') as f:
        db = json.load(f)
    
    orders = db.get('orders', [])
    paid = [o for o in orders if o.get('paid') == True]
    pending = [o for o in orders if not o.get('paid') == True]
    
    today = datetime.now()
    today_start = int(today.replace(hour=0,minute=0,second=0,microsecond=0).timestamp()*1000)
    today_orders = [o for o in orders if o.get('createdAt',0) >= today_start]
    today_paid = [o for o in today_orders if o.get('paid') == True]
    today_rev = sum(o.get('amount',0) for o in today_paid)
    
    week_ago = int((today-timedelta(days=7)).timestamp()*1000)
    week_orders = [o for o in orders if o.get('createdAt',0) >= week_ago]
    week_paid = [o for o in week_orders if o.get('paid') == True]
    week_rev = sum(o.get('amount',0) for o in week_paid)
    
    month_start = int(today.replace(day=1,hour=0,minute=0,second=0,microsecond=0).timestamp()*1000)
    month_orders = [o for o in orders if o.get('createdAt',0) >= month_start]
    month_paid = [o for o in month_orders if o.get('paid') == True]
    month_rev = sum(o.get('amount',0) for o in month_paid)
    
    total_paid = sum(o.get('amount',0) for o in paid)
    total_pending = sum(o.get('amount',0) for o in pending)
    
    print('='*66)
    print('BingDashan Daily Promo Monitor')
    print('='*66)
    print('Total Orders:', len(orders))
    print('Paid:', len(paid), '(¥'+str(total_paid)+')')
    print('Pending:', len(pending), '(¥'+str(total_pending)+')')
    print('Today New:', len(today_orders), ', Paid:', len(today_paid), ', Rev:', today_rev)
    print('Week New:', len(week_orders), ', Paid:', len(week_paid), ', Rev:', week_rev)
    print('Month New:', len(month_orders), ', Paid:', len(month_paid), ', Rev:', month_rev)
    print('='*66)
    
    if today_paid:
        print('\\nToday payments:')
        for o in today_paid:
            print('  OK', o.get('id',''), ':', o.get('amount',0))
except Exception as e:
    print('Error:', str(e))

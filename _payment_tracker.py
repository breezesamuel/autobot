#!/usr/bin/env python3
"""
丙大山 · 支付监控与自动提醒系统
功能：实时监控收入变化，自动发送提醒
"""
import json
import time
from datetime import datetime, timedelta

DB_PATH = '/opt/bingdashan/data/db.json'
LAST_CHECK_FILE = '/tmp/last_check.json'

def load_last_check():
    try:
        with open(LAST_CHECK_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'paid_count': 0, 'paid_amount': 0}

def save_last_check(data):
    with open(LAST_CHECK_FILE, 'w') as f:
        json.dump(data, f)

def check_payments():
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
        
        last = load_last_check()
        new_payments = len(paid) - last['paid_count']
        new_amount = total_paid - last['paid_amount']
        
        result = {
            'total_orders': len(orders),
            'paid': len(paid),
            'pending': len(pending),
            'paid_amount': total_paid,
            'pending_amount': total_pending,
            'today_new': len(today_orders),
            'today_paid': len(today_paid),
            'today_revenue': today_revenue,
            'new_payments': new_payments,
            'new_amount': new_amount,
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        save_last_check({'paid_count': len(paid), 'paid_amount': total_paid})
        
        return result
        
    except Exception as e:
        return {'error': str(e)}

def main():
    print("="*70)
    print("丙大山 · 支付监控系统")
    print("="*70)
    
    while True:
        try:
            stats = check_payments()
            
            if 'error' in stats:
                print(f"[{stats['timestamp']}] Error: {stats['error']}")
            else:
                print(f"\n[{stats['timestamp']}]")
                print(f"总订单: {stats['total_orders']} | 已支付: {stats['paid']} (¥{stats['paid_amount']:.2f}) | 待支付: {stats['pending']} (¥{stats['pending_amount']:.2f})")
                print(f"今日新增: {stats['today_new']}笔 | 今日支付: {stats['today_paid']}笔 | 今日收入: ¥{stats['today_revenue']:.2f}")
                
                if stats['new_payments'] > 0:
                    print(f"\n🎉 新检测到 {stats['new_payments']} 笔支付! 新增金额: ¥{stats['new_amount']:.2f}")
                    print("请立即检查并回复!")
                
                if stats['today_paid'] > 0:
                    print(f"\n💰 今日收入: ¥{stats['today_revenue']:.2f}")
            
            time.sleep(300)  # 每5分钟检查一次
            
        except KeyboardInterrupt:
            print("\n监控已停止")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()

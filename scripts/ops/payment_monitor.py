#!/usr/bin/env python3
"""
丙大山 · 支付回调实时监控脚本
每5分钟检查一次新订单
"""
import json
import time
from datetime import datetime

DB_PATH = '/opt/bingdashan/data/db.json'
LOG_FILE = '/tmp/payment_monitor.log'

def check_payments():
    try:
        with open(DB_PATH, 'r') as f:
            db = json.load(f)
        
        orders = db.get('orders', [])
        
        # 统计已支付和待支付
        paid = [o for o in orders if o.get('paid') == True]
        pending = [o for o in orders if not o.get('paid') == True]
        
        total_paid = sum(o.get('amount', 0) for o in paid)
        total_pending = sum(o.get('amount', 0) for o in pending)
        
        # 今日新订单
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

def main():
    print("="*70)
    print("丙大山 · 支付实时监控")
    print("="*70)
    
    while True:
        try:
            stats = check_payments()
            
            if 'error' in stats:
                print(f"[{stats['timestamp']}] Error: {stats['error']}")
            else:
                print(f"\n[{stats['timestamp']}]")
                print(f"总订单: {stats['total']} | 已支付: {stats['paid']} (¥{stats['paid_amount']:.2f}) | 待支付: {stats['pending']} (¥{stats['pending_amount']:.2f})")
                print(f"今日新增: {stats['today_new']}笔 | 今日支付: {stats['today_paid']}笔 | 今日收入: ¥{stats['today_revenue']:.2f}")
                
                # 如果有新支付，输出详情
                if stats['today_paid'] > 0:
                    print("\n🎉 今日新增支付订单:")
                    with open(DB_PATH, 'r') as f:
                        db = json.load(f)
                    for o in db.get('orders', []):
                        if o.get('paid') and o.get('createdAt', 0) >= int(datetime.now().replace(hour=0,minute=0,second=0,microsecond=0).timestamp()*1000):
                            print(f"  ✓ {o.get('id','')}: ¥{o.get('amount',0)}")
            
            time.sleep(300)  # 每5分钟检查一次
            
        except KeyboardInterrupt:
            print("\n监控已停止")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()

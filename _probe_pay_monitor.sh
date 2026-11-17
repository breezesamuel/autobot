#!/usr/bin/env bash
# 查 CN 现有 alipay 回调/支付事件日志 (决定怎么接自动对账)
echo "=== 1. 看 alipay.js 里 webhook/notify 实现 ==="
grep -n "notify\|callback\|payment_event\|webhook\|log.*pay\|record.*paid" /www/wwwroot/tools-cn.highkingflower.com/api/alipay.js 2>/dev/null | head -20
echo ""
echo "=== 2. 找 alipay 回调文件存储位置 ==="
find /var/log -name "*alipay*" -o -name "*pay*log*" -o -name "*webhook*" 2>/dev/null | head -8
ls -la /opt/bingdashan/data/*.{json,log} 2>/dev/null | grep -iE "log|event|notify" | head -8
echo ""
echo "=== 3. 查 alipay notify URL 配置 ==="
grep -i "notify_url\|notifyUrl\|alipay.notify" /etc/bingdashan-cn.env 2>/dev/null | head -5
grep -rn "notify_url\|notifyUrl" /www/wwwroot/tools-cn.highkingflower.com/api/*.js 2>/dev/null | head -6
echo ""
echo "=== 4. 现有 /api/pay 返回的结构 (看有没有记录 paid 事件的字段) ==="
curl -s "http://127.0.0.1:8794/api/pay?plan=m10&ref=test_notify&slug=test" 2>/dev/null | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin),ensure_ascii=False)[:400])" 2>/dev/null
echo ""
echo "=== 5. 查现有 orders 表结构 (db.json 里订单字段) ==="
python3 -c "import json;d=json.load(open('/opt/bingdashan/data/db.json'));orders=d.get('orders',[]);print('total orders:',len(orders));o=orders[0] if orders else {};print(json.dumps({k:v for k,v in o.items() if k not in ('items','details')},ensure_ascii=False)[:300])" 2>/dev/null
echo done

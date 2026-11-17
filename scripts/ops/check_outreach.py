#!/usr/bin/env python3
"""丙大山 · 激活自动外联系统 - Python 3.6兼容版"""
import subprocess
import json
import sys

def run(cmd):
    try:
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = result.communicate(timeout=30)
        return result.returncode, stdout.decode('utf-8', errors='ignore').strip(), stderr.decode('utf-8', errors='ignore').strip()
    except Exception as e:
        return -1, '', str(e)

def main():
    print("="*70)
    print("丙大山 · 自动外联系统状态检查")
    print("="*70)
    
    # Step 1: 检查SMTP配置
    print("\n【Step 1】检查邮件发送配置...")
    rc, stdout, stderr = run("grep -i 'smtp\\|mail' /opt/bingdashan/.env 2>/dev/null || echo 'NOT_CONFIGURED'")
    if 'NOT_CONFIGURED' in stdout:
        print("❌ 未配置SMTP邮箱")
        print("\n📧 需要配置:")
        print("   SMTP_HOST=smtp.qq.com")
        print("   SMTP_PORT=465")
        print("   SMTP_USER=your_email@qq.com")
        print("   SMTP_PASS=your_authorization_code")
        print("\n获取QQ邮箱授权码:")
        print("   1. 登录QQ邮箱 → 设置 → 账户")
        print("   2. 找到'POP3/IMAP/SMTP服务'")
        print("   3. 开启SMTP服务，获取授权码")
        return 1
    else:
        print("✅ SMTP已配置")
        for line in stdout.split('\n'):
            if line.strip():
                parts = line.split('=', 1)
                if len(parts) == 2:
                    print(f"   {parts[0]}: {parts[1][:10]}***")  # 隐藏密码
    
    # Step 2: 检查leads数据
    print("\n【Step 2】检查线索数据...")
    rc, stdout, stderr = run("python3 -c \"import json; d=json.load(open('/opt/bingdashan/data/db.json')); leads=d.get('leads',[]); print('Total:', len(leads)); emails=[l.get('email','') for l in leads if l.get('email')]; print('With email:', len(emails))\"")
    if rc == 0:
        print(stdout)
    else:
        print(f"Error: {stderr}")
    
    # Step 3: 检查outreach模块
    print("\n【Step 3】检查外联模块...")
    rc, stdout, stderr = run("ls -la /opt/bingdashan/core/outreach.js 2>/dev/null && head -20 /opt/bingdashan/core/outreach.js || echo 'Module not found'")
    print(stdout)
    
    # Step 4: 查看pending订单
    print("\n【Step 4】查看待收款订单...")
    rc, stdout, stderr = run("python3 -c \"import json; d=json.load(open('/opt/bingdashan/data/db.json')); orders=d.get('orders',[]); pending=[o for o in orders if not o.get('paid',False)]; print('Pending orders:', len(pending)); total=sum(o.get('amount',0) for o in pending); print('Total amount: ¥'+str(total))\"")
    if rc == 0:
        print(stdout)
    
    print("\n" + "="*70)
    print("💡 结论:")
    print("   1. 邮件外联需要SMTP配置")
    print("   2. Leads需要email字段才能发送邮件")
    print("   3. 当前没有自动触达机制")
    print("   4. 必须手动发送催款消息")
    print("="*70)

if __name__ == '__main__':
    main()

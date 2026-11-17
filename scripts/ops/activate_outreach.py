#!/usr/bin/env python3
"""丙大山 · 激活自动外联系统"""
import subprocess
import json

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def main():
    print("="*70)
    print("丙大山 · 自动外联系统激活")
    print("="*70)
    
    # Step 1: 检查SMTP配置
    print("\n【Step 1】检查邮件发送配置...")
    rc, stdout, stderr = run("grep -i 'smtp\\|mail' /opt/bingdashan/.env 2>/dev/null || echo 'NOT_CONFIGURED'")
    if 'NOT_CONFIGURED' in stdout:
        print("❌ 未配置SMTP邮箱")
        print("\n📧 配置步骤:")
        print("   1. 登录QQ邮箱 → 设置 → 账户 → POP3/IMAP/SMTP")
        print("   2. 开启SMTP服务，获取授权码")
        print("   3. 添加到.env:")
        print("      SMTP_HOST=smtp.qq.com")
        print("      SMTP_PORT=465")
        print("      SMTP_USER=your_email@qq.com")
        print("      SMTP_PASS=your_authorization_code")
        print("   4. 重启服务: systemctl restart bingdashan-cn")
        return 1
    else:
        print("✅ SMTP已配置")
        print(stdout)
    
    # Step 2: 检查leads数据
    print("\n【Step 2】检查线索数据...")
    rc, stdout, stderr = run("python3 << 'PYEOF'\nimport json\ntry:\n    d=json.load(open('/opt/bingdashan/data/db.json'))\n    leads=d.get('leads',[])\n    emails=[l.get('email','') for l in leads if l.get('email')]\n    print(f'Total leads: {len(leads)}')\n    print(f'With email: {len(emails)}')\n    if emails:\n        print(f'Emails: {emails[:5]}')\nexcept Exception as e:\n    print(f'Error: {e}')\nPYEOF")
    print(stdout)
    
    # Step 3: 测试外联系统
    print("\n【Step 3】测试外联系统...")
    rc, stdout, stderr = run("node -e \"const o=require('/opt/bingdashan/core/outreach'); console.log('Outreach module loaded:', typeof o)\" 2>&1")
    if rc == 0:
        print(f"✅ 外联模块加载成功: {stdout}")
    else:
        print(f"⚠️ {stderr}")
    
    # Step 4: 生成外联计划
    print("\n【Step 4】生成外联计划...")
    rc, stdout, stderr = run("""node -e "
const store = require('/opt/bingdashan/core/store');
const db = store.read();
const leads = db.leads || [];
const highValue = leads.filter(l => l.signal >= 70).slice(0, 10);
console.log('High value leads (signal>=70):', highValue.length);
highValue.forEach((l,i) => console.log(i+1, l.name, 'signal='+l.signal, 'email='+(l.email||'none')));
" 2>&1""")
    print(stdout)
    
    print("\n" + "="*70)
    print("💡 下一步:")
    print("   1. 配置SMTP邮箱（必须）")
    print("   2. 确保leads有email字段")
    print("   3. 运行外联脚本发送消息")
    print("="*70)

if __name__ == '__main__':
    main()

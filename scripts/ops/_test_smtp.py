#!/usr/bin/env python3
"""快速测试 SMTP 是否连通 (不实际发送邮件，只验证连接)"""
import smtplib
from email.mime.text import MIMEText

cfg={'host':'smtp.qq.com','port':465,'user':'460123249@qq.com','pass':'namnbldayykicaji'}
try:
    srv=smtplib.SMTP_SSL(cfg['host'], cfg['port'], timeout=10)
    srv.login(cfg['user'], cfg['pass'])
    print("SMTP CONNECTED OK")
    # 发一封测试邮件给自己
    msg=MIMEText('丙大山 · 系统自检 - SMTP 连通性测试\n\n这是自动发送的测试邮件，证明收款预警邮件系统已就绪。\n时间: {}'.format(__import__('datetime').datetime.now().isoformat()), 'plain', 'utf-8')
    msg['Subject']='[丙大山] 系统自检-SMTP测试'
    msg['From']=cfg['user']
    msg['To']=cfg['user']
    srv.send_message(msg)
    srv.quit()
    print("TEST EMAIL SENT to {}".format(cfg['user']))
except Exception as e:
    print("SMTP FAIL: {}".format(str(e)[:120]))

#!/usr/bin/env python3
"""Send upgrade emails to trial winback users."""
import smtplib, ssl, os, sys, json
from email.mime.text import MIMEText
from email.utils import formatdate

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "460123249@qq.com")
SMTP_PASS = ""

for ef in ["/opt/bingdashan/.env", "/etc/bingdashan-cn.env"]:
    try:
        for line in open(ef, encoding="utf-8", errors="replace"):
            line = line.strip()
            if line.startswith("SMTP_PASS="):
                SMTP_PASS = line.split("=", 1)[1].strip()
                break
            if line.startswith("SMTP_AUTH=") and not SMTP_PASS:
                SMTP_PASS = line.split("=", 1)[1].strip()
    except Exception:
        pass

if not SMTP_PASS:
    print("ERROR: SMTP_PASS not found"); sys.exit(1)

WINBACK_TSV = "/opt/bingdashan/data/billing/trial_winback.tsv"
LOG_FILE = "/opt/bingdashan/data/outbound_log.jsonl"

def send(to_email, ref, plan_price=60):
    link = f"https://tools-cn.highkingflower.com/api/pay?plan=pro&slug=tool&ref={ref}"
    subject = "[丙大山] 您的7天体验已结束 · 升级享9折 (pro ¥60)"
    body = f"""<div style='font-family:sans-serif;max-width:520px;margin:auto'>
      <h2>您的 7 天体验即将到期</h2>
      <p>体验已使用 7 天。升级解锁全部工具 + 专业回测报告(C3) + 行情数据订阅:</p>
      <table><tr><td>专业·月度</td><td><b>¥{plan_price}/31天</b></td></tr></table>
      <p><b>限时新用户 9 折</b> · 升级后: 全部工具 + API + 数据导出 + 优先支持</p>
      <a href="{link}" style='display:inline-block;background:#22c55e;color:#04120a;padding:10px 18px;border-radius:8px;font-weight:700;text-decoration:none'>立即升级 ¥{plan_price}</a>
      <p style='color:#888;font-size:12px'>丙大山工具站 · 本邮件仅提醒, 历史回测不代表未来收益, 非投资建议。退订请回复 U。</p>
      <p style="color:#666">您的账号: {ref}</p>
    </div>"""
    msg = MIMEText(body, "html", "utf-8")
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    ctx = ssl.create_default_context()
    s = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=45)
    s.login(SMTP_USER, SMTP_PASS)
    s.sendmail(SMTP_USER, [to_email], msg.as_string())
    s.quit()
    return True

# Read winback TSV
records = []
with open(WINBACK_TSV, encoding="utf-8") as f:
    header = f.readline().strip().split('\t')
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 4:
            records.append(dict(zip(header, parts)))

print(f"Found {len(records)} winback records")

sent = 0
for r in records:
    ref = r.get("ref", "")
    # visitor format: ip:X_Y_Z_W:ref
    visitor = r.get("visitor", "")
    days_ago = float(r.get("距今天", "0") or 0)
    
    # Try to find email from funnel_inbox or other sources
    # For now, we need to look up by ref
    print(f"  ref={ref} days_ago={days_ago:.1f}")
    # Note: actual sending requires email lookup - placeholder for manual review

print("\nNote: trial_winback TSV doesn't contain email addresses directly.")
print("Use send_upgrade_mail.py manually per customer once email is identified.")
print("Or run: python3 /opt/bingdashan/scripts/ops/send_upgrade_mail.py <email> pro 60 <link> <ref>")

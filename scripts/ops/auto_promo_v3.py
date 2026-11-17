#!/usr/bin/env python3
"""Auto-outreach script: sends payment reminders to pending order customers."""
# Run on server: python3 /opt/bingdashan/scripts/ops/auto_promo_v3.py

import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

DATA_DIR = "/opt/bingdashan/data"
DB_FILE = os.path.join(DATA_DIR, "db.json")
LOG_FILE = os.path.join(DATA_DIR, "outreach_log.jsonl")

def load_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_pending_orders(db):
    orders = db.get("orders", [])
    return [o for o in orders if o.get("status") == "pending"]

def load_outreach_log():
    if not os.path.exists(LOG_FILE):
        return []
    logs = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    logs.append(json.loads(line))
                except:
                    pass
    return logs

def should_remind(order, logs):
    """Check if we've already sent a reminder for this order."""
    oid = order.get("id", "")
    for log in logs:
        if log.get("order_id") == oid and log.get("type") == "reminder_sent":
            return False
    return True

def build_reminder_email(order):
    """Build a polite payment reminder email."""
    customer_name = order.get("customer_name", order.get("name", "Valued Customer"))
    amount = order.get("amount_cny", order.get("amount", 0))
    service = order.get("service", order.get("gig_title", "your order"))
    order_id = order.get("id", "N/A")
    
    subject = f"Payment Reminder: Order #{order_id} - ¥{amount:.2f}"
    
    body = f"""Dear {customer_name},

Thank you for your order! We noticed that payment for order #{order_id} is still pending.

Order Details:
- Service: {service}
- Amount: ¥{amount:.2f}
- Order ID: {order_id}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

To complete your payment, please visit: https://bingdashan.com/pay/{order_id}

If you have already paid, please ignore this message and reply with your payment confirmation.

Need help? Reply to this email and our team will assist you within 2 hours.

Best regards,
BingDashan Team
"""
    return subject, body

def send_email(to_email, subject, body, dry_run=True):
    """Send email (dry run mode by default)."""
    if dry_run:
        print(f"[DRY RUN] Would send to {to_email}: {subject}")
        return True
    
    # Real SMTP config - fill in later
    smtp_host = os.environ.get("SMTP_HOST", "smtp.example.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    from_addr = os.environ.get("FROM_EMAIL", "")
    
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_addr, [to_email], msg.as_string())
        print(f"[SENT] Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send to {to_email}: {e}")
        return False

def main():
    print("=" * 60)
    print("BingDashan Auto-Outreach Script v3")
    print("=" * 60)
    
    # Load data
    db = load_db()
    pending = get_pending_orders(db)
    logs = load_outreach_log()
    
    print(f"\nTotal orders: {len(db.get('orders', []))}")
    print(f"Pending orders: {len(pending)}")
    print(f"Previous outreach logs: {len(logs)}")
    
    if not pending:
        print("\nNo pending orders to remind.")
        return
    
    total_amount = sum(o.get("amount_cny", o.get("amount", 0)) for o in pending)
    print(f"Total pending amount: ¥{total_amount:,.2f}")
    
    # Process each pending order
    sent = 0
    skipped = 0
    
    for order in pending:
        oid = order.get("id", "")
        customer_email = order.get("customer_email", order.get("email", ""))
        customer_name = order.get("customer_name", order.get("name", "Customer"))
        
        if not customer_email:
            print(f"\n⚠️  Order {oid}: No email found, skipping")
            skipped += 1
            continue
        
        if not should_remind(order, logs):
            print(f"\n✓  Order {oid}: Already reminded, skipping")
            skipped += 1
            continue
        
        subject, body = build_reminder_email(order)
        print(f"\n📧 Reminding {customer_name} ({customer_email}): {subject}")
        
        if send_email(customer_email, subject, body, dry_run=True):
            # Log the action
            log_entry = {
                "order_id": oid,
                "type": "reminder_sent",
                "to": customer_email,
                "subject": subject,
                "amount": order.get("amount_cny", order.get("amount", 0)),
                "timestamp": datetime.now().isoformat()
            }
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            sent += 1
    
    print(f"\n{'=' * 60}")
    print(f"Summary: {sent} reminders queued, {skipped} skipped")
    print(f"Potential revenue recovery: ¥{sum(o.get('amount_cny', o.get('amount', 0)) for o in pending[:sent]):,.2f}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()

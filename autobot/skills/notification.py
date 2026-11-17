#!/usr/bin/env python3
"""Notification Skill — 多渠道通知系统
参考: AWS SNS + Telegram Bot API + 企业微信 Webhook
"""
from __future__ import annotations
import json
import smtplib
import ssl
import urllib.request
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
from typing import Any
import os


# ─── 配置（从环境变量读取）─────────────────────────────────────────────────────
class NotifyConfig:
    smtp_host = os.environ.get("SMTP_HOST", "smtp.qq.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    wechat_webhook = os.environ.get("WECHAT_WORK_WEBHOOK", "")
    dingtalk_webhook = os.environ.get("DINGTALK_WEBHOOK", "")
    slack_webhook = os.environ.get("SLACK_WEBHOOK", "")
    alert_email = os.environ.get("ALERT_EMAIL", "")


def _get_secret(key: str, default: str = "") -> str:
    return os.environ.get(key, default) or getattr(NotifyConfig, key.lower(), default)


# ─── 邮件发送 ───────────────────────────────────────────────────────────────────
def send_email(to: str, subject: str, body_html: str,
               smtp_user: str | None = None, smtp_pass: str | None = None) -> bool:
    user = smtp_user or _get_secret("SMTP_USER")
    passwd = smtp_pass or _get_secret("SMTP_PASS")
    if not user or not passwd:
        raise RuntimeError("SMTP_USER / SMTP_PASS not configured")

    msg = MIMEText(body_html, "html", "utf-8")
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(NotifyConfig.smtp_host, NotifyConfig.smtp_port, context=ctx, timeout=30) as s:
        s.login(user, passwd)
        s.sendmail(user, [to], msg.as_string())
    return True


# ─── 企业微信 Webhook ──────────────────────────────────────────────────────────
def send_wechat(content: str, webhook_url: str | None = None, msg_type: str = "text") -> bool:
    url = webhook_url or _get_secret("WECHAT_WORK_WEBHOOK")
    if not url:
        print("[notify] WECHAT_WORK_WEBHOOK not set, skipping")
        return False
    payload = {"msgtype": msg_type, msg_type: {"content": content}}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            ok = result.get("errcode") == 0
            if not ok:
                print(f"[notify] WeChat error: {result.get('errmsg')}")
            return ok
    except Exception as e:
        print(f"[notify] WeChat send failed: {e}")
        return False


# ─── Slack Webhook ──────────────────────────────────────────────────────────────
def send_slack(text: str, webhook_url: str | None = None) -> bool:
    url = webhook_url or _get_secret("SLACK_WEBHOOK")
    if not url:
        return False
    data = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[notify] Slack error: {e}")
        return False


# ─── 便捷通知函数 ───────────────────────────────────────────────────────────────
def notify_payment_received(ref: str, amount: float, details: str = ""):
    """收款到账通知"""
    subject = f"[丙大山] 新收款 ¥{amount:.0f} · ref={ref}"
    body = f"""<div style='font-family:sans-serif;max-width:480px;margin:auto'>
      <h2 style='color:#16a34a'>💰 新收款确认</h2>
      <table style='border-collapse:collapse'>
        <tr><td><b>金额</b></td><td>¥{amount:.2f}</td></tr>
        <tr><td><b>Ref</b></td><td>{ref}</td></tr>
        <tr><td><b>时间</b></td><td>{datetime.now().strftime('%Y-%m-%d %H:%M')}</td></tr>
      </table>
      {f'<p>{details}</p>' if details else ''}
      <p style='color:#888;font-size:12px'>丙大山收款系统自动通知</p>
    </div>"""
    target = _get_secret("ALERT_EMAIL")
    if target:
        send_email(target, subject, body)
    send_wechat(f"💰 新收款: ¥{amount:.0f} · ref={ref} {details}")


def notify_collection_sent(ref: str, amount: float, message_preview: str):
    """催款消息已发出"""
    preview = message_preview[:60] + "..." if len(message_preview) > 60 else message_preview
    send_wechat(f"📨 催款已发: ref={ref} · ¥{amount:.0f}\n{preview}")


def notify_makefun_result(competition: str, submission_id: str, status: str, score: float | None = None):
    """make.fun 提交结果通知"""
    emoji = "✅" if status == "passed" else ("❌" if status == "failed" else "⏳")
    detail = f" Score: {score}%" if score else ""
    send_wechat(f"{emoji} make.fun 提交: {competition} {submission_id[:12]}{detail}")


def notify_fiverr_gig_published(username: str, gig_url: str, gig_title: str):
    """Fiverr Gig 发布通知"""
    send_wechat(f"🎉 Fiverr Gig 已发布!\n{gig_title}\n{gig_url}")


def notify_task_complete(task_name: str, ok: bool, duration_ms: float):
    """通用任务完成通知"""
    emoji = "✅" if ok else "❌"
    send_wechat(f"{emoji} AutoBot: {task_name} ({duration_ms:.0f}ms)")


from datetime import datetime


if __name__ == "__main__":
    print("Notification skill loaded.")
    print(f"  SMTP: {NotifyConfig.smtp_host}:{NotifyConfig.smtp_port}")
    print(f"  WeChat webhook: {'set' if NotifyConfig.wechat_webhook else 'NOT SET'}")

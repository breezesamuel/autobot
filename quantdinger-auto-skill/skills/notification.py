#!/usr/bin/env python3
"""notification skill — 多渠道通知发送：邮件/企业微信/Webhook"""

from __future__ import annotations
import json
import os
import smtplib
import ssl
import urllib.request
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
from typing import Any


# ─── SMTP 配置（从环境变量读取）────────────────────────────────────────────────
SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465


def send_email(to: str, subject: str, body_html: str,
               smtp_user: str | None = None, smtp_pass: str | None = None) -> bool:
    """通过 SMTP 发送邮件（SSL）"""
    user = smtp_user or get_env_secret("SMTP_USER")
    passwd = smtp_pass or get_env_secret("SMTP_PASS")
    if not user or not passwd:
        raise RuntimeError("SMTP_USER / SMTP_PASS not configured")

    msg = MIMEText(body_html, "html", "utf-8")
    msg["From"] = user
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=30) as s:
        s.login(user, passwd)
        s.sendmail(user, [to], msg.as_string())
    return True


def send_wechat_webhook(webhook_url: str, content: str,
                        msg_type: str = "text") -> bool:
    """通过企业微信群机器人 Webhook 发送消息"""
    payload = {
        "msgtype": msg_type,
        msg_type: {"content": content} if msg_type == "text" else {},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            return result.get("errcode") == 0
    except Exception as e:
        print(f"WeChat webhook error: {e}")
        return False


def send_dingtalk_webhook(webhook_url: str, content: str) -> bool:
    """钉钉群机器人 Webhook"""
    payload = {
        "msgtype": "text",
        "text": {"content": content},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            return result.get("errcode") == 0
    except Exception as e:
        print(f"DingTalk webhook error: {e}")
        return False


def send_slack_webhook(webhook_url: str, text: str) -> bool:
    """Slack Incoming Webhook"""
    payload = {"text": text}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Slack webhook error: {e}")
        return False


# ─── 便捷函数 ──────────────────────────────────────────────────────────────────
def notify_payment_received(ref: str, amount: float, channel: str = "email"):
    """收款到账通知"""
    subject = f"[丙大山] 新收款 ¥{amount:.0f} · ref={ref}"
    body = f"""<div style='font-family:sans-serif;max-width:480px;margin:auto'>
      <h2 style='color:#16a34a'>💰 新收款确认</h2>
      <table style='border-collapse:collapse'>
        <tr><td><b>金额</b></td><td>¥{amount:.2f}</td></tr>
        <tr><td><b>Ref</b></td><td>{ref}</td></tr>
        <tr><td><b>时间</b></td><td>{datetime.now().strftime('%Y-%m-%d %H:%M')}</td></tr>
      </table>
      <p style='color:#888;font-size:12px'>丙大山收款系统自动通知</p>
    </div>"""
    target = get_env_secret("ALERT_EMAIL")
    if target:
        send_email(target, subject, body)
    # 同时推送到企业微信群
    webhook = get_env_secret("WECHAT_WORK_WEBHOOK")
    if webhook:
        send_wechat_webhook(webhook, f"💰 新收款: ¥{amount:.0f} · ref={ref}")


def notify_collection_sent(ref: str, amount: float, message_text: str):
    """催款消息已发出通知"""
    webhook = get_env_secret("WECHAT_WORK_WEBHOOK")
    if webhook:
        send_wechat_webhook(webhook,
                            f"📨 催款已发: ref={ref} · ¥{amount:.0f}\n{message_text[:80]}...")


def notify_makefun_submission(competition: str, entry_id: str, status: str, score: float | None = None):
    """make.fun 提交结果通知"""
    webhook = get_env_secret("WECHAT_WORK_WEBHOOK")
    if webhook:
        msg = f"🏆 make.fun 提交结果: {competition}"
        if status == "passed":
            msg += f" ✅ Score: {score}%" if score else " ✅ Passed"
        elif status == "failed":
            msg += " ❌ Failed"
        send_wechat_webhook(webhook, msg)


# ─── Secrets 管理 ──────────────────────────────────────────────────────────────
_ENV_CACHE: dict[str, str] = {}

def get_env_secret(key: str) -> str | None:
    """安全读取环境变量，带缓存"""
    if key in _ENV_CACHE:
        return _ENV_CACHE[key]
    val = os.environ.get(key)
    if val:
        _ENV_CACHE[key] = val
    return val


def load_secrets_from_file(path: str | Path) -> dict:
    """从 .env 文件加载密钥"""
    secrets = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            secrets[k.strip()] = v.strip().strip('"').strip("'")
    _ENV_CACHE.update(secrets)
    return secrets


if __name__ == "__main__":
    print("notification module loaded")
    print(f"SMTP host: {SMTP_HOST}:{SMTP_PORT}")

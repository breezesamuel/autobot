#!/usr/bin/env python3
"""Notification Dispatcher — 统一通知入口，对接多种渠道"""
from __future__ import annotations
import asyncio
from typing import Any
from skills.notification import (
    send_email, send_wechat, send_slack,
    notify_payment_received, notify_collection_sent,
    notify_makefun_result, notify_fiverr_gig_published, notify_task_complete,
)
from skills.monitoring import mark_collection_sent, mark_fiverr_gig_published as mark_gig


class NotificationDispatcher:
    """统一通知分发器 — 支持多渠道并行发送"""

    def __init__(self):
        self._channels = {"wechat": True, "email": False, "slack": False}

    def enable_channel(self, channel: str):
        self._channels[channel] = True

    async def dispatch(self, event_type: str, **kwargs):
        """根据事件类型自动选择合适的通知渠道"""
        handlers = {
            "payment_received": self._on_payment_received,
            "collection_sent": self._on_collection_sent,
            "makefun_result": self._on_makefun_result,
            "fiverr_published": self._on_fiverr_published,
            "task_complete": self._on_task_complete,
            "health_alert": self._on_health_alert,
        }
        handler = handlers.get(event_type)
        if handler:
            await handler(**kwargs)
        else:
            print(f"[notify] Unknown event type: {event_type}")

    async def _on_payment_received(self, ref: str, amount: float, details: str = ""):
        await asyncio.gather(
            asyncio.to_thread(notify_payment_received, ref, amount, details),
            asyncio.to_thread(mark_collection_sent, ref, amount),
        )

    async def _on_collection_sent(self, ref: str, amount: float, message_preview: str):
        notify_collection_sent(ref, amount, message_preview)

    async def _on_makefun_result(self, competition: str, submission_id: str,
                                 status: str, score: float | None = None):
        notify_makefun_result(competition, submission_id, status, score)

    async def _on_fiverr_published(self, username: str, gig_url: str, gig_title: str):
        notify_fiverr_gig_published(username, gig_url, gig_title)
        mark_gig(username, gig_url)

    async def _on_task_complete(self, task_name: str, ok: bool, duration_ms: float):
        notify_task_complete(task_name, ok, duration_ms)

    async def _on_health_alert(self, check_name: str, ok: bool, error: str = ""):
        emoji = "✅" if ok else "🔴"
        msg = f"{emoji} Health check: {check_name}"
        if error:
            msg += f"\nError: {error[:100]}"
        send_wechat(msg)


# 全局单例
dispatcher = NotificationDispatcher()


async def notify(event_type: str, **kwargs):
    """便捷函数：发送通知"""
    await dispatcher.dispatch(event_type, **kwargs)


if __name__ == "__main__":
    print("NotificationDispatcher loaded.")

#!/usr/bin/env python3
"""AutoBot Core — 主调度器 + 任务编排引擎"""

from __future__ import annotations
import asyncio
import json
import signal
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("autobot")


@dataclass
class TaskResult:
    task: str
    ok: bool
    duration_ms: float = 0
    output: Any = None
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "ok": self.ok,
            "duration_ms": self.duration_ms,
            "output": str(self.output) if self.output else None,
            "error": self.error,
        }


@dataclass
class SchedulerJob:
    name: str
    fn: Callable
    cron_expr: str  # "@daily", "@hourly", "0 8 * * *"
    enabled: bool = True
    last_run: str = ""
    next_run: str = ""


class AutoBot:
    """核心编排引擎 — 支持定时任务 + 一键触发 + 状态追踪"""

    def __init__(self, workdir: str | Path = "."):
        self.workdir = Path(workdir)
        self.jobs: list[SchedulerJob] = []
        self.results: dict[str, TaskResult] = {}
        self._running = False
        self._load_state()

    def _state_path(self) -> Path:
        return self.workdir / ".autobot_state.json"

    def _load_state(self):
        p = self._state_path()
        if p.exists():
            try:
                self.results = json.load(open(p))
                log.info(f"Loaded {len(self.results)} previous results")
            except Exception:
                self.results = {}

    def _save_state(self):
        # Convert TaskResult objects to dicts for JSON serialization
        serializable = {}
        for k, v in self.results.items():
            if hasattr(v, 'to_dict'):
                serializable[k] = v.to_dict()
            else:
                serializable[k] = v
        self._state_path().write_text(
            json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def on_cron(self, expr: str):
        """装饰器：注册定时任务"""
        def decorator(fn: Callable):
            self.jobs.append(SchedulerJob(name=fn.__name__, fn=fn, cron_expr=expr))
            log.info(f"Registered cron job: {fn.__name__} @ {expr}")
            return fn
        return decorator

    def on_event(self, name: str):
        """装饰器：注册事件处理器"""
        def decorator(fn: Callable):
            if not hasattr(self, "_events"):
                self._events = {}
            self._events[name] = fn
            log.info(f"Registered event handler: {name}")
            return fn
        return decorator

    async def run_job(self, job: SchedulerJob) -> TaskResult:
        t0 = time.monotonic()
        try:
            if asyncio.iscoroutinefunction(job.fn):
                result = await job.fn()
            else:
                result = job.fn()
            ms = (time.monotonic() - t0) * 1000
            job.last_run = datetime.now(timezone.utc).isoformat()
            r = TaskResult(task=job.name, ok=True, duration_ms=ms, output=result)
            log.info(f"[OK] {job.name} → {ms:.0f}ms")
            return r
        except Exception as e:
            ms = (time.monotonic() - t0) * 1000
            r = TaskResult(task=job.name, ok=False, duration_ms=ms, error=str(e))
            log.error(f"[FAIL] {job.name}: {e}")
            return r

    async def run_all_jobs(self) -> dict[str, TaskResult]:
        """执行所有就绪的任务"""
        now = datetime.now(timezone.utc)
        results = {}
        for job in self.jobs:
            if not job.enabled:
                continue
            if self._should_run(job, now):
                r = await self.run_job(job)
                results[job.name] = r
                self.results[job.name] = r
        self._save_state()
        return results

    def _should_run(self, job: SchedulerJob, now: datetime) -> bool:
        expr = job.cron_expr
        if expr == "@daily":
            if not job.last_run:
                return True
            last = datetime.fromisoformat(job.last_run.replace("Z", "+00:00"))
            return last.date() < now.date()
        elif expr == "@every_6h":
            if not job.last_run:
                return True
            last = datetime.fromisoformat(job.last_run.replace("Z", "+00:00"))
            return (now - last).total_seconds() >= 6 * 3600
        elif expr == "@on_boot":
            return True
        return False

    def trigger(self, name: str, **kwargs) -> asyncio.Task:
        """手动触发某个已注册的handler"""
        handler = getattr(self, f"_handle_{name}", None) or self._events.get(name)
        if not handler:
            raise ValueError(f"No handler for event: {name}")
        if asyncio.iscoroutinefunction(handler):
            return asyncio.create_task(handler(**kwargs))
        return asyncio.create_task(asyncio.to_thread(handler, **kwargs))

    def status(self) -> dict:
        return {
            "workdir": str(self.workdir),
            "total_jobs": len(self.jobs),
            "enabled_jobs": sum(1 for j in self.jobs if j.enabled),
            "recent_results": {k: {"ok": v.ok, "duration_ms": v.duration_ms,
                                    "error": v.error[:80]} for k, v in list(self.results.items())[-10:]},
        }


# ─── 全局单例 ──────────────────────────────────────────────────────────────────
_bot: Optional[AutoBot] = None


def get_bot() -> AutoBot:
    global _bot
    if _bot is None:
        _bot = AutoBot(Path(__file__).parent)
    return _bot


if __name__ == "__main__":
    bot = AutoBot()

    @bot.on_cron("@daily")
    async def daily_collection():
        from skills.collection import run_collection_workflow
        return await run_collection_workflow()

    @bot.on_cron("@every_6h")
    async def hourly_check():
        from skills.monitoring import health_check
        return health_check()

    print("AutoBot initialized. Use `python autobot.py <command>` to run.")

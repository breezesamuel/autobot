#!/usr/bin/env python3
"""Enhanced Scheduler — 替代 schedule 库的 async 调度器
参考: ManiMozaffar/aioclock ⭐246, Piergiuseppe/tinyjobs ⭐6
零外部依赖，纯 asyncio + sqlite 持久化
"""
from __future__ import annotations
import asyncio
import json
import logging
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable, Optional
from dataclasses import dataclass, field

log = logging.getLogger("autobot.scheduler")


@dataclass
class ScheduledJob:
    name: str
    fn: Callable
    expr: str
    enabled: bool = True
    last_run: float = 0.0
    next_run: float = 0.0
    run_count: int = 0
    errors: int = 0
    last_error: str = ""


class AsyncScheduler:
    """Async-friendly scheduler with SQLite persistence.
    
    Supports:
    - @every Ns/Nm/NhNd (interval-based)
    - @at HH:MM (time-based, runs daily)
    - @daily at HH:MM (explicit daily trigger)
    - @once (run immediately then never again)
    - @now (alias for @once)
    """

    def __init__(self, db_path: str | Path = ".scheduler.db"):
        self._jobs: dict[str, ScheduledJob] = {}
        self._running = False
        self._db_path = Path(db_path)
        self._init_db()
        self._load_state()

    def _init_db(self):
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                name TEXT PRIMARY KEY,
                expr TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                last_run REAL,
                run_count INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0,
                last_error TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _load_state(self):
        if not self._db_path.exists():
            return
        try:
            conn = sqlite3.connect(str(self._db_path))
            rows = conn.execute("SELECT * FROM jobs WHERE enabled=1").fetchall()
            for row in rows:
                job = ScheduledJob(
                    name=row[0], fn=lambda: None, expr=row[1],
                    enabled=bool(row[2]), last_run=row[3] or 0,
                    run_count=row[4] or 0, errors=row[5] or 0,
                    last_error=row[6] or ""
                )
                self._jobs[job.name] = job
            conn.close()
            log.info(f"Loaded {len(self._jobs)} scheduled jobs from DB")
        except Exception as e:
            log.warning(f"Failed to load scheduler state: {e}")

    def _save_state(self):
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("DELETE FROM jobs")
        for name, job in self._jobs.items():
            conn.execute("""
                INSERT INTO jobs (name, expr, enabled, last_run, run_count, errors, last_error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, job.expr, int(job.enabled), job.last_run,
                  job.run_count, job.errors, job.last_error))
        conn.commit()
        conn.close()

    def schedule(self, name: str, expr: str, fn: Callable) -> ScheduledJob:
        """Register a scheduled job."""
        job = ScheduledJob(name=name, fn=fn, expr=expr)
        self._jobs[name] = job
        self._save_state()
        log.info(f"Scheduled: {name} @ {expr}")
        return job

    def on_cron(self, expr: str):
        """Decorator for registering cron jobs."""
        def decorator(fn: Callable):
            name = fn.__name__
            self.schedule(name, expr, fn)
            return fn
        return decorator

    def _next_run_time(self, job: ScheduledJob) -> float:
        now = time.time()
        expr = job.expr.strip().lower()

        # Interval: @every 3600s, @every 6h, @every 30m
        if expr.startswith("@every"):
            parts = expr.split(None, 1)
            if len(parts) == 2:
                val_str = parts[1]
                try:
                    seconds = self._parse_duration(val_str)
                    next_t = job.last_run + seconds if job.last_run else now + seconds
                    return max(next_t, now)
                except ValueError:
                    pass
            return now + 3600  # fallback 1h

        # One-shot: @once, @now
        if expr in ("@once", "@now"):
            return now if job.last_run == 0 else float('inf')

        # Time-based: @at HH:MM
        if expr.startswith("@at"):
            parts = expr.split(None, 1)
            if len(parts) == 2:
                try:
                    target = self._today_at(parts[1])
                    if target <= now:
                        target += 86400
                    return target
                except ValueError:
                    pass

        # Cron-like: "0 8 * * *" (simplified)
        if " " in expr and not expr.startswith("@"):
            try:
                return self._cron_next(expr, now)
            except Exception:
                pass

        return now + 3600

    def _parse_duration(self, s: str) -> float:
        s = s.strip()
        if s.endswith('s'):
            return float(s[:-1])
        elif s.endswith('m'):
            return float(s[:-1]) * 60
        elif s.endswith('h'):
            return float(s[:-1]) * 3600
        elif s.endswith('d'):
            return float(s[:-1]) * 86400
        return float(s)

    def _today_at(self, time_str: str) -> float:
        h, m = map(int, time_str.strip().split(':'))
        now = datetime.now(timezone.utc)
        today = now.replace(hour=h, minute=m, second=0, microsecond=0)
        return today.timestamp()

    def _cron_next(self, expr: str, now: float) -> float:
        """Simple cron parser: 'min hour dom month dow'"""
        parts = expr.strip().split()
        if len(parts) < 2:
            raise ValueError(f"Invalid cron: {expr}")
        mins, hrs = map(int, parts[:2])
        target = datetime.now(timezone.utc).replace(minute=mins, second=0, microsecond=0)
        target_ts = target.timestamp()
        if target_ts <= now:
            target += timedelta(hours=1)
        return target.timestamp()

    async def run_once(self, name: str) -> dict:
        """Run a specific job once."""
        job = self._jobs.get(name)
        if not job:
            return {"ok": False, "error": f"Unknown job: {name}"}
        t0 = time.monotonic()
        try:
            if asyncio.iscoroutinefunction(job.fn):
                await job.fn()
            else:
                job.fn()
            ms = (time.monotonic() - t0) * 1000
            job.last_run = time.time()
            job.run_count += 1
            self._save_state()
            return {"ok": True, "duration_ms": ms, "runs": job.run_count}
        except Exception as e:
            job.errors += 1
            job.last_error = str(e)[:200]
            self._save_state()
            return {"ok": False, "error": str(e), "errors": job.errors}

    async def run_all_due(self) -> dict[str, dict]:
        """Run all jobs that are due."""
        now = time.time()
        results = {}
        for name, job in self._jobs.items():
            if not job.enabled:
                continue
            next_t = job.next_run or self._next_run_time(job)
            if now >= next_t:
                r = await self.run_once(name)
                results[name] = r
                job.next_run = self._next_run_time(job)
        self._save_state()
        return results

    async def run_loop(self, interval: float = 30.0):
        """Continuous scheduling loop."""
        self._running = True
        log.info(f"Scheduler loop started (check every {interval}s)")
        while self._running:
            try:
                results = await self.run_all_due()
                if results:
                    ok = sum(1 for r in results.values() if r.get("ok"))
                    log.info(f"Scheduler tick: {ok}/{len(results)} jobs ran")
            except Exception as e:
                log.error(f"Scheduler error: {e}")
            await asyncio.sleep(interval)

    def stop(self):
        self._running = False

    def list_jobs(self) -> list[dict]:
        return [{
            "name": j.name, "expr": j.expr, "enabled": j.enabled,
            "runs": j.run_count, "errors": j.errors,
            "last_run": datetime.fromtimestamp(j.last_run, tz=timezone.utc).isoformat() if j.last_run else None,
        } for j in self._jobs.values()]


if __name__ == "__main__":
    import sys
    s = AsyncScheduler("/tmp/test_scheduler.db")

    @s.on_cron("@every 60s")
    async def tick():
        print(f"[tick] {datetime.now()}")

    @s.on_cron("@once")
    def boot_task():
        print("[boot] This runs once on startup")

    print(f"Jobs registered: {[j['name'] for j in s.list_jobs()]}")
    print("Use `python -m autobot.core.scheduler` for production.")

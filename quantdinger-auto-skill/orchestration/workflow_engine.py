#!/usr/bin/env python3
"""Orchestration Layer — 工作流引擎 + Cron 调度"""

from __future__ import annotations
import asyncio
import json
import signal
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable


# ─── Workflow Engine ───────────────────────────────────────────────────────────
class WorkflowStep:
    """工作流步骤"""
    def __init__(self, name: str, fn: Callable, on_error: str = "stop"):
        self.name = name
        self.fn = fn
        self.on_error = on_error  # "stop" | "skip" | "retry"
        self.result: Any = None
        self.duration_ms: float = 0
        self.error: str | None = None

    async def run(self, context: dict) -> dict:
        t0 = time.monotonic()
        try:
            if asyncio.iscoroutinefunction(self.fn):
                self.result = await self.fn(context)
            else:
                self.result = self.fn(context)
            self.duration_ms = (time.monotonic() - t0) * 1000
            return {"step": self.name, "ok": True, "duration_ms": self.duration_ms, "result": self.result}
        except Exception as e:
            self.error = str(e)
            self.duration_ms = (time.monotonic() - t0) * 1000
            if self.on_error == "stop":
                raise
            elif self.on_error == "retry":
                return await self.run(context)
            else:  # skip
                return {"step": self.name, "ok": False, "error": str(e)}


class WorkflowEngine:
    """多步骤工作流执行器"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self._steps: list[WorkflowStep] = []
        self._context: dict[str, Any] = {}

    def add_step(self, step: WorkflowStep):
        self._steps.append(step)

    def add_async(self, name: str, fn: Callable, on_error: str = "stop"):
        self._steps.append(WorkflowStep(name, fn, on_error))

    async def run(self, initial_context: dict | None = None) -> dict:
        ctx = initial_context or {}
        results = []
        failed_at: str | None = None

        for step in self._steps:
            r = await step.run(ctx)
            results.append(r)
            ctx.update(getattr(step, 'result', {}) or {})
            if not r["ok"]:
                failed_at = step.name
                break

        return {
            "workflow": self.name,
            "completed_steps": len([r for r in results if r["ok"]]),
            "total_steps": len(self._steps),
            "failed_at": failed_at,
            "results": results,
            "final_context": ctx,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }

    def export_summary(self) -> str:
        lines = [f"# Workflow: {self.name}", f"Description: {self.description}", ""]
        for s in self._steps:
            status = "✅" if s.result is not None else ("❌" if s.error else "⏳")
            lines.append(f"  {status} {s.name} ({s.duration_ms:.0f}ms)")
            if s.error:
                lines.append(f"      Error: {s.error}")
        return "\n".join(lines)


# ─── Built-in Workflows ────────────────────────────────────────────────────────
def make_collection_workflow(billing_dir: str, notify_webhook: str = "") -> WorkflowEngine:
    """自动收款工作流：扫描待收 → 生成消息 → 发送通知"""
    from skills.billing import scan_pending_orders, export_messages
    from skills.notification import notify_collection_sent

    wf = WorkflowEngine("auto_collection", "自动扫描待收订单并生成催款消息")

    async def step1_scan(ctx):
        orders = scan_pending_orders(billing_dir)
        return {"pending_orders": orders, "total_amount": sum(o["amount"] for o in orders)}

    async def step2_generate(ctx):
        result = export_messages(ctx["pending_orders"])
        return {"messages_generated": result["total_pending"],
                "total_yuan": result["total_amount_yuan"]}

    async def step3_notify(ctx):
        if notify_webhook:
            from skills.notification import send_wechat_webhook
            msg = f"📊 收款扫描完成: {ctx['messages_generated']} 条待收，总计 ¥{ctx['total_yuan']:.0f}"
            send_wechat_webhook(notify_webhook, msg)
        return {"notified": True}

    wf.add_async("scan_pending", step1_scan)
    wf.add_async("generate_messages", step2_generate)
    wf.add_async("send_notification", step3_notify, on_error="skip")
    return wf


def make_makefun_submission_workflow(repo_dir: str, competition: str,
                                     keypair_path: str, title: str = "") -> WorkflowEngine:
    """make.fun entry 提交工作流"""
    from skills.makefun import MakeFunClient

    wf = WorkflowEngine(f"makefun_submit_{competition}", f"提交 {competition} 竞赛 entry")

    async def step1_check_quota(ctx):
        client = MakeFunClient(keypair_path)
        quota = client.check_quota(competition)
        remaining = quota.get("remaining_today", 0)
        if remaining <= 0:
            return {"can_submit": False, "reason": "quota_exhausted", "resets_at": quota.get("next_reset")}
        return {"can_submit": True, "quota_remaining": remaining}

    async def step2_validate_repo(ctx):
        from skills.makefun import MakeFunClient
        errors = MakeFunClient.validate_entry_requirements(repo_dir, ["main.py", ".makefun/session.json"])
        return {"valid": len(errors) == 0, "missing_files": errors}

    async def step3_git_push(ctx):
        import subprocess
        result = subprocess.run(["git", "-C", repo_dir, "push", "origin", "main"],
                               capture_output=True, text=True, timeout=30)
        sha = subprocess.run(["git", "-C", repo_dir, "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
        return {"pushed": result.returncode == 0, "sha": sha}

    async def step4_submit(ctx):
        if not ctx.get("can_submit"):
            return {"submitted": False, "skipped": True, "reason": ctx.get("reason")}
        import subprocess, tempfile, os
        # 调用 kit bundle + submit
        kit_dir = os.path.join(repo_dir, "..", "tiny-chess-01-kit")
        bundle_cmd = [
            "node", os.path.join(kit_dir, "cli", "makefun.mjs"),
            "bundle", "--repo", ".", "--session", os.path.join(repo_dir, ".makefun", "session.json"),
            "--effort", "default", "--out", os.path.join(repo_dir, "..", "transcripts.tar.gz"),
            "--no-discover", "--harness", "quantdinger-auto-skill",
            "--harness-version", "1.0.0", "--provider", "anthropic",
            "--model", "claude-sonnet-4-20250514",
            "--system-prompt", os.path.join(repo_dir, ".makefun", "system-prompt.txt"),
            "--instructions", "withheld:no-instruction-files",
            "--mcp", "none", "--compress-source", "main.py=engine.py",
        ]
        r = subprocess.run(bundle_cmd, cwd=repo_dir, capture_output=True, text=True, timeout=120)
        return {"bundle_ok": r.returncode == 0, "bundle_stderr": r.stderr[-200:]}

    wf.add_async("check_quota", step1_check_quota)
    wf.add_async("validate_repo", step2_validate_repo)
    wf.add_async("git_push", step3_git_push)
    wf.add_async("bundle_and_submit", step4_submit)
    return wf


# ─── Cron Scheduler ────────────────────────────────────────────────────────────
class CronScheduler:
    """简单 Cron 调度器"""

    def __init__(self):
        self._jobs: list[dict] = []
        self._running = False

    def add_job(self, name: str, cron_expr: str, fn: Callable, args: dict = None):
        """添加定时任务（简化版：支持 @daily, @hourly, @every N）"""
        self._jobs.append({
            "name": name, "cron": cron_expr, "fn": fn,
            "args": args or {}, "last_run": None, "next_run": None,
        })

    async def run_once(self, job: dict) -> dict:
        """执行单次任务"""
        t0 = time.monotonic()
        try:
            if asyncio.iscoroutinefunction(job["fn"]):
                result = await job["fn"](**job["args"])
            else:
                result = job["fn"](**job["args"])
            duration = (time.monotonic() - t0) * 1000
            job["last_run"] = datetime.now(timezone.utc).isoformat()
            return {"job": job["name"], "ok": True, "duration_ms": duration, "result": result}
        except Exception as e:
            return {"job": job["name"], "ok": False, "error": str(e)}

    async def run_all(self) -> list[dict]:
        """执行所有就绪的任务"""
        now = datetime.now(timezone.utc)
        results = []
        for job in self._jobs:
            if self._should_run(job, now):
                r = await self.run_once(job)
                results.append(r)
        return results

    def _should_run(self, job: dict, now: datetime) -> bool:
        """判断是否应该运行"""
        cron = job["cron"]
        if cron == "@daily":
            if job.get("last_run"):
                last = datetime.fromisoformat(job["last_run"].replace("Z", "+00:00"))
                return last.date() < now.date()
            return True
        elif cron == "@hourly":
            if job.get("last_run"):
                last = datetime.fromisoformat(job["last_run"].replace("Z", "+00:00"))
                return last.hour < now.hour or last.date() < now.date()
            return True
        return False


# ─── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    wf = make_collection_workflow("/opt/bingdashan/data/billing")
    print(wf.export_summary())

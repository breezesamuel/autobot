#!/usr/bin/env python3
"""Monitoring Skill — 系统健康检查 + 定时监控
参考: Prometheus node_exporter + cron-based health checks
"""
from __future__ import annotations
import asyncio
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


async def check_ssh_connectivity(hostname: str = "aliyun") -> dict:
    """检查 SSH 连接到服务器的连通性"""
    try:
        r = subprocess.run(["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
                           hostname, "hostname"],
                          capture_output=True, text=True, timeout=10)
        return {"ok": r.returncode == 0, "hostname": r.stdout.strip(),
                "error": r.stderr.strip()[:100] if r.returncode != 0 else ""}
    except Exception as e:
        return {"ok": False, "error": str(e)[:100]}


async def check_server_billing(billing_dir: str = "/opt/bingdashan/data/billing") -> dict:
    """检查服务器 billing 数据完整性"""
    ssh_cmd = ["ssh", "aliyun", f"ls {billing_dir} 2>/dev/null && echo OK || echo FAIL"]
    try:
        r = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
        files_exist = "OK" in r.stdout
        # Simplified: just check key files exist
        keys = ["manual_pending.tsv", "corporate_899.json", "trial_winback.tsv"]
        results = {}
        for k in keys:
            check = f"test -f {billing_dir}/{k} && echo EXISTS || echo MISSING"
            cr = subprocess.run(["ssh", "aliyun", check], capture_output=True, text=True, timeout=5)
            results[k] = "EXISTS" in cr.stdout
        total_files = sum(results.values())
        return {"ok": total_files == len(keys), "files": results, "total_present": total_files}
    except Exception as e:
        return {"ok": False, "error": str(e)[:100]}


async def check_makefun_quota() -> dict:
    """检查 make.fun quota 状态"""
    kp_path = Path.home() / "makefun-keypair.json"
    if not kp_path.exists():
        return {"ok": False, "error": "keypair not found"}
    try:
        r = subprocess.run(
            ["node", "-e",
             "const c=require('./makefun-keypair.json'); "
             "console.log(JSON.stringify({wallet:(c.length===64?require('crypto').createHash('sha512').update(Buffer.from(c.slice(32))).digest().toString('hex').slice(0,44):'?')}))"],
            capture_output=True, text=True, timeout=10)
        return {"ok": True, "keypair": "found", "note": "quota check requires make.fun API login"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:100]}


async def check_local_python_env() -> dict:
    """检查本地 Python 环境"""
    checks = {}
    # Python version
    try:
        r = subprocess.run(["python", "--version"], capture_output=True, text=True)
        checks["python_version"] = r.stdout.strip()
        checks["python_ok"] = True
    except Exception:
        checks["python_ok"] = False

    # Key packages
    for pkg in ["playwright", "httpx", "schedule"]:
        try:
            __import__(pkg)
            checks[f"{pkg}_installed"] = True
        except ImportError:
            checks[f"{pkg}_installed"] = False

    # Node.js
    try:
        r = subprocess.run(["node", "--version"], capture_output=True, text=True)
        checks["node_version"] = r.stdout.strip()
        checks["node_ok"] = True
    except Exception:
        checks["node_ok"] = False

    # Git
    try:
        r = subprocess.run(["git", "--version"], capture_output=True, text=True)
        checks["git_version"] = r.stdout.strip()
        checks["git_ok"] = True
    except Exception:
        checks["git_ok"] = False

    checks["overall_ok"] = all(v for k, v in checks.items() if k.endswith("_ok"))
    return checks


async def check_fiverr_session() -> dict:
    """检查 Fiverr Seller Onboarding 状态（通过本地进程标记文件）"""
    marker = Path("/tmp/fiverr_onboarding_started.flag")
    result = {"marker_exists": marker.exists()}
    if marker.exists():
        result["started_at"] = marker.stat().st_mtime
    # Check if gig was published
    gig_marker = Path("/tmp/fiverr_gig_published.flag")
    result["gig_published"] = gig_marker.exists()
    if gig_marker.exists():
        try:
            data = json.loads(gig_marker.read_text())
            result["gig_url"] = data.get("url", "")
            result["gig_username"] = data.get("username", "")
        except Exception:
            pass
    return result


def mark_fiverr_gig_published(username: str, gig_url: str):
    """标记 Fiverr Gig 已发布"""
    Path("/tmp/fiverr_gig_published.flag").write_text(
        json.dumps({"username": username, "url": gig_url,
                    "published_at": datetime.now(timezone.utc).isoformat()}),
        encoding="utf-8")
    Path("/tmp/fiverr_onboarding_started.flag").touch()


def mark_collection_sent(ref: str, amount: float):
    """标记某条收款消息已发送"""
    log = Path("/tmp/autobot_collection_log.jsonl")
    entry = {
        "event": "collection_sent",
        "ref": ref,
        "amount": amount,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


async def health_check() -> dict:
    """全量健康检查（供 Cron 调度器调用）"""
    t0 = time.monotonic()
    results = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checks": {},
    }
    results["checks"]["ssh"] = await check_ssh_connectivity()
    results["checks"]["server_billing"] = await check_server_billing()
    results["checks"]["makefun_keypair"] = await check_makefun_quota()
    results["checks"]["python_env"] = await check_local_python_env()
    results["checks"]["fiverr_status"] = await check_fiverr_session()

    all_ok = all(c.get("ok", False) or c.get("overall_ok", True)
                 for c in results["checks"].values())
    results["overall_ok"] = all_ok
    results["duration_ms"] = (time.monotonic() - t0) * 1000
    return results


async def run_monitoring_loop(interval_seconds: int = 3600):
    """持续监控循环（每分钟检查一次）"""
    while True:
        try:
            result = await health_check()
            status_file = Path("/tmp/autobot_health.json")
            status_file.write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                  encoding="utf-8")
            ok_count = sum(1 for c in result["checks"].values()
                          if c.get("ok") or c.get("overall_ok"))
            total = len(result["checks"])
            print(f"[monitor] {result['checked_at']} {ok_count}/{total} OK "
                  f"({result['duration_ms']:.0f}ms)")
        except Exception as e:
            print(f"[monitor] Error: {e}")
        await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    result = asyncio.run(health_check())
    print(json.dumps(result, indent=2, ensure_ascii=False))

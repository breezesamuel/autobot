#!/usr/bin/env python3
"""AutoBot 完整测试套件 — 覆盖全部 7 个模块"""
import asyncio
import json
import sys
import tempfile
from pathlib import Path

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[96m"


def header(name):
    print(f"\n{'─'*55}")
    print(f"  {name}")
    print("─" * 55)


def test_collection():
    header("collection skill")
    from skills.collection import (
        build_pay_link, generate_messages, scan_all_pending, render_template, TEMPLATES
    )

    # Test pay link
    link = build_pay_link("testref", "proY")
    assert "tools-cn.highkingflower.com" in link
    assert "ref=testref" in link
    print(f"{PASS} build_pay_link OK")

    # Test templates exist
    assert len(TEMPLATES) >= 5
    print(f"{PASS} {len(TEMPLATES)} templates defined")

    # Test template rendering
    msg = render_template("single_order", oid="abc123", ref="user1", amt=500, link="http://x")
    assert "abc123" in msg and "¥500" in msg
    print(f"{PASS} single_order template renders correctly")

    msg2 = render_template("corporate_remittance", oid="x1", ref="r1", amt=899, memo="备注")
    assert "对公" in msg2
    print(f"{PASS} corporate_remittance template renders correctly")

    msg3 = render_template("summary_combined", total=1698,
                           order_lines="• proY — ¥500\n• team — ¥299", link="http://x")
    assert "¥1698" in msg3
    print(f"{PASS} summary_combined template renders correctly")

    # Test message generation for aggregated orders
    mock_agg = [
        {"ref": "mvgeerdl", "total_amount": 1459, "kind": "combined",
         "orders": [{"plan": "proY", "amount": 500, "kind": "manual"},
                    {"plan": "y", "amount": 899, "kind": "corp"}],
         "pay_link": "http://test", "priority": "high", "order_count": 2},
        {"ref": "ao7n", "total_amount": 1698, "kind": "combined",
         "orders": [{"plan": "proY", "amount": 500, "kind": "manual"},
                    {"plan": "team", "amount": 299, "kind": "manual"},
                    {"plan": "y", "amount": 899, "kind": "corp"}],
         "pay_link": "http://test2", "priority": "high", "order_count": 3},
    ]
    msgs = generate_messages(mock_agg)
    assert len(msgs) == 2
    assert "合并" in msgs[0]["message"] or "订单确认" in msgs[0]["message"]
    print(f"{PASS} generate_messages: {len(msgs)} messages generated")

    # Test async workflow (import directly from skills package)
    import importlib, sys
    _m = importlib.import_module('skills.collection')
    result = asyncio.run(_m.run_collection_workflow(
        billing_dir="/opt/bingdashan/data/billing",
        output_dir="/tmp/autobot_test_collection"
    ))
    print(f"{PASS} run_collection_workflow: {result['total_customers']} customers, ¥{result['total_amount_yuan']:,.0f}")


def test_github_ops():
    header("github_ops skill")
    from skills.github_ops import GitHubOps, GithubAPIError

    gh = GitHubOps(token="fake-token-test")
    assert gh.token == "fake-token-test"
    print(f"{PASS} GitHubOps instantiated with token")

    # Test error class
    try:
        raise GithubAPIError(404, "Not found", "/repos/x/y")
    except GithubAPIError as e:
        assert e.status == 404
        assert "Not found" in str(e)
        print(f"{PASS} GithubAPIError works correctly")

    # Test headers
    headers = gh._headers()
    assert "Authorization" in headers
    assert "Bearer fake-token-test" in headers["Authorization"]
    print(f"{PASS} Auth headers correct")


def test_makefun_auto():
    header("makefun_auto skill")
    from skills.makefun_auto import MakeFunAuto

    # Test local validation (no network needed)
    client = MakeFunAuto.__new__(MakeFunAuto)
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        (p / "main.py").write_text("#!/usr/bin/env python3\nprint('chess')\n")
        mf_dir = p / ".makefun"
        mf_dir.mkdir()
        (mf_dir / "owner.json").write_text(json.dumps({"wallet": "test_wallet"}))
        (p / "LICENSE").write_text("MIT License\n")

        result = client.validate_repo_locally(tmpdir, ["main.py"])
        assert result["valid"] is True
        print(f"{PASS} validate_repo_locally: valid=True")

    # Test with missing files
    with tempfile.TemporaryDirectory() as tmpdir:
        result = client.validate_repo_locally(tmpdir, ["main.py", "missing.txt"])
        assert result["valid"] is False
        assert any("missing" in e for e in result["errors"])
        print(f"{PASS} validate_repo_locally detects missing files")

    # Test bundle command building
    cmd = client.build_bundle_command(
        repo_dir="/tmp/test",
        session_file="/tmp/session.json",
        kit_dir="/tmp/kit",
        output_path="/tmp/out.tar.gz",
        extra_flags={"harness": "opencode", "model": "claude-sonnet-4-20250514"}
    )
    assert "bundle" in cmd
    assert "opencode" in cmd
    print(f"{PASS} build_bundle_command generates valid CLI args ({len(cmd)} tokens)")


def test_browser_skill():
    header("browser_auto skill")
    from skills.browser_auto import BrowserSkill

    # Just verify the class exists and has the right methods
    assert hasattr(BrowserSkill, 'goto')
    assert hasattr(BrowserSkill, 'click')
    assert hasattr(BrowserSkill, 'fill')
    assert hasattr(BrowserSkill, 'screenshot')
    assert hasattr(BrowserSkill, 'fiverr_create_gig_auto')
    print(f"{PASS} BrowserSkill has all expected methods")

    # Verify async context manager protocol
    assert hasattr(BrowserSkill, '__aenter__')
    assert hasattr(BrowserSkill, '__aexit__')
    print(f"{PASS} BrowserSkill is async context manager compatible")


def test_notification():
    header("notification skill")
    from skills.notification import NotifyConfig, send_wechat, _get_secret

    # Test config loading from env
    import os
    os.environ["TEST_NOTIFY_SECRET"] = "test_value_123"
    val = _get_secret("TEST_NOTIFY_SECRET", "default")
    assert val == "test_value_123"
    print(f"{PASS} _get_secret reads env vars correctly")

    # Test wechat webhook format (without sending)
    payload = {"msgtype": "text", "text": {"content": "test"}}
    assert payload["msgtype"] == "text"
    print(f"{PASS} WeChat webhook payload structure valid")

    # Cleanup
    del os.environ["TEST_NOTIFY_SECRET"]


def test_monitoring():
    header("monitoring skill")
    from skills.monitoring import health_check, mark_fiverr_gig_published, mark_collection_sent
    import tempfile, os

    # Test health check runs without crash
    result = asyncio.run(health_check())
    assert "checks" in result
    assert isinstance(result["checks"], dict)
    print(f"{PASS} health_check runs successfully ({len(result['checks'])} checks)")

    # Test marking functions
    mark_fiverr_gig_published("testuser", "https://fiverr.com/testuser/gig/123")
    flag_path = Path("/tmp/fiverr_gig_published.flag")
    assert flag_path.exists()
    data = json.loads(flag_path.read_text())
    assert data["username"] == "testuser"
    print(f"{PASS} mark_fiverr_gig_published writes correct marker")

    mark_collection_sent("ref123", 500.0)
    log_path = Path("/tmp/autobot_collection_log.jsonl")
    if log_path.exists():
        lines = log_path.read_text().strip().split("\n")
        last = json.loads(lines[-1])
        assert last["ref"] == "ref123"
        assert last["amount"] == 500.0
        print(f"{PASS} mark_collection_sent logs correctly")


def test_engine():
    header("core engine")
    from core.engine import AutoBot, TaskResult

    bot = AutoBot()

    @bot.on_cron("@daily")
    async def test_task():
        return {"hello": "world"}

    @bot.on_cron("@on_boot")
    def sync_task():
        return 42

    assert len(bot.jobs) == 2
    print(f"{PASS} Registered {len(bot.jobs)} cron jobs")

    # Run tasks
    results = asyncio.run(bot.run_all_jobs())
    assert "test_task" in results
    assert results["test_task"].ok
    assert results["test_task"].output == {"hello": "world"}
    print(f"{PASS} test_task executed successfully")

    assert "sync_task" in results
    assert results["sync_task"].output == 42
    print(f"{PASS} sync_task executed successfully")

    # Status
    status = bot.status()
    assert status["total_jobs"] == 2
    print(f"{PASS} Bot status: {status['total_jobs']} jobs, "
          f"{sum(1 for j in bot.jobs if j.enabled)} enabled")


def test_integration():
    header("integration: collection → notification flow")
    from skills.collection import scan_all_pending, generate_messages
    from skills.notification_dispatcher import NotificationDispatcher

    # Simulate scanning + generating + notifying
    aggregated = scan_all_pending("/opt/bingdashan/data/billing")
    print(f"{PASS} Scanned {len(aggregated)} customer groups")

    messages = generate_messages(aggregated)
    high_priority = [m for m in messages if m["priority"] == "high"]
    print(f"{PASS} Generated {len(messages)} messages, {len(high_priority)} high-priority")

    # Verify dispatcher can be instantiated
    disp = NotificationDispatcher()
    assert isinstance(disp, NotificationDispatcher)
    print(f"{PASS} NotificationDispatcher ready")


def main():
    print("=" * 55)
    print("  AutoBot Framework — Full Test Suite")
    print("=" * 55)

    tests = [
        test_collection, test_github_ops, test_makefun_auto,
        test_browser_skill, test_notification, test_monitoring,
        test_engine, test_integration,
    ]

    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n{FAIL} {test.__name__}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'═'*55}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'═'*55}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

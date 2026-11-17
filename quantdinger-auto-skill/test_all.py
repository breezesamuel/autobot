#!/usr/bin/env python3
"""完整测试套件 — 验证所有 skill 模块"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[96m"


def test_header(name):
    print(f"\n{'─'*50}")
    print(f"  {name}")
    print("─" * 50)


def test_billing():
    test_header("billing skill")
    from skills.billing import build_pay_link, generate_message, TEMPLATES

    # Test pay link generation
    link = build_pay_link("testref", "proY")
    assert "tools-cn.highkingflower.com" in link
    assert "ref=testref" in link
    print(f"{PASS} build_pay_link: {link[:60]}...")

    # Test template rendering
    msg = generate_message({"kind": "manual", "plan": "proY", "ref": "mvgeerdl", "amount": 500})
    assert "mvgeerdl" in msg or "¥500" in msg
    print(f"{PASS} generate_message proY: {msg[:80]}...")

    msg2 = generate_message({"kind": "corp", "ref": "ao7n", "amount": 899, "order_id": "abc123"})
    assert "对公" in msg2
    print(f"{PASS} generate_message corp: {msg2[:80]}...")

    msg3 = generate_message({"kind": "trial", "plan": "pro", "ref": "aodm", "amount": 60})
    print(f"  DEBUG msg3={repr(msg3[:100])}")
    assert "体验" in msg3 or "升级" in msg3, f"Trial msg missing keywords: {msg3[:80]}"
    print(f"{PASS} generate_message trial: {msg3[:80]}...")

    print(f"\n{PASS} billing: all 3 message types passed")


def test_github():
    test_header("github skill")
    from skills.github import GitHubClient

    # Test instantiation (no network needed)
    gh = GitHubClient(token="fake-token-for-testing")
    assert gh.token == "fake-token-for-testing"
    print(f"{PASS} GitHubClient instantiated")

    # Test validate_local_repo
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        (p / "main.py").write_text("#!/usr/bin/env python3\nprint('hello')\n")
        errors = GitHubClient.validate_local_repo(tmpdir, ["main.py", "README.md"])
        # README.md missing → should be in errors
        assert "README.md" in errors, f"Expected README.md in errors, got {errors}"
        print(f"{PASS} validate_local_repo: {len(errors)} issues found (expected)")


def test_fiverr():
    test_header("fiverr skill")
    from skills.fiverr import GIG_TEMPLATES, FiverrGigBuilder

    assert len(GIG_TEMPLATES) >= 4
    print(f"{PASS} Found {len(GIG_TEMPLATES)} gig templates")

    builder = FiverrGigBuilder("python_automation")
    data = builder.render_gig_data()
    assert "I will build custom python automation" in data["title"]
    assert data["packages"]["basic"]["price"] == 50
    assert data["packages"]["premium"]["price"] == 300
    print(f"{PASS} python_automation template rendered correctly")

    builder2 = FiverrGigBuilder("discord_bot")
    data2 = builder2.render_gig_data()
    assert "discord" in data2["title"].lower()
    print(f"{PASS} discord_bot template rendered correctly")


def test_makefun():
    test_header("makefun skill")
    from skills.makefun import MakeFunClient

    # Test validation without network
    with tempfile.TemporaryDirectory() as tmpdir:
        p = Path(tmpdir)
        (p / "main.py").write_text("print('chess engine')\n")
        mf_dir = p / ".makefun"
        mf_dir.mkdir()
        (mf_dir / "owner.json").write_text(json.dumps({"wallet": "test_wallet_abc"}))
        (p / "LICENSE").write_text("MIT License\n")

        errors = MakeFunClient.validate_entry_requirements(tmpdir, ["main.py"])
        assert len(errors) == 0, f"Expected 0 errors, got {errors}"
        print(f"{PASS} makefun entry validation passed")


def test_agent():
    test_header("core agent")
    from core.agent import AutoAgent, AgentSession

    session = AgentSession(session_id="test-001")
    session.add_user_message("Hello")
    assert len(session.messages) == 1
    print(f"{PASS} add_user_message works")

    session.add_assistant_message("Hi there!")
    assert len(session.messages) == 2
    assert session.turn_count == 1
    print(f"{PASS} add_assistant_message works, turn_count={session.turn_count}")

    # Test save/load roundtrip
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    session.save(path)
    loaded = AgentSession.load(path)
    assert loaded.session_id == "test-001"
    assert len(loaded.messages) == 2
    print(f"{PASS} save/load roundtrip OK")

    # Test ToolRegistry
    agent = AutoAgent()
    agent.registry.register("echo", lambda x: f"echo:{x}", "Echo tool", {"R"})
    result = agent.run_tool("echo", {"x": "hello"})
    assert result.ok
    assert result.data == "echo:hello"
    print(f"{PASS} ToolRegistry + run_tool works")


def test_notification():
    test_header("notification skill")
    from skills.notification import get_env_secret, load_secrets_from_file

    # Test secret loading from file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("SMTP_USER=test@example.com\nSMTP_PASS=secret123\nWEBHOOK_URL=https://example.com/hook\n")
        path = f.name
    secrets = load_secrets_from_file(path)
    assert secrets.get("SMTP_USER") == "test@example.com"
    assert secrets.get("SMTP_PASS") == "secret123"
    print(f"{PASS} load_secrets_from_file works")

    # Test env lookup
    val = get_env_secret("NONEXISTENT_KEY_12345")
    assert val is None
    print(f"{PASS} get_env_secret returns None for missing key")


def test_workflow():
    test_header("workflow engine")
    from orchestration.workflow_engine import WorkflowEngine, WorkflowStep

    async def step1(ctx):
        return {"step": "scan", "count": 5}

    async def step2(ctx):
        count = ctx.get("count", 0)
        return {"step": "process", "messages": count * 2}

    wf = WorkflowEngine("test_workflow", "Test workflow")
    wf.add_async("scan", step1)
    wf.add_async("process", step2)

    result = asyncio.run(wf.run())
    assert result["completed_steps"] == 2
    assert result["total_steps"] == 2
    assert result["final_context"]["messages"] == 10
    print(f"{PASS} WorkflowEngine: 2/2 steps completed, messages={result['final_context']['messages']}")


def main():
    print("=" * 50)
    print("  QuantDinger Auto-Skill Framework — Test Suite")
    print("=" * 50)

    tests = [test_billing, test_github, test_fiverr, test_makefun, test_agent, test_notification, test_workflow]
    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n{FAIL} {test.__name__}: {e}")

    print(f"\n{'═'*50}")
    print(f"  Results: {passed} passed, {failed} failed")
    print(f"{'═'*50}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

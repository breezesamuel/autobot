#!/usr/bin/env python3
"""AutoBot CLI — 主入口命令"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def cmd_collect(args):
    """生成收款消息包"""
    from skills.collection import run_collection_workflow
    result = asyncio.run(run_collection_workflow(args.billing_dir, args.output))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    txt_path = Path(args.output) / "collection_messages.txt"
    if txt_path.exists():
        print(f"\n📄 TXT: {txt_path}")
        # Print top messages for quick copy
        lines = txt_path.read_text(encoding="utf-8").split("\n")
        in_msg = False
        msg_lines = []
        for line in lines:
            if line.startswith("---"):
                if msg_lines and in_msg:
                    print("".join(msg_lines))
                    print()
                msg_lines = [line + "\n"]
                in_msg = True
            elif in_msg:
                msg_lines.append(line + "\n")


def cmd_health(args):
    """系统健康检查"""
    from skills.monitoring import health_check
    result = asyncio.run(health_check())
    print(json.dumps(result, indent=2, ensure_ascii=False))
    ok_count = sum(1 for c in result["checks"].values()
                   if c.get("ok") or c.get("overall_ok"))
    total = len(result["checks"])
    status = "✅ ALL OK" if result["overall_ok"] else "⚠️ ISSUES FOUND"
    print(f"\n{status} ({ok_count}/{total} checks passed)")


def cmd_makefun(args):
    """make.fun 提交/检查"""
    from skills.makefun_auto import MakeFunAuto
    client = MakeFunAuto(args.keypair)

    if args.action == "validate":
        result = client.validate_repo_locally(args.repo_dir, args.files or ["main.py"])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.action == "quota":
        q = client.check_quota(args.competition)
        print(json.dumps(q, indent=2, ensure_ascii=False))
    elif args.action == "profile":
        p = client.profile()
        print(f"Handle: {p.get('handle', '?')}")
        print(f"Wallet: {client.wallet_address}")
    elif args.action == "submit":
        # Full pipeline submission
        result = client.submit_pipeline(
            competition=args.competition,
            repo_dir=args.repo_dir,
            kit_dir=args.kit_dir,
            title=args.title,
            git_remote=args.git_remote,
            session_file=args.session,
            system_prompt=args.system_prompt,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Unknown action: {args.action}")


def cmd_github(args):
    """GitHub 操作"""
    import os
    from skills.github_ops import GitHubOps
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN required", file=sys.stderr)
        sys.exit(1)
    gh = GitHubOps(token)

    if args.action == "repos":
        repos = gh.list_repos(username=args.username)
        print(f"Total: {len(repos)} repos")
        for r in repos[:10]:
            print(f"  {r['full_name']} · ⭐{r['stargazers_count']} · {r.get('language','-')}")
    elif args.action == "verify_makefun":
        result = gh.verify_makefun_compliance(args.owner, args.repo, args.sha,
                                               args.expected_files or [])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Unknown action: {args.action}")


def cmd_browser(args):
    """浏览器自动化（Fiverr 等）"""
    print("[browser] Use BrowserSkill as async context manager:")
    print("  async with BrowserSkill(headless=False) as bot:")
    print("      await bot.goto('https://www.fiverr.com/seller_onboarding/overview')")
    print("      await bot.fiverr_create_gig_auto(gig_data)")


def cmd_monitor(args):
    """启动持续监控"""
    from skills.monitoring import run_monitoring_loop
    print(f"Starting monitor loop (interval={args.interval}s)...")
    asyncio.run(run_monitoring_loop(args.interval))


def main():
    parser = argparse.ArgumentParser(description="AutoBot — 全自动运营机器人")
    sub = parser.add_subparsers(dest="command")

    # collect
    p_collect = sub.add_parser("collect", help="生成收款消息包")
    p_collect.add_argument("--billing-dir", default="/opt/bingdashan/data/billing")
    p_collect.add_argument("--output", default="/tmp/outreach")
    p_collect.set_defaults(func=cmd_collect)

    # health
    p_health = sub.add_parser("health", help="系统健康检查")
    p_health.set_defaults(func=cmd_health)

    # makefun
    p_mf = sub.add_parser("makefun", help="make.fun 竞赛管理")
    p_mf.add_argument("--keypair", default=str(Path.home() / "makefun-keypair.json"))
    p_mf.add_argument("--competition", default="tiny-chess-01")
    p_mf.add_argument("--repo-dir", default=".")
    p_mf.add_argument("--kit-dir", default="../makefun/tiny-chess-01-kit")
    p_mf.add_argument("--action", choices=["validate", "quota", "profile", "submit"],
                      default="validate")
    p_mf.add_argument("--files", nargs="*")
    p_mf.add_argument("--title")
    p_mf.add_argument("--git-remote")
    p_mf.add_argument("--session")
    p_mf.add_argument("--system-prompt")
    p_mf.set_defaults(func=cmd_makefun)

    # github
    p_gh = sub.add_parser("github", help="GitHub API 操作")
    p_gh.add_argument("--token")
    p_gh.add_argument("--action", choices=["repos", "verify_makefun"])
    p_gh.add_argument("--owner")
    p_gh.add_argument("--repo")
    p_gh.add_argument("--sha")
    p_gh.add_argument("--username")
    p_gh.add_argument("--expected-files", nargs="*")
    p_gh.set_defaults(func=cmd_github)

    # browser
    p_br = sub.add_parser("browser", help="浏览器自动化（查看用法）")
    p_br.set_defaults(func=cmd_browser)

    # monitor
    p_mon = sub.add_parser("monitor", help="启动持续监控")
    p_mon.add_argument("--interval", type=int, default=3600)
    p_mon.set_defaults(func=cmd_monitor)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()

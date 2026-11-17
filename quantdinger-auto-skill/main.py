#!/usr/bin/env python3
"""CLI 入口 — quantdinger-auto-skill 命令行工具"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到 PATH
sys.path.insert(0, str(Path(__file__).parent))


def cmd_billing(args):
    """收款消息生成"""
    from skills.billing import scan_pending_orders, export_messages
    orders = scan_pending_orders(args.billing_dir)
    result = export_messages(orders, args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_makefun(args):
    """make.fun 相关操作"""
    from skills.makefun import MakeFunClient
    client = MakeFunClient(args.keypair)

    if args.action == "quota":
        q = client.check_quota(args.competition)
        print(json.dumps(q, indent=2))
    elif args.action == "profile":
        p = client.profile()
        print(f"Handle: {p.get('handle')}")
        print(f"Wallet: {client.wallet}")
    elif args.action == "competitions":
        comps = client.list_open_competitions()
        for c in comps:
            print(f"  {c.get('slug','?'):30s} | ${c.get('reward','?')} | deadline {str(c.get('deadline',''))[:10]}")
    elif args.action == "submit":
        # 实际提交需要 bundle 文件，这里只做检查
        errors = MakeFunClient.validate_entry_requirements(args.repo_dir, args.files or ["main.py"])
        print(json.dumps({"valid": len(errors) == 0, "missing": errors}, indent=2))
    else:
        print(f"Unknown action: {args.action}")


def cmd_github(args):
    """GitHub 操作"""
    import os
    from skills.github import GitHubClient
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN required", file=sys.stderr)
        sys.exit(1)
    gh = GitHubClient(token)

    if args.action == "repos":
        repos = gh.list_repos(username=args.username)
        print(f"Total: {len(repos)}")
        for r in repos[:10]:
            print(f"  {r['full_name']} · ⭐{r['stargazers_count']} · {r.get('language','-')}")
    elif args.action == "verify_makefun":
        result = gh.verify_makefun_entry(args.owner, args.repo, args.sha, args.expected_files)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Unknown action: {args.action}")


def cmd_fiverr(args):
    """Fiverr Gig 管理"""
    from skills.fiverr import FiverrGigBuilder, generate_all_gigs
    if args.action == "generate":
        results = generate_all_gigs(args.output)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif args.action == "render":
        builder = FiverrGigBuilder(args.template)
        data = builder.render_gig_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_workflow(args):
    """执行工作流"""
    from orchestration.workflow_engine import make_collection_workflow, WorkflowEngine

    wf = make_collection_workflow(args.billing_dir, args.webhook)
    result = asyncio.run(wf.run())
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_health(args):
    """系统健康检查"""
    checks = {}
    # billing dir
    bd = Path("/opt/bingdashan/data/billing")
    if bd.exists():
        files = list(bd.glob("*.json")) + list(bd.glob("*.tsv"))
        checks["billing_data"] = {"ok": len(files) > 0, "files": len(files)}
    else:
        checks["billing_data"] = {"ok": False, "error": "billing dir not found"}

    # makefun keypair
    kp = Path(args.keypair) if hasattr(args, 'keypair') and args.keypair else Path.home() / "makefun-keypair.json"
    checks["makefun_keypair"] = {"ok": kp.exists(), "path": str(kp)}

    # node version
    import subprocess
    try:
        r = subprocess.run(["node", "--version"], capture_output=True, text=True)
        checks["node_version"] = {"ok": True, "version": r.stdout.strip()}
    except Exception as e:
        checks["node_version"] = {"ok": False, "error": str(e)}

    print(json.dumps(checks, indent=2))


def main():
    parser = argparse.ArgumentParser(description="QuantDinger Auto-Skill CLI")
    sub = parser.add_subparsers(dest="command")

    # billing
    p_billing = sub.add_parser("billing", help="收款消息管理")
    p_billing.add_argument("--billing-dir", default="/opt/bingdashan/data/billing")
    p_billing.add_argument("--output", default="/tmp/outreach")
    p_billing.set_defaults(func=cmd_billing)

    # makefun
    p_mf = sub.add_parser("makefun", help="make.fun 竞赛管理")
    p_mf.add_argument("--keypair", default=str(Path.home() / "makefun-keypair.json"))
    p_mf.add_argument("--competition")
    p_mf.add_argument("--action", choices=["quota", "profile", "competitions", "submit", "status"])
    p_mf.add_argument("--repo-dir")
    p_mf.add_argument("--files", nargs="*")
    p_mf.set_defaults(func=cmd_makefun)

    # github
    p_gh = sub.add_parser("github", help="GitHub API")
    p_gh.add_argument("--token")
    p_gh.add_argument("--action", choices=["repos", "verify_makefun"])
    p_gh.add_argument("--owner")
    p_gh.add_argument("--repo")
    p_gh.add_argument("--sha")
    p_gh.add_argument("--username")
    p_gh.add_argument("--expected-files", nargs="*")
    p_gh.set_defaults(func=cmd_github)

    # fiverr
    p_fv = sub.add_parser("fiverr", help="Fiverr Gig 管理")
    p_fv.add_argument("--action", choices=["generate", "render"])
    p_fv.add_argument("--template", default="python_automation")
    p_fv.add_argument("--output", default="/tmp/fiverr_gigs")
    p_fv.set_defaults(func=cmd_fiverr)

    # workflow
    p_wf = sub.add_parser("workflow", help="执行工作流")
    p_wf.add_argument("--type", default="collection")
    p_wf.add_argument("--billing-dir", default="/opt/bingdashan/data/billing")
    p_wf.add_argument("--webhook")
    p_wf.set_defaults(func=cmd_workflow)

    # health
    p_h = sub.add_parser("health", help="系统健康检查")
    p_h.add_argument("--keypair", default=str(Path.home() / "makefun-keypair.json"))
    p_h.set_defaults(func=cmd_health)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()

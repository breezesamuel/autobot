#!/usr/bin/env python3
"""github skill — GitHub API 封装：Repo/PR/Issue/Release 操作"""

from __future__ import annotations
import base64
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class GitHubClient:
    """GitHub REST API v3 客户端（urllib，无第三方依赖）"""

    def __init__(self, token: str | None = None):
        self.token = token
        self._cache: dict[str, Any] = {}

    def _headers(self) -> dict[str, str]:
        h = {"Accept": "application/vnd.github.v3+json", "User-Agent": "QuantDinger-AutoSkill/1.0"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _req(self, method: str, path: str, body: Any = None) -> Any:
        url = f"https://api.github.com{path}"
        data = json.dumps(body).encode() if body else None
        req = Request(url, data=data, headers=self._headers(), method=method)
        try:
            with urlopen(req, timeout=15) as resp:
                if resp.status == 204:
                    return {}
                return json.loads(resp.read().decode())
        except HTTPError as e:
            raise RuntimeError(f"GitHub API {e.code}: {e.reason}")
        except URLError as e:
            raise RuntimeError(f"Network error: {e.reason}")

    # ── Repos ─────────────────────────────────────────────────────────────────
    def create_repo(self, name: str, description: str = "", private: bool = False,
                    auto_init: bool = True) -> dict:
        return self._req("POST", "/user/repos", {
            "name": name, "description": description,
            "private": private, "auto_init": auto_init,
        })

    def get_repo(self, owner: str, repo: str) -> dict:
        return self._req("GET", f"/repos/{owner}/{repo}")

    def list_repos(self, username: str = "", affiliation: str = "owner") -> list[dict]:
        path = f"/user/repos" if not username else f"/users/{username}/repos"
        return self._req("GET", f"{path}?type=all&sort=updated")

    def delete_repo(self, owner: str, repo: str) -> None:
        self._req("DELETE", f"/repos/{owner}/{repo}")

    # ── Contents ────────────────────────────────────────────────────────────────
    def get_file(self, owner: str, repo: str, path: str, ref: str = "HEAD") -> dict:
        content_b64 = self._req("GET", f"/repos/{owner}/{repo}/contents/{path}?ref={ref}")
        raw = base64.b64decode(content_b64["content"]).decode("utf-8")
        return {"sha": content_b64["sha"], "content": raw, "path": content_b64["path"]}

    def put_file(self, owner: str, repo: str, path: str, content: str,
                 message: str = "Update file", sha: str = "") -> dict:
        payload = {"message": message, "content": base64.b64encode(content.encode()).decode()}
        if sha:
            payload["sha"] = sha
        return self._req("PUT", f"/repos/{owner}/{repo}/contents/{path}", payload)

    # ── Issues ──────────────────────────────────────────────────────────────────
    def create_issue(self, owner: str, repo: str, title: str, body: str,
                     labels: list[str] | None = None) -> dict:
        payload = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels
        return self._req("POST", f"/repos/{owner}/{repo}/issues", payload)

    def list_issues(self, owner: str, repo: str, state: str = "open",
                    labels: list[str] | None = None) -> list[dict]:
        path = f"/repos/{owner}/{repo}/issues?state={state}"
        if labels:
            path += "&labels=" + ",".join(labels)
        return self._req("GET", path)

    # ── Pull Requests ───────────────────────────────────────────────────────────
    def create_pr(self, owner: str, repo: str, title: str, head: str, base: str,
                  body: str = "") -> dict:
        return self._req("POST", f"/repos/{owner}/{repo}/pulls", {
            "title": title, "head": head, "base": base, "body": body,
        })

    def merge_pr(self, owner: str, repo: str, pr_number: int,
                 commit_title: str = "", commit_msg: str = "") -> dict:
        payload = {}
        if commit_title:
            payload["commit_title"] = commit_title
        if commit_msg:
            payload["commit_message"] = commit_msg
        return self._req("PUT", f"/repos/{owner}/{repo}/pulls/{pr_number}/merge", payload)

    # ── Checks ─────────────────────────────────────────────────────────────────
    def create_check_run(self, owner: str, repo: str, name: str,
                         head_sha: str, status: str = "in_progress",
                         details_url: str = "", output: dict = None) -> dict:
        payload = {"name": name, "head_sha": head_sha, "status": status}
        if output:
            payload["output"] = output
        if details_url:
            payload["details_url"] = details_url
        return self._req("POST", f"/repos/{owner}/{repo}/check-runs", payload)

    def update_check_run(self, check_id: int, status: str,
                         output: dict = None) -> dict:
        payload = {"status": status}
        if output:
            payload["output"] = output
        return self._req("PATCH", f"/check-runs/{check_id}", payload)

    # ── make.fun 专用 ───────────────────────────────────────────────────────────
    def verify_makefun_entry(self, owner: str, repo: str, commit_sha: str,
                             expected_files: list[str]) -> dict:
        """验证仓库是否符合 make.fun 提交要求"""
        errors = []
        warnings = []

        # 检查 LICENSE
        try:
            lic = self.get_file(owner, repo, "LICENSE")
            if "MIT" not in lic["content"] and "Apache" not in lic["content"]:
                warnings.append("LICENSE 建议用 MIT 或 Apache-2.0")
        except Exception as e:
            errors.append(f"LICENSE 文件缺失: {e}")

        # 检查 .makefun/owner.json
        owner_json_path = ".makefun/owner.json"
        try:
            of = self.get_file(owner, repo, owner_json_path)
            data = json.loads(of["content"])
            if "wallet" not in data:
                errors.append(f"{owner_json_path} 缺少 'wallet' 字段")
        except HTTPError as e:
            if e.code == 404:
                errors.append(f"{owner_json_path} 不存在，需要添加 wallet 声明")
            else:
                raise

        # 检查 required files
        for fp in expected_files:
            try:
                self.get_file(owner, repo, fp)
            except HTTPError as e:
                if e.code == 404:
                    errors.append(f"缺少必需文件: {fp}")

        # 检查 commits 是否在新仓库中
        commits = self._req("GET", f"/repos/{owner}/{repo}/commits?per_page=5")
        recent_shas = [c["sha"][:8] for c in commits]

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "recent_commits": recent_shas,
            "has_license": not any("LICENSE" in e for e in errors),
            "has_owner_json": not any("owner.json" in e for e in errors),
        }

    @staticmethod
    def validate_local_repo(repo_dir: str | Path, expected_files: list[str]) -> list[str]:
        """本地验证仓库文件是否齐全（不做网络请求，供测试使用）"""
        missing = []
        rd = Path(repo_dir)
        for fp in expected_files:
            if not (rd / fp).exists():
                missing.append(fp)
        lic_found = any((rd / f).exists() for f in ["LICENSE", "LICENSE.md", "LICENSE.txt"])
        if not lic_found:
            missing.append("LICENSE")
        return missing


# ─── CLI demo ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    TOKEN = os.environ.get("GITHUB_TOKEN")
    if not TOKEN:
        print("Usage: GITHUB_TOKEN=xxx python github_skill.py"); exit(1)

    gh = GitHubClient(TOKEN)
    repos = gh.list_repos()
    print(f"Total repos: {len(repos)}")
    for r in repos[:5]:
        print(f"  {r['full_name']} · stars={r['stargazers_count']} · lang={r.get('language')}")

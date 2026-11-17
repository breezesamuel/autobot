#!/usr/bin/env python3
"""GitHub Operations Skill — REST API v3 完整封装（无第三方依赖）
参考: PyGithub / github3.py 的设计模式，但零依赖纯 stdlib 实现
"""
from __future__ import annotations
import base64
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timezone


class GitHubOps:
    """GitHub REST API v3 客户端（urllib，零外部依赖）"""

    def __init__(self, token: str | None = None):
        self.token = token
        self._base = "https://api.github.com"

    def _headers(self) -> dict[str, str]:
        h = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AutoBot/1.0 (quantdinger)",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _req(self, method: str, path: str, body: Any = None,
             params: dict = None) -> Any:
        url = self._base + path
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items())
            url += "?" + qs
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=self._headers(), method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 204:
                    return {}
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="replace")
            raise GithubAPIError(e.code, body_text[:200], path)
        except urllib.error.URLError as e:
            raise GithubAPIError(0, str(e.reason), path)

    # ── Repositories ───────────────────────────────────────────────────────────
    def create_repo(self, name: str, description: str = "", private: bool = False,
                    auto_init: bool = True, license_template: str = "mit") -> dict:
        payload = {
            "name": name, "description": description,
            "private": private, "auto_init": auto_init,
        }
        if license_template:
            payload["license_template"] = license_template
        return self._req("POST", "/user/repos", payload)

    def get_repo(self, owner: str, repo: str) -> dict:
        return self._req("GET", f"/repos/{owner}/{repo}")

    def list_repos(self, username: str = "", affiliation: str = "owner",
                   sort: str = "updated") -> list[dict]:
        path = f"/user/repos" if not username else f"/users/{username}/repos"
        return self._req("GET", f"{path}?type=all&sort={sort}&per_page=100")

    def delete_repo(self, owner: str, repo: str) -> None:
        self._req("DELETE", f"/repos/{owner}/{repo}")

    # ── Contents ────────────────────────────────────────────────────────────────
    def get_file(self, owner: str, repo: str, path: str, ref: str = "HEAD") -> dict:
        data = self._req("GET", f"/repos/{owner}/{repo}/contents/{path}?ref={ref}")
        raw = base64.b64decode(data["content"]).decode("utf-8")
        return {"sha": data["sha"], "content": raw, "path": data["path"],
                "size": data.get("size", 0)}

    def put_file(self, owner: str, repo: str, filepath: str, content: str,
                 message: str = "Update file", branch: str = "main",
                 sha: str = "") -> dict:
        payload = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha
        return self._req("PUT", f"/repos/{owner}/{repo}/contents/{filepath}", payload)

    def create_branch(self, owner: str, repo: str, new_branch: str,
                      from_sha: str) -> dict:
        return self._req("POST", f"/repos/{owner}/{repo}/git/refs", {
            "ref": f"refs/heads/{new_branch}", "sha": from_sha
        })

    # ── Issues & PRs ────────────────────────────────────────────────────────────
    def create_issue(self, owner: str, repo: str, title: str, body: str,
                     labels: list[str] | None = None, assignees: list[str] | None = None) -> dict:
        payload = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels
        if assignees:
            payload["assignees"] = assignees
        return self._req("POST", f"/repos/{owner}/{repo}/issues", payload)

    def list_issues(self, owner: str, repo: str, state: str = "open",
                    labels: list[str] | None = None, sort: str = "created") -> list[dict]:
        path = f"/repos/{owner}/{repo}/issues?state={state}&sort={sort}&direction=desc"
        if labels:
            path += "&labels=" + ",".join(labels)
        return self._req("GET", path)

    def create_pr(self, owner: str, repo: str, title: str, head: str, base: str,
                  body: str = "", draft: bool = False) -> dict:
        return self._req("POST", f"/repos/{owner}/{repo}/pulls", {
            "title": title, "head": head, "base": base,
            "body": body, "draft": draft,
        })

    def merge_pr(self, owner: str, repo: str, pr_number: int,
                 commit_title: str = "", commit_message: str = "",
                 sha: str = "") -> dict:
        payload = {}
        if commit_title:
            payload["commit_title"] = commit_title
        if commit_message:
            payload["commit_message"] = commit_message
        if sha:
            payload["sha"] = sha
        return self._req("PUT", f"/repos/{owner}/{repo}/pulls/{pr_number}/merge", payload)

    # ── Commits ─────────────────────────────────────────────────────────────────
    def list_commits(self, owner: str, repo: str, sha: str = "main",
                     limit: int = 10) -> list[dict]:
        return self._req("GET",
                         f"/repos/{owner}/{repo}/commits?sha={sha}&per_page={limit}")

    def get_commit(self, owner: str, repo: str, sha: str) -> dict:
        return self._req("GET", f"/repos/{owner}/{repo}/commits/{sha}")

    # ── make.fun 专用验证工具 ───────────────────────────────────────────────────
    def verify_makefun_compliance(self, owner: str, repo: str, expected_commit: str,
                                   required_files: list[str]) -> dict:
        """验证仓库是否符合 make.fun 提交要求"""
        errors, warnings = [], []

        # Check LICENSE
        try:
            lic = self.get_file(owner, repo, "LICENSE")
            content = lic["content"]
            if "MIT" not in content and "Apache" not in content:
                warnings.append("LICENSE should contain MIT or Apache-2.0 SPDX identifier")
        except GithubAPIError as e:
            if e.status == 404:
                errors.append("LICENSE file not found in repository root")
            else:
                raise

        # Check .makefun/owner.json
        try:
            of = self.get_file(owner, repo, ".makefun/owner.json")
            data = json.loads(of["content"])
            if "wallet" not in data:
                errors.append(".makefun/owner.json missing 'wallet' field")
        except GithubAPIError as e:
            if e.status == 404:
                errors.append(".makefun/owner.json not found (needed for wallet-only accounts)")
            else:
                raise

        # Check required files
        for fp in required_files:
            try:
                self.get_file(owner, repo, fp)
            except GithubAPIError as e:
                if e.status == 404:
                    errors.append(f"Required file missing: {fp}")

        # Verify commit exists
        try:
            commit = self.get_commit(owner, repo, expected_commit)
            actual_sha = commit["sha"][:8]
            if actual_sha != expected_commit[:8]:
                warnings.append(f"Commit SHA mismatch: expected {expected_commit[:8]}, got {actual_sha}")
        except GithubAPIError:
            errors.append(f"Commit {expected_commit} not found in repository")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "commit_sha": expected_commit[:12],
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }


class GithubAPIError(Exception):
    def __init__(self, status: int, message: str, path: str):
        self.status = status
        self.message = message
        self.path = path
        super().__init__(f"GitHub API {status} on {path}: {message}")


# ─── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Usage: GITHUB_TOKEN=xxx python github_ops.py", flush=True)
        exit(1)

    gh = GitHubOps(token)
    repos = gh.list_repos()
    print(f"Total repos: {len(repos)}")
    for r in repos[:5]:
        print(f"  {r['full_name']} · ⭐{r['stargazers_count']} · {r.get('language','-')}")

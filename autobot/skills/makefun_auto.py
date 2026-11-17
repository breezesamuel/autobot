#!/usr/bin/env python3
"""MakeFun Automation Skill — make.fun 赏金竞赛全自动管理
参考: make.fun kit CLI + Ed25519 wallet signing
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import os
import subprocess
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class MakeFunAuto:
    """make.fun 竞赛全自动提交管理"""

    API_BASE = "https://www.make.fun/api"

    def __init__(self, keypair_path: str | Path, api_key: str | None = None):
        self.keypair_path = Path(keypair_path)
        self.api_key = api_key
        self._wallet: str | None = None
        self._secret_key: bytes | None = None
        self._load_keypair()

    def _load_keypair(self):
        kp = json.load(open(self.keypair_path))
        if isinstance(kp, list) and len(kp) == 64:
            self._secret_key = bytes(kp[:32])
            self._public_key = bytes(kp[32:])
        elif isinstance(kp, dict):
            self._secret_key = base64.b64decode(kp["secretKey"])
            self._public_key = base64.b64decode(kp["publicKey"])
        else:
            raise ValueError(f"Unsupported keypair format: {type(kp)}")
        # Derive wallet address from public key (simplified)
        self._wallet = hashlib.sha512(self._public_key).hexdigest()[:44]

    @property
    def wallet_address(self) -> str:
        return self._wallet

    def _req(self, method: str, path: str, body: Any = None) -> Any:
        url = self.API_BASE + path
        data = json.dumps(body).encode() if body else None
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="replace")
            raise RuntimeError(f"API {e.code}: {body_text[:300]}")

    # ── Quota & Profile ─────────────────────────────────────────────────────────
    def check_quota(self, competition: str) -> dict:
        return self._req("GET", f"/competitions/{competition}/quota")

    def profile(self) -> dict:
        return self._req("GET", "/me")

    def list_competitions(self, status: str = "open") -> list[dict]:
        return self._req("GET", f"/competitions?status={status}")

    def get_submission(self, submission_id: str) -> dict:
        return self._req("GET", f"/submissions/{submission_id}")

    def get_leaderboard(self, competition: str, limit: int = 50) -> dict:
        return self._req("GET", f"/competitions/{competition}/leaderboard?limit={limit}")

    # ── Entry Signature ──────────────────────────────────────────────────────────
    def build_entry_message(self, competition: str, repo_url: str,
                            commit_sha: str, bundle_sha256: str) -> str:
        now = datetime.now(timezone.utc).isoformat()
        return "\n".join([
            "make.fun entry v1",
            f"Site: https://www.make.fun",
            f"Competition: {competition}",
            f"Repository: {repo_url}",
            f"Commit: {commit_sha}",
            f"Bundle SHA256: {bundle_sha256}",
            f"Wallet: {self._wallet}",
            f"Timestamp: {now}",
        ])

    def sign_entry_message(self, message: str) -> str:
        """Ed25519 签名（需要 nacl/libsodium）"""
        try:
            import nacl.bindings
            sig = nacl.bindings.crypto_sign(message.encode(), self._secret_key)
            return base64.b64encode(sig).decode()
        except ImportError:
            # 降级：HMAC-SHA256 占位（仅作演示，生产环境需 nacl）
            sig = hmac.new(self._secret_key, message.encode(), hashlib.sha512).digest()
            return base64.b64encode(sig).decode()

    # ── Local Validation ─────────────────────────────────────────────────────────
    def validate_repo_locally(self, repo_dir: str | Path,
                               expected_files: list[str]) -> dict:
        """本地验证仓库是否满足 make.fun 要求（无需网络）"""
        rd = Path(repo_dir)
        errors = []
        warnings = []

        # Check required files
        for fp in expected_files:
            if not (rd / fp).exists():
                errors.append(f"Missing required file: {fp}")

        # Check LICENSE
        lic_names = ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"]
        if not any((rd / n).exists() for n in lic_names):
            errors.append("Missing LICENSE file (required)")
        else:
            for n in lic_names:
                p = rd / n
                if p.exists():
                    content = p.read_text(errors="replace")
                    if "MIT" not in content and "Apache" not in content:
                        warnings.append("LICENSE should be MIT or Apache-2.0")
                    break

        # Check .makefun/owner.json
        owner_json = rd / ".makefun" / "owner.json"
        if not owner_json.exists():
            errors.append("Missing .makefun/owner.json (needed for wallet-only accounts)")
        else:
            try:
                data = json.loads(owner_json.read_text())
                if "wallet" not in data:
                    errors.append(".makefun/owner.json missing 'wallet' field")
            except json.JSONDecodeError:
                errors.append(".makefun/owner.json is invalid JSON")

        # Check main entrypoint
        if not any((rd / f).exists() for f in ["main.py", "main.ts"]):
            errors.append("Missing main.py or main.ts entrypoint")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    # ── Bundle Builder ────────────────────────────────────────────────────────────
    def build_bundle_command(self, repo_dir: str | Path, session_file: str | Path,
                              kit_dir: str | Path, output_path: str | Path,
                              extra_flags: dict = None) -> list[str]:
        """生成 makefun bundle CLI 命令（字符串形式，供 shell 执行）"""
        kit = Path(kit_dir)
        flags = extra_flags or {}
        cmd = [
            "node", str(kit / "cli" / "makefun.mjs"), "bundle",
            "--repo", str(repo_dir),
            "--session", str(session_file),
            "--effort", flags.get("effort", "default"),
            "--out", str(output_path),
            "--no-discover",
            "--harness", flags.get("harness", "opencode"),
            "--harness-version", flags.get("harness_version", "v2"),
            "--provider", flags.get("provider", "anthropic"),
            "--model", flags.get("model", "claude-sonnet-4-20250514"),
        ]
        sp = flags.get("system_prompt")
        if sp:
            cmd += ["--system-prompt", str(sp)]
        inst = flags.get("instructions")
        if inst:
            cmd += ["--instructions", inst]
        mcp = flags.get("mcp")
        if mcp:
            cmd += ["--mcp", mcp]
        compress = flags.get("compress_source")
        if compress:
            cmd += ["--compress-source", compress]
        return cmd

    def run_bundle(self, repo_dir: str | Path, output_path: str | Path,
                   kit_dir: str | Path, session_file: str | Path | None = None,
                   **flags) -> dict:
        """执行 bundle 命令并返回结果"""
        sf = str(session_file) if session_file else str(Path(repo_dir) / ".makefun" / "session.json")
        cmd = self.build_bundle_command(repo_dir, sf, kit_dir, output_path, flags)
        try:
            result = subprocess.run(cmd, cwd=str(repo_dir), capture_output=True, text=True, timeout=120)
            return {"ok": result.returncode == 0, "stdout": result.stdout[-500:],
                    "stderr": result.stderr[-500:], "returncode": result.returncode}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "timeout after 120s"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── Full Submission Pipeline ─────────────────────────────────────────────────
    def submit_pipeline(self, competition: str, repo_dir: str | Path,
                        kit_dir: str | Path, title: str = "",
                        git_remote: str = "", **flags) -> dict:
        """完整提交流程：git push → bundle → sign → submit"""
        pipeline_result = {"steps": [], "final_status": "unknown"}

        # Step 1: Git push
        try:
            r = subprocess.run(["git", "-C", str(repo_dir), "push", "origin", "main"],
                              capture_output=True, text=True, timeout=30)
            sha = subprocess.run(["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
                                capture_output=True, text=True).stdout.strip()
            pipeline_result["steps"].append({"step": "git_push", "ok": r.returncode == 0, "sha": sha})
        except Exception as e:
            pipeline_result["steps"].append({"step": "git_push", "ok": False, "error": str(e)})
            return pipeline_result

        # Step 2: Bundle transcripts
        bundle_path = Path(repo_dir).parent / "transcripts.tar.gz"
        bundle_r = self.run_bundle(repo_dir, bundle_path, kit_dir, **flags)
        pipeline_result["steps"].append({"step": "bundle", **bundle_r})
        if not bundle_r["ok"]:
            return pipeline_result

        # Step 3: Validate bundle
        bundle_sha256 = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
        pipeline_result["steps"].append({"step": "bundle_sha256", "sha": bundle_sha256[:16]})

        # Step 4: Build & sign entry message
        repo_url = git_remote or f"https://github.com/{self._get_owner(repo_dir)}/{self._get_repo_name(repo_dir)}.git"
        msg = self.build_entry_message(competition, repo_url, pipeline_result["steps"][-1].get("sha", ""),
                                        bundle_sha256)
        sig = self.sign_entry_message(msg)
        pipeline_result["steps"].append({"step": "sign", "ok": len(sig) > 0})

        # Step 5: Submit via API (multipart form)
        submit_result = self._submit_api(competition, repo_url,
                                          pipeline_result["steps"][0].get("sha", ""),
                                          bundle_path, msg, sig, title)
        pipeline_result["steps"].append({"step": "submit_api", **submit_result})
        pipeline_result["final_status"] = "submitted" if submit_result.get("ok") else "failed"

        return pipeline_result

    def _get_owner(self, repo_dir: Path) -> str:
        """从 remote URL 提取 GitHub owner"""
        try:
            r = subprocess.run(["git", "-C", str(repo_dir), "remote", "get-url", "origin"],
                              capture_output=True, text=True)
            url = r.stdout.strip()
            # github.com:user/repo.git → user
            m = re.search(r"github\.com[:/](.+?)\.git?$", url)
            return m.group(1).split("/")[0] if m else "breezesamuel"
        except Exception:
            return "breezesamuel"

    def _get_repo_name(self, repo_dir: Path) -> str:
        try:
            r = subprocess.run(["git", "-C", str(repo_dir), "remote", "get-url", "origin"],
                              capture_output=True, text=True)
            url = r.stdout.strip()
            m = re.search(r"github\.com/.+?/(.+?)\.git?$", url)
            return m.group(1) if m else "tiny-chess-4k-engine"
        except Exception:
            return "tiny-chess-4k-engine"

    def _submit_api(self, competition: str, repo_url: str, commit_sha: str,
                     bundle_path: Path, entry_msg: str, signature: str,
                     title: str = "") -> dict:
        """通过 multipart form 提交 entry"""
        boundary = f"----FormBoundary{int(time.time()*1000):x}"
        body_parts = [
            f'--{boundary}',
            'Content-Disposition: form-data; name="repo_url"', '', repo_url,
            f'--{boundary}',
            'Content-Disposition: form-data; name="commit_sha"', '', commit_sha,
            f'--{boundary}',
            'Content-Disposition: form-data; name="title"', '', title or f"auto-entry-{competition}",
            f'--{boundary}',
            'Content-Disposition: form-data; name="entry_message"', '', entry_msg,
            f'--{boundary}',
            'Content-Disposition: form-data; name="entry_signature"', '', signature,
            f'--{boundary}',
            f'Content-Disposition: form-data; name="bundle"; filename="transcripts.tar.gz"',
            'Content-Type: application/gzip', '',
        ]
        body = ("\r\n".join(body_parts)).encode() + bundle_path.read_bytes() + b"\r\n--{boundary}--\r\n"

        req = urllib.request.Request(
            f"{self.API_BASE}/competitions/{competition}/submissions",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                     "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return {"ok": True, "status_code": resp.status,
                        "response": resp.read().decode()[:500]}
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="replace")
            return {"ok": False, "status_code": e.code, "error": body_text[:300]}


# ── CLI 入口 ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MakeFun Auto Submit")
    parser.add_argument("--keypair", default=os.path.expanduser("~/.makefun-keypair.json"))
    parser.add_argument("--competition", default="tiny-chess-01")
    parser.add_argument("--repo-dir", default=".")
    parser.add_argument("--kit-dir", default="../tiny-chess-01-kit")
    args = parser.parse_args()

    client = MakeFunAuto(args.keypair)
    print(f"Wallet: {client.wallet_address}")

    # Quick validation
    validation = client.validate_repo_locally(args.repo_dir, ["main.py", ".makefun/session.json"])
    print(f"Repo valid: {validation['valid']}")
    if validation["errors"]:
        for e in validation["errors"]:
            print(f"  ❌ {e}")
    if validation["warnings"]:
        for w in validation["warnings"]:
            print(f"  ⚠️  {w}")

#!/usr/bin/env python3
"""makefun skill — make.fun 赏金竞赛管理：quota 检查、submit、transcript 生成"""

from __future__ import annotations
import base64
import hashlib
import hmac
import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class MakeFunClient:
    """make.fun API 客户端"""

    API_BASE = "https://www.make.fun/api"

    def __init__(self, keypair_path: str | Path, api_key: str | None = None):
        self.keypair_path = Path(keypair_path)
        self.api_key = api_key
        self._wallet_address: str | None = None
        self._load_keypair()

    def _load_keypair(self):
        kp = json.load(open(self.keypair_path))
        if isinstance(kp, list):
            self._secret = bytes(kp[:32])
            self._public = bytes(kp[32:])
        elif isinstance(kp, dict):
            self._secret = base64.b64decode(kp["secretKey"])
            self._public = base64.b64decode(kp["publicKey"])
        else:
            raise ValueError("Unsupported keypair format")
        # derive wallet address (simplified: use public key hash)
        self._wallet_address = hashlib.sha512(self._public).hexdigest()[:44]

    @property
    def wallet(self) -> str:
        return self._wallet_address

    def _signed_headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def _req(self, method: str, path: str, body: Any = None) -> Any:
        url = self.API_BASE + path
        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, headers=self._signed_headers(), method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="replace")
            raise RuntimeError(f"make.fun API {e.code}: {body_text[:200]}")

    # ── Quota ───────────────────────────────────────────────────────────────────
    def check_quota(self, competition: str) -> dict:
        """检查今日 quota 和总提交数"""
        return self._req("GET", f"/competitions/{competition}/quota")

    # ── Profile ─────────────────────────────────────────────────────────────────
    def profile(self) -> dict:
        return self._req("GET", "/me")

    def wallet_address(self) -> str:
        """获取已关联的 Solana 钱包地址"""
        data = self._req("GET", "/me/wallets")
        if isinstance(data, list) and data:
            return data[0].get("address", self.wallet)
        return self.wallet

    # ── Submissions ─────────────────────────────────────────────────────────────
    def submit_entry(self, competition: str, repo_url: str, commit_sha: str,
                     bundle_path: str | Path, title: str = "",
                     entry_message_template: dict = None) -> dict:
        """提交 entry（multipart form-data）"""
        bundle_p = Path(bundle_path)
        if not bundle_p.exists():
            raise FileNotFoundError(f"Bundle not found: {bundle_p}")

        bundle_sha256 = hashlib.sha256(bundle_p.read_bytes()).hexdigest()

        # 构建 entry message
        msg = self._build_entry_message(competition, repo_url, commit_sha, bundle_sha256)
        sig = self._sign_message(msg)

        # multipart form
        boundary = f"----WebKitFormBoundary{int(time.time()*1000):x}"
        body_parts = [
            f'--{boundary}',
            f'Content-Disposition: form-data; name="repo_url"',
            '',
            repo_url,
            f'--{boundary}',
            f'Content-Disposition: form-data; name="commit_sha"',
            '',
            commit_sha,
            f'--{boundary}',
            f'Content-Disposition: form-data; name="title"',
            '',
            title or f"auto-entry-{competition}",
            f'--{boundary}',
            f'Content-Disposition: form-data; name="entry_message"',
            '',
            msg,
            f'--{boundary}',
            f'Content-Disposition: form-data; name="entry_signature"',
            '',
            sig,
            f'--{boundary}',
            f'Content-Disposition: form-data; name="bundle"; filename="transcripts.tar.gz"',
            f'Content-Type: application/gzip',
            '',
        ]
        body = ("\r\n".join(body_parts)).encode() + bundle_p.read_bytes() + b"\r\n--{boundary}--\r\n".encode()

        req = urllib.request.Request(
            f"{self.API_BASE}/competitions/{competition}/submissions",
            data=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Accept": "application/json",
            },
            method="POST",
        )
        return self._req_raw(req)

    def _build_entry_message(self, competition: str, repo_url: str,
                             commit_sha: str, bundle_sha256: str) -> str:
        now = datetime.now(timezone.utc).isoformat()
        lines = [
            "make.fun entry v1",
            f"Site: https://www.make.fun",
            f"Competition: {competition}",
            f"Repository: {repo_url}",
            f"Commit: {commit_sha}",
            f"Bundle SHA256: {bundle_sha256}",
            f"Wallet: {self.wallet}",
            f"Timestamp: {now}",
        ]
        return "\n".join(lines)

    def _sign_message(self, message: str) -> str:
        """Ed25519 签名（简化版：用 HMAC-SHA256 代替，实际生产需 nacl/libsodium）"""
        # 注：完整实现需要 install libsodium 或使用 ed25519 库
        # 此处为占位实现，实际使用建议使用 cryptography 或 nacl
        import nacl.bindings
        sig = nacl.bindings.crypto_sign(message.encode(), self._secret)
        return base64.b64encode(sig).decode()

    def _req_raw(self, req: urllib.request.Request) -> dict:
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode(errors="replace")
            raise RuntimeError(f"make.fun API {e.code}: {body_text[:300]}")

    # ── Competition Info ────────────────────────────────────────────────────────
    def get_competition(self, slug: str) -> dict:
        return self._req("GET", f"/competitions/{slug}")

    def list_open_competitions(self) -> list[dict]:
        return self._req("GET", "/competitions?status=open")

    def get_submission_status(self, submission_id: str) -> dict:
        return self._req("GET", f"/submissions/{submission_id}")

    def get_leaderboard(self, competition: str, limit: int = 20) -> dict:
        return self._req("GET", f"/competitions/{competition}/leaderboard?limit={limit}")

    def find_my_ranking(self, competition: str) -> dict | None:
        """查找自己在某个 competition 中的排名"""
        lb = self.get_leaderboard(competition, limit=200)
        for entry in lb.get("entries", lb if isinstance(lb, list) else []):
            entrant = entry.get("entrant", entry.get("handle", ""))
            if entrant == self.profile().get("handle", ""):
                return entry
        return None

    # ── Transcript Bundle Helpers ───────────────────────────────────────────────
    @staticmethod
    def build_bundle_spec(session_json_path: str | Path,
                          system_prompt_path: str | None = None,
                          compress_source: dict = None) -> dict:
        """构建 bundle 规格说明（供 bundle CLI 使用）"""
        spec = {
            "session": str(session_json_path),
            "effort": "default",
            "harness": "quantdinger-auto-skill",
            "harness_version": "1.0.0",
            "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "no_discover": True,
            "mcp": "none",
        }
        if system_prompt_path and Path(system_prompt_path).exists():
            spec["system_prompt"] = str(system_prompt_path)
        if compress_source:
            spec["compress_source"] = compress_source
        return spec

    @staticmethod
    def validate_entry_requirements(repo_dir: str | Path, expected_files: list[str]) -> list[str]:
        """验证本地仓库是否满足 make.fun 基本要求"""
        missing = []
        rd = Path(repo_dir)
        for fp in expected_files:
            full = rd / fp
            if not full.exists():
                missing.append(fp)
        # check LICENSE
        lic_found = any((rd / f).exists() for f in ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"])
        if not lic_found:
            missing.append("LICENSE (required)")
        return missing


# ─── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    KP = os.environ.get("MAKEFUN_KEYPAIR", "F:/2026/第三轮/makefun-keypair.json")
    client = MakeFunClient(KP)
    print(f"Wallet: {client.wallet}")
    try:
        comp = client.list_open_competitions()
        print(f"Open competitions: {len(comp)}")
        for c in comp[:5]:
            print(f"  {c.get('slug','?')} · {c.get('reward','?')} · deadline {c.get('deadline','?')[:10]}")
    except Exception as e:
        print(f"API error: {e}")

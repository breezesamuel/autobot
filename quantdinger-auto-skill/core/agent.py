#!/usr/bin/env python3
"""Core Agent — 轻量级 AI Agent 基类，支持工具调用和 Session 管理"""

from __future__ import annotations
import json
import uuid
import time
from pathlib import Path
from typing import Any, Callable, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


@dataclass
class ToolCall:
    """工具调用记录"""
    name: str
    arguments: dict[str, Any]
    result: Any = None
    timestamp: float = field(default_factory=time.time)
    call_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])


@dataclass
class ToolResult:
    ok: bool
    data: Any | None = None
    error: str | None = None


class ToolRegistry:
    """工具注册表 — 支持权限级别"""

    def __init__(self):
        self._tools: dict[str, tuple[Callable, str, set]] = {}  # name -> (fn, desc, scopes)

    def register(self, name: str, fn: Callable, description: str, scopes: set[str] | None = None):
        self._tools[name] = (fn, description, scopes or {"R"})

    def list_tools(self) -> list[dict]:
        return [
            {"name": n, "description": d, "scopes": sorted(s)}
            for n, (_, d, s) in self._tools.items()
        ]

    def resolve(self, name: str) -> Callable | None:
        entry = self._tools.get(name)
        return entry[0] if entry else None

    def check_scope(self, name: str, requested: set[str]) -> bool:
        entry = self._tools.get(name)
        if not entry:
            return False
        required = entry[2]
        return required.issubset(requested)


@dataclass
class AgentSession:
    """Agent 会话 — 用于 make.fun transcript gate 合规"""
    session_id: str
    harness: str = "quantdinger-auto-skill"
    harness_version: str = "1.0.0"
    provider: str = "anthropic"
    model: str = "claude-sonnet-4-20250514"
    system_prompt: str = ""
    instructions: str = "none"
    mcp_servers: list[dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    messages: list[dict] = field(default_factory=list)
    _tool_calls: list[ToolCall] = field(default_factory=list)

    @property
    def turn_count(self) -> int:
        return len([m for m in self.messages if m.get("role") == "assistant"])

    @property
    def last_assistant_turn(self) -> dict | None:
        for m in reversed(self.messages):
            if m.get("role") == "assistant":
                return m
        return None

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content, "timestamp": datetime.now(timezone.utc).isoformat()})

    def add_assistant_message(self, content: str, tool_calls: list[dict] | None = None):
        msg: dict = {"role": "assistant", "content": content, "timestamp": datetime.now(timezone.utc).isoformat()}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.messages.append(msg)

    def record_tool_call(self, tc: ToolCall):
        self._tool_calls.append(tc)
        # 同步到 messages 作为 tool_result
        self.messages.append({
            "role": "tool",
            "tool_call_id": tc.call_id,
            "content": json.dumps(tc.result, default=str, ensure_ascii=False) if tc.result else "",
            "timestamp": datetime.fromtimestamp(tc.timestamp, tz=timezone.utc).isoformat(),
        })

    def save(self, path: str | Path):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "session_id": self.session_id,
            "harness": self.harness,
            "harness_version": self.harness_version,
            "provider": self.provider,
            "model": self.model,
            "system": self.system_prompt,
            "instructions": self.instructions,
            "mcp_servers": self.mcp_servers,
            "created_at": self.created_at,
            "messages": self.messages,
        }
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")

    @classmethod
    def load(cls, path: str | Path) -> "AgentSession":
        p = Path(path)
        data = json.load(open(p, encoding="utf-8"))
        s = cls(session_id=data["session_id"])
        s.__dict__.update(data)
        return s


class AutoAgent:
    """主 Agent 类"""

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.anthropic.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.registry = ToolRegistry()
        self.session: AgentSession | None = None
        self._tool_history: list[ToolCall] = []

    def use_session(self, sid: str, save_to: str | None = None):
        """启动一个新 session"""
        self.session = AgentSession(session_id=sid)
        if save_to:
            self._save_path = Path(save_to)
        return self.session

    def resume_session(self, path: str | Path) -> AgentSession:
        """恢复已有 session"""
        self.session = AgentSession.load(path)
        self._save_path = Path(path)
        return self.session

    def run_tool(self, name: str, arguments: dict) -> ToolResult:
        """执行一个已注册的工具"""
        fn = self.registry.resolve(name)
        if not fn:
            return ToolResult(ok=False, error=f"Unknown tool: {name}")
        try:
            result = fn(**arguments)
            tc = ToolCall(name=name, arguments=arguments, result=result)
            self._tool_history.append(tc)
            if self.session:
                self.session.record_tool_call(tc)
            return ToolResult(ok=True, data=result)
        except Exception as e:
            return ToolResult(ok=False, error=str(e))

    def build_dossier_view(self) -> dict:
        """生成 dossier view（供 make.fun 使用）"""
        if not self.session:
            return {}
        return {
            "session_id": self.session.session_id,
            "turn_count": self.session.turn_count,
            "message_count": len(self.session.messages),
            "tool_call_count": len(self._tool_history),
            "last_update": self.session.messages[-1].get("timestamp") if self.session.messages else None,
        }

    def export_run_record(self) -> dict:
        """导出 make.fun 要求的 run_record"""
        if not self.session:
            raise RuntimeError("No active session")
        return {
            "format": "makefun-run/1",
            "prompt": {"text": "", "origin": "typed", "via": None},
            "system_prompt": {"status": self.session.instructions, "why": None},
            "instructions": {"status": "none", "why": None},
            "mcp_servers": self.session.mcp_servers,
            "declared": {
                "harness": self.session.harness,
                "harness_version": self.session.harness_version,
                "provider": self.session.provider,
                "model": self.session.model,
                "reasoning_effort": None,
                "notes": None,
            },
        }

    def save_session(self):
        """保存当前 session"""
        if self.session and getattr(self, "_save_path", None):
            self.session.save(self._save_path)
            print(f"[AutoAgent] Session saved → {self._save_path}")


if __name__ == "__main__":
    # 演示用法
    agent = AutoAgent()
    session = agent.use_session("demo-session-001", save_to="/tmp/demo_session.json")
    session.add_user_message("你好，帮我查一下 btc 价格")
    agent.run_tool("get_price", {"symbol": "BTCUSDT"})
    session.add_assistant_message("BTC 当前价格为 $67,542.30")
    agent.save_session()
    print(json.dumps(agent.build_dossier_view(), indent=2, ensure_ascii=False))

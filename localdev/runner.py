"""Run an agent (its agent.yaml + attached skills) locally via the **Claude Agent SDK**, on your
**Claude subscription** — a fast local loop for iterating on an agent before you build the real
Claude Managed Agent in your workspace.

Auth: your own Claude subscription. Authenticate the Claude Code CLI once —
  `claude setup-token`   (sets CLAUDE_CODE_OAUTH_TOKEN — good for headless), or
  `claude login`         (interactive)
— and the Agent SDK uses it. No Anthropic API key here (that's only for pushing to your CMA
workspace, a separate step — see docs/building-agents.md).

Tools: an agent gets exactly what it declares in `mctools` — your own function tools and/or a
remote MCP server you wire yourself (e.g. the company MCP). Declare nothing and it's a pure
conversational agent (like the demo). We do not inject any tools for you.

`Conversation` wraps the async SDK client behind a plain sync `.send(text)` so the CLI and the
Streamlit app can both stay simple.
"""
import asyncio
import json
import os
import pathlib

import yaml
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    tool,
)


def _load_env() -> None:
    """Load localdev/.env (yours) or, if absent, localdev/.env.example into the environment
    without overriding anything already set. Handy for keeping a company-MCP token out of git and
    referencing it from agent.yaml as ${MCCTX_MCP_URL} etc."""
    here = pathlib.Path(__file__).parent
    for fn in (".env", ".env.example"):
        p = here / fn
        if not p.is_file():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())
        break  # your own .env wins; fall back to .env.example only when there's no .env


def load_agent(agent_dir: str):
    """Compose the system prompt: agent.yaml `system` + each attached skill's SKILL.md body
    (read from <agent_dir>/skills/<name>/SKILL.md). Path-agnostic — point it at any agent folder."""
    base = pathlib.Path(agent_dir)
    cfg = yaml.safe_load((base / "agent.yaml").read_text())
    model = cfg.get("model") or "claude-opus-4-8"
    system = (cfg.get("system") or "").strip()
    for name in cfg.get("skills") or []:
        skill = base / "skills" / name / "SKILL.md"
        if skill.exists():
            system += f"\n\n---\n# Attached skill: {name}\n\n{skill.read_text()}"
    return model, system


def _load_function_tools(agent_dir: str, names: list[str]):
    """Each STRING entry in `mctools` is a function tool at mctools/<name>/tool.py
    (NAME / DESCRIPTION / INPUT_SCHEMA + run(args)). Wrap each as an in-process SDK tool.
    Skips anything malformed (never crash the chat)."""
    import importlib.util
    sdk_tools, tool_names = [], []
    for name in names:
        tp = pathlib.Path(agent_dir) / "mctools" / name / "tool.py"
        if not tp.is_file():
            print(f"  [local-dev] mctools '{name}': no mctools/{name}/tool.py — skipped")
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"_mctool_{name}", tp)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"  [local-dev] mctools '{name}': failed to load ({e}) — skipped")
            continue
        if not hasattr(mod, "run"):
            print(f"  [local-dev] mctools '{name}': no run(args) function — skipped")
            continue
        tname = str(getattr(mod, "NAME", name))
        desc = str(getattr(mod, "DESCRIPTION", "") or tname)
        schema = getattr(mod, "INPUT_SCHEMA", None) or {"type": "object", "properties": {}}

        @tool(tname, desc, schema)
        async def _wrapped(args: dict, _run=mod.run):
            res = _run(args)
            text = res if isinstance(res, str) else json.dumps(res, default=str)
            return {"content": [{"type": "text", "text": text}]}

        sdk_tools.append(_wrapped)
        tool_names.append(tname)
        print(f"  [local-dev] loaded custom tool '{tname}' from mctools/{name}/tool.py")
    return sdk_tools, tool_names


def _remote_mcp_servers(entries: list[dict]):
    """DICT entries in `mctools` are remote MCP servers ({name, url}); the agent connects directly.
    (A {name, command, ...} stdio form is also accepted.) `${VARS}` in url/command/args/env are
    expanded from the environment (and .env), so you can keep a token out of a committed file."""
    servers: dict = {}
    allowed: list[str] = []
    ex = os.path.expandvars
    for entry in entries:
        name = entry.get("name")
        if not name:
            print(f"  [local-dev] skipping mctools entry (mapping needs `name`): {entry!r}")
            continue
        if entry.get("url"):
            servers[name] = {"type": entry.get("transport", "http"), "url": ex(str(entry["url"]))}
            if entry.get("headers"):  # e.g. Authorization: Bearer ${TOKEN}
                servers[name]["headers"] = {k: ex(str(v)) for k, v in entry["headers"].items()}
        elif entry.get("command"):
            servers[name] = {"type": "stdio", "command": ex(str(entry["command"])),
                             "args": [ex(str(a)) for a in (entry.get("args") or [])],
                             "env": {k: ex(str(v)) for k, v in (entry.get("env") or {}).items()}}
        else:
            print(f"  [local-dev] skipping mctools '{name}' — needs `url` (remote MCP) or `command`")
            continue
        allowed += ([f"mcp__{name}__{t}" for t in entry["tools"]] if entry.get("tools")
                    else [f"mcp__{name}"])
        print(f"  [local-dev] loaded remote MCP server '{name}' from mctools")
    return servers, allowed


def build_options(agent_dir: str) -> ClaudeAgentOptions:
    model, system = load_agent(agent_dir)
    cfg = yaml.safe_load((pathlib.Path(agent_dir) / "agent.yaml").read_text()) or {}
    entries = cfg.get("mctools") or []
    fn_tools, _ = _load_function_tools(agent_dir, [e for e in entries if isinstance(e, str)])
    servers, allowed = _remote_mcp_servers([e for e in entries if isinstance(e, dict)])

    # No tools are injected for you. The agent gets exactly what it declares in `mctools`: a remote
    # MCP server you wire yourself (e.g. the company MCP — its URL + token are yours to plug in)
    # and/or your own function tools. Declare nothing (like the demo) → a pure conversational agent.
    if fn_tools:
        servers["custom"] = create_sdk_mcp_server(name="custom", version="1.0.0", tools=fn_tools)
        allowed.append("mcp__custom")

    return ClaudeAgentOptions(
        model=model,
        system_prompt=system,
        mcp_servers=servers,
        # scoped to exactly what the agent declares — deliberately NOT the ambient/built-in tools
        # (Bash/Read/Web, your personal MCPs) that a deployed managed agent wouldn't have either.
        allowed_tools=allowed,
        tools=[],
        setting_sources=[],
    )


class Conversation:
    """A multi-turn chat with one agent. `.send(text)` returns the agent's reply text; conversation
    state persists for the life of the object. One persistent event loop holds the async SDK client
    so this works cleanly from both the CLI and Streamlit."""

    def __init__(self, agent_dir: str):
        _load_env()
        self.agent_dir = agent_dir
        self.options = build_options(agent_dir)
        self.model = self.options.model
        self.tool_calls: list[dict] = []   # every tool the agent calls, whatever it declared
        self._loop = asyncio.new_event_loop()
        self._client = ClaudeSDKClient(options=self.options)
        self._loop.run_until_complete(self._client.connect())
        if any(isinstance(s, dict) and s.get("type") in ("http", "sse")
               for s in self.options.mcp_servers.values()):
            # a REMOTE MCP attaches asynchronously — warm it up so the first real turn has tools
            print("  [local-dev] connecting to your remote MCP tools…")
            self._loop.run_until_complete(self._warm_up())

    def send(self, text: str) -> str:
        return self._loop.run_until_complete(self._turn(text))

    async def _warm_up(self, timeout_s: float = 25.0) -> None:
        """Wait for remote MCP servers to finish connecting (they attach asynchronously) so the
        first real turn isn't tool-less. Cheap warmup turn(s) until nothing is 'pending'."""
        import time as _t
        deadline = _t.monotonic() + timeout_s
        while _t.monotonic() < deadline:
            await self._client.query("(local-dev warmup — reply OK)")
            pending = False
            async for msg in self._client.receive_response():
                if isinstance(msg, SystemMessage):
                    servers = (getattr(msg, "data", {}) or {}).get("mcp_servers") or []
                    pending = any(s.get("status") == "pending" for s in servers)
            if not pending:
                return
            await asyncio.sleep(1)

    async def _turn(self, text: str) -> str:
        await self._client.query(text)
        out: list[str] = []
        async for msg in self._client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        out.append(block.text)
                    elif isinstance(block, ToolUseBlock):
                        self.tool_calls.append({"tool": block.name, "input": block.input})
        return "".join(out).strip()

    def close(self):
        try:
            self._loop.run_until_complete(self._client.disconnect())
        finally:
            self._loop.close()

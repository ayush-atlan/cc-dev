# localdev — chat with your agent locally

A fast local loop for building an agent *before* you stand up the real Claude Managed Agent in
your workspace. It runs an agent (an `agent.yaml` + its `skills/`) on your machine via the
**Claude Agent SDK**, on **your own Claude subscription** — so you can chat, watch what it does,
tweak, and chat again in seconds. It's agent-agnostic: point it at any folder with an `agent.yaml`.

## Setup

1. **Claude Code CLI** (the SDK runs on it):
   `npm install -g @anthropic-ai/claude-code`
2. **Authenticate with your Claude subscription** (no API key needed):
   - `claude setup-token` — prints a long-lived token; export it as `CLAUDE_CODE_OAUTH_TOKEN`
     (good for headless), **or**
   - `claude login` — interactive, one-time.
3. **Python deps:** `pip install -r localdev/requirements.txt`

## Run

- **Browser:** `streamlit run localdev/chat_streamlit.py`
- **Terminal:** `python localdev/chat_cli.py demo` (or any folder with an `agent.yaml`)

Run from the repo root. With no argument the CLI picks the demo, or the first agent it finds.

## How it works

`runner.py` loads your agent's `agent.yaml` (system prompt + attached `skills/`) and runs it as a
multi-turn agent through the Claude Agent SDK. **An agent gets exactly the tools it declares** —
nothing is injected for you:

```yaml
mctools:
  - my_lookup                 # (A) a function tool you write, at mctools/my_lookup/tool.py
  - name: company             # (B) a remote MCP server you wire yourself (e.g. the company MCP)
    url: "${MCCTX_MCP_URL}"   #     ${VARS} are read from localdev/.env — keep tokens out of git
    transport: http
```

- **(A) Function tool** — a string entry `my_lookup` maps to `mctools/my_lookup/tool.py`, which
  defines `NAME`, `DESCRIPTION`, `INPUT_SCHEMA`, and a `run(args)` function.
- **(B) Remote MCP server** — a `{name, url}` mapping; your agent connects to it directly. The
  company tools are an MCP you're given a URL + token for — plugging it in is part of the job
  (see `../docs/company-tools.md`). Keep the token in `localdev/.env` (copy `.env.example`).

Declare nothing under `mctools` and you get a **pure conversational agent** — that's the `demo/`.

## This is local iteration, not deployment

Local dev is for fast iteration. When you're happy, you build the real **Claude Managed Agent** in
your own workspace and push it with the official CLI — that's what the bench runs against. See
[`../docs/building-agents.md`](../docs/building-agents.md). One stays your sketchpad; the other is
your submission. There's no push-to-main here.

> Auth note: this uses *your own* Claude subscription through the official CLI login — the
> supported way to run the Agent SDK on a subscription. No shared key to manage.

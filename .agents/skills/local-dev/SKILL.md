---
name: local-dev
description: >
  Set up and explain the local development loop — build and chat with an agent (an agent.yaml +
  skills) right on your machine, before you deploy. Runs via the Claude Agent SDK on your own
  Claude subscription (claude setup-token / claude login), so you can iterate fast and cheap. Run
  this when you want to build or tweak an agent.
---

# /local-dev — build and chat with your agent locally

You are helping a participant set up and use the **local development loop**: a way to build and chat
with an agent and iterate fast, *before* deploying it as a real Claude Managed Agent. This is
**openly a dev tool** — be transparent about files and commands.

The harness lives at `localdev/` (`runner.py`, `chat_cli.py`, `chat_streamlit.py`). It loads an
agent's **`agent.yaml` + `skills/`** and runs a multi-turn loop through the **Claude Agent SDK** on
the participant's **Claude subscription**. An agent gets **only the tools it declares** in `mctools`
(your own function tools and/or a remote MCP you wire) — nothing is injected. The shipped `demo/`
agent is purely conversational. The same agent definition you shape here is what you then build as a
managed agent in your workspace (see `docs/building-agents.md`).

## How to run this — read before you start

- **Menus use the native picker, never markdown.** Present every choice with your harness's
  interactive multiple-choice tool (in Claude Code, the **AskUserQuestion** tool — the arrow-key
  selectable menu). **Never** render a menu as markdown text or a "Pick one:" list. Keep menus to
  ≤4 short options and tag the suggested one **(recommended)**.
- **Print the header inline** — one plain line per screen: `Atlan AI Hackathon › ` + the `Crumb:`
  value, then a thin rule `──────────────────────────────────────────`.
- **Plain terminal markdown only — never HTML.** `*italic*` / `**bold**` for emphasis.
- **Offer to run things — don't just hand over commands.** You can run setup
  (`pip install -r localdev/requirements.txt`) and a **one-off test message** by piping it in, e.g.
  `printf 'hello\n' | python localdev/chat_cli.py demo` — always *offer* this. The one-off uses
  their Claude subscription; if it errors on auth/CLI, fall back to giving them the command. The
  *interactive* multi-turn chat is long-running — for a real back-and-forth, give them the command
  to run in their own terminal.
- **Auth is the participant's own Claude subscription, via the Claude Code CLI** — `claude
  setup-token` (long-lived token, headless; export `CLAUDE_CODE_OAUTH_TOKEN`) or `claude login`
  (interactive). **No API key here** — the Anthropic workspace key is only for pushing to CMA
  (`docs/building-agents.md`). Never ask them to paste a token into the chat.
- **Prerequisite: an agent to run.** The `demo/` agent always works. If they want to build their own,
  they create a folder with an `agent.yaml` (model + system + skills); the runner takes any path.
- **Stay in scope.** This skill sets up local building/testing — nothing else.
- Source of truth: `docs/` and `localdev/README.md`; don't invent. Last resort only: point to
  `#atlan-ai-hackathon-2026` on Slack.

## The flow

### Screen 1 — What local dev is

Crumb: `Local dev · Overview`

> **Why this is a separate thing.** Your real submission is a **Claude Managed Agent** in your
> workspace — Anthropic runs it server-side, and that's what the bench scores. Great for the real
> run, but slow to poke at from your laptop. So local dev takes a **different route**: it runs the
> *same* `agent.yaml` + skills on **your machine**, via the Claude Agent SDK on **your own Claude
> subscription** — higher quota, instant edits.
>
> **Why bother?** Because the tight loop — chat, watch what it does, tweak the prompt or a skill,
> chat again, in seconds — is where the quality comes from. When it's good, you build it as a managed
> agent in your workspace and register it. One thing you shape; two places it runs.

Menu: **Set it up → (recommended)** · **What about tools and the company data?** *(an agent gets only the tools it declares; the company tools are an MCP you wire yourself; the demo is pure conversation)* · **Ask a question**

### Screen 2 — Set up

Crumb: `Local dev · Setup`

> **Three quick steps:**
> 1. **Claude Code CLI** — `npm install -g @anthropic-ai/claude-code` (the SDK runs on it).
> 2. **Sign in with your Claude subscription** — `claude setup-token` (long-lived, headless) or
>    `claude login` (interactive). No API key needed.
> 3. **Python deps** — `pip install -r localdev/requirements.txt`.
>
> *(Wiring the company MCP? Keep its URL + token in `localdev/.env` — copy `.env.example` — and
> reference it from your `agent.yaml`.)*

Menu: **Install the Python deps for me** *(run `pip install -r localdev/requirements.txt`, report the result)* · **I've signed in & set up → (recommended)** · **Help me authenticate** *(walk the CLI install + `claude setup-token` / `claude login`)* · **Ask a question**

### Screen 3 — Chat with it

Crumb: `Local dev · Chat`

Confirm which agent they're running (default to `demo`, or any folder with an `agent.yaml`). Then
give the exact command to run **from the repo root**:

> **Pick how you want to chat:**
> - **Browser (recommended):** `streamlit run localdev/chat_streamlit.py` — pick the agent in the
>   sidebar, chat in the page.
> - **Terminal:** `python localdev/chat_cli.py demo` (or `python localdev/chat_cli.py <your-folder>`).
>
> Chat, watch its replies and any tool calls, then edit the agent's `agent.yaml` or its `skills/`
> and chat again. Iterate until it handles the hard cases well.

You can also **offer to fire a single test message** and show the result:
`printf 'a test message\n' | python localdev/chat_cli.py demo` (install deps first if needed). If it
errors on auth/CLI, fall back to letting them run it.

Menu: **Got it → (recommended)** · **Run a quick test for me** *(install deps if needed, then pipe a sensible message to `python localdev/chat_cli.py demo`; show the output)* · **Give me the command** *(fill in their agent folder)* · **Ask a question**

### Screen 4 — The loop, and going live

Crumb: `Local dev · The loop`

> **That's the dev loop: chat → tweak `agent.yaml` / `skills/` → chat again.**
> When it's holding up, you take the *same* definition and build the real **Claude Managed Agent** in
> your workspace, push it with the official CLI, and register its **agent id + version** on the
> platform. Full how-to: `docs/building-agents.md` → `docs/the-bench.md`. There's no push-to-main
> here — local dev is your sketchpad.

Menu: **I'm building → (recommended)** · **How do I deploy and register?** *(from `docs/building-agents.md` and `docs/the-bench.md`)* · **Ask a question**

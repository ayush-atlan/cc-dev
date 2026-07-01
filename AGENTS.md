# AGENTS.md — Atlan AI Hackathon

> Working guide for any AI coding agent (Claude Code, Codex, Cursor, pi, OpenCode, …) used in this repo.

## What this repo is

Your team's working repo for the Atlan AI Hackathon. You're an **AI agency**; **McContext** is your
client. You build agents (as **Claude Managed Agents** in your own workspace), wrap them in a
product, and pitch it. The agent you register on the platform is what the bench scores.

## Getting started

Run the **onboarding** skill first — it covers the hackathon, the challenges, and how to build & submit:

| Harness | How to start |
|---|---|
| **Claude Code** | `/onboarding` |
| **Codex / pi** | `$onboarding` (or `/skills`) |
| **OpenCode** | `/skills`, then `onboarding` |

Skills live in **`.agents/skills/`** (`onboarding`, `demo`, `local-dev`); `.claude/skills` is a
symlink to it.

## The build loop

- **Pick a challenge** — `tasks/<id>/task.md`.
- **Iterate locally** — `/local-dev` (Claude Agent SDK on your Claude subscription). Practice: `/demo`.
- **Deploy** — build the real Claude Managed Agent in your workspace (`docs/building-agents.md`).
- **Bench** — register the agent id + version on the platform; 3 lives; submit (`docs/the-bench.md`).

Reference docs: `docs/building-agents.md`, `docs/the-bench.md`, `docs/hackathon.md`, `docs/faq.md`.

## Ground rules

- **Build the agent definition yourself.** There's no scaffold or converter — that's part of the
  job. Use the official Claude Managed Agents docs (linked in `docs/building-agents.md`).
- **Two credentials, two jobs.** Local dev → your Claude subscription (no API key). Deploy → your
  Anthropic workspace key. Don't cross them.
- **Never commit secrets.** Keep the MCP token and any keys in a gitignored `.env` (see
  `localdev/.env.example`); never paste them into chats, logs, or a committed `agent.yaml`.
- **Don't hardcode the data.** The bench uses held-out cases — build for the general job.
- **Handle company data responsibly.** It's read-only; don't exfiltrate it or send secrets to
  external services.

Questions not answered in `docs/`? Ask in **`#atlan-ai-hackathon-2026`** on Slack.

# CLAUDE.md — Atlan AI Hackathon (Claude Code)

> Quick reference for Claude Code. Full guide: `AGENTS.md`.

## Start here

Run **`/onboarding`** — it covers the hackathon, the challenges, and how to build & submit. Skills
live in `.agents/skills/` (`onboarding`, `demo`, `local-dev`); `.claude/skills` symlinks to it.

## The build loop

- **Pick a challenge** — `tasks/<id>/task.md`.
- **Iterate locally** — `/local-dev` (runs on your Claude subscription). New? `/demo`.
- **Deploy** — build the real Claude Managed Agent in your workspace — `docs/building-agents.md`.
- **Bench** — register the agent id + version on the platform; 3 lives; submit — `docs/the-bench.md`.

## Ground rules

- Build the agent definition yourself — no scaffold or converter (it's part of the job). Official
  Claude Managed Agents docs are linked in `docs/building-agents.md`.
- Two credentials: **local dev → your Claude subscription** (no API key); **deploy → your Anthropic
  workspace key**. Company tools are an **MCP** (URL + token) you wire yourself.
- **Never commit secrets** — tokens go in a gitignored `.env`. Don't hardcode held-out data.

Help: `#atlan-ai-hackathon-2026` on Slack.

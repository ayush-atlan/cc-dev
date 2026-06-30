# Atlan AI Hackathon — Onboarding & Practice

This is the **onboarding repo** — a hands-on warm-up so you get comfortable with the whole flow
**before** the hackathon starts. Today you'll build a tiny agent, run it locally, deploy it to your
own Claude Managed Agents workspace, and run it there — end to end, with nothing at stake.

> **Today vs tomorrow.** This repo has **one practice challenge** so you can rehearse the loop.
> **Tomorrow you'll get your real hackathon repo** — the *same* onboarding flow, but with the
> **actual challenges** and the briefs you're scored on. Get your hands dirty here first.

## Start here

Open this folder in **Claude Code** and run:

```
/onboarding
```

It covers the mission, how you build on Claude Managed Agents, the practice challenge, and how
you're scored — then walks you through the whole loop on a tiny practice agent.

> On Codex, pi, or OpenCode? The skills are standard Agent Skills in `.agents/skills/` — run
> `$onboarding` or `/skills`.

## The practice loop (today)

1. **Meet an agent** — `/demo` walks you through a tiny, conversational example end to end.
2. **Build & iterate locally** — `/local-dev` runs an agent on your own Claude subscription.
3. **Deploy to your workspace** — build the real Claude Managed Agent; it gets an agent id +
   version. See [`docs/building-agents.md`](./docs/building-agents.md).
4. **Run it in your workspace** — open a session and chat with it live.
5. **Rehearse the bench** — the practice challenge in `tasks/practice/` lets you walk
   register → run → submit. See [`docs/the-bench.md`](./docs/the-bench.md).

Tomorrow, the same flow runs against the **real challenges** in your hackathon repo.

## What's in here

| Path | What it is |
|------|------------|
| `.agents/skills/` | The skills — `onboarding`, `demo`, `local-dev` (`.claude/skills` symlinks here) |
| `tasks/practice/` | The one **practice** challenge (real challenges arrive tomorrow) |
| `docs/` | How to build, the company tools, the bench, scoring, FAQ |
| `localdev/` | The local Agent SDK harness — chat with your agent on your subscription |
| `demo/` | A tiny, not-scored conversational example agent |

## Credentials, at a glance

- **Local dev** runs on **your Claude subscription** (`claude setup-token` / `claude login`) — no API key.
- **Deploying to your workspace** uses your **Anthropic workspace key** (organizers provide it via 1Password).
- **Never commit secrets** — keep keys and tokens in a gitignored `.env`.

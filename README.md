# Atlan AI Hackathon

This is your team's hackathon repo. You're an **AI agency**; **McContext** — a 2,000-store burger
chain that just went AI-native — is your client. You build agents, wrap them in a product, and pitch
them.

**The challenges are live.** Their briefs are in `tasks/`.

## Start here

Open this folder in **Claude Code** and run:

```
/start-hackathon
```

It kicks off the hackathon: the challenge gallery, the full brief for any one you open, how you win,
and the handoff to building. New to all this (or missed onboarding)? Run **`/onboarding`** first, or
**`/demo`** for a hands-on tour of what an agent even is.

> On Codex, pi, or OpenCode? The skills are standard Agent Skills in `.agents/skills/` — run
> `$start-hackathon`, `$onboarding`, or `/skills`.

## The build loop

1. **Pick a challenge** — the briefs are in `tasks/`. Depth beats breadth; take one or a few.
2. **Build & iterate locally** — `/local-dev` runs your agent on your own Claude subscription.
3. **Deploy to your workspace** — build the real Claude Managed Agent; it gets an agent id +
   version. See [`docs/building-agents.md`](./docs/building-agents.md).
4. **Prove it on the bench** — register the id + version on the platform, spend **3 lives** running
   against real hidden cases, then submit. See [`docs/the-bench.md`](./docs/the-bench.md).
5. **Build the product and pitch it** — the bench is one input; the product and pitch carry real
   weight. The top 7 teams present live to McContext's founders.

## What's in here

| Path | What it is |
|------|------------|
| `.agents/skills/` | The skills — `start-hackathon`, `onboarding`, `demo`, `local-dev` (`.claude/skills` symlinks here) |
| `tasks/` | The challenge briefs — plus a no-stakes **practice** warm-up |
| `docs/` | How to build, the bench, the hackathon brief, FAQ |
| `localdev/` | The local Agent SDK harness — chat with your agent on your subscription |
| `demo/` | A tiny, not-scored conversational example agent |

## Credentials, at a glance

- **Local dev** runs on **your Claude subscription** (`claude setup-token` / `claude login`) — no API key.
- **Deploying to your workspace** uses your **Anthropic workspace key** (organizers provide it).
- **Company data & tools** come as an **MCP** (URL + token) you wire yourself.
- **Never commit secrets** — keep keys and tokens in a gitignored `.env`.

# FAQ

**How do I get started?**
Run **`/onboarding`** for the guided tour, or jump in: run **`/demo`** for a hands-on practice agent
(not scored), then **`/local-dev`** to build and chat with your own. Pick a challenge in `tasks/`.
When your agent is good, build it as a Claude Managed Agent in your workspace and register it on the
platform ([`the-bench.md`](./the-bench.md)).

**What's the demo?**
A tiny, not-scored conversational agent in `demo/`. Run `/demo` (or `python localdev/chat_cli.py
demo`) to see how an agent is built, chat with it, and tweak it. The fastest way to learn the loop.

**Do I have to do all the challenges?**
No. Pick the ones you want - depth often beats breadth.

**How do I build and submit my agent?**
Build it as a Claude Managed Agent in your own workspace and push it with the official CLI
([`building-agents.md`](./building-agents.md)). Your workspace gives it an **agent id + version**;
paste those into the platform to register it for a challenge, then Run the bench
([`the-bench.md`](./the-bench.md)).

**Do you scaffold the agent for me?**
No. There's no template or converter - building the agent definition is part of the job. The
official Claude Managed Agents docs are your reference (linked in `building-agents.md`).

**Local dev - which credentials?**
Local dev runs on **your Claude subscription** via the Claude Code CLI (`claude setup-token` or
`claude login`) - higher quota, fast iteration, no API key. The **Anthropic workspace key** is only
for pushing to your CMA workspace. Two credentials, two jobs.

**How do I get the company data and tools?**
You're given the company **MCP** - a URL and an OAuth token. Wiring it into your agent is part of
the challenge. Keep the token out of git.

**How many tries do I get?**
**3 lives per challenge.** Each Run spends one; Submit is your final answer (its score stays with
the organizers). Iterate between lives by pushing a new version and re-registering.

**What model should I use?**
Your choice. Pick what gives the best quality for the job.

**Is there a playbook for each challenge?**
No, on purpose. We give you the brief and the data, not the answers.

**Where do I ask for help?**
The **`#atlan-ai-hackathon-2026`** Slack channel. Check this FAQ and `docs/` first.

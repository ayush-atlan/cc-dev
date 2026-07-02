# Scott — Stock Inventory & Supply Agent · Project Log

> Handoff / write-up for the Atlan AI Hackathon 2026, **Stock** challenge. Everything we did, the
> decisions and their rationale, what's verified, and what's next. Written to drop into Confluence.

**Team:** CompactionCrew · **Challenge:** Stock (Inventory & Supply) · **Agent persona:** Scott
**Data clock:** the world runs on `world_meta.now` = **2026-06-24** (never wall-clock).

---

## 1. What we're building

McContext (the client) needs an inventory & supply agent that runs the stockroom across its stores.
The agent, **Scott**, does four jobs and can explain any call it makes:

1. **Variance & root cause** — what stock *should* remain vs what was counted, and *why* the gap.
2. **Demand forecast** — per store, per SKU, next N days, graded against hidden actuals.
3. **Smart reorder** — turn the forecast into a real order (whole cases, respect shelf life).
4. **Waste markdown** — spot near-expiry stock and price it to recover the most value.

Plus **integrity**: stay in inventory's lane (refuse customer/finance data), decline when the data
can't support an answer, and never fabricate a number.

### Two surfaces (the core mental model)

The hackathon scores two different things, and we treat them separately:

- **Bench agent (scored).** A **Claude Managed Agent** = model + system prompt + skills + wired
  tools. Stateless per session. The *only* thing the bench grades, through four submit tools. Keep
  it tight — anything stateful or flashy does **not** belong here.
- **Product (pitch).** A demo/site wrapped around the same agent for the sales pitch. Reads the same
  data, not graded, but carries real weight in judging.

Every feature idea has to compile down to the bench agent's four primitives, or it lives in the
product. This split drove every scoping decision below.

---

## 2. How the environment is wired

- **Local dev loop.** `localdev/` runs the same `agent.yaml` + skills on our own Claude subscription
  via the Claude Agent SDK — fast, cheap iteration before spending bench lives. Chat with
  `.venv/bin/python localdev/chat_cli.py stock`.
- **Python 3.12 venv.** System `python3` is 3.9, too old for the SDK (needs 3.10+). We created a
  `uv`-managed `.venv` on 3.12 and install `localdev/requirements.txt` there. **Always use
  `.venv/bin/python`.**
- **Company data = the MCP.** McContext exposes a hosted MCP (URL + Bearer token in the gitignored
  `localdev/.env`). It provides:
  - `run_sql` — read-only SELECT/WITH against the `world` schema (args `{query, purpose}`).
  - `submit_variance` / `submit_forecast` / `submit_reorder` / `submit_markdown` — the action tools
    that carry each duty's graded answer.
- **Auth fix we had to make.** `localdev/runner.py` originally only forwarded a `url` for remote MCP
  servers. We patched it to also forward a `headers` map (with `${VAR}` expansion), so `agent.yaml`
  can pass `Authorization: Bearer ${MCP_AUTH_TOKEN}`.

### The direct-Postgres dead end (and how we routed around it)

We were also handed a raw read-only Postgres URL (`WORLD_DB_URL`). It **never connected** — TCP opens
but the server drops the connection during the Postgres startup handshake, on every SSL/GSSAPI
combination and across retries (the Railway instance appears paused/unavailable). The **MCP's
`run_sql` reaches the same data fine**, so:

- The bench agent queries **only** through the MCP (`run_sql`) — which is also correct for
  bench parity (no local DB tool exists on the bench anyway).
- For local scripts (the backtest), we wrote `localdev/mcctx.py` — a tiny client that calls `run_sql`
  over the MCP's streamable-HTTP transport, so we never depend on the dead direct route.
- The old `stock/mctools/world_db/tool.py` (direct-Postgres SQL tool) is left on disk but **unwired**
  from `agent.yaml`.

---

## 3. What we learned about the data (findings)

Verified against the live DB via the MCP:

- **Small curated world:** 10 stores, 11 SKUs, 6 menu items (the "~2,000 stores" is brand framing).
- **Sales:** `inv_sales_daily`, 2025-12-24 → 2026-06-23, 10,920 rows, all 10 stores. We derive
  per-SKU demand as **`sales × recipe`** (`inv_sales_daily` ⋈ `inv_recipes`) — this is the only
  source with full-store breadth.
- **Usage:** `inv_usage_daily` covers **only ~3 stores** — usable for the over-portion signal, not
  for breadth.
- **Counts / receipts:** `inv_counts` and `inv_receipts` cover **3 stores, one week** (Jun 17–23) —
  so variance/reorder cases are a thin slice; queries must be robust to a single window.
- **Catering:** `world.catering_orders` exists (store_id, event_local, headcount, status) — a real
  upcoming-demand signal, so the catering-aware forecast is data-backed.
- **Stores:** real `market` + `timezone` per store; **no ownership field** and **no promo table**.
- **Waste:** 6 months of `inv_waste_logs`, all `spoilage`, totalling **$325** at cost across 10
  stores.

Key inventory tables: `inv_counts, inv_receipts, inv_recipes, inv_sales_daily, inv_usage_daily,
inv_waste_logs, inv_shift_logs, inv_skus`.

---

## 4. The feature freeze (what's in, what's out, and why)

We froze scope in `stock/FINAL.md`. `#` is our own index; verdict = BUILD / NARRATE / CUT.

| # | Feature | Surface | Verdict | Why |
|---|---------|---------|---------|-----|
| core | 4 duties | Bench | **BUILD** | The whole graded job. |
| int | Scope refusal + no-fabrication | Bench | **BUILD** | "Know its limits" is a scored dimension. |
| 1 | Quiet-week / don't cry wolf | Bench | **BUILD** | Say "it reconciles" when true; false alarms lose points. |
| 2 | Ask-why / justify-from-trace | Bench | **BUILD** | Always show the query + reasoning behind a call. |
| 4 | Markdown self-negotiation | Bench | **BUILD** | Compare ≥2 discount/timing options by recovered value. |
| 5 | Catering-aware forecast | Bench | **BUILD** | `catering_orders.headcount × recipe` uplift (data exists). |
| 3 | Retroactive audit ("$X caught") | Product | **BUILD** | Backtest math → the credibility number. |
| 7 | Savings counter | Product | **BUILD** | Dollars saved + shadow "lost without Scott." |
| 8 | Sustainability (lbs / CO2e) | Product | **BUILD** | Σ(waste × factor); factors are stated knobs. |
| 9 | EPS / P&L framing | Product | **BUILD** | Annualized projection, **labelled**. |
| rb | Inter-store rebalancing | Product | **BUILD (display-only)** | No submit tool exists → never scored. |
| 6 | Override-learning | — | **NARRATE** | Needs cross-session persistence a CMA doesn't have. |
| 10 | Ownership-aware tuning | — | **CUT** | No ownership field in the data. |

**Locked decisions:** MCP-only data path (bench parity); assumptions (catering menu-mix, markdown
elasticity, CO2 factors, the 2,000-store multiple) are stated in-answer as assumptions, never as
measured; folder stays `stock/`, persona is Scott.

---

## 5. How we implemented the bench agent

### `stock/agent.yaml`
- `model: claude-opus-4-8`.
- System-prompt spine, applied every turn: **investigate with `run_sql` → compute in SQL → submit
  through the matching action tool → show your work in 2–3 lines.** Plus the integrity rules
  (decline-if-thin, quiet-week, scope refusal, no fabrication) and "read the world clock."
- `mctools`: the `mcctx` MCP only (Bearer header). `world_db` dropped.
- Skills: `duties` + `context`.

**Why:** grounding by construction. Making the model do arithmetic **in SQL** (not in its head) hits
three scoring dimensions at once — accuracy, tool use, and efficiency — and makes every answer
auditable.

### `stock/skills/duties/SKILL.md`
Each duty is one block: **Needs / Decline-if / Formula / Query / Submit / Say.** The scored
"features" (#1, #2, #4, #5) are folded in as reasoning steps, not separate systems:

- **Variance:** `expected = opening + Σreceipts − Σ(sold·recipe) − Σwaste`; `gap = expected −
  closing`. Root cause picked from evidence (`inv_waste_logs.reason`, `inv_shift_logs.note`, usage vs
  recipe-implied) and mapped to the enum; `unknown` is a valid answer.
- **Forecast:** trailing 8-week mean **× day-of-week share** (weekly seasonality dominates a burger
  chain; explainable, no black-box ML), plus a catering uplift when an event falls in the horizon.
  Always submit `predicted_daily[]` (per-day accuracy is rewarded).
- **Reorder:** `need = forecast(lead+horizon) − on_hand`; `order = ceil(net/pack)·pack` (whole
  cases); shelf-life cap so we never order more perishable stock than sells before it expires.
- **Markdown:** find near-expiry lots, estimate what won't clear at current velocity, then pick the
  discount that **recovers the most value** (compare ≥2 options), effective now.

**Why day-of-week mean:** it's the simplest method that captures the dominant signal (weekly
seasonality), it's fully explainable to a judge, and we **validated it empirically** (see §7) rather
than reaching for ML we couldn't justify.

### `stock/skills/context/SKILL.md`
Static reference the schema lacks: the **real store roster** (market/timezone) and the **promo
calendar**. Crucially, **promotions = none confirmed → apply no uplift** — inventing promos would
have skewed the bench forecast. Per-store operating quirks point at the live `inv_shift_logs` rather
than authoring fake demand multipliers.

**Why:** authored context is legitimate domain knowledge, but only when it's *true*. We grounded it
in the real `stores` table and refused to fabricate the parts that don't exist.

---

## 6. How we implemented the dev harness

- **`localdev/mcctx.py`** — blocking `run_sql(query, purpose)` helper over the MCP streamable-HTTP
  client; loads auth from `.env`. Lets plain scripts hit the same read path the agent uses.
- **`localdev/backtest.py`** — forecast backtest that validates the *method* before we spend bench
  lives. Holds out the last 7 days, trains DoW means on the rest, scores **WAPE** per store/SKU.
  Computed **entirely in SQL** (one row per store/SKU) because `run_sql` caps returned rows — a raw
  row-dump only returned one series. Doubles as the retroactive-audit engine for the pitch.
- **`localdev/runner.py`** — the headers-forwarding fix for authenticated remote MCPs.

**Why in-SQL:** same lesson as the agent — the row cap forced us to aggregate server-side, which is
also faster and the pattern we want the agent itself to follow (return the answer, not the rows).

---

## 7. What's verified (evidence)

All four duties were run end-to-end against the **live MCP** in local dev:

| Check | Result |
|-------|--------|
| Scope refusal | Refused "last month's refund totals" as finance/customer data, offered inventory help. ✅ |
| Tool discovery | Queried `information_schema` to find the 8 `inv_*` tables (not hardcoded). ✅ |
| **Forecast** | `str_001/sku_bacon`, 7 days: DoW-mean, 19.64 kg total; checked catering + promos; `submit_forecast` with `predicted_daily[]`. ✅ |
| **Variance** | `str_001/sku_cheese` Jun 17–23: expected 33.25 vs counted 25.25 → gap 8; ruled out waste; found the Jun 21 shift note (new hand over-portioning) → `over_portion`. ✅ |
| **Reorder** | Same SKU: 14 cases (70 kg), pack-rounded, shelf-life cap checked, review-horizon assumption stated. ✅ |
| **Markdown** | Only lot 10 days out → **declined** ("no markdown needed") — quiet-week behavior. ✅ |
| **Forecast backtest** | 110 store/SKU pairs, holdout last 7 days → **5.6% median WAPE** (best 2.6%, worst 41.6%). ✅ |

**Proof numbers for the pitch (measured):** 5.6% median forecast WAPE; $325 six-month spoilage on
the 10-store pilot; a real $43.20 over-portion catch (8 units × $5.40) traced to a shift note.
Chain-wide figures are labelled projections.

---

## 8. The product surface (landing + live chat)

`product/index.html` — self-contained landing page in Scott's voice ("Never short. Never wasteful.").
Sections: the four duties, **measured** proof stats, the itemized real catch, the quiet-week
principle, "why different," and a technical-buyer explainer. Rebalancing is **display-only** and
honestly framed — the pilot data (no SKU counted at ≥2 stores) can't back a real cross-store
snapshot, so we didn't fake one. **Theme:** re-skinned to a dark "liquid-glass" look (hero video +
Instrument Serif + glassmorphism cards); the hero video/font are external CDNs with graceful
fallbacks (gradient + `serif`).

`chat/` — a **browser chat that replaces Streamlit**, no npm/React/build:
- `chat/server.py` — stdlib `http.server` (zero deps). Serves the landing at `/`, the chat UI at
  `/chat`, and `POST /api/chat` which wraps the existing `localdev` `Conversation` (same agent, same
  Claude subscription as `chat_cli.py`). One server, one command: `.venv/bin/python chat/server.py`.
- `chat/index.html` — dark chat page modeled on a shadcn prompt-box (we replicated the *look* in
  plain HTML/CSS; a React component can't drop into a Python repo). Natural, ops-manager quick
  prompts ("Where did our cheese go?") that resolve store *names* → IDs via the `context` skill.
- The landing's "Chat with Scott" CTAs route to `/chat`; the chat page links back to `/`.

**Why the lazy HTML path, not React/shadcn:** there is no frontend toolchain in this repo. Standing
up Vite/Tailwind/shadcn + an API bridge for a chat box is the over-engineering trap; the stdlib
server + one HTML file does the whole job.

---

## 9. Repo map

```
stock/
  agent.yaml              # bench agent: model + prompt + skills + MCP (world_db removed)
  skills/duties/SKILL.md  # the four grounded duty blocks
  skills/context/SKILL.md # store roster + "no promos" + shift-log pointer
  FINAL.md                # feature freeze
  FINDINGS.md             # verified data facts
  BUILDIT.md              # detailed executable build plan
  LANDING.md              # pitch copy
  PROJECT-LOG.md          # this file
localdev/
  mcctx.py                # run_sql over the MCP, for scripts
  backtest.py             # in-SQL forecast backtest (5.6% WAPE)
  runner.py               # patched: forward MCP auth headers
  requirements.txt        # psycopg dropped (only world_db used it)
chat/
  server.py               # stdlib server: / landing, /chat UI, POST /api/chat -> agent
  index.html              # dark chat page (Streamlit replacement)
product/
  index.html              # liquid-glass landing page; CTAs -> /chat
```

**Git:** branch **`compactioncrew/scott`** (renamed from `feat/stock-scott-agent`), pushed to two
remotes: **origin** = `atlanhq/atlan-hackathon-onboarding`, **cc-dev** = `ayush-atlan/cc-dev`. Latest
commit `1610a4d`. Secrets stay in gitignored `localdev/.env` (verified never committed). Note: a
second checkout exists at `~/compactioncrew/scott-agent` with the same branch/commits.

---

## 10. Deploying to Claude Managed Agents (CMA) — DONE

Deployed via the `ant` CLI (v1.13.0). The **live agent is `agent_01LnuHzFhUWutjtkRkLU5HNQ`,
currently version 2**, model `claude-opus-4-8`.

**How (repeat/iterate):**
1. Participant `ANTHROPIC_API_KEY` in a gitignored root `.env` (from 1Password — **never the judge
   key**). MCP url/token in `localdev/.env`.
2. Build the deployed system prompt = the *exact* local one (agent.yaml + both skills concatenated):
   `.venv/bin/python -c "import sys;sys.path.insert(0,'localdev');from runner import load_agent;m,s=load_agent('stock');open('/tmp/scott_system.txt','w').write(s)"`
3. `ant beta:agents create --name "Scott — Inventory & Supply" --model '{id: claude-opus-4-8}'
   --system "$(cat /tmp/scott_system.txt)" --mcp-server "{type: url, name: mcctx, url: \"$MCCTX_MCP_URL\"}"
   --tool '{type: agent_toolset_20260401}' --tool '{type: mcp_toolset, mcp_server_name: mcctx,
   default_config: {permission_policy: {type: always_allow}}}' --format json`
4. Iterate → new version: `ant beta:agents update --agent-id <id> --version <current> --system "$(cat /tmp/scott_system.txt)"`.
5. Register `agent_01LnuHzFhUWutjtkRkLU5HNQ` on the McContext platform **Deploy** page → **Resolve**
   (pulls latest version) → **Run** (spends 1 of 3 lives) → **Submit**.

**CMA gotchas we hit (things the repo guide under-specifies):**
- `--model` needs the **object** form `'{id: claude-opus-4-8}'`, not a bare string.
- **MCP auth is NOT in the agent** — the agent only declares `{type:url,name,url}`; the Bearer token
  is supplied at **session** time via a **vault** (URL-matched). At grading time the platform
  provides it; for our own Console test sessions, pick the pre-provisioned `hackathon-participant`
  environment (it supplies MCP auth) — no vault needed there.
- **`mcp_toolset` defaults to `always_ask`** → an autonomous bench run would freeze. We set
  `default_config.permission_policy.type = always_allow`. **If Scott ever stalls mid-run, this is why.**
- **Skills are inlined** into the system prompt for now (`skills: []` first-class). Exact parity with
  local. Upgrade path = first-class `--skill` for progressive disclosure (see §12).
- **Can't find the agent in the Console?** It's scoped to the workspace the API key belongs to — pick
  the workspace that also shows the "Frye (demo)" agent. The API confirms it exists regardless
  (`ant beta:agents list`).

---

## 11. Trap-hardening (the most important quality change) — DONE, deployed as v2

The organizers' platform walkthrough revealed the scoring principle: **the database has intentional
traps, `world_meta.now` is the source of truth for "today," and agents that skip verification (to
save tokens, or via custom tools) hallucinate and score 0.** Example trap: a simulated user claims
"it's been 10 days" but the data says 17 — a refund/expiry window flips on the true date.

We hardened Scott (`agent.yaml` + `duties` skill) on the two named failure modes:
- **Trust the data, not the claim** — never take a user-asserted date/quantity/status at face value;
  look it up; if the data disagrees, go with the data and say so.
- **Grounding beats efficiency** — never skip a verification query to save tokens/tool calls.
- **Always read `world_meta.now`** as "today" before any date-dependent step.

**Verified** with a deliberate double-trap prompt ("Today is Jan 15 2026… expires in 8 days"): Scott
queried the clock, corrected *both* facts from the data (real date 2026-06-24; real shelf life 14d →
10 days left, not 8), and declined the markdown. Exactly the failure mode the video described,
defeated. Deployed as v2.

---

## 12. Open work / next steps (for whoever picks this up)

**Efficiency — findings 1–3 APPLIED (deployed as v3); finding 4 held:**
- ✅ **`world_meta` shape bug fixed** — was `world_meta.now` (a column) but it's `key/value`, causing
  **~3 discovery calls/session**. Now the prompt + `duties` give the exact one-call query
  `SELECT value FROM world.world_meta WHERE key='now'`. Correctness + efficiency win.
- ✅ **Clock read scoped** — was "ALWAYS at the start" (over-fired on scope refusals); now "before
  any date-dependent step."
- ✅ **Discovery scoped** — removed "discover via information_schema"; the `duties` skill lists all
  tables, so Scott queries them directly and only probes `information_schema` if something's missing.
- ⏸ **~4,054 tokens inlined every turn** (both skills in the system prompt) — HELD. Token lever =
  move `duties`/`context` to first-class `--skill` (CMA progressive disclosure). Trades determinism;
  grounding wins the bench, so leave inlined unless efficiency scoring demands it.

**Product / pitch:**
- Wire the retroactive-audit dollar figure + savings counter from `backtest.py`; add sustainability
  (lbs/CO2e) and EPS framing as **labelled projections**; static rebalancing + Patty-handoff illustration.
- Deck + walkthrough video. Narrate override-learning (#6) as roadmap; be explicit pilot vs projection.

**Bench:**
- Spend life #1: Run `agent_01LnuHzFhUWutjtkRkLU5HNQ` on the platform, read the trace, fix, hold lives 2–3.
- Harden thin slices: variance/reorder only have 3 stores × 1 week of counts — decline cleanly when a
  count is missing rather than guessing.
- Tune forecast knobs with `backtest.py` (4 vs 8 wk window, catering uplift); keep what lowers WAPE.

**Open data questions (one query each):** is `inv_usage_daily.qty_used` recorded actuals or
theoretical (decides the over-portion signal)? How are `inv_counts` spaced (is a "window" the span
between two consecutive counts per store/sku)?

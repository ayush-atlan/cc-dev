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

## 8. The product surface

`product/index.html` — a self-contained static landing page in Scott's voice ("Never short. Never
wasteful."). Sections: the four duties, **measured** proof stats, the itemized real catch, the
quiet-week principle, "why different," and a technical-buyer explainer. Rebalancing is presented as
**display-only** and honestly framed — the pilot data (no SKU counted at ≥2 stores) can't back a real
cross-store snapshot, so we didn't fake one.

---

## 9. Repo map

```
stock/
  agent.yaml              # bench agent: model + prompt + skills + MCP
  skills/duties/SKILL.md  # the four grounded duty blocks
  skills/context/SKILL.md # store roster + "no promos" + shift-log pointer
  mctools/world_db/       # direct-Postgres SQL tool — UNWIRED (dev-only)
  FINAL.md                # feature freeze
  FINDINGS.md             # verified data facts
  BUILDIT.md              # detailed executable build plan
  LANDING.md              # pitch copy
  PROJECT-LOG.md          # this file
localdev/
  mcctx.py                # run_sql over the MCP, for scripts
  backtest.py             # in-SQL forecast backtest (5.6% WAPE)
  runner.py               # patched: forward MCP auth headers
product/
  index.html              # pitch landing page
```

Committed on branch **`feat/stock-scott-agent`**. Secrets stay in the gitignored `localdev/.env`.

---

## 10. What's next

1. **Spend bench life #1.** Deploy the CMA in our workspace (`docs/building-agents.md`), register the
   agent id + version, and do one **Run** against the hidden set to see where we stand. Fix from the
   trace; hold lives #2 and #3.
2. **Harden the thin slices.** Variance/reorder only have 3 stores × 1 week of counts — the bench
   likely targets exactly that slice. Make sure the queries degrade gracefully (decline clearly when
   a count is missing rather than guessing).
3. **Tune the forecast knobs.** Sweep the trailing window (4 vs 8 weeks) and the catering uplift with
   `backtest.py`; keep whichever lowers median WAPE. Confirm the over-portion signal by checking
   whether `inv_usage_daily.qty_used` is recorded actuals vs theoretical.
4. **Finish the product.** Wire the retroactive-audit dollar figure and savings counter from the
   backtest, add the sustainability (lbs/CO2e) and EPS framing as labelled projections, and the
   static rebalancing + Patty-handoff illustration.
5. **Pitch.** Deck + walkthrough video; narrate override-learning (#6) as roadmap; be explicit that
   the 10-store numbers are a pilot and the chain-wide ones are projections.

**Open questions to close:** is `inv_usage_daily` actuals or theoretical? How are `inv_counts`
spaced (is a "window" the span between two consecutive counts)? Both are one query each.

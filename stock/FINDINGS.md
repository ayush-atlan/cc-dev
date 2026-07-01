# Scott — architecture findings

Working notes for **Scott**, our agent for the Stock (inventory & supply) challenge. Secrets live in
`localdev/.env` (gitignored) — never copied here.

## Scale & history (verified against the live DB)

- **Tiny curated world:** 10 stores, 11 SKUs, 6 menu items (not 2,000 — that's brand framing).
- `inv_sales_daily`: 2025-12-24 → 2026-06-23, 10,920 rows, **10 stores** → use `sales×recipe` for
  breadth.
- `inv_usage_daily`: same range but **3 stores** only → use for the over-portion signal, not breadth.
- `inv_counts` / `inv_receipts`: **3 stores, one week** (Jun 17–23) → variance/reorder cases are a
  thin slice.
- `catering_orders`: 30 rows, has `store_id, event_local, headcount, status` → catering-aware
  forecast (#5) is data-backed.
- `stores` has **no ownership field** → ownership-aware markdown (#10) is dead.
- Data clock (`world_meta.now`) = 2026-06-24.

## Two surfaces (where each feature lives)

The bench scores **only the 4 duties + integrity**, via the 4 submit tools. No `submit_transfer`, no
persistence, no counter. So:

- **Bench agent** (moves the score): system prompt + duty skills + SQL. Stateless per session.
  Bench-relevant features: quiet-week/don't-cry-wolf (#1), justify-from-trace (#2),
  markdown self-negotiation (#4), catering-aware forecast (#5).
- **Scott the product** (moves the pitch): separate UI/site, mostly static. Rebalancing + Patty stub
  (§4), retroactive audit (#3), savings counter (#7), sustainability/EPS framing (#8/#9).
  Override-learning (#6) = roadmap narration, not built.

## Shared context (§3) — no persistence framework

Nothing persists across bench sessions. Real "shared context" = three cheap things:
- **Reads:** the world DB (all duties query the same tables) — free shared read context.
- **Authored:** one static JSON in the skill for what the schema lacks — promo calendar + store notes.
- **Writes:** the 4 submit tools.
The "markdown → better next-week forecast" loop is a **demo replay** in the product UI, not agent
state. Building a live context-object system into the CMA is the over-engineering trap.

## In scope vs out of scope

**In scope** — lives in the agent, touches the bench score. This is the whole build-for-score
surface (encode it in the `duties` skill):

- 4 core duties: variance & root cause, demand forecast, smart reorder, waste markdown.
- #1 quiet-week / don't cry wolf → system prompt + every duty.
- #2 ask-why → free if it always shows its work + the SQL.
- #4 markdown self-negotiation → reasoning step inside the markdown duty.
- #5 catering-aware forecast → `catering_orders.headcount × recipe` bump in the forecast duty.
- Hard refusal boundary → decline customer data (`customers`, `orders`, `loyalty_*`, `tickets`) and
  finance P&L (`fin_*`), and say why. `inv_receipts.unit_cost_cents` stays in scope (stock cost).

**Out of scope** — product/pitch surface, does *not* touch the bench score (~6 of 10 headline
features): §4 rebalancing + Patty handoff, #3 retroactive audit, #6 override-learning, #7 savings
counter, #8 sustainability, #9 EPS framing. **Dead:** #10 ownership tuning (no schema field).

## The hard constraint

On the bench, the **only** thing that runs is the Claude Managed Agent: model + system prompt +
skills + tools (MCP + custom). No external orchestrator rides along at grade time. So every design
idea has to compile down to those four primitives. "Harness" splits in two:

- **In-agent** — system + skills + tools that ship and run on the bench.
- **Local eval** — the loop you run on your own Claude subscription to iterate before spending any
  of your **3 bench lives** (`localdev/chat_cli.py stock`). Keep it light: chat-test + a by-hand
  backtest, not a framework.

## MCP wiring (done)

- Endpoint + token: `MCCTX_MCP_URL` / `MCP_AUTH_TOKEN` in `localdev/.env`. Auth = `Authorization:
  Bearer <token>` (verified: 401 without, 200 with).
- `stock/agent.yaml` declares the MCP under `mctools` as `name: mcctx`, `url: ${MCCTX_MCP_URL}`,
  with a `headers.Authorization: "Bearer ${MCP_AUTH_TOKEN}"`.
- `localdev/runner.py` now forwards a `headers` map on remote MCP entries (with `${VAR}` expansion)
  — it previously only wired `url`.

## Company MCP tools

Read: `run_sql` (READ-ONLY SELECT/WITH against the `world` schema; args `{query, purpose}`).

Action / submit (each duty's graded output goes through one of these):

- **Stock:** `submit_variance`, `submit_forecast`, `submit_reorder`, `submit_markdown`
- Support (Patty): `issue_credit`, `issue_refund`, `escalate`, `create_ticket`
- Finance (Penny): `submit_match_exception`, `submit_settlement`, `submit_loss_flag`,
  `submit_duplicate_payment`, `submit_cogs_variance`, `submit_cash_variance`
- Analyst (Pivot): `submit_answer`, `submit_report`

## `run_sql` vs local `world_db` — parity

The MCP exposes `run_sql`, so the deployed CMA queries through it. The local `world_db` custom tool
(`stock/mctools/world_db/tool.py`, points at `WORLD_DB_URL`) does the same thing locally but **won't
exist on the bench**. Decision: **drop `world_db` from `stock/agent.yaml`** so the agent queries the
same way locally and on the bench.

## `world` schema — inventory tables

44 tables total; the Stock-relevant ones:

```
inv_counts       id, store_id, sku_id, count_date, counted_qty          -- physical counts
inv_receipts     id, store_id, sku_id, qty, unit_cost_cents, received_at
inv_recipes      menu_item_id, sku_id, qty_per                          -- SKU per menu item
inv_sales_daily  store_id, menu_item_id, sales_date, qty_sold
inv_usage_daily  store_id, sku_id, usage_date, qty_used                 -- per-SKU daily consumption
inv_waste_logs   id, store_id, sku_id, waste_date, qty, reason, note
inv_shift_logs   id, store_id, shift_date, shift, manager, note
inv_skus         id, name, category, unit, pack_size, shelf_life_days,
                 lead_time_days, unit_cost_cents, perishable
```

## Submit-tool schemas (required fields **bold**)

- **submit_variance** — **store_id, sku_id, gap_qty, root_cause**, expected_qty?, counted_qty?,
  explanation?. `root_cause` enum: `over_portion, spoilage, expiry, theft, miscount,
  delivery_short, prep_error, unknown`.
- **submit_forecast** — **store_id, sku_id, horizon_days**, predicted_total?, predicted_daily?
  (one value per day — per-day accuracy is rewarded).
- **submit_reorder** — **store_id, sku_id, order_qty**, unit?. Must be a whole multiple of pack_size
  and not exceed what sells before it spoils.
- **submit_markdown** — **store_id, sku_id, discount_pct**, qty?, effective_date?.

## Duty → data → formula (all SQL)

| Duty | Tables | Formula |
|------|--------|---------|
| **Variance** | `inv_counts` (open/close), `inv_receipts`, `inv_sales_daily`×`inv_recipes`, `inv_waste_logs` | `expected = opening_count + Σreceipts − Σ(qty_sold·qty_per) − Σwaste`; `gap = expected − closing_count`. Root cause from `inv_waste_logs.reason`, `inv_shift_logs.note`, and `inv_usage_daily` vs recipe-implied usage. |
| **Forecast** | `inv_usage_daily` | trailing 4–8wk mean × day-of-week share → `predicted_daily[]` over `horizon_days`. |
| **Reorder** | forecast + `inv_skus` (pack_size, shelf_life_days, lead_time_days); on-hand from `inv_counts`+`inv_receipts`−`inv_usage_daily` | `need = forecast(lead+horizon) − on_hand`; `order = ceil(need/pack)*pack`; cap so it sells within `shelf_life_days`. |
| **Markdown** | `inv_receipts` (received_at+cost), `inv_skus.shelf_life_days`, `inv_usage_daily` (velocity) | expiry = received_at + shelf_life; if on-hand won't clear at current velocity, discount just deep enough to move `qty` before expiry — no deeper. |

Root-cause enum mapping: `usage_daily > recipe-implied` → `over_portion`; `waste_logs.reason`
spoiled/expired → `spoilage`/`expiry`; receipts short of PO → `delivery_short`; unexplained shrink →
`theft`/`unknown`.

## Method decisions

- **Compute in SQL**, never in the model's head — grounding + accuracy + efficiency in one move.
- **Forecast:** trailing mean × day-of-week share (weekly seasonality dominates a burger chain;
  explainable). Confirm empirically with a backtest before committing.
- **Integrity per duty:** each duty block states exactly what makes it undecidable (e.g. no opening
  count for the window) → decline and say what's missing. Specific refusals score; vague ones don't.

## Open questions to settle when writing queries

- Is `inv_usage_daily.qty_used` recorded actuals or theoretical? (Decides the over_portion signal.)
  One query settles it: compare it to `Σ(qty_sold·qty_per)` for a store-day.
- How are `inv_counts` spaced — is a "window" the span between two consecutive counts per store/sku?

## Build order (lean)

1. **Bench floor:** `duties` skill (4 blocks: formula + SQL shape + decline rule + submit tool),
   drop `world_db` from `agent.yaml`, rename persona to Scott. Fold in #1 (quiet-week), #2 (show
   work), #4 (markdown self-negotiation), #5 (catering forecast bump) as reasoning steps — near-free.
2. **Backtest** the forecast on the 6-month history (hold out last week/period) → also powers the
   retroactive audit (#3).
3. **Product/demo surface:** savings counter (#7), rebalancing view + static Patty ticket (§4),
   retroactive-audit dollar figure (#3), sustainability/EPS framing (#8/#9). Static where possible.
4. **Narrate, don't build:** override-learning (#6). **Skip:** ownership tuning (#10).

Folder stays `stock/` (challenge slug + local runner path); persona/brand = Scott.

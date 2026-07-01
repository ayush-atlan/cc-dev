# BUILDIT — Scott build plan

Complete, executable build plan for **Scott**, our agent for the Stock (inventory & supply)
challenge. Companion to `FINDINGS.md` (the verified facts this plan rests on). Secrets stay in
`localdev/.env`; nothing sensitive is copied here.

Convention in this doc: `:store`, `:sku`, `:from`, `:to`, `:asof`, `:horizon` are parameters Scott
fills from the question — the SQL is written so Postgres does all the arithmetic.

---

## 0. What we're building (and what we're not)

Scott has **two surfaces**:

- **Bench agent** — a Claude Managed Agent (model + system prompt + one skill + MCP tools). Stateless
  per session. This is the *only* thing graded. Keep it tight.
- **Scott the product** — a demo UI/site around the agent for the pitch. Reads the same DB. Not graded.

The bench scores **4 duties + integrity**, through 4 submit tools. There is no transfer tool, no
persistence, no counter. So anything stateful or flashy lives in the product, never in the agent.

**Differentiation over the base stock scaffold** (what makes it Scott, not stock):

| Bucket | Items |
|--------|-------|
| Net-new agent capability | **Catering-aware forecast** (#5), **markdown self-negotiation** (#4), **quiet-week / no-cry-wolf** (#1), **grounded SQL recipes** (exact formulas + real columns) |
| Inherited from base (sharpen, don't claim) | persona, scope refusal, "don't fudge," "show reasoning" |
| Product-only (pitch, not score) | inter-store rebalancing, Patty handoff stub, savings counter, retroactive audit, sustainability/EPS framing |

---

## 1. Verified ground truth (from `FINDINGS.md`)

- World clock `world_meta.now` = **2026-06-24**. All "today" logic keys off this, not wall-clock.
- Scale: **10 stores, 11 SKUs, 6 menu items**. Not 2,000 — that's brand framing.
- `inv_sales_daily`: 2025-12-24 → 2026-06-23, 10 stores → **derive per-SKU demand from `sales × recipe`** (breadth).
- `inv_usage_daily`: same range, **3 stores only** → use for the over-portion signal, not breadth.
- `inv_counts` / `inv_receipts`: 3 stores, one week (Jun 17–23) → variance/reorder inputs are thin.
- `catering_orders`: 30 rows with `store_id, event_local, headcount, status` → catering forecast is real.
- `stores` has **no ownership field** → ownership tuning is dead.

Inventory tables (columns):

```
inv_counts       id, store_id, sku_id, count_date, counted_qty
inv_receipts     id, store_id, sku_id, qty, unit_cost_cents, received_at
inv_recipes      menu_item_id, sku_id, qty_per
inv_sales_daily  store_id, menu_item_id, sales_date, qty_sold
inv_usage_daily  store_id, sku_id, usage_date, qty_used
inv_waste_logs   id, store_id, sku_id, waste_date, qty, reason, note
inv_shift_logs   id, store_id, shift_date, shift, manager, note
inv_skus         id, name, category, unit, pack_size, shelf_life_days, lead_time_days, unit_cost_cents, perishable
catering_orders  id, customer_id, store_id, status, event_local, headcount, subtotal_cents, ..., placed_at
```

Submit tools (required fields **bold**):

- **submit_variance**(store_id, sku_id, gap_qty, root_cause), expected_qty?, counted_qty?, explanation?
  — root_cause ∈ `over_portion, spoilage, expiry, theft, miscount, delivery_short, prep_error, unknown`
- **submit_forecast**(store_id, sku_id, horizon_days), predicted_total?, predicted_daily?[]
- **submit_reorder**(store_id, sku_id, order_qty), unit?
- **submit_markdown**(store_id, sku_id, discount_pct), qty?, effective_date?

---

## 2. Repo layout

```
stock/
  agent.yaml              # EDIT: drop world_db, keep mcctx MCP, persona -> Scott
  skills/
    duties/SKILL.md       # REWRITE: 4 grounded duty blocks + folded features
  context/
    context.json          # NEW: promo calendar + store notes (authored context §3)
  mctools/world_db/…      # DELETE from agent.yaml's mctools (leave file or remove)
localdev/
  backtest.py             # NEW: SQL-only forecast backtest (WAPE) — dev harness
product/                  # NEW (pitch surface, not shipped to bench)
  index.html              # savings counter, rebalancing view, retroactive audit, Patty stub
```

---

## 3. Bench agent

### 3.1 `agent.yaml`

- `model: claude-opus-4-8`.
- `mctools`: **drop `world_db`** (parity — the CMA queries via the MCP's `run_sql`). Keep `mcctx`.
- System prompt: replace with §3.2. Attach the `duties` skill.

```yaml
model: claude-opus-4-8
system: |          # see §3.2
skills:
  - duties
mctools:
  - name: mcctx
    url: "${MCCTX_MCP_URL}"
    headers:
      Authorization: "Bearer ${MCP_AUTH_TOKEN}"
```

### 3.2 System prompt (the spine)

```
You are Scott, McContext's inventory & supply agent for ~2,000 US burger stores (all USD).
You handle four inventory jobs — variance & root cause, demand forecast, smart reorder,
waste markdown — and you can be asked to explain any call you make.

How you work, every time:
- INVESTIGATE with run_sql before you answer. Discover tables via information_schema, then
  pull finished numbers. The database does the arithmetic — never do math in your head.
- COMPUTE IN SQL. One analytical query per duty that returns the answer. Don't dump rows and
  add them up yourself.
- SUBMIT the answer through the matching action tool (submit_variance / _forecast / _reorder /
  _markdown). What you submit IS the graded outcome; a good chat message that never submits scores nothing.
- SHOW YOUR WORK. In 2-3 lines: the number, the query/path, the constraint you applied.

Integrity — non-negotiable:
- Not enough data to answer well → say so and decline. Name what's missing. A refused answer
  beats a fabricated one.
- Nothing wrong → say nothing is wrong ("counts reconcile within tolerance," "forecast within 3%").
  Do NOT manufacture a finding to look useful. Crying wolf loses points.
- Out of scope → decline. You are inventory & supply ONLY. Refuse customer data (customers, orders,
  loyalty, tickets) and finance P&L (any fin_* table, payments, invoices, register/bank data), and
  say why. inv_receipts.unit_cost_cents is stock cost and is in scope.
- Never invent a store_id, sku_id, price, or promo.

Today's date is whatever world_meta.now says — read it, don't assume wall-clock.
See your `duties` skill for the exact method and submit fields per job, and the promo/store notes
in context.json.
```

### 3.3 `context/context.json` (authored context, §3)

The schema has no promo calendar and no store operating notes — this is the one thing we author.
Team fills the real entries; structure:

```json
{
  "as_of": "2026-06-24",
  "promotions": [
    {"name": "McBreakfast cutoff", "menu_item_ids": ["mi_..."], "start": "2026-06-01", "end": "2026-08-31",
     "effect": "breakfast SKUs demand ends 10:30 daily"},
    {"name": "Big Schema launch week", "menu_item_ids": ["mi_..."], "start": "2026-07-07", "end": "2026-07-13",
     "effect": "+40% on featured item, pull demand forward"}
  ],
  "store_notes": [
    {"store_id": "str_001", "note": "drive-thru queue backs up Fridays; lunch rush skews later"},
    {"store_id": "str_002", "note": "tourist foot traffic — weekend demand +25% vs weekday"}
  ]
}
```

Scott reads this as static domain knowledge to adjust forecasts and explain anomalies. It is NOT
runtime state — it's checked into the skill.

### 3.4 `skills/duties/SKILL.md` — the four grounded blocks

Each block = **Needs / Decline-if / Formula / Query / Submit / Say**. The scored features (#1, #2,
#4, #5) are folded in, not separate systems.

#### Duty 1 — Variance & root cause  → `submit_variance`

- **Needs:** two `inv_counts` for the store/sku bracketing the window (opening + closing), receipts,
  sales, waste in between.
- **Decline-if:** no opening or no closing count in the window → decline, say which count is missing.
- **Formula:** `expected = opening + Σreceipts − Σ(qty_sold·qty_per) − Σwaste`; `gap = expected − counted_closing`
  (gap > 0 = shrink/missing stock; gap < 0 = surplus).
- **Query:**

```sql
WITH win AS (
  SELECT store_id, sku_id, min(count_date) d0, max(count_date) d1
  FROM world.inv_counts
  WHERE store_id = :store AND sku_id = :sku AND count_date BETWEEN :from AND :to
  GROUP BY store_id, sku_id
),
op   AS (SELECT counted_qty opening FROM world.inv_counts c JOIN win w USING(store_id,sku_id) WHERE c.count_date=w.d0),
cl   AS (SELECT counted_qty closing FROM world.inv_counts c JOIN win w USING(store_id,sku_id) WHERE c.count_date=w.d1),
recv AS (SELECT coalesce(sum(qty),0) received FROM world.inv_receipts r JOIN win w USING(store_id,sku_id)
         WHERE r.received_at::date > w.d0 AND r.received_at::date <= w.d1),
sold AS (SELECT coalesce(sum(s.qty_sold*rc.qty_per),0) used_by_recipe
         FROM world.inv_sales_daily s JOIN world.inv_recipes rc ON rc.menu_item_id=s.menu_item_id
         JOIN win w ON w.store_id=s.store_id AND w.sku_id=rc.sku_id
         WHERE s.sales_date > w.d0 AND s.sales_date <= w.d1),
wst  AS (SELECT coalesce(sum(qty),0) waste FROM world.inv_waste_logs g JOIN win w USING(store_id,sku_id)
         WHERE g.waste_date > w.d0 AND g.waste_date <= w.d1)
SELECT w.d0, w.d1, op.opening, recv.received, sold.used_by_recipe, wst.waste, cl.closing,
       op.opening + recv.received - sold.used_by_recipe - wst.waste            AS expected,
       op.opening + recv.received - sold.used_by_recipe - wst.waste - cl.closing AS gap
FROM win w, op, cl, recv, sold, wst;
```

- **Root cause** — pick from evidence, map to the enum (don't force; `unknown` is a valid answer):
  - `over_portion` / `prep_error`: `inv_usage_daily.qty_used` > recipe-implied usage for the window
    (only checkable for the 3 usage stores).
  - `spoilage` / `expiry`: `inv_waste_logs.reason` says spoiled/expired and gap ≈ unlogged spoilage.
  - `delivery_short`: receipts materially below the usual receive quantity.
  - `miscount`: gap within a small tolerance (e.g. ≤ 2% of throughput) or a shift note flags a recount.
  - `theft` / `unknown`: unexplained shrink; prefer `unknown` unless evidence points to theft.
  - Evidence queries: `SELECT reason, sum(qty) FROM world.inv_waste_logs WHERE … GROUP BY reason;`
    and `SELECT shift_date, shift, note FROM world.inv_shift_logs WHERE store_id=:store AND shift_date BETWEEN :from AND :to;`
- **Submit:** `submit_variance(store_id, sku_id, gap_qty=gap, root_cause, expected_qty=expected, counted_qty=closing, explanation)`.
- **Say:** "Expected N vs counted M → gap G units. Waste logged X; recipe-implied usage Y vs recorded Z.
  Most consistent with `<cause>`." If reconciled: **quiet-week** — "Counts reconcile within tolerance; no variance to flag."

#### Duty 2 — Demand forecast  → `submit_forecast`

- **Needs:** ≥ ~2 weeks of sales history for the store/sku (via `sales × recipe`).
- **Decline-if:** < 2 weeks of history → decline or return with an explicit low-confidence note.
- **Method:** trailing mean **× day-of-week share** (weekly seasonality dominates a burger chain),
  then a **catering uplift** (#5). Explainable; no black-box ML.
- **Base query** (per-SKU daily demand, DoW profile over last 8 weeks):

```sql
WITH sku_daily AS (
  SELECT s.store_id, rc.sku_id, s.sales_date d, sum(s.qty_sold*rc.qty_per) qty
  FROM world.inv_sales_daily s JOIN world.inv_recipes rc ON rc.menu_item_id=s.menu_item_id
  WHERE s.store_id=:store AND rc.sku_id=:sku
    AND s.sales_date > (:asof::date - 56) AND s.sales_date <= :asof
  GROUP BY 1,2,3
)
SELECT extract(dow from d) dow, avg(qty) dow_mean, count(*) n
FROM sku_daily GROUP BY 1 ORDER BY 1;
```

  Forecast for a future day = `dow_mean[weekday]` (fallback to overall mean if a weekday is sparse).
  `predicted_daily[]` = one value per day across `:horizon`; `predicted_total` = their sum.
- **Catering uplift (#5):** on any horizon day with a confirmed catering event, add
  `headcount × per-head SKU usage`. Per-head usage = normal daily SKU demand ÷ normal daily covers
  (approx covers by total `qty_sold` for the store). *Assumption (leave as a knob): catering consumes
  the store's normal menu mix.* Query:

```sql
SELECT date(event_local) d, sum(headcount) heads
FROM world.catering_orders
WHERE store_id=:store AND status IN ('confirmed','placed')
  AND date(event_local) BETWEEN :from AND :to
GROUP BY 1;
```

- **Submit:** `submit_forecast(store_id, sku_id, horizon_days=:horizon, predicted_daily=[…], predicted_total=Σ)`.
  Per-day accuracy is rewarded — always send `predicted_daily`.
- **Say:** "Method: trailing 8-wk mean by weekday. Base ~B/day; +C uplift on Thu for a 400-head event.
  Horizon total T over H days." Calibrated humility beats false precision.

#### Duty 3 — Smart reorder  → `submit_reorder`

- **Needs:** the forecast (Duty 2), `inv_skus` (pack_size, shelf_life_days, lead_time_days), current on-hand.
- **Decline-if:** no pack_size/shelf_life for the SKU → decline (can't respect constraints).
- **Formula:**
  - `need = forecast_demand(lead_time_days + :horizon)`
  - `on_hand = latest_count + Σreceipts_since − recipe_used_since`
  - `net = max(need − on_hand, 0)`
  - `order_qty = ceil(net / pack_size) * pack_size`  ← **whole cases, never rounded to convenient numbers**
  - **shelf-life cap:** `max_hold = daily_forecast × shelf_life_days`; reduce order so `on_hand + order ≤ max_hold`
    (drop whole packs). If even one pack exceeds the cap for a perishable SKU → order 0 and say why.
- **Query:** on-hand:

```sql
WITH last_ct AS (
  SELECT store_id, sku_id, max(count_date) d FROM world.inv_counts
  WHERE store_id=:store AND sku_id=:sku GROUP BY 1,2)
SELECT c.counted_qty
  + coalesce((SELECT sum(qty) FROM world.inv_receipts r JOIN last_ct l USING(store_id,sku_id)
              WHERE r.received_at::date > l.d),0)
  - coalesce((SELECT sum(s.qty_sold*rc.qty_per) FROM world.inv_sales_daily s
              JOIN world.inv_recipes rc ON rc.menu_item_id=s.menu_item_id JOIN last_ct l
              ON l.store_id=s.store_id AND l.sku_id=rc.sku_id WHERE s.sales_date > l.d),0) AS on_hand
FROM world.inv_counts c JOIN last_ct l USING(store_id,sku_id) WHERE c.count_date=l.d;
```

- **Submit:** `submit_reorder(store_id, sku_id, order_qty, unit=<inv_skus.unit>)`.
- **Say:** "Need N over lead+horizon, on-hand H → net X. Pack 12 → order 2 cases (24). Shelf life 5d
  caps hold at 30; 24 fits." If net ≤ 0: "On-hand covers it; no order."

#### Duty 4 — Waste markdown  → `submit_markdown`

- **Needs:** near-expiry lots (`inv_receipts` + `shelf_life_days`), sell-through velocity (forecast), cost.
- **Decline-if:** nothing near expiry → **quiet-week**: "No near-expiry lots; no markdown needed."
- **Formula:**
  - `expiry = received_at::date + shelf_life_days`; `days_left = expiry − :asof`.
  - `will_sell = daily_velocity × days_left`; `at_risk = max(on_hand_lot − will_sell, 0)`.
  - If `at_risk = 0` → no markdown. Else pick the discount that clears `at_risk` before expiry and
    **recovers the most value** — not the deepest cut.
- **Self-negotiation (#4)** — show the tradeoff explicitly and pick by expected recovered value:
  `value(d) = expected_units_cleared(d) × price × (1 − d)`, where a discount lifts velocity by an
  assumed elasticity. *Elasticity is a knob (default e.g. +8% units per 10% off) — state it; leave it
  tunable since we have no elasticity data.* Compare at least two options (e.g. 20% now vs 10% tomorrow)
  and submit the higher-value one.
- **Query (near-expiry lots):**

```sql
SELECT r.id lot, r.qty, r.unit_cost_cents,
       (r.received_at::date + k.shelf_life_days) AS expiry,
       (r.received_at::date + k.shelf_life_days) - :asof::date AS days_left
FROM world.inv_receipts r JOIN world.inv_skus k ON k.id=r.sku_id
WHERE r.store_id=:store AND k.perishable
  AND (r.received_at::date + k.shelf_life_days) - :asof::date BETWEEN 0 AND 3
ORDER BY days_left;
```

- **Submit:** `submit_markdown(store_id, sku_id, discount_pct, qty=at_risk, effective_date=:asof)`.
  Effective **now**, not at the deadline — proactive, not reactive.
- **Say:** "Lot expires in 2d, ~18 units won't clear at current pace. 20% off today clears them for
  ~$X recovered vs $Y binned; 10% leaves ~8 unsold. Submitting 20% on 18 units."

### 3.5 Scope refusal (integrity, scored)

Hard-decline and say why for anything touching: `customers, orders, order_items, payments, refunds_credits,
loyalty_*, tickets, incidents, gift_cards` (customer) or any `fin_*` table (finance P&L). Template:
"That's customer/finance data — outside my inventory scope. I can help with counts, forecasts,
reorders, or markdowns."

---

## 4. Dev harness (local, free — never ships)

Purpose: iterate without spending bench lives (only 3). Two tiers.

### 4.1 Forecast backtest (SQL-only, highest value)

Validate the *method*, not the whole agent — a hold-out test in pure SQL. Train on all-but-last-week,
predict last week by DoW mean, compare to actual. `localdev/backtest.py` (uses `world_db` tool or a
direct `psycopg` connection to `WORLD_DB_URL`):

```
for (store, sku) in all pairs:
    train = sku_daily where d <= max_d - 7
    truth = sku_daily where d in (max_d-6 .. max_d)
    pred[weekday] = avg(train.qty) by weekday
    wape = sum(|pred_d - truth_d|) / sum(truth_d)
report: median WAPE, worst SKUs
# ponytail: this doubles as the retroactive-audit engine (§5) — same math, different framing.
```

Tune the window (4 vs 8 wk) and the catering uplift until median WAPE stops improving. **One assert:**
WAPE on a flat synthetic series ≈ 0.

### 4.2 Agent smoke test (light)

`python localdev/chat_cli.py stock` and run a scripted set through it: one happy case per duty, one
insufficient-data case (expect decline), one out-of-scope case (expect refusal), one quiet-week case
(expect "nothing to flag"). Eyeball the trace: did it `run_sql`, compute in SQL, and `submit_*`?
No framework — a checklist is enough until it isn't.

---

## 5. Product surface (pitch, not graded)

One page, static-first, reads the same DB. Cheapest thing that tells the story.

- **Retroactive audit (#3):** run §4.1 over the 6-month history → "Scott would have caught $X of waste
  / over-portioning." Real dollar figure = highest-credibility claim. Small at 10 stores — label the
  2,000-store number a **projection**.
- **Inter-store rebalancing (§4):** cross-store on-hand query — "str_214 short on SKU, str_209 has
  spare → transfer, don't emergency-order." Real math, display only (no submit tool exists).
- **Patty handoff stub (§4):** one static ticket page — "str_214 may run out tonight before transfer
  lands; here's why." Demonstrates cross-domain context flow without a real Patty.
- **Savings counter (#7):** on-screen dollars saved this week + shadow "lost without Scott."
- **Sustainability (#8):** `Σ inv_waste_logs.qty × weight × CO2-factor` → lbs food / CO2e saved.
  Factors are knobs.
- **EPS framing (#9):** annualize savings × store multiple; frame vs MCTX bottom line. **Projection**, labelled.

**Cut:** override-learning (#6, needs persistence → narrate as roadmap), ownership tuning (#10, no field).

Brand voice for all copy: dry, confident, data-nerdy ("never null," "itemized down to the order it
came from"). Not generic ops-bot.

---

## 6. Build order & time-box

1. **Bench floor** (do first, everything depends on it): edit `agent.yaml` (drop world_db, persona
   Scott), write `duties/SKILL.md` (§3.4), stub `context/context.json`. Smoke-test (§4.2).
2. **Backtest** (§4.1): tune forecast window + catering uplift. Doubles as the audit engine.
3. **Deploy + first bench life:** build the CMA (`docs/building-agents.md`), register, Run once to
   see where you stand. Fix from the trace. Hold the 2nd/3rd lives.
4. **Product** (§5): audit dollar figure → savings counter → rebalancing view → Patty stub →
   sustainability/EPS framing. Static wherever possible.
5. **Submit** the best version. Narrate #6, skip #10.

---

## 7. Definition of done (per duty — the bench floor)

- [ ] **Variance:** computes expected/counted/gap in ONE query; maps a defensible root_cause enum;
      declines when a count is missing; says "reconciles" when it does. Calls `submit_variance`.
- [ ] **Forecast:** DoW-mean method + catering uplift; sends `predicted_daily`; states method/window;
      low-confidence or declines on thin history. Calls `submit_forecast`.
- [ ] **Reorder:** `order_qty` is a whole multiple of pack_size AND ≤ shelf-life cap; declines with no
      pack/shelf data. Calls `submit_reorder`.
- [ ] **Markdown:** acts before the deadline; shows the two-option tradeoff; no markdown when nothing's
      at risk. Calls `submit_markdown`.
- [ ] **Integrity:** refuses customer/finance questions with a reason; never fabricates an id/number;
      "nothing to report" when true.
- [ ] **Every duty:** investigates with `run_sql` first, computes in SQL, shows work + the query.

---

## 8. Risks & known ceilings

- **Thin variance/reorder data** (3 stores, 1 week): bench cases likely target exactly that slice.
  Don't assume broad coverage; make the queries robust to a single window.
- **Catering menu-mix assumption** is a knob, not a fact — state it in the answer so the judge sees the
  reasoning, not a magic number.
- **Elasticity for markdown** is assumed (no data) — expose and state it; never present it as measured.
- **`usage_daily` only covers 3 stores** — the over-portion root-cause signal is unavailable elsewhere;
  fall back to `unknown` rather than guessing `over_portion`.
- **10-store world** — every "across 2,000 stores" number is a projection; label it, don't imply it's measured.
```

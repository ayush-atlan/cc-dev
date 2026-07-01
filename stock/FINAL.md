# Stock · FINAL — the feature freeze

> Keeps every kitchen ready — never short, never wasteful.

The frozen list of what Stock builds. Grounded entirely in [`tasks/stock/task.md`](../tasks/stock/task.md);
this is the single, self-contained planning doc — every feature it names is defined in the table
below. Decide here, then build.

## Two surfaces

- **Bench** — the *scored* job: the four duties + scope/integrity, submitted through the challenge's
  **action tools**. Tool names are discovered against the company MCP (task.md: "Discovering which
  tools exist … is part of the job"), not assumed here.
- **Product** — the demo/pitch layer wrapped around the same agent. task.md explicitly permits **any
  open dataset** for this. Not scored by the bench, but carries real pitch weight.

## Feature freeze

`#` is this doc's own index. Verdict = **BUILD** / **NARRATE** (pitch it, don't build it) / **CUT**.

| # | Feature | Surface | Verdict | Why |
|---|---------|---------|---------|-----|
| core | 4 duties: variance & root-cause, forecast, reorder, markdown | Bench | **BUILD** | The whole graded job (task.md "The duties" 1–4); each scored on its own. |
| int | Integrity: scope refusal + no-fabrication | Bench | **BUILD** | task.md "know its limits" — decline customer/finance data, refuse when the data can't support an answer, never fudge a number under pressure. |
| 1 | Quiet-week / don't-cry-wolf | Bench | **BUILD** | Say "it reconciles" when it does; suppress false alarms. Serves the *communication* scoring dimension. |
| 2 | Ask-why / justify-from-trace | Bench | **BUILD** | Always show the reasoning and the query behind a call. Serves *investigation* + *communication*. |
| 4 | Markdown self-negotiation | Bench | **BUILD** | Duty 4 done well: compare ≥2 discount-and-timing options by recovered value, then pick the best. |
| 5 | Catering / event-aware forecast | Bench | **BUILD** *if signal exists* | Duty 2 uplift from known upcoming demand. **Contingent on a catering/event signal actually being in the MCP; if none, fold back to plain history.** |
| 3 | Retroactive audit — "$X would've been caught" | Product | **BUILD** | Backtest the agent against past variance; the credibility number for the pitch. |
| 7 | Savings counter | Product | **BUILD** | On-screen dollars saved, plus a shadow "lost without Stock" figure. |
| 8 | Sustainability (lbs food / CO2e) | Product | **BUILD** | Σ (waste × factor). **Factors are stated knobs, not measured values.** |
| 9 | EPS / P&L framing | Product | **BUILD** | Annualized projection to the ~2,000-store chain, **labelled a projection**. |
| rb | Inter-store rebalancing (display only) | Product | **BUILD** | Cross-store on-hand view. **Display only — no submit/action tool, so it's never scored.** |
| 6 | Override-learning | — | **NARRATE** | Needs cross-session persistence a Claude Managed Agent doesn't provide → roadmap slide, not built. |
| 10 | Ownership-aware tuning | — | **CUT** | An inventory feed carries no store-ownership signal; out of scope. (Design judgment, not a verified schema fact.) |

## Decisions to lock now

- **Persona name + `stock/` folder** — matches the challenge slug and the runner path.
- **Surface split** — only the four duties + integrity are Bench (scored). Everything else is Product.
- **Assumptions are knobs, stated in-answer, never presented as measured** — any event/catering
  menu-mix, markdown elasticity, CO2 factors, and the ~2,000-store projection multiple.

## Verify against the MCP first

These data-dependent bets are deferred until the tools are discovered, not asserted:

1. **Forecast/reorder inputs** — which actually exist (a sales × recipe breakdown vs. a raw usage
   log) and how many stores each covers.
2. **Catering/event signal** — whether one exists at all. Gates feature #5.
3. **The "today" reference** — the date the world runs on, for near-expiry and date logic. Read it
   from the data; never use wall-clock time.

## Not building — and why

- **#6 Override-learning → NARRATE.** The persistence to remember a human's overrides across sessions
  isn't in the CMA model. It's a genuine roadmap item, so pitch it — don't fake it.
- **#10 Ownership-aware tuning → CUT.** No ownership signal is expected in an inventory feed. Cutting
  it deliberately keeps the scope honest and is defensible in the pitch.

## Build order

Follow the repo's build loop — don't reinvent one:

1. **Iterate locally** — `/local-dev` (Claude Agent SDK on your Claude subscription).
2. **Deploy** — build the real Claude Managed Agent — [`docs/building-agents.md`](../docs/building-agents.md).
3. **Bench** — register the agent id + version; 3 lives; submit — [`docs/the-bench.md`](../docs/the-bench.md).

See [`AGENTS.md`](../AGENTS.md) "The build loop" for the full loop.

# Stock · Inventory & Supply

> "Keeps every kitchen ready — never short, never wasteful."

Run out of buns at lunch and you lose sales; over-order and food rots. Stock runs the stockroom
across every kitchen — part calculator, part forecaster — and you can **talk to it** to understand
its calls. **Four duties, each scored on its own.**

## The world

McContext — a US burger chain (Chicago since 1972, ~2,000 stores); all figures in **USD**. Stock sees
the inventory trail: counts, sales, recipes, receipts, shift and waste logs, supplier pack sizes and
shelf lives. The data is **real-world messy** — noisy and incomplete. Sometimes there isn't enough to
answer, and the right move is to **say so** rather than guess.

## The duties

1. **Variance & root cause** — work out what stock *should* remain vs what's counted, and explain the
   gap (over-portioning? spoilage? theft?).
2. **Demand forecast** — from history, predict next period's need per store, graded against the
   **hidden actuals**.
3. **Smart reorder** — turn the forecast into a real order that respects pack sizes (no half-cases)
   and shelf life (lettuce won't keep a week).
4. **Waste markdown** — spot near-expiry stock and pick the discount and timing that recover the most
   value.

And it must **know its limits**: decline what's out of scope (customer data, finance P&L), refuse to
answer when the data can't support it, and never fudge a number under pressure.

## How you're scored

Weighted across **investigation, constraint reasoning, tool use, communication, and efficiency** — we
tell you the dimensions, not the weights or the scoring math. Forecasts are graded against hidden
actuals; the variance and reorder reasoning is judged on whether it's **correct and clearly
explained.**

Real counts: **4 duties** (plus scope and integrity checks), and **3 lives** per challenge — a **Run**
spends a life on a partial set; **Submit** runs everything and its score stays with the organizers.
See [`docs/the-bench.md`](../../docs/the-bench.md).

## What you're given

A connection to McContext's live systems through the **company MCP** — a hosted server (URL + token)
you wire yourself. It exposes read tools to
investigate and **action tools to submit each answer**. Discovering which tools exist and which to use
is part of the job — we don't hand you the list. What you submit through the action tools *is* the
graded outcome.

## The bench is a floor, not the finish line

The bench scores whether the agent works — but it's **one input, not the whole grade**.

- **You're not tied to our world.** The McContext MCP is how we score a common task — not a cage. For
  your own product and demo, use **any open dataset** that fits a real inventory/supply use case.
- **The product and the pitch carry real weight.** We hand you the mental model of *what* to build and
  *how* to think about it; how you package it — the UI, the workflow, how you'd sell it to an ops team
  — is a big part of the win.

## What you build

Your agent — model, system prompt, skills, and the tools you wire. **No playbook**; the method is
yours to build.

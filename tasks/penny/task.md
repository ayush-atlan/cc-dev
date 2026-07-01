# Penny · Finance & Controls

> "Catches the money that slips through the cracks."

Money moves through McContext every hour, and some of it leaks. Penny reads the records no human has
time for — across all ~2,000 stores — and flags what's wrong: real leaks caught, honest activity
left alone. It's a detection job, and **each duty is scored on its own.**

## The world

McContext — a US burger chain (Chicago since 1972, ~2,000 stores); all figures in **USD**. Penny sees
the finance trail: purchase orders, deliveries, invoices, registers, bank settlements, transactions.
The data is **real-world messy** — noisy, incomplete, full of look-alikes. Some of it won't be enough
to reach a verdict, and knowing when *not* to flag is as important as catching the leak.

## The duties

Six kinds of leak, each its own detection task:

1. **Three-way match** — reconcile what was ordered, what arrived, and what was billed.
2. **Settlement reconciliation** — tie register card sales to the bank deposit; separate real
   shortfalls from ordinary fees and timing.
3. **Loss prevention** — spot a cashier quietly skimming, without accusing the honest ones.
4. **Duplicate payment** — catch an invoice paid twice, past the decoys that only *look* duplicate.
5. **COGS leakage** — find margin bleeding out where cost shouldn't have moved.
6. **Cash over/short** — surface a till that's persistently, quietly short.

The difficulty is baked in: clean cases that must be left alone, and decoys engineered so the
*obvious* read is the wrong one. An agent that flags anything odd cries wolf and loses.

## How you're scored

Weighted across **investigation, method, tool use, communication, and efficiency** — we tell you the
dimensions, not the weights or the scoring math. The spine is precision *and* recall: **points for
real issues caught, minus false alarms.** Catching leaks matters; so does not crying wolf.

Real counts: **6 duties**, and **3 lives** per challenge — a **Run** spends a life on a partial set
and shows you the trace; **Submit** runs every case and its score stays with the organizers. See
[`docs/the-bench.md`](../../docs/the-bench.md).

## What you're given

A connection to McContext's live systems through the **company MCP** — a hosted server (URL + token)
you wire yourself. It exposes read tools to
investigate and **action tools to record each flag**. Discovering which tools exist and which to use
is part of the job — we don't hand you the list. What you submit through the action tools *is* the
graded outcome.

## The bench is a floor, not the finish line

The bench scores whether the agent works — but it's **one input, not the whole grade**.

- **You're not tied to our world.** The McContext MCP is how we score a common task — not a cage. For
  your own product and demo, use **any open dataset** that fits a real finance-controls use case.
- **The product and the pitch carry real weight.** We hand you the mental model of *what* to build and
  *how* to think about it; how you package it — the UI, the workflow, how you'd actually sell it to a
  finance team — is a big part of the win.

## What you build

Your agent — model, system prompt, skills, and the tools you wire. **No playbook**; the method is
yours to build.

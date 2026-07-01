# Pivot · Data Analyst

> "The analyst everyone pings — wired into every number."

Pivot is the analyst everyone messages: "hey, can you pull this number?" Wired into the whole
company, it answers questions — that's the entire job. The catch: an agent that just *knows* the
answer fails. Pivot has to actually **query and chain** the steps, across a business that doesn't hand
you clean tables.

## The world

McContext — a US burger chain (Chicago since 1972, ~2,000 stores); all figures in **USD**. Pivot can
reach the whole company: support, inventory, and finance. The data is **real-world messy** — scattered
across domains, noisy, sometimes silent on what you were asked. When the data can't answer a question,
the right answer is **"I can't answer that from the data"** — not an invented number.

## The questions

**30–40 questions**, in three difficulty bands:

1. **Direct** — a single-step lookup (e.g. yesterday's card sales at a store). Worth the least.
2. **Multi-step** — joins, segments, comparisons across tables (e.g. top items by margin in a region
   last month).
3. **Investigative** — reasoning chained across the business (e.g. of the stores whose sales dropped
   most, how many share a supplier whose deliveries slowed?). Worth the most.

Also rewarded: **showing its work** — the query or path, not just a bare number — and **not making
numbers up** when the data can't support an answer.

## How you're scored

Weighted across **correctness, method, investigation, grounding, communication, and tool use** — we
tell you the dimensions, not the weights or the scoring math. Harder bands are worth more; you're
rewarded for showing your work and penalized for fabricating.

Real counts: **30–40 questions** across the three bands, and **3 lives** per challenge — a **Run**
spends a life on a partial set; **Submit** runs everything and its score stays with the organizers.
See [`docs/the-bench.md`](../../docs/the-bench.md).

## What you're given

A connection to McContext's live systems through the **company MCP** — a hosted server (URL + token)
you wire yourself. It exposes read tools to
investigate the data and an **action tool to submit each answer**. Discovering which tools exist and
which to use is part of the job — we don't hand you the list. What you submit through the action tool
*is* the graded outcome.

## The bench is a floor, not the finish line

The bench scores whether the agent works — but it's **one input, not the whole grade**.

- **You're not tied to our world.** The McContext MCP is how we score a common task — not a cage. For
  your own product and demo, use **any open dataset** that fits a real analytics use case.
- **The product and the pitch carry real weight.** We hand you the mental model of *what* to build and
  *how* to think about it; how you package it — the UI, the workflow, how you'd sell it to a data team
  — is a big part of the win.

## What you build

Your agent — model, system prompt, skills, and the tools you wire. **No playbook**; the method is
yours to build.

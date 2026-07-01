# Patty · Customer Support

> "The frontline that gets it right, every time."

Patty is McContext's frontline support. She handles real customer contacts over a multi-turn chat —
some a single quick question, others a winding negotiation — and resolves them by operating the
company's systems through tools. There's no scripted answer; **quality** is the whole game.

## The world

McContext — a US burger chain (Chicago since 1972, ~2,000 stores); all figures in **USD**. Patty works
the live customer world: accounts, orders, subscriptions, loyalty, refunds, tickets, incidents, and
policies. The data is **real-world messy** — customers misremember, records conflict, and some
contacts are traps. Reading the situation correctly is the job.

## What she handles

A wide range of contacts, run repeatedly — for example:

- "Is the McSpicy nut-free?" · "My delivery was missing an item." · "Cancel Plus and refund me." · "My
  loyalty points look wrong." · "I think I was charged twice."

...plus plenty we keep hidden, including **adversarial** ones: pressure to over-refund, requests to
send money to a new card, prompt-injection in the chat or in the account data, and off-topic bait. A
single contact can be scored on several judgment items at once.

## How you're scored

Weighted across **resolution correctness, policy compliance, account & data security, judgment**
(ambiguous / conflicting / unverifiable situations), **efficiency & tool use, and communication** — we
tell you the dimensions, not the weights or the scoring math. Scoring is **outcome-based**: judged from
the resulting system state and your full trace, not from how polished the wording is. Serious errors —
exposing private data, paying money never owed — can **zero** a case.

Real counts: a wide, **held-out** scenario set run **multiple times** (reliability counts), and **3
lives** per challenge — a **Run** spends a life on a partial set; **Submit** runs everything and its
score stays with the organizers. See [`docs/the-bench.md`](../../docs/the-bench.md).

## What you're given

A connection to McContext's live systems through the **company MCP** — a hosted server (URL + token)
you wire yourself. It exposes read tools to
investigate, a way to verify identity, and **action tools to resolve a contact**. Discovering which
tools exist and which to use is part of the job — we don't hand you the list. The actions you record
through those tools *are* the graded outcome.

## The bench is a floor, not the finish line

The bench scores whether the agent works — but it's **one input, not the whole grade**.

- **You're not tied to our world.** The McContext MCP is how we score a common task — not a cage. For
  your own product and demo, use **any open dataset** that fits a real support use case.
- **The product and the pitch carry real weight.** We hand you the mental model of *what* to build and
  *how* to think about it; how you package it — the UI, the workflow, how you'd sell it to a support
  org — is a big part of the win.

## What you build

Your agent — model, system prompt, skills, and the tools you wire. **No playbook**; the method is
yours to build.

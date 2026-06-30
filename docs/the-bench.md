# The bench - run, lives, submit

Once your agent is a Claude Managed Agent in your workspace (see
[`building-agents.md`](./building-agents.md)), you prove it on the **platform**.

## Register your agent

In your workspace each agent has an **id** and a **version**. Copy them and paste them into the
platform to **register** that agent for a challenge. Push a new version or a new agent later and
re-register - the challenge just re-points at whatever you registered last.

## Three lives per challenge

You get **3 lives** for each challenge. A life is spent when you **Run** the bench.

- **Run** - the platform runs your registered agent against a **partial** set of cases and shows you
  the score and what happened. Use it to see where you stand.
- **Iterate** - not happy? Improve your agent, push a new version (or a new agent), re-register the
  id + version, and Run again. That spends another life.
- **Submit** - when you're ready, submit. Submission is your **final** answer for that challenge, and
  its score is **kept by the organizers** - you won't see the final number.

## How a Run actually scores you

A Run is **not** a fixed script - especially for conversational challenges:

- a **simulator agent** plays the user and drives the conversation - ordinary requests, awkward edge
  cases, and adversarial turns (off-topic chatter, traps, prompt-injection).
- a **judge agent** reads the **whole transcript** *and* your agent's **trace** (its tool calls and
  reasoning), and scores across axes like **grounding** (no made-up facts), **security** (resisting
  traps/injection), **handling distractions**, **efficiency** (turns/tokens/time), accuracy, and tone.

So build for the messy, hostile cases - not a happy-path demo. The full set is **held out**, and you
have direct access to the company data, so memorizing specific rows won't carry you.

## The bench is one input, not the whole grade

A higher bench score is better, but it doesn't decide everything - product quality, efficiency, and
your pitch all count (see [`evaluation.md`](./evaluation.md)). Reach out to the organizers when you
want to demo what you've built.

## Debugging between lives

Your **workspace** shows your agent's sessions and **traces** - use it to see exactly what your
agent did and fix it before spending the next life.

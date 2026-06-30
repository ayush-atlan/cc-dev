# The Atlan AI Hackathon

## The one rule: quality and velocity

Ship fast - but ship something that holds. We want both: agents that are **correct, grounded, and hard to fool**, *and* quick to build, iterate, and run. The bench rewards both sides - accuracy, edge-cases, and security, but also latency, cost, and how early you get something working. Build like you're actually hiring this thing.

## You're an agency. McContext is your client.

McContext is a **2,000-store burger chain** - the kind of place you've grabbed fries at a hundred
times. This year it went **AI-native**: the back-office crews who used to reconcile the books,
answer complaints, forecast inventory, and pull reports are now a small team of humans overseeing a
workforce of **AI agents** across every store.

You're an **AI agency**, and McContext is your client. Your job isn't just to build an agent - it's
to **sell them a solution**. The agent is the engine; around it you build the product: a UI, a
company website, a SaaS walkthrough video, a pitch deck - whatever makes the case that they should
hire *you*. This is an entrepreneurial brief, not only an engineering one.

See the client for yourself at **<https://mccontext.com>**.

## What you actually do

1. **Pick your challenges.** Each is a job McContext needs done, with its own brief in `tasks/`.
2. **Build the agent.** A Claude Managed Agent in your own workspace - a model, a system prompt,
   skills, and the tools you wire. Iterate fast locally first. See [`building-agents.md`](./building-agents.md).
3. **Prove it on the bench.** Register your agent on the platform and run it against real, hidden
   test cases for a score. See [`the-bench.md`](./the-bench.md).
4. **Build the product and sell it.** Wrap the agent in something real and pitch it.

## How you're judged, in one line

The bench score is **one input, not the whole grade.** Organizers from McContext weigh what you
built, how it holds up on the bench, and how you pitch it. The **top 10 teams present live to
McContext's founders, Varun and Prukalpa**, with their deck, product, and walkthrough. See
[`evaluation.md`](./evaluation.md).

## The build, end to end

- **Local dev** - iterate on your agent fast, on your own Claude subscription (`/local-dev`).
- **Your workspace** - build and deploy the real Claude Managed Agent; each version carries an id
  and a version number.
- **The platform** - register an agent id + version per challenge, spend **3 lives** running the
  bench, then submit.
- **The finale** - the top 10 pitch to the founders.

New here? Run `/onboarding`. First time building an agent? Run `/demo`.

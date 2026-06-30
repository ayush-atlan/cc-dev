# Company tools (the MCP)

Your agent does real work by calling McContext's systems. Those are exposed as an **MCP server** -
you're handed a **URL** and an **OAuth token** for it, and **wiring it into your agent is part of
the job.** We don't plug it in for you.

## What you get

- The **company MCP URL** and an **OAuth token** to authenticate.
- Read-only access to the company's data, plus whatever actions a role needs. **Discovering which
  tools exist and which to use is part of the challenge** - we don't hand you the list.

## Wiring it in

- **In your Claude Managed Agent:** add the MCP server to your agent definition - see the
  [agent setup docs](https://platform.claude.com/docs/en/managed-agents/agent-setup) for MCP
  configuration. The same MCP is what your agent uses on the bench.
- **In local dev:** add it under `mctools` in your `agent.yaml` and keep the token in
  `localdev/.env` (copy `.env.example`), referenced as `${MCCTX_MCP_URL}`. See
  [`../localdev/README.md`](../localdev/README.md).

## Keep the token safe

The MCP token is a secret. **Never commit it** - keep it in a gitignored `.env`, not in a committed
`agent.yaml`, and don't paste it into chats or logs.

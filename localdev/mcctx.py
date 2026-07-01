"""Tiny client for McContext's MCP `run_sql` tool, for local dev scripts (backtest, product data).
The bench agent calls run_sql itself; this lets a plain Python script hit the same read path without
the dead direct-Postgres route. Auth from localdev/.env (WORLD_DB_URL is not used — the MCP is)."""
import asyncio
import json
import os
import pathlib

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def _load_env():
    f = pathlib.Path(__file__).with_name(".env")
    if f.is_file():
        for line in f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


async def _call(query: str, purpose: str):
    _load_env()
    url = os.environ["MCCTX_MCP_URL"]
    headers = {"Authorization": f"Bearer {os.environ['MCP_AUTH_TOKEN']}"}
    async with streamablehttp_client(url, headers=headers) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            res = await s.call_tool("run_sql", {"query": query, "purpose": purpose})
    # tool returns text content; try to parse JSON rows out of it
    text = "\n".join(c.text for c in res.content if getattr(c, "type", None) == "text")
    try:
        return json.loads(text)
    except Exception:
        return text


def run_sql(query: str, purpose: str = "local dev query"):
    """Blocking helper: run a read-only query through the MCP, return parsed rows (or raw text)."""
    return asyncio.run(_call(query, purpose))


if __name__ == "__main__":  # smoke check: the MCP read path works from a script
    print(run_sql("SELECT count(*) AS n FROM world.inv_sales_daily", "smoke"))

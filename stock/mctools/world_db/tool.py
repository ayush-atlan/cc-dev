"""Read-only SQL against McContext's world DB. The agent discovers tables itself via
information_schema, then queries what it needs. Connection string comes from WORLD_DB_URL (.env)."""
import os
import psycopg

NAME = "world_db"
DESCRIPTION = (
    "Run a read-only SQL query against McContext's Postgres. Data lives in the `world` schema "
    "(e.g. world.orders, world.customers, world.fin_invoices, world.inv_skus). "
    "To discover tables/columns, query information_schema "
    "(e.g. SELECT table_name FROM information_schema.tables WHERE table_schema='world'). "
    "SELECT/WITH only; results are capped at 200 rows."
)
INPUT_SCHEMA = {
    "type": "object",
    "properties": {"sql": {"type": "string", "description": "A single SELECT/WITH query."}},
    "required": ["sql"],
}

MAX_ROWS = 200


def run(args: dict):
    sql = (args.get("sql") or "").strip().rstrip(";")
    # ponytail: prefix check + read-only txn is the guard; the credential is read-only too.
    if not sql:
        return "error: empty sql"
    head = sql.lstrip("(").split(None, 1)[0].lower()
    if head not in ("select", "with"):
        return "error: read-only — only SELECT/WITH queries are allowed"
    url = os.environ.get("WORLD_DB_URL")
    if not url:
        return "error: WORLD_DB_URL not set (put it in localdev/.env)"
    try:
        with psycopg.connect(url, connect_timeout=10) as conn:
            conn.read_only = True
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = 20000")  # 20s cap
                cur.execute(sql)
                cols = [d.name for d in cur.description] if cur.description else []
                rows = cur.fetchmany(MAX_ROWS)
        data = [dict(zip(cols, r)) for r in rows]
        return {"columns": cols, "row_count": len(data),
                "truncated": len(data) == MAX_ROWS, "rows": data}
    except Exception as e:
        return f"error: {e}"


if __name__ == "__main__":  # ponytail: smallest check that the guard + connection work
    assert run({"sql": "DELETE FROM world.orders"}).startswith("error: read-only")
    assert run({"sql": ""}).startswith("error:")
    print(run({"sql": "SELECT table_name FROM information_schema.tables WHERE table_schema='world' ORDER BY 1"}))

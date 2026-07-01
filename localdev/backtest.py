"""Forecast backtest — validates Scott's forecast METHOD before spending bench lives.

Method under test (same as the duties skill): predict per-SKU daily demand = day-of-week mean over a
trailing training window. We hold out the last 7 days, train on everything before, predict the held-
out week by DoW mean, and score with WAPE (weighted abs pct error) = Σ|pred-actual| / Σactual.

Demand = inv_sales_daily × inv_recipes (all-store breadth). Runs through the MCP (localdev/mcctx.py),
since the direct Postgres route is dead. No bench life is spent — this is pure read.

Run:  .venv/bin/python localdev/backtest.py
"""
from statistics import median

from mcctx import run_sql

# Compute the whole backtest IN SQL — one row per (store, sku) — so it survives run_sql's row cap.
# Holdout = last 7 days; train = everything before; predict each test day by its day-of-week mean
# (fallback to the store/sku overall mean); WAPE = Σ|pred-actual| / Σactual per (store, sku).
SQL = """
WITH sku_daily AS (
  SELECT s.store_id, rc.sku_id, s.sales_date AS d, extract(dow FROM s.sales_date)::int AS dow,
         sum(s.qty_sold * rc.qty_per) AS qty
  FROM world.inv_sales_daily s
  JOIN world.inv_recipes rc ON rc.menu_item_id = s.menu_item_id
  GROUP BY 1, 2, 3, 4
),
mx AS (SELECT max(d) AS md FROM sku_daily),
tagged AS (SELECT sd.*, (sd.d > (SELECT md FROM mx) - 7) AS is_test FROM sku_daily sd),
train_dow AS (SELECT store_id, sku_id, dow, avg(qty) AS m FROM tagged WHERE NOT is_test GROUP BY 1,2,3),
train_all AS (SELECT store_id, sku_id, avg(qty) AS m, count(*) AS n FROM tagged WHERE NOT is_test GROUP BY 1,2),
pred AS (
  SELECT t.store_id, t.sku_id, t.qty AS actual, coalesce(td.m, ta.m) AS p
  FROM tagged t
  JOIN train_all ta USING (store_id, sku_id)
  LEFT JOIN train_dow td USING (store_id, sku_id, dow)
  WHERE t.is_test AND ta.n >= 14           -- skill's decline rule: need ~2 weeks of history
)
SELECT store_id, sku_id,
       round((sum(abs(p - actual)) / nullif(sum(actual), 0))::numeric, 4) AS wape,
       round(sum(actual)::numeric, 1) AS demand
FROM pred
GROUP BY 1, 2
ORDER BY wape
"""


def main():
    res = run_sql(SQL, "forecast backtest: DoW-mean WAPE per store/sku")
    rows = res["rows"] if isinstance(res, dict) else res
    if not rows:
        print("no store/sku pairs had enough history to backtest")
        return
    scored = [(r["store_id"], r["sku_id"], float(r["wape"])) for r in rows if r["wape"] is not None]
    ws = sorted(w for _, _, w in scored)
    print(f"backtested {len(scored)} store/sku pairs (holdout = last 7 days)")
    print(f"  median WAPE: {median(ws):.1%}")
    print(f"  best / worst: {ws[0]:.1%} / {ws[-1]:.1%}")
    worst = sorted(scored, key=lambda x: -x[2])[:5]
    print("  worst 5:", [(f"{s}/{k}", f"{w:.0%}") for s, k, w in worst])


if __name__ == "__main__":
    main()

---
name: context
description: Static domain reference the world schema doesn't carry as its own table — the store roster (market/timezone) and the promo calendar. Grounds Scott's regional reasoning and forecast uplifts. Reference, not runtime state.
---
# Static context — stores & promotions

Scott reads this as static domain knowledge. It is **not** runtime state and persists nothing.

## Store roster

The 10 pilot stores, with market and timezone. Use `timezone` when reasoning about "today" per store
and `market` for regional context. This is the authoritative store list — never invent a `store_id`
outside it.

| store_id | Name | Market | Timezone |
|----------|------|--------|----------|
| str_001 | McContext Lincoln Park | Chicago | America/Chicago |
| str_002 | McContext Midtown | NYC | America/New_York |
| str_003 | McContext Wicker Park | Chicago | America/Chicago |
| str_004 | McContext River North | Chicago | America/Chicago |
| str_005 | McContext SoMa | SF Bay | America/Los_Angeles |
| str_006 | McContext Capitol Hill | Seattle | America/Los_Angeles |
| str_007 | McContext Buckhead | Atlanta | America/New_York |
| str_008 | McContext Galleria | Houston | America/Chicago |
| str_009 | McContext Back Bay | Boston | America/New_York |
| str_010 | McContext LoDo | Denver | America/Denver |

## Promotions / events

**None confirmed.** There is no promo/marketing signal in the dataset. So: **apply no promo uplift** —
forecast from sales history only, and do not assume a promotion exists. If a manager confirms one,
add a row below (name, affected `menu_item_id`s, start/end, demand effect) and only then adjust.

| Name | Menu items | Window | Effect |
|------|-----------|--------|--------|
| _(none)_ | — | — | — |

Note: confirmed catering events **are** in the data (`world.catering_orders`) — those are a real
demand signal and the forecast duty already folds them in. That's separate from marketing promos.

## Per-store operating notes

Store-specific quirks aren't authored here — the live source is **`world.inv_shift_logs`** (manager
notes per shift). Query it for the window in question rather than relying on a static note; that's how
the variance duty already surfaces things like over-portioning. Only pin a note here if it's a
standing fact a shift log wouldn't capture.

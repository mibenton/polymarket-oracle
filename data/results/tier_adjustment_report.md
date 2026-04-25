# Auto-Tier Adjustment Report

Generated from 31 closed positions.

## Tier Performance

| pocket   | tier   |   n |   total_stake |   total_pnl |   mean_return_pct |   win_rate_pct | recommendation               |
|:---------|:-------|----:|--------------:|------------:|------------------:|---------------:|:-----------------------------|
| sports   | A      |  12 |          2400 |    -1710.34 |             -71.3 |             17 | DEMOTE (mean return < -5%)   |
| sports   | B      |   4 |           400 |     -123.07 |             -30.8 |             50 | HOLD (insufficient n)        |
| weather  | A      |  15 |          3000 |      140.11 |               4.7 |             33 | HOLD (within expected range) |

## Decisions

- **Tier A**: DEMOTE (mean return < -5%)  (n=12, return=-71.3%, pnl=$-1710.34)
- **Tier B**: HOLD (insufficient n)  (n=4, return=-30.8%, pnl=$-123.07)
- **Tier A**: HOLD (within expected range)  (n=15, return=4.7%, pnl=$140.11)

## Rule
- Demote if mean return < -5% with n>=8
- Promote if mean return > 15% with n>=8
- Hold otherwise

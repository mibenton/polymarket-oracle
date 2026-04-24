# Auto-Tier Adjustment Report

Generated from 16 closed positions.

## Tier Performance

| pocket   | tier   |   n |   total_stake |   total_pnl |   mean_return_pct |   win_rate_pct | recommendation             |
|:---------|:-------|----:|--------------:|------------:|------------------:|---------------:|:---------------------------|
| sports   | A      |  12 |          2400 |    -1710.34 |             -71.3 |             17 | DEMOTE (mean return < -5%) |
| weather  | A      |   4 |           800 |      472.73 |              59.1 |             50 | HOLD (insufficient n)      |

## Decisions

- **Tier A**: DEMOTE (mean return < -5%)  (n=12, return=-71.3%, pnl=$-1710.34)
- **Tier A**: HOLD (insufficient n)  (n=4, return=59.1%, pnl=$472.73)

## Rule
- Demote if mean return < -5% with n>=8
- Promote if mean return > 15% with n>=8
- Hold otherwise

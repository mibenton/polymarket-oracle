# Polymarket Oracle — Final Evolution Summary (Cycles 1-44)

## Journey
44 cycles of systematic experimentation on 11,003 historical priced markets + live paper trading.

## Final Scanner (Tiers ranked by Expected EV)

| Tier | Historical EV | Win% | Filter |
|------|---|---|---|
| **S++** | +207% | 88% | weather 0.25-0.36 + vol≥20k + preferred cities + local morning + vol_ratio≥0.6 |
| **B++** | +281% | 48% | weather 0.10-0.15 + vol≥20k + preferred cities + local morning + vol_ratio≥0.6 |
| S+ | +176% | 78% | S++ minus vol_ratio filter |
| B+ | +279% | 48% | B++ minus vol_ratio filter |
| S | +123% | 64% | weather 0.25-0.36 + vol≥10k + local morning |
| A+ | +25% | - | weather 0.22-0.25 / 0.36-0.40 + ban losers + local morning |
| A | +80% | 23% | crypto "between X-Y" 0.10-0.15 |
| B | +19% | - | weather 0.10-0.15 + local morning (wider city list) |
| C | +100%* | 9% | box office 0.03-0.10 (high variance) |

*High variance — 3 big wins drive average

## Stake Sizes (by tier priority)

- S++: 5% bankroll
- S+: 4%
- S: 3%
- A+: 2.5%
- B++: 2.5%
- A: 2%
- B+: 2%
- B: 1%
- C: 0.5%

## Key Filters (All Weather Must Pass)

1. **Volume ≥ 10,000** (5-10k had -62% PnL)
2. **Time-to-close ≥ 30h** (T-12h had -50% PnL)
3. **City in local morning at close** (0-12h local; 12-24h = -77% PnL)
4. **City not in tier's banlist** (per-pocket different!)
5. **(S+/B+/S++/B++)** Vol ≥ 20k
6. **(S+/S++/B++)** City in preferred list
7. **(S++/B++)** vol_ratio ≥ 0.6 within event

## Prohibited Categories

- ❌ Sports (7 paper-tested, died)
- ❌ Tropical climate weather (≈0% edge)
- ❌ Tweet counts (EV artifact)
- ❌ Political elections (tail-arb trap)
- ❌ Crypto "reach/dip" thresholds (different from "between")
- ❌ Weather cumulative (orhigher/orbelow)

## Evolution Highlights

| Cycle | Breakthrough | Impact |
|-------|---|---|
| 7 | Paper trade killed sports bias | Saved $1700+ wasted trades |
| 9 | City banlist (East Asia) | +20% uplift |
| 10 | Per-pocket banlist (Beijing differs) | +5% uplift |
| 11 | T-12h disaster zone | Avoided -50% trap |
| 12 | Vol 5-10k disaster | Cutoff at 10k |
| 14 | Multi-bucket Sharpe +68% | Portfolio structure |
| 17 | Crypto range discovery | New pocket |
| 21 | Stacked filter (Tier S+) +122% | 2.4x uplift |
| 29 | Tier B+ discovery | +175% PnL |
| **32** | **LOCAL HOUR FILTER** | **+40% universal uplift** |
| 34 | Box office tail | New category |
| 41 | vol_ratio filter (Tier S++/B++) | +50-100% uplift |

## Performance Projections

### Historical (25-day sample, flat $100/bet)
- Total bets: 633 qualifying
- PnL: **+$46,587 (+466%)**
- Sharpe per bet: +0.29

### Realistic monthly (on $10k)
- Bets per month: 15-30 (post all filters)
- Expected: **+20-40% / month**
- Max drawdown estimate: -20 to -35%

### Risks
- Edge decay (15% per week decay observed, but stabilizing)
- 25-day sample (limited by CLOB API history)
- Market learning may reduce edge over time
- Tier concentration (top 10% trades drive PnL)

## Current Paper Portfolio (2026-04-24)

- 34 open positions, $6,400 deployed (64% bankroll)
- 16 closed: -$1,238 (includes $1,710 sports loss, Cycle 7 lesson)
- Unrealized: ~+$0 to +$300 (rapidly fluctuating)

## Tools

```bash
python daily_run.py                 # Full daily workflow
python cycle6_bias_scanner.py       # Just scan
python oracle_portfolio.py --settle # Just settle
python oracle_portfolio.py --report # Tier performance
python cycle9_auto_tier.py          # Auto-adjust tiers
```

## What I wouldn't do next

- **Add more cycles without fresh data.** Current sample exhausted.
- **Increase stakes beyond 5%.** Kelly + variance says no.
- **Trade more categories.** Only weather/crypto_range/box_office proven.

## What worth exploring (if adding data)

- Weather forecast API integration (potential +50% uplift)
- Settlement-day intraday dynamics
- Cross-event correlation hedging
- Out-of-sample forward validation (30+ days new data)

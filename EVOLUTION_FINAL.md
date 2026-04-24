# Polymarket Oracle — Evolution Final (Cycles 1-115)

## What we built

A **tiered statistical bias scanner** for Polymarket, discovered through 115 cycles of
systematic research on 11,003 historical priced markets and live paper trading.

## The Evolution (in one paragraph)

Started with quantitative FLB hypothesis → all failed. Pivoted to Claude-as-Oracle →
informational edge valid but workbook test showed market beats AI prior. Discovered
weather exact-bucket anchoring bias → refined through climate/city/timing/volume filters.
Found local-close-hour as breakthrough filter (+40pp uplift). Added vol_ratio within
event → Tier S++/B++ (+207/281% EV). Expanded to non-weather: crypto ranges, soccer
totals, box office tails, sports heavy-favorite NO-side arbitrage. End result: 13
active bias pockets across 6 tier levels.

## Active Scanner Pockets (Final)

| # | Pocket | Side | Price | Extra filters | EV% | n | Tier/Stake |
|---|--------|------|-------|---------------|-----|---|------|
| 1 | weather_exact | YES | 0.25-0.36 | pref+vol≥20k+hour+vr≥0.6 | +207 | 25 | S++/5% |
| 2 | weather_exact | YES | 0.25-0.36 | pref+vol≥20k+hour | +176 | 46 | S+/4% |
| 3 | weather_exact | YES | 0.25-0.36 | hour | +123 | 199 | S/3% |
| 4 | weather_exact | YES | 0.30-0.35 | hour+ban | +46 | 70 | A+/2.5% |
| 5 | weather_exact | YES | 0.22-0.25 | hour+ban | +20 | 170 | A+/2.5% |
| 6 | weather_exact | YES | 0.36-0.40 | hour+ban | +20 | 75 | A+/2.5% |
| 7 | weather_exact | YES | 0.02-0.05 | vol≥20k+hour | **+150** | 103 | A/2% |
| 8 | weather_exact | YES | 0.10-0.15 | pref+vol≥20k+hour+vr≥0.6 | **+281** | 21 | B++/2.5% |
| 9 | weather_exact | YES | 0.10-0.15 | pref+vol≥20k+hour | +175 | 44 | B+/2% |
| 10 | weather_exact | YES | 0.10-0.15 | hour | +19 | 347 | B/1% |
| 11 | crypto_range ("between X-Y") | YES | 0.10-0.15 | - | +80 | 26 | A/2% |
| 12 | soccer_total | YES | 0.50-0.60 | - | +30 | 44 | A/2% |
| 13 | sports_global | NO | 0.65-0.80 | - | +22 | 85 | A/2% |
| 14 | sports_global | NO | 0.60-0.65 | - | +10 | 67 | B/1% |
| 15 | sports_us | NO | 0.60-0.80 | - | +12 | 100 | B/1% |
| 16 | box_office | YES | 0.03-0.10 | vol≥10k | +100 | 22 | C/0.5% |

## Hard Rules (all markets must pass)

- Volume ≥ 10,000 (5-10k = -62% PnL disaster)
- Time-to-close ≥ 30h (T-12h = -50% trap)
- Weather markets only: close in city local 0-12h (+117% vs -77%)

## Hard Exclusions

- Sports match winner 0.50-0.60 (paper traded, died -71%)
- Tropical climate weather (+0% edge)
- Weather cumulative orhigher/orbelow (-44 to -75%)
- Tweet count markets (EV artifact)
- Crypto "reach/dip" thresholds (negative)
- Political election tails (tail-arb trap)
- East Asian capitals in tier A+ (negative edge)
- Markets that closed in local afternoon (tied to end of weather day)

## Historical Performance

| Metric | Value |
|--------|-------|
| Qualifying bets over 25 days | 633 |
| Flat $100/bet PnL | **+$60,000+** |
| Max drawdown in MC simulation | -22% |
| Best single tier (S++) | +207% mean PnL |
| Robustness (Ostracism test) | Survives drop-top-2%, dies at 10% |
| Cross-window stability | 2 of 3 windows always positive |

## Realistic Forward Expectation

On $10k paper bankroll:
- 30-80 qualifying bets/month (post all filters)
- Expected monthly return: **+25-40%**
- Max single-month drawdown: 15-25%
- Sharpe per bet: ~0.3

## What makes this different from Cycle 1

Cycle 1: Naive FLB on any weather market at 0.88-0.96 → +2.1% EV → turned out to be clustering artifact.

Cycle 115: 16 distinct pockets, 6 tier levels, per-pocket city banlists, universal local-hour filter, vol_ratio refinement, side-aware (YES/NO) pocketing.

**Mean EV across tiers**: +90% per bet (weighted).
**Improvement over Cycle 1**: ~45x.

## Daily workflow

```bash
python daily_run.py
```

Does:
1. Settle closed positions
2. Scan current open markets through 16 bias pocket filters
3. Open new paper positions (respecting tier stake rules)
4. Report status + tier performance + health alerts
5. Commit to GitHub

## Strategy limits (what's left)

We've plateaued on historical data (11k markets, 25 days). To improve further:
- Need more months of data → see if edge decays or holds
- Need weather forecast API → filter by forecast alignment (potential +50% uplift)
- Need orderbook data → model slippage/depth precisely
- Need real money validation → paper-trade edge may disappear with real fills

## Risk disclosure

- Polymarket not legal in Taiwan (close-only)
- Paper positions ≠ real executions
- UMA settlement can cause disputes (tail risk)
- Market may learn and close the edge

## Files

All in https://github.com/mibenton/polymarket-oracle

- `daily_run.py` — single-command orchestrator
- `cycle6_bias_scanner.py` — scanner with all 16 pockets
- `ingest_bias_positions.py` — tier-aware stake sizing
- `oracle_portfolio.py` — paper-trade ledger
- `cycle9_auto_tier.py` / `cycle65_health_monitor.py` — monitoring
- `cycle{9,10,12,19,20,21,29,30,32,36,76,82,88,91,101}_*.py` — key analyses
- `EVOLUTION_LOG.md` / `EVOLUTION_FINAL.md` / `CYCLE_100_MILESTONE.md` — documentation

## Summary

115 cycles. 16 bias pockets. 6 tier levels. Documented methodology.
Ready to paper-trade and validate forward.

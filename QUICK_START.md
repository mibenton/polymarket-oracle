# Polymarket Oracle — Quick Start

## Every morning

```bash
cd "E:/claude make money"
python daily_run.py
```

That's it. Script will:
1. Settle closed positions
2. Scan current market candidates
3. Show tiered opportunities (S++/S+/S/A+/A/B++/B+/B/C)
4. Open new paper positions if any qualify
5. Print status (PnL, capital at risk)
6. Commit + push to GitHub

## Understand the tiers

| Tier | Recipe | Stake |
|------|--------|-------|
| **S++** | Weather 0.25-0.36, preferred city, vol≥20k, morning close, vol≥60% of event max | 5% |
| **S+** | Above minus vol-ratio | 4% |
| **S** | Weather 0.25-0.36 + morning close | 3% |
| **A+** | Weather 0.22-0.25 / 0.36-0.40 + ban list | 2.5% |
| **B++** | Weather 0.10-0.15, preferred city, vol≥20k, morning close, vol-ratio≥0.6 | 2.5% |
| **B+** | Above minus vol-ratio | 2% |
| **A** | Crypto "between X-Y" 0.10-0.15 | 2% |
| **B** | Weather 0.10-0.15 + morning close | 1% |
| **C** | Box office 0.03-0.10 (high variance) | 0.5% |

## Rules of thumb

### ✅ DO bet when
- City in preferred list for pocket
- Close time is local MORNING (0-12h)
- Volume ≥ 20,000 (ideally)
- Bucket has highest volume in its event
- Target temp near forecast range
- ≥ 30h to resolution

### ❌ DON'T bet when
- Price 0-0.10 OR > 0.40 (edge narrows)
- Tropical climate city (no edge)
- East Asian capital in Tier A+/S+ (negative edge)
- Close < 30h away (T-12h disaster zone)
- Volume < 10k (disaster)
- Close time is local afternoon/evening (−77%)

## Monthly review

After closed positions accumulate:
```bash
python cycle9_auto_tier.py
```

This tells you which tiers are over/under-performing vs historical.

## Weekly check

Look at `data/oracle_positions.csv` to see if:
- Closed positions are winning > 50% in Tier S+/S++
- Tier B++ winning > 30%
- Any tier systematically dying → re-run segmentation

## Bankroll discipline

- Starting bankroll: $10,000 paper
- Max concurrent positions: 30-40
- Max capital at risk: 60-70% bankroll
- Max single position: 5% (S++ only) / 4% (S+) / else smaller
- Compound: reinvest as bankroll grows (Kelly works that way)

## If you want to go live on real Polymarket

1. **Taiwan users: Polymarket is close-only**. Need VPN + risk acceptance.
2. Slippage: expect 1-3% worse fills than paper
3. Settlement: 2h challenge + possible UMA dispute (risk)
4. Fees: 1-1.5% taker per trade (1.5% for crypto, 0.75% sports)
5. Start with $500-1000 to validate edge persists LIVE

## Emergency

If strategy clearly dying:
- 2 consecutive weeks negative on S+/S++ → pause
- Bankroll drawdown > 30% → reset to $10k paper, re-evaluate
- New Polymarket fee structure → recalibrate

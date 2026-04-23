# Polymarket Oracle — Bias-Pocket Paper Trader

Statistical-bias scanner + paper-trade ledger for Polymarket.

## Overview

**Cycle 7 update (2026-04-24)**: Paper trade of 16 Tier-A positions over 2 days
revealed that only ONE bias is real:

| Pocket | Historical | Paper trade result | Status |
|---|---|---|---|
| **weather_exact 0.25-0.40 YES** | +28% EV, n=416, CI [+13, +44] | 2/4 wins, +$473 | ✅ **Survives** |
| sports_global 0.50-0.60 YES | +13% EV, n=115, 3-window stable | 2/12 wins, -$1,710 | ❌ **Killed** |

### Why weather survived and sports died

- **Weather exact-bucket**: has structural reason for mispricing — retail anchors on
  "this specific temperature won't hit" and underprices the 2-3 buckets nearest the
  forecast mean. Mechanism explains the +9pp bias.
- **Sports 0.5-0.6 YES**: no structural reason found. Cross-window stability was
  incidental. When paper-traded 12 times (10 tennis), win rate collapsed to 17% vs
  expected 55%.

### Rule update
Only trade biases with **both** cross-window stability AND explainable mechanism.

## Daily Workflow (remote agent)

```bash
python oracle_portfolio.py --settle    # realize closed positions
python cycle6_bias_scanner.py          # scan current markets
python ingest_bias_positions.py        # add new Tier-A candidates
python oracle_portfolio.py --status    # show PnL snapshot
```

Log accumulates in `data/results/daily_log.txt`.

## Files

### Data (committed)
- `data/oracle_decisions.jsonl` — decision log (append-only)
- `data/oracle_positions.csv` — paper positions (open + closed)
- `data/results/bias_candidates.csv` — latest scan snapshot
- `data/results/daily_log.txt` — daily summary log

### Data (git-ignored, regenerated from API if needed)
- `data/markets*.parquet` — 318k historical markets (60MB)
- `data/prices*.parquet` — 12k price histories

### Scripts (committed)
- `cycle6_bias_scanner.py` — live scanner with Tier A/B/C pockets
- `oracle_portfolio.py` — paper-trade ledger (--settle, --status, --ingest, --report)
- `ingest_bias_positions.py` — bias_candidates.csv → decisions.jsonl
- `pattern_analysis.py` / `pattern_calibration.py` — offline research (needs parquet)
- `cycle6_stability.py` / `cycle6_esports_deepdive.py` — validation

## Research Findings Summary

Cycles 1-3 proved **quant FLB has no edge** in Polymarket (2026-03 to 2026-04 sample):
- Naïve FLB +2.1% was 12-day artifact
- Bootstrap CI "significant" at +3.6% was survivorship + bucket-spam
- Ostracism test + cluster-robust t=0.23 → no edge after correction

Cycle 4 ruled out:
- Cross-platform arb (Taiwan geoblocked + 2.7pp < 2.75% costs)
- Unity constraint cold-start (0/200 current windows; HFT captures)

Cycle 5 built Oracle (Claude judgment) framework — SKIP discipline valid but
calibration without WebSearch worse than market (Brier 0.37 vs 0.13 on 100-Q workbook).

Cycle 6 found **two structurally stable bias pockets** via cross-window test,
which drive the current paper portfolio.

## Bankroll

Starting: $10,000 (paper)
Max per position: 2% ($200)
Target: 15-25 concurrent positions, ~40% bankroll deployed

## Limitations

- Sample span is only 30 days (CLOB API retains ~30d price history)
- Categories with small n (UFC, Dota, specific leagues) may be noise
- Claude didn't analyze individual markets — purely statistical
- UMA dispute risk not modeled (can void 1+ month of profit)

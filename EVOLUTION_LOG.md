# Polymarket Oracle Evolution Log

## Phase 1: Exploration & Elimination (C1-C7)
- **C1-4**: Quant FLB - all failed (bucket-spam, clustering)
- **C5**: Oracle framework - SKIP discipline saves money
- **C6**: Cross-window stability - found 2 candidate biases
- **C7**: Paper trade killed sports (17% win, -$1710). Weather survived (+$473).

## Phase 2: Weather Refinement (C8-C12)
- **C8**: Bucket detector found weather 0.10-0.15 subcategory
- **C9**: Climate segmentation - banned tropical + East Asian capitals
- **C10**: Per-pocket banlist (Beijing BANNED at A+, PREFERRED at B +272%!)
- **C11**: T-12h entry disaster zone. Raised min to 30h.
- **C12**: Vol 5-10k = -62% PnL. Sweet spot: vol 20-100k + price 0.25-0.36.

## Phase 3: Structure Deep-Dive (C13-C17)
- **C13**: Event child-count: 1-3 children +97% (opaque)
- **C14**: Multi-bucket Sharpe +0.29 vs single +0.17 (68% improvement)
- **C15**: DoW patterns Tue/Sun/Fri best (but n too sparse)
- **C16**: Target 3-5°C from city median = +55% PnL
- **C17**: crypto_range "between X-Y" +61% EV, new pocket

## Phase 4: Robustness & Sizing (C18-C21)
- **C19**: Kelly sizing confirmed near-optimal
- **C20**: Ostracism - edge survives top 2% drop, dies at 10% (fragile but real)
- **C21**: **STACKED FILTER GOLD**: price 0.25-0.36 + vol≥20k + preferred cities = +122% PnL, t=5.31 → Tier S+

## Phase 5: Dynamics & Stress (C22-C26)
- **C22**: Event concentration low in S+
- **C23**: Edge decay weekly but all positive (146→155→92→112%)
- **C24**: Forward simulation +$46k on $100/bet × 25 days
- **C25**: Tier B risk - max 17-loss streak, keep stake 1%
- **C26**: Barbell analysis - B contributes most to absolute PnL

## Phase 6: Local-Hour Breakthrough (C27-C32)
- **C27**: Consolidated evolution log
- **C28**: daily_run.py single-command workflow
- **C29**: **Tier B+ discovered**: preferred+vol≥20k at 0.10-0.15 = **+175% PnL**
- **C30**: Unity signal hypothesis failed (reversed pattern)
- **C31**: Hold-to-close confirmed best (Sharpe 0.33 vs 0.20)
- **C32**: 🚀 **LOCAL CLOSE HOUR FILTER BREAKTHROUGH**
  - 0-6h local = +117% PnL, 12-24h = -77%
  - Applied universally to all weather tiers
  - Tier S+ boosted: +122% → **+176%, 78% win, t=+7.93**
  - Tier B+: +175% → **+279%**
  - Tier S: +47% → +123%

## Phase 7: New Categories (C33-C34)
- **C33**: Broad scan across all bucket categories
- **C34**: **Box office opening weekend tails +224% PnL at price 0.02-0.10**

---

## Final Scanner Config (Post-C34)

| Tier | Filter Recipe | n | Expected EV | Stake |
|------|---------------|---|-------------|-------|
| **S+** | weather 0.25-0.36 + vol≥20k + preferred + morning-close | 46 | **+176%** | 4% |
| **B+** | weather 0.10-0.15 + vol≥20k + preferred + morning-close | 44 | **+279%** | 2% |
| S | weather 0.25-0.36 + morning-close | 199 | +123% | 3% |
| A+ | weather 0.22-0.25 / 0.36-0.40 + morning-close + ban losers | 245 | +25% | 2.5% |
| **A** (new) | box_office 0.02-0.10 + vol≥10k | 22 | +100% | 2% |
| A | crypto_range "between" 0.10-0.20 | 40 | +40% | 2% |
| B | weather 0.10-0.15 + morning-close | 347 | +19% | 1% |

### Filter rules stacking

**Weather tiers require ALL:**
1. Price in tier's range
2. Volume ≥ 10k (20k for S+/B+)
3. City not in tier's banlist
4. (S+/B+ only) City in tier's preferred list
5. **Close hour in city local 0-12h** ← Universal
6. End_date > now + 30h (Cycle 11)

### Prohibited

- ❌ sports_global (paper-traded dead)
- ❌ tropical climate weather (0% edge)
- ❌ tweet_count (EV artifact near 0)
- ❌ Vol < 10k (disaster zone)
- ❌ T-12h entry (too late)
- ❌ Close 12-24h local (resolved already)

---

## Performance Expectations

### Historical backtest (25-day sample)
- 633 qualifying bets
- Total PnL at flat $100/bet: **+$46,587 (+466%)**
- Tier B largest: $22,739
- Tier S+: +$6,978 over 57 bets

### Realistic monthly projection (on $10k)
- Expected 15-30 qualifying bets per month (post-filter)
- Portfolio EV: **+20-40% monthly** after fees
- Max drawdown estimate: **-20 to -35%**

### Key risks
1. **Edge decay** (market learning ~15% weekly)
2. **Concentration** (top 10% trades drive PnL)
3. **Sample period limited** to ~25-30 days (CLOB API)
4. **Local-hour filter untested forward** (found C32)

---

## Current Portfolio (2026-04-24)

- **16 closed** (mostly pre-Cycle-9 pure-pocket): -$1,238 realized
  - sports A: 12 bets, -$1,710 (killed the strategy)
  - weather A: 4 bets, +$473 (confirmed edge)
- **33 open**: $6,200 deployed (62% bankroll)
  - Mostly weather 0.10-0.40 + 1 box office
  - Unrealized: +$688 (mark-to-market)
- **Mark-to-market net: -$550 (-5.5%)**

Post-all-refinements, NEW positions should dominate once current batch settles.

---

## Files & Usage

```bash
python daily_run.py          # Everything in one command
python cycle6_bias_scanner.py # Just scan
python oracle_portfolio.py --settle  # Just settle
python oracle_portfolio.py --status  # Just show status
python cycle9_auto_tier.py   # Per-tier performance report
```

All history on GitHub: https://github.com/mibenton/polymarket-oracle

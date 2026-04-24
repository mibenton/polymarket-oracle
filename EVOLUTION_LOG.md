# Polymarket Oracle Evolution Log

## Evolution summary: Cycles 1-26

### Phase 1: Quant-FLB exploration (dead end)
- **Cycles 1-4**: Tested naive FLB, bootstrap CI, ostracism → all failed
  - Bucket-spam + cluster issues made false positives
  - Real n_eff << raw n

### Phase 2: Oracle framework (partial)
- **Cycle 5**: Built Claude-as-Oracle. SKIP discipline valid but Claude's prior worse than market

### Phase 3: Cross-window bias discovery
- **Cycle 6**: Found weather 0.25-0.40 YES + sports_global 0.50-0.60 YES with cross-window stability
- **Cycle 7**: Forward paper trade killed sports (12 bets, 17% win, -$1710). Weather survived (2/4 win, +$473).

### Phase 4: Weather mechanism refinement
- **Cycle 8**: Bucket detector found weather 0.10-0.15 as additional pocket (n=347)
- **Cycle 9**: Segmentation by climate, city, price, day, volume
  - Banned East Asian capitals (Beijing/Taipei/etc: -33 to -80% PnL)
  - Found sweet spot 0.30-0.36 (+68% EV)
- **Cycle 10**: Per-pocket banlist (Beijing banned at A+, PREFERRED at B)

### Phase 5: Timing & volume precision
- **Cycle 11**: T-12h entry is disaster zone (-15 to -50%). T-72h near-optimal.
- **Cycle 12**: Vol 5-10k = -62% PnL. Sweet spot: vol 20-100k + price 0.25-0.36 = +65-93%

### Phase 6: Portfolio construction
- **Cycle 13**: Event child-count: 1-3 children = +97% (opaque mechanism)
- **Cycle 14**: Multi-bucket per event: Sharpe +0.29 vs single +0.17 (68% improvement)

### Phase 7: Cross-category search
- **Cycle 15**: DoW patterns (Tue/Sun/Fri best) but sample too sparse
- **Cycle 16**: Target 3-5°C deviation from city median = +55% PnL
- **Cycle 17**: crypto_range "between X-Y" markets at 0.10-0.20 = +61% EV (n=40)

### Phase 8: Sizing & robustness
- **Cycle 19**: Kelly sizing analysis. Confirmed current stakes ~optimal, minor refinements.
- **Cycle 20**: Ostracism test. Weather edge survives top 2% drop, dies at 10%. Fragile but real.
- **Cycle 21**: **Stacked filter GOLD**: price 0.25-0.36 + vol>=20k + preferred cities = **+122% PnL, t=5.31, n=57** → Tier S+

### Phase 9: Dynamics & stress
- **Cycle 22**: Event concentration low in S+ (1.23 buckets per unique event avg)
- **Cycle 23**: Edge decay week-by-week but remains positive (146% → 92% → 112%)
- **Cycle 24**: Historical compound simulation: absurd numbers but validates tier ordering
- **Cycle 25**: Tier B risk profile: max 17-loss streak. Keep stake 1% conservative.
- **Cycle 26**: Barbell analysis. Tier B biggest PnL contributor (+$22,739 over 25 days flat $100/bet)

---

## Current Scanner Configuration (after Cycle 26)

### Bias Pockets (tiered)

| Tier | Category | Price | Side | Stake | n | EV% | Notes |
|------|----------|-------|------|-------|---|-----|-------|
| **S+** | weather_exact | 0.25-0.36 | YES | **4%** | 57 | +122% | Preferred cities only + vol>=20k |
| S | weather_exact | 0.25-0.36 | YES | 3% | 221 | +55% | All non-banned cities |
| A+ | weather_exact | 0.22-0.25 | YES | 2.5% | 170 | +25% | Banlist applied |
| A+ | weather_exact | 0.36-0.40 | YES | 2.5% | 75 | +20% | |
| A | crypto_range | 0.10-0.20 | YES | 2% | 40 | +40% | "between X-Y" pattern only |
| B | weather_exact | 0.10-0.15 | YES | 1% | 347 | +19% | Different city list per C10 |

### Filter rules

- **Minimum volume**: 10,000 (all), 20,000 (Tier S+)
- **Minimum time to close**: 30 hours (Cycle 11 found T-12h disastrous)
- **S+ preferred cities** (16): dallas, austin, moscow, madrid, wellington, miami, tel-aviv, milan, los-angeles, lucknow, san-francisco, denver, wuhan, toronto, nyc, chongqing
- **A+ banned cities**: atlanta, ankara, london, amsterdam, hong-kong, warsaw, beijing, taipei, seoul, singapore, shanghai
- **B banned cities**: miami, shenzhen, madrid, seoul, moscow, buenos-aires, atlanta, london

### Excluded categories (found negative or unstable EV)

- sports_global 0.50-0.60 (Cycle 7 paper trade killed)
- tropical weather (Cycle 9 found ~0% edge)
- tweet_count ranges (Cycle 17 found -56% to -71%)
- box_office_range (Cycle 17)
- Cumulative weather (orhigher/orbelow variants)

---

## Performance Expectations (realistic)

Historical backtest on 633 qualifying bets over 25 days (no liquidity constraints):
- Without compounding @ $100/bet: **+$46,587 (+466% over 25 days)**
- Tier B largest contributor: **+$22,739**
- Tier S+ concentrated edge: +$6,978 (57 bets × $122 avg)

After realistic haircuts (edge decay, market depth, daily volume limits):
- **Expected monthly return: +15-30% on $10k bankroll**
- Daily bet count: ~5-15 (not 25/day as in historical sample)
- Capital at risk: 30-50% of bankroll typical

## Known risks

1. **Edge decay**: Week-over-week declining (146→92→112%). Market may be learning.
2. **Tier B variance**: 17-loss streaks seen. Keep stake <= 1%.
3. **Fragile concentration**: Top 10% of winners drive most edge. Don't over-size any single bet.
4. **Weather data limit**: Only ~30 days of history due to CLOB API. Cross-month validation not possible.
5. **Cloud allowlist**: Polymarket API blocked from Anthropic CCR. Must run locally.

## Future evolution direction

Not yet explored:
- Weather forecast API integration (Accuweather) → filter buckets by ±1°C of forecast
- Order-book depth analysis (entry at best-ask vs limit order)
- Settlement-day effects (time-of-day on close date)
- Correlation among multiple city-date bets
- Non-weather bucket markets (sports totals, economics exact ranges)

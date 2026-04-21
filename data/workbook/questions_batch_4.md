# Oracle Backtest Workbook — Batch 4

**Task**: 分析以下 20 題。每題只給你 T-72h 前的市場快照和題目，不告訴你結果。你的任務是給出 Decision JSON。

**規則**：
- 禁止使用 WebSearch 或 WebFetch 查結果
- 只能用你的訓練知識 + 題目提供的資訊
- 誠實估 p_claude。如果你完全不知道，寫 confidence=1 然後 SKIP
- SKIP 率高沒關係，這正是框架目標

**Decision JSON 格式**（每題一個）：
```json
{
  "q_id": 整數,
  "slug": "...",
  "decision": "BUY YES" | "BUY NO" | "SKIP",
  "p_claude": 0.00,
  "entry_price": 0.00,
  "edge_bps": 整數,
  "confidence": 1-5,
  "reasoning": "簡短"
}
```

## Q61

- **slug**: `bra-san-cre-2026-04-02-cre`
- **question**: Will Clube do Remo win on 2026-04-02?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.855 (ask 0.865, bid 0.845)
- **other side**: Yes @ mid 0.145
- **volume at close**: $33,910
- **duration**: 151h
- **close date**: 2026-04-03

→ 你的 Decision JSON:
```json
{
  "q_id": 61,
  "slug": "bra-san-cre-2026-04-02-cre",
  ...
}
```

## Q62

- **slug**: `will-russia-capture-kupiansk-vuzlovyi-by-march-31`
- **question**: Will Russia capture Kupiansk-Vuzlovyi by March 31?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.993 (ask 0.999, bid 0.983)
- **other side**: Yes @ mid 0.007
- **volume at close**: $41,651
- **duration**: 1491h
- **close date**: 2026-04-01

→ 你的 Decision JSON:
```json
{
  "q_id": 62,
  "slug": "will-russia-capture-kupiansk-vuzlovyi-by-march-31",
  ...
}
```

## Q63

- **slug**: `will-lng-tam-quang-be-the-next-prime-minister-of-vietnam`
- **question**: Will Lương Tam Quang be the next Prime Minister of Vietnam?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.999 (ask 0.999, bid 0.989)
- **other side**: Yes @ mid 0.001
- **volume at close**: $380,961
- **duration**: 1847h
- **close date**: 2026-04-07

→ 你的 Decision JSON:
```json
{
  "q_id": 63,
  "slug": "will-lng-tam-quang-be-the-next-prime-minister-of-vietnam",
  ...
}
```

## Q64

- **slug**: `arg-cat-tig-2026-04-12-cat`
- **question**: Will CA Tucumán win on 2026-04-12?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.640 (ask 0.650, bid 0.630)
- **other side**: Yes @ mid 0.360
- **volume at close**: $307,267
- **duration**: 391h
- **close date**: 2026-04-13

→ 你的 Decision JSON:
```json
{
  "q_id": 64,
  "slug": "arg-cat-tig-2026-04-12-cat",
  ...
}
```

## Q65

- **slug**: `nhl-sea-col-2026-04-16-total-5pt5`
- **question**: Kraken vs. Avalanche: O/U 5.5
- **outcomes**: Over / Under
- **favorite at T-72h**: Over @ mid 0.565 (ask 0.575, bid 0.555)
- **other side**: Under @ mid 0.435
- **volume at close**: $15,184
- **duration**: 664h
- **close date**: 2026-04-17

→ 你的 Decision JSON:
```json
{
  "q_id": 65,
  "slug": "nhl-sea-col-2026-04-16-total-5pt5",
  ...
}
```

## Q66

- **slug**: `will-djia-reach-48300-in-march-653-889`
- **question**: Will Dow Jones (DJIA) hit 48300 (HIGH) in March?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.822 (ask 0.832, bid 0.811)
- **other side**: Yes @ mid 0.178
- **volume at close**: $21,579
- **duration**: 530h
- **close date**: 2026-03-31

→ 你的 Decision JSON:
```json
{
  "q_id": 66,
  "slug": "will-djia-reach-48300-in-march-653-889",
  ...
}
```

## Q67

- **slug**: `will-tisza-win-9099-seats-in-the-hungarian-national-assembly-in-this-election`
- **question**: Will Tisza win 90–99 seats in the Hungarian National Assembly in this election?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.910 (ask 0.920, bid 0.900)
- **other side**: Yes @ mid 0.090
- **volume at close**: $32,054
- **duration**: 747h
- **close date**: 2026-04-13

→ 你的 Decision JSON:
```json
{
  "q_id": 67,
  "slug": "will-tisza-win-9099-seats-in-the-hungarian-national-assembly-in-this-election",
  ...
}
```

## Q68

- **slug**: `will-bully-kanye-west-be-the-billboard-200-1-album-for-the-week-of-april-11`
- **question**: Will "Bully - Kanye West" be the Billboard 200 #1 album for the week of April 11?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.910 (ask 0.920, bid 0.900)
- **other side**: Yes @ mid 0.090
- **volume at close**: $36,723
- **duration**: 171h
- **close date**: 2026-04-07

→ 你的 Decision JSON:
```json
{
  "q_id": 68,
  "slug": "will-bully-kanye-west-be-the-billboard-200-1-album-for-the-week-of-april-11",
  ...
}
```

## Q69

- **slug**: `scop-cel-stm-2026-04-11-total-4pt5`
- **question**: Celtic FC vs. St Mirren FC: O/U 4.5
- **outcomes**: Over / Under
- **favorite at T-72h**: Under @ mid 0.735 (ask 0.745, bid 0.725)
- **other side**: Over @ mid 0.265
- **volume at close**: $11,101
- **duration**: 308h
- **close date**: 2026-04-11

→ 你的 Decision JSON:
```json
{
  "q_id": 69,
  "slug": "scop-cel-stm-2026-04-11-total-4pt5",
  ...
}
```

## Q70

- **slug**: `el1-wim-sto-2026-04-15-wim`
- **question**: Will AFC Wimbledon win on 2026-04-15?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.765 (ask 0.775, bid 0.755)
- **other side**: Yes @ mid 0.235
- **volume at close**: $14,842
- **duration**: 333h
- **close date**: 2026-04-16

→ 你的 Decision JSON:
```json
{
  "q_id": 70,
  "slug": "el1-wim-sto-2026-04-15-wim",
  ...
}
```

## Q71

- **slug**: `will-choosin-texas-ella-langley-be-the-billboard-hot-100-1-song-for-the-week-of-april-11`
- **question**: Will "Choosin' Texas - Ella Langley" be the Billboard Hot 100 #1 song for the week of April 11?
- **outcomes**: Yes / No
- **favorite at T-72h**: Yes @ mid 0.905 (ask 0.915, bid 0.895)
- **other side**: No @ mid 0.095
- **volume at close**: $12,520
- **duration**: 171h
- **close date**: 2026-04-07

→ 你的 Decision JSON:
```json
{
  "q_id": 71,
  "slug": "will-choosin-texas-ella-langley-be-the-billboard-hot-100-1-song-for-the-week-of-april-11",
  ...
}
```

## Q72

- **slug**: `over-4m-committed-to-the-fluent-public-sale`
- **question**: Over $4M committed to the Fluent public sale?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.825 (ask 0.835, bid 0.815)
- **other side**: Yes @ mid 0.175
- **volume at close**: $26,986
- **duration**: 171h
- **close date**: 2026-04-13

→ 你的 Decision JSON:
```json
{
  "q_id": 72,
  "slug": "over-4m-committed-to-the-fluent-public-sale",
  ...
}
```

## Q73

- **slug**: `lib-lan-alw-2026-04-16-lan`
- **question**: Will CA Lanús win on 2026-04-16?
- **outcomes**: Yes / No
- **favorite at T-72h**: Yes @ mid 0.785 (ask 0.795, bid 0.775)
- **other side**: No @ mid 0.215
- **volume at close**: $49,371
- **duration**: 491h
- **close date**: 2026-04-17

→ 你的 Decision JSON:
```json
{
  "q_id": 73,
  "slug": "lib-lan-alw-2026-04-16-lan",
  ...
}
```

## Q74

- **slug**: `itsb-pal-ave-2026-04-05-pal`
- **question**: Will Palermo FC win on 2026-04-05?
- **outcomes**: Yes / No
- **favorite at T-72h**: Yes @ mid 0.645 (ask 0.655, bid 0.635)
- **other side**: No @ mid 0.355
- **volume at close**: $15,709
- **duration**: 326h
- **close date**: 2026-04-05

→ 你的 Decision JSON:
```json
{
  "q_id": 74,
  "slug": "itsb-pal-ave-2026-04-05-pal",
  ...
}
```

## Q75

- **slug**: `aus-vic-ccm-2026-03-21-draw`
- **question**: Will Melbourne Victory FC vs. Central Coast Mariners FC end in a draw?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.810 (ask 0.820, bid 0.800)
- **other side**: Yes @ mid 0.190
- **volume at close**: $21,629
- **duration**: 661h
- **close date**: 2026-03-21

→ 你的 Decision JSON:
```json
{
  "q_id": 75,
  "slug": "aus-vic-ccm-2026-03-21-draw",
  ...
}
```

## Q76

- **slug**: `ethereum-above-2300-on-march-31`
- **question**: Will the price of Ethereum be above $2,300 on March 31?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.981 (ask 0.991, bid 0.971)
- **other side**: Yes @ mid 0.019
- **volume at close**: $57,011
- **duration**: 171h
- **close date**: 2026-03-31

→ 你的 Decision JSON:
```json
{
  "q_id": 76,
  "slug": "ethereum-above-2300-on-march-31",
  ...
}
```

## Q77

- **slug**: `will-wti-dip-to-105-by-april-6-2026`
- **question**: Will WTI Crude Oil (WTI) hit (LOW) $105 Week of April 6 2026?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.505 (ask 0.515, bid 0.495)
- **other side**: Yes @ mid 0.495
- **volume at close**: $13,715
- **duration**: 100h
- **close date**: 2026-04-08

→ 你的 Decision JSON:
```json
{
  "q_id": 77,
  "slug": "will-wti-dip-to-105-by-april-6-2026",
  ...
}
```

## Q78

- **slug**: `will-fewer-than-10-ships-transit-the-strait-of-hormuz-between-march-17-23`
- **question**: Will fewer than 10 ships transit the Strait of Hormuz between March 17-23?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 1.000 (ask 0.999, bid 0.990)
- **other side**: Yes @ mid 0.000
- **volume at close**: $56,331
- **duration**: 350h
- **close date**: 2026-03-31

→ 你的 Decision JSON:
```json
{
  "q_id": 78,
  "slug": "will-fewer-than-10-ships-transit-the-strait-of-hormuz-between-march-17-23",
  ...
}
```

## Q79

- **slug**: `solana-up-or-down-on-april-10-2026`
- **question**: Solana Up or Down on April 10?
- **outcomes**: Up / Down
- **favorite at T-72h**: Up @ mid 1.000 (ask 0.999, bid 0.990)
- **other side**: Down @ mid 0.000
- **volume at close**: $11,930
- **duration**: 146h
- **close date**: 2026-04-14

→ 你的 Decision JSON:
```json
{
  "q_id": 79,
  "slug": "solana-up-or-down-on-april-10-2026",
  ...
}
```

## Q80

- **slug**: `dota2-lynx-yes-2026-04-09`
- **question**: Dota 2: Team Lynx vs Yellow Submarine (BO3) - European Pro League Group A
- **outcomes**: Team Lynx / Yellow Submarine
- **favorite at T-72h**: Yellow Submarine @ mid 0.525 (ask 0.535, bid 0.515)
- **other side**: Team Lynx @ mid 0.475
- **volume at close**: $12,008
- **duration**: 115h
- **close date**: 2026-04-12

→ 你的 Decision JSON:
```json
{
  "q_id": 80,
  "slug": "dota2-lynx-yes-2026-04-09",
  ...
}
```

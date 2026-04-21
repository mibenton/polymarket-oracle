# Oracle Backtest Workbook — Batch 1

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

## Q1

- **slug**: `val-rose-d1-2026-04-13`
- **question**: Valorant: ROSE vs Division One (BO3) - VCL North America: Stage 2 Group Stage
- **outcomes**: ROSE / Division One
- **favorite at T-72h**: Division One @ mid 0.695 (ask 0.705, bid 0.685)
- **other side**: ROSE @ mid 0.305
- **volume at close**: $13,048
- **duration**: 131h
- **close date**: 2026-04-14

→ 你的 Decision JSON:
```json
{
  "q_id": 1,
  "slug": "val-rose-d1-2026-04-13",
  ...
}
```

## Q2

- **slug**: `j1100-kyo-fag-2026-04-11-kyo`
- **question**: Will Kyōto Sanga FC win on 2026-04-11?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.505 (ask 0.515, bid 0.495)
- **other side**: Yes @ mid 0.495
- **volume at close**: $16,495
- **duration**: 664h
- **close date**: 2026-04-11

→ 你的 Decision JSON:
```json
{
  "q_id": 2,
  "slug": "j1100-kyo-fag-2026-04-11-kyo",
  ...
}
```

## Q3

- **slug**: `msft-up-or-down-on-april-13-2026`
- **question**: Microsoft (MSFT) Up or Down on April 13?
- **outcomes**: Up / Down
- **favorite at T-72h**: Up @ mid 0.515 (ask 0.525, bid 0.505)
- **other side**: Down @ mid 0.485
- **volume at close**: $39,649
- **duration**: 86h
- **close date**: 2026-04-14

→ 你的 Decision JSON:
```json
{
  "q_id": 3,
  "slug": "msft-up-or-down-on-april-13-2026",
  ...
}
```

## Q4

- **slug**: `fif-aut-gha-2026-03-27-gha`
- **question**: Will Ghana win on 2026-03-27?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.800 (ask 0.810, bid 0.790)
- **other side**: Yes @ mid 0.200
- **volume at close**: $76,738
- **duration**: 656h
- **close date**: 2026-03-27

→ 你的 Decision JSON:
```json
{
  "q_id": 4,
  "slug": "fif-aut-gha-2026-03-27-gha",
  ...
}
```

## Q5

- **slug**: `elc-mid-mil-2026-04-03-total-2pt5`
- **question**: Middlesbrough FC vs. Millwall FC: O/U 2.5
- **outcomes**: Over / Under
- **favorite at T-72h**: Over @ mid 0.560 (ask 0.570, bid 0.550)
- **other side**: Under @ mid 0.440
- **volume at close**: $60,784
- **duration**: 651h
- **close date**: 2026-04-03

→ 你的 Decision JSON:
```json
{
  "q_id": 5,
  "slug": "elc-mid-mil-2026-04-03-total-2pt5",
  ...
}
```

## Q6

- **slug**: `will-bitcoin-reach-78k-march-30-april-5`
- **question**: Will Bitcoin reach $78,000 March 30-April 5?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.994 (ask 0.999, bid 0.984)
- **other side**: Yes @ mid 0.006
- **volume at close**: $288,351
- **duration**: 171h
- **close date**: 2026-04-06

→ 你的 Decision JSON:
```json
{
  "q_id": 6,
  "slug": "will-bitcoin-reach-78k-march-30-april-5",
  ...
}
```

## Q7

- **slug**: `onefootball-fdv-above-100m-one-day-after-launch-371-375`
- **question**: OneFootball FDV above $100M one day after launch?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.735 (ask 0.745, bid 0.725)
- **other side**: Yes @ mid 0.265
- **volume at close**: $71,728
- **duration**: 337h
- **close date**: 2026-04-10

→ 你的 Decision JSON:
```json
{
  "q_id": 7,
  "slug": "onefootball-fdv-above-100m-one-day-after-launch-371-375",
  ...
}
```

## Q8

- **slug**: `lol-vfb-es1-2026-04-08`
- **question**: LoL: VfB eSports vs Eintracht Spandau (BO1) - Prime League 1st Division Regular Season
- **outcomes**: VfB eSports / Eintracht Spandau
- **favorite at T-72h**: Eintracht Spandau @ mid 0.845 (ask 0.855, bid 0.835)
- **other side**: VfB eSports @ mid 0.155
- **volume at close**: $21,261
- **duration**: 105h
- **close date**: 2026-04-08

→ 你的 Decision JSON:
```json
{
  "q_id": 8,
  "slug": "lol-vfb-es1-2026-04-08",
  ...
}
```

## Q9

- **slug**: `highest-temperature-in-lagos-on-april-15-2026-35c`
- **question**: Will the highest temperature in Lagos be 35°C on April 15?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.855 (ask 0.865, bid 0.845)
- **other side**: Yes @ mid 0.145
- **volume at close**: $10,024
- **duration**: 80h
- **close date**: 2026-04-16

→ 你的 Decision JSON:
```json
{
  "q_id": 9,
  "slug": "highest-temperature-in-lagos-on-april-15-2026-35c",
  ...
}
```

## Q10

- **slug**: `gpt-5pt5-released-by-april-15-2026`
- **question**: GPT-5.5 released by April 15, 2026?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.915 (ask 0.925, bid 0.905)
- **other side**: Yes @ mid 0.085
- **volume at close**: $179,521
- **duration**: 827h
- **close date**: 2026-04-16

→ 你的 Decision JSON:
```json
{
  "q_id": 10,
  "slug": "gpt-5pt5-released-by-april-15-2026",
  ...
}
```

## Q11

- **slug**: `will-trump-say-farmer-during-the-white-house-easter-egg-roll`
- **question**: Will Trump say "Farmer" during the White House Easter Egg Roll?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.665 (ask 0.675, bid 0.655)
- **other side**: Yes @ mid 0.335
- **volume at close**: $14,433
- **duration**: 147h
- **close date**: 2026-04-06

→ 你的 Decision JSON:
```json
{
  "q_id": 11,
  "slug": "will-trump-say-farmer-during-the-white-house-easter-egg-roll",
  ...
}
```

## Q12

- **slug**: `will-phm-minh-chnh-be-the-next-prime-minister-of-vietnam`
- **question**: Will Phạm Minh Chính be the next Prime Minister of Vietnam?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.997 (ask 0.999, bid 0.987)
- **other side**: Yes @ mid 0.003
- **volume at close**: $661,740
- **duration**: 1846h
- **close date**: 2026-04-07

→ 你的 Decision JSON:
```json
{
  "q_id": 12,
  "slug": "will-phm-minh-chnh-be-the-next-prime-minister-of-vietnam",
  ...
}
```

## Q13

- **slug**: `itsb-mon-bar-2026-04-11-mon`
- **question**: Will AC Monza win on 2026-04-11?
- **outcomes**: Yes / No
- **favorite at T-72h**: Yes @ mid 0.735 (ask 0.745, bid 0.725)
- **other side**: No @ mid 0.265
- **volume at close**: $25,955
- **duration**: 327h
- **close date**: 2026-04-11

→ 你的 Decision JSON:
```json
{
  "q_id": 13,
  "slug": "itsb-mon-bar-2026-04-11-mon",
  ...
}
```

## Q14

- **slug**: `nhl-col-edm-2026-04-13-total-5pt5`
- **question**: Avalanche vs. Oilers: O/U 5.5
- **outcomes**: Over / Under
- **favorite at T-72h**: Over @ mid 0.510 (ask 0.520, bid 0.500)
- **other side**: Under @ mid 0.490
- **volume at close**: $24,321
- **duration**: 663h
- **close date**: 2026-04-14

→ 你的 Decision JSON:
```json
{
  "q_id": 14,
  "slug": "nhl-col-edm-2026-04-13-total-5pt5",
  ...
}
```

## Q15

- **slug**: `den-vib-agf-2026-04-06-total-4pt5`
- **question**: Viborg FF vs. Aarhus GF: O/U 4.5
- **outcomes**: Over / Under
- **favorite at T-72h**: Under @ mid 0.830 (ask 0.840, bid 0.820)
- **other side**: Over @ mid 0.170
- **volume at close**: $15,887
- **duration**: 671h
- **close date**: 2026-04-06

→ 你的 Decision JSON:
```json
{
  "q_id": 15,
  "slug": "den-vib-agf-2026-04-06-total-4pt5",
  ...
}
```

## Q16

- **slug**: `microstrategy-announces-1000-btc-purchase-april-7-13`
- **question**: MicroStrategy announces >1000 BTC purchase April 7-13?
- **outcomes**: Yes / No
- **favorite at T-72h**: Yes @ mid 0.972 (ask 0.982, bid 0.962)
- **other side**: No @ mid 0.028
- **volume at close**: $72,522
- **duration**: 178h
- **close date**: 2026-04-13

→ 你的 Decision JSON:
```json
{
  "q_id": 16,
  "slug": "microstrategy-announces-1000-btc-purchase-april-7-13",
  ...
}
```

## Q17

- **slug**: `rus-zen-kra-2026-04-12-kra`
- **question**: Will FK Krasnodar win on 2026-04-12?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.745 (ask 0.755, bid 0.735)
- **other side**: Yes @ mid 0.255
- **volume at close**: $16,257
- **duration**: 387h
- **close date**: 2026-04-12

→ 你的 Decision JSON:
```json
{
  "q_id": 17,
  "slug": "rus-zen-kra-2026-04-12-kra",
  ...
}
```

## Q18

- **slug**: `will-keaton-wagler-win-the-2026-outstanding-player-of-the-tournament-for-the-2026-mens-ncaa-tournament`
- **question**: Will Keaton Wagler win the 2026 Outstanding Player of the tournament for the 2026 Mens NCAA Tournament?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.871 (ask 0.881, bid 0.861)
- **other side**: Yes @ mid 0.129
- **volume at close**: $13,491
- **duration**: 685h
- **close date**: 2026-04-07

→ 你的 Decision JSON:
```json
{
  "q_id": 18,
  "slug": "will-keaton-wagler-win-the-2026-outstanding-player-of-the-tournament-for-the-2026-mens-ncaa-tournament",
  ...
}
```

## Q19

- **slug**: `will-30-39-ships-transit-the-strait-of-hormuz-between-april-6-april-12`
- **question**: Will 30-39 ships transit the Strait of Hormuz between April 6-April 12?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.960 (ask 0.970, bid 0.950)
- **other side**: Yes @ mid 0.040
- **volume at close**: $28,988
- **duration**: 259h
- **close date**: 2026-04-14

→ 你的 Decision JSON:
```json
{
  "q_id": 19,
  "slug": "will-30-39-ships-transit-the-strait-of-hormuz-between-april-6-april-12",
  ...
}
```

## Q20

- **slug**: `will-tesla-deliver-between-475000-and-500000-vehicles-in-q1-2026`
- **question**: Will Tesla deliver between 475000 and 500000 vehicles in Q1 2026
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 1.000 (ask 0.999, bid 0.990)
- **other side**: Yes @ mid 0.000
- **volume at close**: $46,302
- **duration**: 2156h
- **close date**: 2026-04-02

→ 你的 Decision JSON:
```json
{
  "q_id": 20,
  "slug": "will-tesla-deliver-between-475000-and-500000-vehicles-in-q1-2026",
  ...
}
```

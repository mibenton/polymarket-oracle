# Oracle Backtest Workbook — Batch 5

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

## Q81

- **slug**: `lol-rmd-reda-2026-04-08`
- **question**: LoL: RMD Gaming vs RED Academy (BO1) - Circuito Desafiante Regular Season
- **outcomes**: RMD Gaming / RED Academy
- **favorite at T-72h**: RED Academy @ mid 0.810 (ask 0.820, bid 0.800)
- **other side**: RMD Gaming @ mid 0.190
- **volume at close**: $98,376
- **duration**: 151h
- **close date**: 2026-04-09

→ 你的 Decision JSON:
```json
{
  "q_id": 81,
  "slug": "lol-rmd-reda-2026-04-08",
  ...
}
```

## Q82

- **slug**: `lol-genga-t1a-2026-04-09-game2`
- **question**: LoL: Gen.G Global Academy vs T1 Academy - Game 2 Winner
- **outcomes**: Gen.G Global Academy / T1 Academy
- **favorite at T-72h**: Gen.G Global Academy @ mid 0.505 (ask 0.515, bid 0.495)
- **other side**: T1 Academy @ mid 0.495
- **volume at close**: $21,185
- **duration**: 107h
- **close date**: 2026-04-09

→ 你的 Decision JSON:
```json
{
  "q_id": 82,
  "slug": "lol-genga-t1a-2026-04-09-game2",
  ...
}
```

## Q83

- **slug**: `elc-wat-lei-2026-03-21-lei`
- **question**: Will Leicester City FC win on 2026-03-21?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.735 (ask 0.745, bid 0.725)
- **other side**: Yes @ mid 0.265
- **volume at close**: $30,923
- **duration**: 665h
- **close date**: 2026-03-21

→ 你的 Decision JSON:
```json
{
  "q_id": 83,
  "slug": "elc-wat-lei-2026-03-21-lei",
  ...
}
```

## Q84

- **slug**: `fl1-sbr-ren-2026-04-04-total-2pt5`
- **question**: Stade Brestois 29 vs. Stade Rennais FC 1901: O/U 2.5
- **outcomes**: Over / Under
- **favorite at T-72h**: Over @ mid 0.515 (ask 0.525, bid 0.505)
- **other side**: Under @ mid 0.485
- **volume at close**: $29,124
- **duration**: 220h
- **close date**: 2026-04-04

→ 你的 Decision JSON:
```json
{
  "q_id": 84,
  "slug": "fl1-sbr-ren-2026-04-04-total-2pt5",
  ...
}
```

## Q85

- **slug**: `epl-ful-bur-2026-03-21-spread-home-1pt5`
- **question**: Spread: Fulham FC (-1.5)
- **outcomes**: Fulham FC / Burnley FC
- **favorite at T-72h**: Burnley FC @ mid 0.630 (ask 0.640, bid 0.620)
- **other side**: Fulham FC @ mid 0.370
- **volume at close**: $37,181
- **duration**: 325h
- **close date**: 2026-03-21

→ 你的 Decision JSON:
```json
{
  "q_id": 85,
  "slug": "epl-ful-bur-2026-03-21-spread-home-1pt5",
  ...
}
```

## Q86

- **slug**: `nhl-cal-col-2026-04-09`
- **question**: Flames vs. Avalanche
- **outcomes**: Flames / Avalanche
- **favorite at T-72h**: Avalanche @ mid 0.715 (ask 0.725, bid 0.705)
- **other side**: Flames @ mid 0.285
- **volume at close**: $370,603
- **duration**: 662h
- **close date**: 2026-04-10

→ 你的 Decision JSON:
```json
{
  "q_id": 86,
  "slug": "nhl-cal-col-2026-04-09",
  ...
}
```

## Q87

- **slug**: `lol-vfb-g2nord-2026-04-10`
- **question**: LoL: VfB eSports vs G2 NORD (BO1) - Prime League 1st Division Regular Season
- **outcomes**: VfB eSports / G2 NORD
- **favorite at T-72h**: G2 NORD @ mid 0.855 (ask 0.865, bid 0.845)
- **other side**: VfB eSports @ mid 0.145
- **volume at close**: $17,323
- **duration**: 141h
- **close date**: 2026-04-10

→ 你的 Decision JSON:
```json
{
  "q_id": 87,
  "slug": "lol-vfb-g2nord-2026-04-10",
  ...
}
```

## Q88

- **slug**: `will-the-indiana-pacers-have-the-worst-record-in-the-nba`
- **question**: Will the Indiana Pacers have the worst record in the NBA?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.865 (ask 0.875, bid 0.855)
- **other side**: Yes @ mid 0.135
- **volume at close**: $84,891
- **duration**: 4104h
- **close date**: 2026-04-11

→ 你的 Decision JSON:
```json
{
  "q_id": 88,
  "slug": "will-the-indiana-pacers-have-the-worst-record-in-the-nba",
  ...
}
```

## Q89

- **slug**: `elc-sto-swe-2026-04-03-swe`
- **question**: Will Sheffield Wednesday FC win on 2026-04-03?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.920 (ask 0.930, bid 0.910)
- **other side**: Yes @ mid 0.080
- **volume at close**: $34,335
- **duration**: 662h
- **close date**: 2026-04-03

→ 你的 Decision JSON:
```json
{
  "q_id": 89,
  "slug": "elc-sto-swe-2026-04-03-swe",
  ...
}
```

## Q90

- **slug**: `bl2-fcm-boc-2026-04-04-draw`
- **question**: Will 1. FC Magdeburg vs. VfL Bochum end in a draw?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.750 (ask 0.760, bid 0.740)
- **other side**: Yes @ mid 0.250
- **volume at close**: $31,307
- **duration**: 325h
- **close date**: 2026-04-04

→ 你的 Decision JSON:
```json
{
  "q_id": 90,
  "slug": "bl2-fcm-boc-2026-04-04-draw",
  ...
}
```

## Q91

- **slug**: `will-ethereum-reach-2800-march-23-29`
- **question**: Will Ethereum reach $2,800 March 23-29?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.998 (ask 0.999, bid 0.988)
- **other side**: Yes @ mid 0.002
- **volume at close**: $36,149
- **duration**: 170h
- **close date**: 2026-03-30

→ 你的 Decision JSON:
```json
{
  "q_id": 91,
  "slug": "will-ethereum-reach-2800-march-23-29",
  ...
}
```

## Q92

- **slug**: `mezo-fdv-above-100m-one-day-after-launch`
- **question**: Mezo FDV above $100M one day after launch?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.690 (ask 0.700, bid 0.680)
- **other side**: Yes @ mid 0.310
- **volume at close**: $47,113
- **duration**: 1571h
- **close date**: 2026-04-03

→ 你的 Decision JSON:
```json
{
  "q_id": 92,
  "slug": "mezo-fdv-above-100m-one-day-after-launch",
  ...
}
```

## Q93

- **slug**: `cs2-ast10-mibr-2026-04-04`
- **question**: Counter-Strike: Astralis vs MIBR (BO3) - PGL Bucharest Group Stage
- **outcomes**: Astralis / MIBR
- **favorite at T-72h**: Astralis @ mid 0.805 (ask 0.815, bid 0.795)
- **other side**: MIBR @ mid 0.195
- **volume at close**: $81,763
- **duration**: 74h
- **close date**: 2026-04-04

→ 你的 Decision JSON:
```json
{
  "q_id": 93,
  "slug": "cs2-ast10-mibr-2026-04-04",
  ...
}
```

## Q94

- **slug**: `will-spx-dip-to-4750-in-march`
- **question**: Will S&P 500 (SPX) hit 4750 (LOW) in March?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.996 (ask 0.999, bid 0.986)
- **other side**: Yes @ mid 0.004
- **volume at close**: $44,755
- **duration**: 530h
- **close date**: 2026-03-31

→ 你的 Decision JSON:
```json
{
  "q_id": 94,
  "slug": "will-spx-dip-to-4750-in-march",
  ...
}
```

## Q95

- **slug**: `lib-alw-lqu-2026-04-07-alw`
- **question**: Will Club Always Ready win on 2026-04-07?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.615 (ask 0.625, bid 0.605)
- **other side**: Yes @ mid 0.385
- **volume at close**: $29,467
- **duration**: 278h
- **close date**: 2026-04-08

→ 你的 Decision JSON:
```json
{
  "q_id": 95,
  "slug": "lib-alw-lqu-2026-04-07-alw",
  ...
}
```

## Q96

- **slug**: `will-starmer-say-mr-speaker-30-times-during-the-next-prime-ministers-questions-event-576`
- **question**: Will Starmer say "Mr. Speaker" 30+ times during the next Prime Minister's Questions event?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.725 (ask 0.735, bid 0.715)
- **other side**: Yes @ mid 0.275
- **volume at close**: $10,975
- **duration**: 474h
- **close date**: 2026-04-15

→ 你的 Decision JSON:
```json
{
  "q_id": 96,
  "slug": "will-starmer-say-mr-speaker-30-times-during-the-next-prime-ministers-questions-event-576",
  ...
}
```

## Q97

- **slug**: `will-isaline-cornil-be-the-next-mayor-of-toulon`
- **question**: Will Isaline Cornil be the next mayor of Toulon?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 1.000 (ask 0.999, bid 0.990)
- **other side**: Yes @ mid 0.000
- **volume at close**: $31,092
- **duration**: 564h
- **close date**: 2026-03-27

→ 你的 Decision JSON:
```json
{
  "q_id": 97,
  "slug": "will-isaline-cornil-be-the-next-mayor-of-toulon",
  ...
}
```

## Q98

- **slug**: `nhl-lak-van-2026-04-14-total-6pt5`
- **question**: Kings vs. Canucks: O/U 6.5
- **outcomes**: Over / Under
- **favorite at T-72h**: Under @ mid 0.580 (ask 0.590, bid 0.570)
- **other side**: Over @ mid 0.420
- **volume at close**: $20,717
- **duration**: 663h
- **close date**: 2026-04-15

→ 你的 Decision JSON:
```json
{
  "q_id": 98,
  "slug": "nhl-lak-van-2026-04-14-total-6pt5",
  ...
}
```

## Q99

- **slug**: `den-vib-agf-2026-04-06-agf`
- **question**: Will Aarhus GF win on 2026-04-06?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.565 (ask 0.575, bid 0.555)
- **other side**: Yes @ mid 0.435
- **volume at close**: $21,184
- **duration**: 673h
- **close date**: 2026-04-06

→ 你的 Decision JSON:
```json
{
  "q_id": 99,
  "slug": "den-vib-agf-2026-04-06-agf",
  ...
}
```

## Q100

- **slug**: `will-20-ships-transit-the-strait-of-hormuz-on-any-day-april-812`
- **question**: Will 20 ships transit the Strait of Hormuz on any day April 8–12?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.852 (ask 0.862, bid 0.842)
- **other side**: Yes @ mid 0.148
- **volume at close**: $69,827
- **duration**: 145h
- **close date**: 2026-04-14

→ 你的 Decision JSON:
```json
{
  "q_id": 100,
  "slug": "will-20-ships-transit-the-strait-of-hormuz-on-any-day-april-812",
  ...
}
```

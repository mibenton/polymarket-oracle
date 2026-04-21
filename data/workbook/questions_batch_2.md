# Oracle Backtest Workbook — Batch 2

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

## Q21

- **slug**: `will-usd-fall-to-1pt4m-iranian-rials-by-march-31-256-348-996`
- **question**: Will USD fall to 1.4M Iranian rials by March 31?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.986 (ask 0.996, bid 0.976)
- **other side**: Yes @ mid 0.014
- **volume at close**: $24,320
- **duration**: 538h
- **close date**: 2026-04-02

→ 你的 Decision JSON:
```json
{
  "q_id": 21,
  "slug": "will-usd-fall-to-1pt4m-iranian-rials-by-march-31-256-348-996",
  ...
}
```

## Q22

- **slug**: `will-xrp-dip-to-1pt2-march-30-april-5`
- **question**: Will XRP dip to $1.20 March 30-April 5?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.905 (ask 0.915, bid 0.895)
- **other side**: Yes @ mid 0.095
- **volume at close**: $39,363
- **duration**: 170h
- **close date**: 2026-04-06

→ 你的 Decision JSON:
```json
{
  "q_id": 22,
  "slug": "will-xrp-dip-to-1pt2-march-30-april-5",
  ...
}
```

## Q23

- **slug**: `sea-sas-cag-2026-04-04-draw`
- **question**: Will US Sassuolo Calcio vs. Cagliari Calcio end in a draw?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.695 (ask 0.705, bid 0.685)
- **other side**: Yes @ mid 0.305
- **volume at close**: $98,520
- **duration**: 330h
- **close date**: 2026-04-04

→ 你的 Decision JSON:
```json
{
  "q_id": 23,
  "slug": "sea-sas-cag-2026-04-04-draw",
  ...
}
```

## Q24

- **slug**: `will-tiktok-be-banned-by-march-31`
- **question**: Will TikTok be banned by March 31?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.996 (ask 0.999, bid 0.986)
- **other side**: Yes @ mid 0.004
- **volume at close**: $26,994
- **duration**: 3515h
- **close date**: 2026-04-01

→ 你的 Decision JSON:
```json
{
  "q_id": 24,
  "slug": "will-tiktok-be-banned-by-march-31",
  ...
}
```

## Q25

- **slug**: `nhl-nsh-lak-2026-04-06-total-6pt5`
- **question**: Predators vs. Kings: O/U 6.5
- **outcomes**: Over / Under
- **favorite at T-72h**: Under @ mid 0.515 (ask 0.525, bid 0.505)
- **other side**: Over @ mid 0.485
- **volume at close**: $16,510
- **duration**: 664h
- **close date**: 2026-04-07

→ 你的 Decision JSON:
```json
{
  "q_id": 25,
  "slug": "nhl-nsh-lak-2026-04-06-total-6pt5",
  ...
}
```

## Q26

- **slug**: `cs2-aur1-mglz-2026-03-27-map-handicap-home-1pt5`
- **question**: Map Handicap: MGLZ (-1.5) vs Aurora Gaming (+1.5)
- **outcomes**: TheMongolz / Aurora Gaming
- **favorite at T-72h**: Aurora Gaming @ mid 0.600 (ask 0.610, bid 0.590)
- **other side**: TheMongolz @ mid 0.400
- **volume at close**: $32,778
- **duration**: 90h
- **close date**: 2026-03-27

→ 你的 Decision JSON:
```json
{
  "q_id": 26,
  "slug": "cs2-aur1-mglz-2026-03-27-map-handicap-home-1pt5",
  ...
}
```

## Q27

- **slug**: `will-kanye-west-have-the-greatest-number-of-monthly-spotify-listeners-this-month-116`
- **question**: Will Kanye West have the greatest number of monthly Spotify listeners this month?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 1.000 (ask 0.999, bid 0.990)
- **other side**: Yes @ mid 0.000
- **volume at close**: $23,790
- **duration**: 788h
- **close date**: 2026-03-31

→ 你的 Decision JSON:
```json
{
  "q_id": 27,
  "slug": "will-kanye-west-have-the-greatest-number-of-monthly-spotify-listeners-this-month-116",
  ...
}
```

## Q28

- **slug**: `fif-civ-sco-2026-03-31-sco`
- **question**: Will Scotland win on 2026-03-31?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.735 (ask 0.745, bid 0.725)
- **other side**: Yes @ mid 0.265
- **volume at close**: $36,808
- **duration**: 657h
- **close date**: 2026-03-31

→ 你的 Decision JSON:
```json
{
  "q_id": 28,
  "slug": "fif-civ-sco-2026-03-31-sco",
  ...
}
```

## Q29

- **slug**: `val-t1-var-2026-04-03`
- **question**: Valorant: T1 vs VARREL (BO3) - VCT Pacific Group Omega
- **outcomes**: T1 / VARREL
- **favorite at T-72h**: T1 @ mid 0.705 (ask 0.715, bid 0.695)
- **other side**: VARREL @ mid 0.295
- **volume at close**: $43,593
- **duration**: 383h
- **close date**: 2026-04-03

→ 你的 Decision JSON:
```json
{
  "q_id": 29,
  "slug": "val-t1-var-2026-04-03",
  ...
}
```

## Q30

- **slug**: `will-the-miami-heat-win-the-nba-eastern-conference-finals`
- **question**: Will the Miami Heat win the NBA Eastern Conference Finals?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.993 (ask 0.999, bid 0.983)
- **other side**: Yes @ mid 0.007
- **volume at close**: $551,267
- **duration**: 6522h
- **close date**: 2026-04-15

→ 你的 Decision JSON:
```json
{
  "q_id": 30,
  "slug": "will-the-miami-heat-win-the-nba-eastern-conference-finals",
  ...
}
```

## Q31

- **slug**: `cricpsl-lah-que-2026-04-17`
- **question**: Pakistan Super League: Lahore Qalandars vs Quetta Gladiators
- **outcomes**: Lahore Qalandars / Quetta Gladiators
- **favorite at T-72h**: Lahore Qalandars @ mid 0.565 (ask 0.575, bid 0.555)
- **other side**: Quetta Gladiators @ mid 0.435
- **volume at close**: $143,922
- **duration**: 172h
- **close date**: 2026-04-17

→ 你的 Decision JSON:
```json
{
  "q_id": 31,
  "slug": "cricpsl-lah-que-2026-04-17",
  ...
}
```

## Q32

- **slug**: `nba-lal-gsw-2026-04-09`
- **question**: Lakers vs. Warriors
- **outcomes**: Lakers / Warriors
- **favorite at T-72h**: Warriors @ mid 0.750 (ask 0.760, bid 0.740)
- **other side**: Lakers @ mid 0.250
- **volume at close**: $4,932,566
- **duration**: 160h
- **close date**: 2026-04-10

→ 你的 Decision JSON:
```json
{
  "q_id": 32,
  "slug": "nba-lal-gsw-2026-04-09",
  ...
}
```

## Q33

- **slug**: `cwbb-tx-ucla-2026-04-03`
- **question**: Texas Longhorns vs. UCLA Bruins (W)
- **outcomes**: Texas Longhorns / UCLA Bruins
- **favorite at T-72h**: Texas Longhorns @ mid 0.545 (ask 0.555, bid 0.535)
- **other side**: UCLA Bruins @ mid 0.455
- **volume at close**: $82,495
- **duration**: 89h
- **close date**: 2026-04-04

→ 你的 Decision JSON:
```json
{
  "q_id": 33,
  "slug": "cwbb-tx-ucla-2026-04-03",
  ...
}
```

## Q34

- **slug**: `crint-nam-sco-2026-04-15`
- **question**: T20 Series Namibia vs Scotland: Namibia vs Scotland
- **outcomes**: Namibia / Scotland
- **favorite at T-72h**: Scotland @ mid 0.859 (ask 0.869, bid 0.849)
- **other side**: Namibia @ mid 0.141
- **volume at close**: $51,368
- **duration**: 169h
- **close date**: 2026-04-15

→ 你的 Decision JSON:
```json
{
  "q_id": 34,
  "slug": "crint-nam-sco-2026-04-15",
  ...
}
```

## Q35

- **slug**: `will-trump-praise-allah-again-by-april-15-423`
- **question**: Will Trump praise Allah again by April 15?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.875 (ask 0.885, bid 0.865)
- **other side**: Yes @ mid 0.125
- **volume at close**: $319,190
- **duration**: 91h
- **close date**: 2026-04-16

→ 你的 Decision JSON:
```json
{
  "q_id": 35,
  "slug": "will-trump-praise-allah-again-by-april-15-423",
  ...
}
```

## Q36

- **slug**: `will-ethereum-dip-to-2000-march-23-29`
- **question**: Will Ethereum dip to $2,000 March 23-29?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.640 (ask 0.650, bid 0.630)
- **other side**: Yes @ mid 0.360
- **volume at close**: $28,681
- **duration**: 105h
- **close date**: 2026-03-27

→ 你的 Decision JSON:
```json
{
  "q_id": 36,
  "slug": "will-ethereum-dip-to-2000-march-23-29",
  ...
}
```

## Q37

- **slug**: `over-60m-committed-to-the-p2p-protocol-public-sale-889-592-482-156`
- **question**: Over $60M committed to the P2P Protocol public sale?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.903 (ask 0.913, bid 0.893)
- **other side**: Yes @ mid 0.097
- **volume at close**: $65,959
- **duration**: 413h
- **close date**: 2026-04-01

→ 你的 Decision JSON:
```json
{
  "q_id": 37,
  "slug": "over-60m-committed-to-the-p2p-protocol-public-sale-889-592-482-156",
  ...
}
```

## Q38

- **slug**: `lol-bce-lds-2026-04-15`
- **question**: LoL: Barcząca Esports vs Lodis (BO3) - Rift Legends Regular Season
- **outcomes**: Barcząca Esports / Lodis
- **favorite at T-72h**: Barcząca Esports @ mid 0.825 (ask 0.835, bid 0.815)
- **other side**: Lodis @ mid 0.175
- **volume at close**: $22,738
- **duration**: 159h
- **close date**: 2026-04-16

→ 你的 Decision JSON:
```json
{
  "q_id": 38,
  "slug": "lol-bce-lds-2026-04-15",
  ...
}
```

## Q39

- **slug**: `nba-phx-okc-2026-04-12`
- **question**: Suns vs. Thunder
- **outcomes**: Suns / Thunder
- **favorite at T-72h**: Thunder @ mid 0.785 (ask 0.795, bid 0.775)
- **other side**: Suns @ mid 0.215
- **volume at close**: $1,201,945
- **duration**: 159h
- **close date**: 2026-04-13

→ 你的 Decision JSON:
```json
{
  "q_id": 39,
  "slug": "nba-phx-okc-2026-04-12",
  ...
}
```

## Q40

- **slug**: `will-bitcoin-reach-80k-march-30-april-5`
- **question**: Will Bitcoin reach $80,000 March 30-April 5?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.998 (ask 0.999, bid 0.988)
- **other side**: Yes @ mid 0.002
- **volume at close**: $194,085
- **duration**: 171h
- **close date**: 2026-04-06

→ 你的 Decision JSON:
```json
{
  "q_id": 40,
  "slug": "will-bitcoin-reach-80k-march-30-april-5",
  ...
}
```

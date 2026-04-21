# Oracle Backtest Workbook

**Task**: 分析以下 100 題。每題只給你 T-72h 前的市場快照和題目，不告訴你結果。你的任務是給出 Decision JSON。

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

## Q41

- **slug**: `will-scottie-scheffler-make-the-cut-at-the-2026-masters`
- **question**: Will Scottie Scheffler make the cut at the 2026 Masters?
- **outcomes**: Yes / No
- **favorite at T-72h**: Yes @ mid 0.880 (ask 0.890, bid 0.870)
- **other side**: No @ mid 0.120
- **volume at close**: $35,050
- **duration**: 94h
- **close date**: 2026-04-11

→ 你的 Decision JSON:
```json
{
  "q_id": 41,
  "slug": "will-scottie-scheffler-make-the-cut-at-the-2026-masters",
  ...
}
```

## Q42

- **slug**: `will-the-calgary-flames-win-the-2026-nhl-stanley-cup`
- **question**: Will the Calgary Flames win the 2026 NHL Stanley Cup?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 1.000 (ask 0.999, bid 0.990)
- **other side**: Yes @ mid 0.000
- **volume at close**: $1,182,097
- **duration**: 6929h
- **close date**: 2026-04-08

→ 你的 Decision JSON:
```json
{
  "q_id": 42,
  "slug": "will-the-calgary-flames-win-the-2026-nhl-stanley-cup",
  ...
}
```

## Q43

- **slug**: `nhl-cbj-mon-2026-04-11`
- **question**: Blue Jackets vs. Canadiens
- **outcomes**: Blue Jackets / Canadiens
- **favorite at T-72h**: Canadiens @ mid 0.535 (ask 0.545, bid 0.525)
- **other side**: Blue Jackets @ mid 0.465
- **volume at close**: $513,193
- **duration**: 660h
- **close date**: 2026-04-12

→ 你的 Decision JSON:
```json
{
  "q_id": 43,
  "slug": "nhl-cbj-mon-2026-04-11",
  ...
}
```

## Q44

- **slug**: `will-crude-oil-cl-settle-at-70-75-in-march-528`
- **question**: Will Crude Oil (CL) settle at $70-$75 in March?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.996 (ask 0.999, bid 0.986)
- **other side**: Yes @ mid 0.004
- **volume at close**: $80,068
- **duration**: 679h
- **close date**: 2026-04-01

→ 你的 Decision JSON:
```json
{
  "q_id": 44,
  "slug": "will-crude-oil-cl-settle-at-70-75-in-march-528",
  ...
}
```

## Q45

- **slug**: `bra2-csc-nau-2026-04-11-csc`
- **question**: Will Ceará SC win on 2026-04-11?
- **outcomes**: Yes / No
- **favorite at T-72h**: Yes @ mid 0.515 (ask 0.525, bid 0.505)
- **other side**: No @ mid 0.485
- **volume at close**: $12,462
- **duration**: 657h
- **close date**: 2026-04-12

→ 你的 Decision JSON:
```json
{
  "q_id": 45,
  "slug": "bra2-csc-nau-2026-04-11-csc",
  ...
}
```

## Q46

- **slug**: `will-trove-refund-ico-participants-412`
- **question**: Will Trove refund ICO participants?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.992 (ask 0.999, bid 0.982)
- **other side**: Yes @ mid 0.008
- **volume at close**: $24,819
- **duration**: 1695h
- **close date**: 2026-04-01

→ 你的 Decision JSON:
```json
{
  "q_id": 46,
  "slug": "will-trove-refund-ico-participants-412",
  ...
}
```

## Q47

- **slug**: `will-patrick-reed-win-the-2026-masters-tournament`
- **question**: Will Patrick Reed win the 2026 Masters tournament?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.951 (ask 0.961, bid 0.941)
- **other side**: Yes @ mid 0.049
- **volume at close**: $1,397,383
- **duration**: 5445h
- **close date**: 2026-04-13

→ 你的 Decision JSON:
```json
{
  "q_id": 47,
  "slug": "will-patrick-reed-win-the-2026-masters-tournament",
  ...
}
```

## Q48

- **slug**: `bkkbl-seo2-son-2026-03-29`
- **question**: Seoul Thunders vs. Sonic Boom
- **outcomes**: Seoul Thunders / Sonic Boom
- **favorite at T-72h**: Seoul Thunders @ mid 0.505 (ask 0.515, bid 0.495)
- **other side**: Sonic Boom @ mid 0.495
- **volume at close**: $35,828
- **duration**: 79h
- **close date**: 2026-03-29

→ 你的 Decision JSON:
```json
{
  "q_id": 48,
  "slug": "bkkbl-seo2-son-2026-03-29",
  ...
}
```

## Q49

- **slug**: `will-bitcoin-dip-to-58k-march-30-april-5`
- **question**: Will Bitcoin dip to $58,000 March 30-April 5?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.978 (ask 0.988, bid 0.968)
- **other side**: Yes @ mid 0.022
- **volume at close**: $306,808
- **duration**: 171h
- **close date**: 2026-04-06

→ 你的 Decision JSON:
```json
{
  "q_id": 49,
  "slug": "will-bitcoin-dip-to-58k-march-30-april-5",
  ...
}
```

## Q50

- **slug**: `will-trump-say-n-word-in-march`
- **question**: Will Trump say "N Word" in March?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.989 (ask 0.999, bid 0.979)
- **other side**: Yes @ mid 0.011
- **volume at close**: $58,292
- **duration**: 799h
- **close date**: 2026-04-01

→ 你的 Decision JSON:
```json
{
  "q_id": 50,
  "slug": "will-trump-say-n-word-in-march",
  ...
}
```

## Q51

- **slug**: `2026-masters-tournament-top20-cameron-smith`
- **question**: Will Cameron Smith finish in the Top 20 at the 2026 Augusta National Invitational?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.695 (ask 0.705, bid 0.685)
- **other side**: Yes @ mid 0.305
- **volume at close**: $13,253
- **duration**: 105h
- **close date**: 2026-04-11

→ 你的 Decision JSON:
```json
{
  "q_id": 51,
  "slug": "2026-masters-tournament-top20-cameron-smith",
  ...
}
```

## Q52

- **slug**: `val-100t1-eg2-2026-04-11`
- **question**: Valorant: 100 Thieves vs Evil Geniuses (BO3) - VCT Americas Stage 1 Group Omega
- **outcomes**: 100 Thieves / Evil Geniuses
- **favorite at T-72h**: 100 Thieves @ mid 0.680 (ask 0.690, bid 0.670)
- **other side**: Evil Geniuses @ mid 0.320
- **volume at close**: $144,336
- **duration**: 452h
- **close date**: 2026-04-12

→ 你的 Decision JSON:
```json
{
  "q_id": 52,
  "slug": "val-100t1-eg2-2026-04-11",
  ...
}
```

## Q53

- **slug**: `will-starmer-say-united-states-during-the-next-prime-ministers-questions-event`
- **question**: Will Starmer say "United States" during the next Prime Minister's Questions event?
- **outcomes**: Yes / No
- **favorite at T-72h**: Yes @ mid 0.590 (ask 0.600, bid 0.580)
- **other side**: No @ mid 0.410
- **volume at close**: $19,860
- **duration**: 475h
- **close date**: 2026-04-15

→ 你的 Decision JSON:
```json
{
  "q_id": 53,
  "slug": "will-starmer-say-united-states-during-the-next-prime-ministers-questions-event",
  ...
}
```

## Q54

- **slug**: `uef-bih-ita-2026-03-31-btts`
- **question**: Bosnia and Herzegovina vs. Italy: Both Teams to Score
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.565 (ask 0.575, bid 0.555)
- **other side**: Yes @ mid 0.435
- **volume at close**: $43,466
- **duration**: 99h
- **close date**: 2026-03-31

→ 你的 Decision JSON:
```json
{
  "q_id": 54,
  "slug": "uef-bih-ita-2026-03-31-btts",
  ...
}
```

## Q55

- **slug**: `meta-above-560-on-march-31-2026`
- **question**: Will Meta (META) close above $560 end of March?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.755 (ask 0.765, bid 0.745)
- **other side**: Yes @ mid 0.245
- **volume at close**: $25,494
- **duration**: 767h
- **close date**: 2026-03-31

→ 你的 Decision JSON:
```json
{
  "q_id": 55,
  "slug": "meta-above-560-on-march-31-2026",
  ...
}
```

## Q56

- **slug**: `nba-tor-nyk-2026-04-10`
- **question**: Raptors vs. Knicks
- **outcomes**: Raptors / Knicks
- **favorite at T-72h**: Knicks @ mid 0.705 (ask 0.715, bid 0.695)
- **other side**: Raptors @ mid 0.295
- **volume at close**: $1,807,114
- **duration**: 158h
- **close date**: 2026-04-11

→ 你的 Decision JSON:
```json
{
  "q_id": 56,
  "slug": "nba-tor-nyk-2026-04-10",
  ...
}
```

## Q57

- **slug**: `will-nflx-reach-455-in-march`
- **question**: Will Netflix reach $455 in March?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 1.000 (ask 0.999, bid 0.990)
- **other side**: Yes @ mid 0.000
- **volume at close**: $53,680
- **duration**: 833h
- **close date**: 2026-03-31

→ 你的 Decision JSON:
```json
{
  "q_id": 57,
  "slug": "will-nflx-reach-455-in-march",
  ...
}
```

## Q58

- **slug**: `mlb-oak-tor-2026-03-27-spread-home-1pt5`
- **question**: Spread: Toronto Blue Jays (-1.5)
- **outcomes**: Toronto Blue Jays / Athletics
- **favorite at T-72h**: Athletics @ mid 0.660 (ask 0.670, bid 0.650)
- **other side**: Toronto Blue Jays @ mid 0.340
- **volume at close**: $79,042
- **duration**: 75h
- **close date**: 2026-03-28

→ 你的 Decision JSON:
```json
{
  "q_id": 58,
  "slug": "mlb-oak-tor-2026-03-27-spread-home-1pt5",
  ...
}
```

## Q59

- **slug**: `minneapolis-border-patrol-shooter-firedresigns-by-march-31`
- **question**: Minneapolis Border Patrol Shooter fired/resigns by March 31?
- **outcomes**: Yes / No
- **favorite at T-72h**: No @ mid 0.989 (ask 0.999, bid 0.979)
- **other side**: Yes @ mid 0.011
- **volume at close**: $83,487
- **duration**: 1553h
- **close date**: 2026-04-01

→ 你的 Decision JSON:
```json
{
  "q_id": 59,
  "slug": "minneapolis-border-patrol-shooter-firedresigns-by-march-31",
  ...
}
```

## Q60

- **slug**: `fif-egy-esp-2026-03-30-total-1pt5`
- **question**: Egypt vs. Spain: O/U 1.5
- **outcomes**: Over / Under
- **favorite at T-72h**: Over @ mid 0.835 (ask 0.845, bid 0.825)
- **other side**: Under @ mid 0.165
- **volume at close**: $29,019
- **duration**: 676h
- **close date**: 2026-04-01

→ 你的 Decision JSON:
```json
{
  "q_id": 60,
  "slug": "fif-egy-esp-2026-03-30-total-1pt5",
  ...
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

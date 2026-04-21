# Oracle Backtest Workbook — Batch 3

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

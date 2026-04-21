# Candidate Analysis: gd-quarterly-earnings-gaap-eps-04-22-2026-3pt67

**Question**: Will General Dynamics (GD) beat quarterly earnings?

**Category detected**: `earnings`
**Hours to resolution**: 92.7h  (end: 2026-04-22T13:00:00Z)
**Volume**: $5,621   Liquidity: $3,722
**Outcomes**: ['Yes', 'No']
**Best bid/ask**: 0.88 / 0.89   Mid: 0.885
**Favorite**: Yes @ 0.885
**Resolution source**: https://seekingalpha.com/

## Layer 1: 量化 Edge
- Matched strategy: **Fav 0.88-0.96, vol $5-10k, ~3d out**
- Expected edge: **+3.60%** per bet
- Est. win rate: **97%**
- Favorite side: **Yes** @ ask **0.89**


## Layer 2: 主觀分析框架（Claude 填寫）

回答以下 4 題：

1. **這個市場在問什麼？有沒有模糊空間？**
   （仔細讀 question + description，找可能爭議點）

2. **目前價格 0.885 合理嗎？你估的真實機率是多少？**
   （用 p_claude 表示，例如 p_claude = 0.88）

3. **價差 |p_market - p_claude| 方向是否支持「買熱門」？**
   - 如果 p_claude > p_market → 市場低估熱門方 → 量化策略相符 ✓
   - 如果 p_claude < p_market → 市場高估熱門方 → **不買（與量化策略衝突）**
   - 如果 p_claude ≈ p_market → 無資訊 edge，但量化仍有結構性 edge → 可進但倉位減半

4. **有沒有已知黑天鵝風險？**
   - UMA 結算爭議歷史
   - 事件被推遲、取消、重新定義
   - 主觀題（「算不算」「多久算」）

## Layer 3: 客觀資料 Checklist

根據類別 `earnings`，應該要拉：
- [ ] Analyst consensus (Yahoo Finance, Seeking Alpha)
- [ ] Recent company news / pre-announcements
- [ ] Last 4 quarters: how often did they beat?
- [ ] Options-implied move

## 決策框架

| 量化 | 主觀 | 客觀 | 決策 |
|---|---|---|---|
| ✓ | p_claude > p_market | 無反向訊號 | **下單** |
| ✓ | p_claude ≈ p_market | 無反向訊號 | **下單（半倉）** |
| ✓ | p_claude < p_market | 任何 | **跳過** |
| ✓ | 任何 | 有反向訊號 | **跳過** |

## 最終決策

- [ ] 下單
- [ ] 跳過
- [ ] 待更多資料

**倉位**: $_____
**進場價**: _____
**預期持有時長**: _____
**退出條件**: （通常是持有至結算）
**備註**:

# Oracle Analysis Task

你是一個 Polymarket 資訊優勢 (informational edge) 分析師。你的任務不是做統計 edge，而是找到 **Claude 獨有的資訊整合優勢**。

## Market Facts

- **Question**: Toronto Blue Jays vs. Los Angeles Angels
- **Slug**: `mlb-tor-laa-2026-04-20`
- **Category auto-detected**: `sports` (信不信由你自己判斷)
- **Outcomes**: `Toronto Blue Jays` / `Los Angeles Angels`
- **Current mid price**: 1.000  (ask 1.000, bid 0.999)
- **Spread**: 0.001
- **Volume**: $778,080
- **Liquidity (CLOB)**: $745,333
- **Hours to close**: 163.2
- **Resolution source**: https://www.mlb.com/
- **End date**: 2026-04-28T01:38:00Z
- **Favorite side**: Toronto Blue Jays @ 1.000

## 執行步驟

### Step 1: 理解題目（不可跳過）
1. 閱讀 question + resolution source URL 的結算準則（用 WebFetch）
2. 找出可能的**模糊點**：有哪些邊界 case 可能引發 UMA 爭議？
3. 如果題目有 2+ 個合理詮釋，直接 **SKIP**

### Step 2: 客觀資料蒐集（category = `sports`）
   - ESPN / team beat writer for starting lineup + injuries
   - Recent form (last 10 games) for both teams
   - Head-to-head this season
   - DraftKings/FanDuel moneyline (convert to vig-free implied prob)
   - Home/away, rest days, back-to-back

用 WebSearch 和 WebFetch 實際抓。不要用模型記憶臆測。

### Step 3: 估計 p_claude
- 根據 Step 2 的資料，估你對 YES 發生的真實機率 `p_claude`
- 務必**誠實**：如果你的資訊和市場共識沒有差距，就 SKIP
- 如果估的機率信心區間超過 20 個百分點（例如 30%-60%），代表你不知道 → SKIP

### Step 4: 計算 edge
- `p_market` = YES 邊的 ask 價（你若買 YES 必須吃 ask）= 1.000
- YES 邊 edge (bps) = (p_claude - 1.000) × 10000
- NO 邊 edge (bps) = ((1-p_claude) - 0.001) × 10000  (買 NO 吃 (1-bid))

### Step 5: 決策規則
- **|edge| < 500 bps (5%)** → SKIP（資訊優勢不夠）
- **edge 500-1000 bps** → 小倉（bankroll × Kelly × 0.25, cap 2%）
- **edge 1000-2000 bps** → 中倉（Kelly × 0.5, cap 3%）
- **edge > 2000 bps** → 大倉但要再檢查「我是不是漏了什麼才覺得這麼便宜」（Kelly × 0.5, cap 5%）
- 信心 < 3/5 → SKIP
- 題目有 UMA 爭議先例 → SKIP

### Step 6: 黑天鵝自檢
- 如果結算源（URL）今明兩天可能 downtime 或被改動 → SKIP
- 如果事件本身可能被推遲/取消/void → 用信心打折
- 如果你的論點依賴「市場笨」→ 警戒（通常市場不笨）

## 輸出格式（**嚴格 JSON**）

```json
{
  "slug": "mlb-tor-laa-2026-04-20",
  "decision": "BUY YES" | "BUY NO" | "SKIP",
  "p_claude": 0.000,
  "p_market_yes": 1.000,
  "edge_bps": 0,
  "confidence": 1-5,
  "kelly_fraction": 0.00,
  "position_pct_of_bankroll": 0.00,
  "reasoning": "一段簡短論述",
  "key_facts": ["資料 1", "資料 2", "資料 3"],
  "skip_reasons": ["若 SKIP，填這裡"],
  "black_swan_notes": "已知風險"
}
```

在 JSON 之後可附 1 段中文白話補充。

## 重要警告

- **不要**只憑訓練資料記憶回答。**必須** WebSearch/WebFetch 實際查當前資料。
- **不要**因為用戶希望看到交易信號就降低 confidence 門檻。
- **SKIP 是正確答案的大多數時候**。10 個候選裡 SKIP 7 個是健康的。
- 你的目標不是「找到交易」，是「找到真 edge」。

"""Oracle Analyzer — Layer 2+3 via structured subagent dispatch.

Usage:
  python oracle_analyze.py --top 6
    → pick top 6 candidates by rank_score, generate analysis briefs
  python oracle_analyze.py --slug <slug>
    → analyze one specific candidate

Each brief is a *self-contained* research prompt that a Claude subagent can execute
and return a structured JSON decision.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

CANDIDATES = Path("data/results/oracle_candidates.csv")
BRIEFS = Path("data/oracle_briefs")
BRIEFS.mkdir(parents=True, exist_ok=True)


DATA_CHECKLIST = {
    "sports": [
        "ESPN / team beat writer for starting lineup + injuries",
        "Recent form (last 10 games) for both teams",
        "Head-to-head this season",
        "DraftKings/FanDuel moneyline (convert to vig-free implied prob)",
        "Home/away, rest days, back-to-back",
    ],
    "crypto": [
        "Spot price on Binance/Coinbase right now",
        "Distance to target price (as % and sigma of 30d realized vol)",
        "Funding rate on Binance/Bybit perps",
        "Open interest trend last 7 days",
        "Upcoming macro (FOMC, CPI, ETF flows)",
    ],
    "earnings": [
        "Analyst consensus (Yahoo Finance / Refinitiv)",
        "Options-implied move",
        "Last 4 quarters beat/miss record",
        "Recent company news, pre-announcements, guidance",
    ],
    "politics_macro": [
        "Polling aggregator (538, RCP, Polymarket-tracker)",
        "News last 7 days on major candidates",
        "Official statements from relevant body (Fed, CBR, etc)",
        "Base-rate from similar historical events",
    ],
    "behavior": [
        "Subject's historical baseline frequency",
        "Current schedule / trigger events this period",
        "Pattern from past similar markets (check xtracker)",
        "UMA resolver reliability for this type of market",
    ],
    "weather": [
        "Historical avg high temp this date",
        "7-day forecast from accuweather / weather.com",
        "Current trend (warmer/colder than normal?)",
        "Resolution source URL — which weather station?",
    ],
    "entertainment": [
        "Boxoffice mojo pre-sale trend",
        "Opening screen count",
        "Similar film openings (base rate)",
        "Reviews sentiment",
    ],
    "other": [
        "Resolution source URL — click through and understand criteria",
        "Baseline probability of similar events",
        "News last 7 days containing key terms from the question",
    ],
}


def load_candidates() -> pd.DataFrame:
    if not CANDIDATES.exists():
        raise SystemExit("Run oracle_scanner.py first")
    return pd.read_csv(CANDIDATES)


def build_brief(row: dict) -> str:
    cat = row["category"]
    checks = DATA_CHECKLIST.get(cat, DATA_CHECKLIST["other"])
    checks_md = "\n".join(f"   - {c}" for c in checks)

    mid = row["mid"]
    ask = row["best_ask"]
    bid = row["best_bid"]
    outcomes = [row["yes_outcome"], row["no_outcome"]]

    # determine favorite side for reference
    if mid >= 0.5:
        fav_side = outcomes[0]
        fav_price = mid
    else:
        fav_side = outcomes[1]
        fav_price = 1 - mid

    prompt = f"""# Oracle Analysis Task

你是一個 Polymarket 資訊優勢 (informational edge) 分析師。你的任務不是做統計 edge，而是找到 **Claude 獨有的資訊整合優勢**。

## Market Facts

- **Question**: {row['question']}
- **Slug**: `{row['slug']}`
- **Category auto-detected**: `{cat}` (信不信由你自己判斷)
- **Outcomes**: `{outcomes[0]}` / `{outcomes[1]}`
- **Current mid price**: {mid:.3f}  (ask {ask:.3f}, bid {bid:.3f})
- **Spread**: {row['spread']:.3f}
- **Volume**: ${row['volume']:,}
- **Liquidity (CLOB)**: ${row['liquidity_clob']:,}
- **Hours to close**: {row['hours_to_close']}
- **Resolution source**: {row['resolution_source']}
- **End date**: {row['end_date']}
- **Favorite side**: {fav_side} @ {fav_price:.3f}

## 執行步驟

### Step 1: 理解題目（不可跳過）
1. 閱讀 question + resolution source URL 的結算準則（用 WebFetch）
2. 找出可能的**模糊點**：有哪些邊界 case 可能引發 UMA 爭議？
3. 如果題目有 2+ 個合理詮釋，直接 **SKIP**

### Step 2: 客觀資料蒐集（category = `{cat}`）
{checks_md}

用 WebSearch 和 WebFetch 實際抓。不要用模型記憶臆測。

### Step 3: 估計 p_claude
- 根據 Step 2 的資料，估你對 YES 發生的真實機率 `p_claude`
- 務必**誠實**：如果你的資訊和市場共識沒有差距，就 SKIP
- 如果估的機率信心區間超過 20 個百分點（例如 30%-60%），代表你不知道 → SKIP

### Step 4: 計算 edge
- `p_market` = YES 邊的 ask 價（你若買 YES 必須吃 ask）= {ask:.3f}
- YES 邊 edge (bps) = (p_claude - {ask:.3f}) × 10000
- NO 邊 edge (bps) = ((1-p_claude) - {1-bid:.3f}) × 10000  (買 NO 吃 (1-bid))

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
{{
  "slug": "{row['slug']}",
  "decision": "BUY YES" | "BUY NO" | "SKIP",
  "p_claude": 0.000,
  "p_market_yes": {ask:.3f},
  "edge_bps": 0,
  "confidence": 1-5,
  "kelly_fraction": 0.00,
  "position_pct_of_bankroll": 0.00,
  "reasoning": "一段簡短論述",
  "key_facts": ["資料 1", "資料 2", "資料 3"],
  "skip_reasons": ["若 SKIP，填這裡"],
  "black_swan_notes": "已知風險"
}}
```

在 JSON 之後可附 1 段中文白話補充。

## 重要警告

- **不要**只憑訓練資料記憶回答。**必須** WebSearch/WebFetch 實際查當前資料。
- **不要**因為用戶希望看到交易信號就降低 confidence 門檻。
- **SKIP 是正確答案的大多數時候**。10 個候選裡 SKIP 7 個是健康的。
- 你的目標不是「找到交易」，是「找到真 edge」。
"""
    return prompt


def write_brief(row: dict) -> Path:
    brief = build_brief(row)
    slug = row["slug"]
    path = BRIEFS / f"{slug}.md"
    path.write_text(brief, encoding="utf-8")
    return path


def pick_top(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """Stratified top-N across categories (ensure diversity)."""
    df = df.copy()
    if "rank_score" not in df.columns:
        df["rank_score"] = df["clarity"] * 2 + (df["volume"] / 50_000).clip(upper=5)
    out = []
    cats = df["category"].unique()
    per_cat = max(1, n // len(cats)) + 1
    for cat in cats:
        out.append(df[df["category"] == cat].nlargest(per_cat, "rank_score"))
    combined = pd.concat(out).sort_values("rank_score", ascending=False).head(n)
    return combined


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--slug", type=str)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    df = load_candidates()
    if args.slug:
        sub = df[df["slug"] == args.slug]
        if sub.empty:
            raise SystemExit(f"slug not found: {args.slug}")
        rows = sub.to_dict("records")
    elif args.all:
        rows = df.to_dict("records")
    else:
        rows = pick_top(df, args.top).to_dict("records")

    print(f"Generating {len(rows)} briefs...")
    for r in rows:
        p = write_brief(r)
        print(f"  {p}  (cat={r['category']}, clarity={r['clarity']}, vol=${r['volume']:,})")

    print(f"\nBriefs saved to {BRIEFS}/")
    print(f"\nNext step:")
    print(f"  Dispatch each brief to a subagent (parallel).")
    print(f"  Agent returns structured JSON → append to data/oracle_decisions.jsonl")


if __name__ == "__main__":
    main()

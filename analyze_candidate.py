"""Layer 2+3 candidate analyzer.

Usage:
  python analyze_candidate.py --slug <market-slug>
  python analyze_candidate.py --all   # analyze all rows in live_candidates.csv

For each candidate:
  - Pulls Gamma API metadata (question, description, end date, current prices)
  - Categorizes the event type (sports, crypto, earnings, politics, other)
  - Generates a structured analysis brief for Claude to review
  - Saves brief to data/briefs/<slug>.md so you can review before trading
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

GAMMA = "https://gamma-api.polymarket.com/markets"
BRIEFS = Path("data/briefs")
BRIEFS.mkdir(exist_ok=True, parents=True)


def fetch_market_by_slug(slug: str) -> dict | None:
    r = requests.get(GAMMA, params={"slug": slug, "limit": 1}, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data:
        return None
    return data[0] if isinstance(data, list) else None


def categorize(m: dict) -> tuple[str, list[str]]:
    """Classify the event and suggest what objective data to pull."""
    q = (m.get("question") or "").lower()
    slug = (m.get("slug") or "").lower()
    desc = (m.get("description") or "").lower()
    blob = f"{q} {slug} {desc}"

    if any(k in blob for k in ["mlb", "nba", "nfl", "nhl", "soccer", "spread",
                                "atp", "wta", "cbb", "epl", "ucl", "lol", "ufc"]):
        return "sports", [
            "Check starting lineup / injuries (ESPN, team beat writer)",
            "Recent team form (last 10 games)",
            "Head-to-head history",
            "Pinnacle / Betfair odds for cross-market sanity check",
        ]
    if any(k in blob for k in ["bitcoin", "btc", "ethereum", "eth", "solana",
                                "crypto", "price of", "updown"]):
        return "crypto", [
            "Current spot price on Binance / Coinbase",
            "Distance to target price (%)",
            "Recent volatility (ATR, 30d realized vol)",
            "Open interest + funding rate (bybit / binance)",
        ]
    if any(k in blob for k in ["earnings", "eps", "beat", "q1", "q2", "q3", "q4",
                                "revenue", "miss", "guidance"]):
        return "earnings", [
            "Analyst consensus (Yahoo Finance, Seeking Alpha)",
            "Recent company news / pre-announcements",
            "Last 4 quarters: how often did they beat?",
            "Options-implied move",
        ]
    if any(k in blob for k in ["president", "election", "vote", "poll", "congress",
                                "senate", "minister", "parliament"]):
        return "politics", [
            "Latest poll aggregators (538, RCP, Polymarket-tracker)",
            "News in last 7 days on major candidates",
            "Historical resolution rate of similar question",
            "Confirm UMA resolution source is reliable",
        ]
    if any(k in blob for k in ["trump", "musk", "tweet", "post", "insult"]):
        return "behavior", [
            "Baseline frequency: how often historically?",
            "Current schedule / events that day",
            "Previous similar resolutions (pattern)",
            "Who is the UMA resolver, any ambiguity?",
        ]
    return "other", [
        "Read resolution source URL carefully",
        "Check for ambiguity in resolution criteria",
        "Search Twitter / news for event mentions in last 48h",
    ]


def build_brief(m: dict, strategy_row: dict | None = None) -> str:
    slug = m.get("slug")
    try:
        outcomes = json.loads(m.get("outcomes") or "[]")
    except Exception:
        outcomes = []

    best_ask = m.get("bestAsk")
    best_bid = m.get("bestBid")
    try:
        ask = float(best_ask); bid = float(best_bid)
    except Exception:
        ask = bid = None
    mid = (ask + bid) / 2 if (ask and bid) else None

    end_date = m.get("endDate", "")
    try:
        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        h_to_close = (end_dt - datetime.now(timezone.utc)).total_seconds() / 3600
    except Exception:
        h_to_close = None

    cat, data_sources = categorize(m)

    strat_block = ""
    if strategy_row:
        strat_block = f"""
## Layer 1: 量化 Edge
- Matched strategy: **{strategy_row.get('strategy_label', 'N/A')}**
- Expected edge: **+{strategy_row.get('expected_edge', 0)*100:.2f}%** per bet
- Est. win rate: **{strategy_row.get('est_win_rate', 0)*100:.0f}%**
- Favorite side: **{strategy_row.get('fav_side')}** @ ask **{strategy_row.get('fav_ask')}**
"""

    fav_display = "?" if mid is None else (outcomes[0] if mid >= 0.5 else outcomes[1] if len(outcomes) == 2 else "?")
    fav_price = "?" if mid is None else (mid if mid >= 0.5 else 1 - mid)

    return f"""# Candidate Analysis: {slug}

**Question**: {m.get('question')}

**Category detected**: `{cat}`
**Hours to resolution**: {h_to_close:.1f}h  (end: {end_date})
**Volume**: ${float(m.get('volumeNum') or 0):,.0f}   Liquidity: ${float(m.get('liquidityClob') or 0):,.0f}
**Outcomes**: {outcomes}
**Best bid/ask**: {bid} / {ask}   Mid: {mid}
**Favorite**: {fav_display} @ {fav_price if isinstance(fav_price, str) else f'{fav_price:.3f}'}
**Resolution source**: {m.get('resolutionSource', 'N/A')}
{strat_block}

## Layer 2: 主觀分析框架（Claude 填寫）

回答以下 4 題：

1. **這個市場在問什麼？有沒有模糊空間？**
   （仔細讀 question + description，找可能爭議點）

2. **目前價格 {mid} 合理嗎？你估的真實機率是多少？**
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

根據類別 `{cat}`，應該要拉：
""" + "\n".join(f"- [ ] {d}" for d in data_sources) + """

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
"""


def analyze_one(slug: str, strategy_row: dict | None = None) -> Path:
    m = fetch_market_by_slug(slug)
    if not m:
        raise SystemExit(f"Market not found: {slug}")
    brief = build_brief(m, strategy_row)
    path = BRIEFS / f"{slug}.md"
    path.write_text(brief, encoding="utf-8")
    return path


def analyze_all():
    csv = Path("data/results/live_candidates.csv")
    if not csv.exists():
        raise SystemExit("Run live_scanner.py first")
    df = pd.read_csv(csv)
    paths = []
    for _, row in df.iterrows():
        try:
            p = analyze_one(row["slug"], row.to_dict())
            paths.append(p)
            print(f"  brief: {p}")
        except Exception as e:
            print(f"  FAIL {row['slug']}: {e}")
    print(f"\nGenerated {len(paths)} briefs in {BRIEFS}/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    if args.all:
        analyze_all()
    elif args.slug:
        p = analyze_one(args.slug)
        print(f"brief: {p}")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()

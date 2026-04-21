"""Oracle Scanner — Layer 1 of the Claude-as-Oracle pipeline.

不再做 FLB 量化 profile 匹配。改成挑「Claude 能深度分析」的事件：
  - 有明確結算源 URL（避開模糊主觀題）
  - 非 bucket-spam（同事件子市場 < 3）
  - 2-14 天到期（夠時間研究、不會過遠）
  - volume >= $10k（有足夠流動性進出）
  - orderbook spread < 4%
  - 支援的類別：crypto、earnings、politics、sports、behavior、other
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

import pandas as pd
import requests

GAMMA = "https://gamma-api.polymarket.com/markets"
OUT = Path("data/results/oracle_candidates.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

# filters
MIN_VOLUME = 10_000
MAX_SPREAD = 0.04
MIN_HOURS_TO_CLOSE = 48       # 2 days research time
MAX_HOURS_TO_CLOSE = 14 * 24  # 14 days
MIN_LIQUIDITY = 1_000
MAX_SUB_MARKETS_PER_EVENT = 3  # skip bucket-spam


def fetch_open_markets(limit_pages: int = 15) -> list[dict]:
    out = []
    for offset in range(0, limit_pages * 500, 500):
        try:
            r = requests.get(GAMMA, params={
                "closed": "false", "active": "true",
                "limit": 500, "offset": offset,
                "volume_num_min": MIN_VOLUME,
                "order": "volume", "ascending": "false",
            }, timeout=30)
            data = r.json()
            if not isinstance(data, list) or not data:
                break
            out.extend(data)
            time.sleep(0.2)
        except Exception as e:
            print(f"  fetch err @ offset {offset}: {e}")
            break
    return out


def categorize(m: dict) -> str:
    q = (m.get("question") or "").lower()
    slug = (m.get("slug") or "").lower()
    blob = f"{q} {slug}"
    if any(k in blob for k in ["mlb", "nba", "nfl", "nhl", "atp", "wta",
                                "cbb", "epl", "ucl", "uel", "lol", "ufc",
                                "soccer", "bundesliga"]):
        return "sports"
    if any(k in blob for k in ["bitcoin", "btc", "ethereum", "eth", "solana",
                                "crypto", "-updown-", "price of"]):
        return "crypto"
    if any(k in blob for k in ["earnings", "eps", "beat", "q1", "q2", "q3", "q4",
                                "revenue"]):
        return "earnings"
    if any(k in blob for k in ["president", "election", "vote", "poll", "congress",
                                "senate", "minister", "parliament", "rate", "fed",
                                "fomc", "cpi"]):
        return "politics_macro"
    if any(k in blob for k in ["tweet", "post", "insult", "musk", "trump-"]):
        return "behavior"
    if any(k in blob for k in ["highest-temp", "weather", "snowfall"]):
        return "weather"
    if any(k in blob for k in ["oscar", "grammy", "box-office", "movie"]):
        return "entertainment"
    return "other"


def clarity_score(m: dict) -> tuple[int, list[str]]:
    """0-5 integer: higher = clearer resolution criteria.
    Returns (score, reasons)."""
    score = 0
    reasons = []

    res_source = m.get("resolutionSource") or ""
    if res_source and res_source.startswith("http"):
        score += 2
        reasons.append("has resolution URL")

    desc = m.get("description") or ""
    if len(desc) > 50:
        score += 1
        reasons.append("has description")

    if "official" in desc.lower() or "confirmed" in desc.lower():
        score += 1
        reasons.append("uses 'official'")

    # penalize vague questions
    q = (m.get("question") or "").lower()
    if any(k in q for k in ["publicly insult", "mention", "reference",
                             "considered", "be seen as"]):
        score -= 2
        reasons.append("VAGUE keyword (-2)")

    # neg-risk markets usually have cleaner resolution
    if m.get("negRisk"):
        score += 1
        reasons.append("negRisk format")

    return max(0, min(5, score)), reasons


def process_markets(raw: list[dict]) -> pd.DataFrame:
    """Filter, enrich, return candidates."""
    # First pass: group by event_id to detect bucket-spam
    event_counts = defaultdict(int)
    for m in raw:
        events = m.get("events") or []
        if events:
            eid = events[0].get("id")
            if eid:
                event_counts[eid] += 1

    candidates = []
    now = datetime.now(timezone.utc)

    for m in raw:
        try:
            outcomes = json.loads(m.get("outcomes") or "[]")
            tokens = json.loads(m.get("clobTokenIds") or "[]")
        except Exception:
            continue
        if len(outcomes) != 2 or len(tokens) != 2:
            continue

        volume = float(m.get("volumeNum") or 0)
        if volume < MIN_VOLUME:
            continue

        liquidity = float(m.get("liquidityClob") or 0)
        if liquidity < MIN_LIQUIDITY:
            continue

        end_date = m.get("endDate")
        if not end_date:
            continue
        try:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except Exception:
            continue
        h_to_close = (end_dt - now).total_seconds() / 3600
        if not (MIN_HOURS_TO_CLOSE <= h_to_close <= MAX_HOURS_TO_CLOSE):
            continue

        # spread check
        try:
            ask = float(m.get("bestAsk") or 0)
            bid = float(m.get("bestBid") or 0)
        except Exception:
            continue
        if ask <= 0 or bid <= 0 or ask <= bid:
            continue
        spread = ask - bid
        if spread > MAX_SPREAD:
            continue
        mid = (ask + bid) / 2

        # bucket-spam check
        events = m.get("events") or []
        eid = events[0].get("id") if events else None
        sub_count = event_counts.get(eid, 0) if eid else 0
        if sub_count > MAX_SUB_MARKETS_PER_EVENT:
            continue

        cat = categorize(m)
        clarity, clarity_reasons = clarity_score(m)
        if clarity < 2:  # too vague
            continue

        candidates.append({
            "slug": m.get("slug"),
            "question": (m.get("question") or "")[:120],
            "category": cat,
            "clarity": clarity,
            "clarity_reasons": "; ".join(clarity_reasons),
            "mid": round(mid, 4),
            "best_ask": ask,
            "best_bid": bid,
            "spread": round(spread, 4),
            "volume": round(volume),
            "liquidity_clob": round(liquidity),
            "hours_to_close": round(h_to_close, 1),
            "event_sub_count": sub_count,
            "resolution_source": m.get("resolutionSource") or "",
            "end_date": end_date,
            "market_id": m.get("id"),
            "condition_id": m.get("conditionId"),
            "yes_token": tokens[0],
            "no_token": tokens[1],
            "yes_outcome": outcomes[0],
            "no_outcome": outcomes[1],
        })

    return pd.DataFrame(candidates)


def main():
    print("Oracle Scanner v2 — analyzable event hunter")
    print(f"  vol >= ${MIN_VOLUME}, spread <= {MAX_SPREAD}, "
          f"close in {MIN_HOURS_TO_CLOSE}-{MAX_HOURS_TO_CLOSE}h")
    print(f"  bucket-spam filter: event sub-markets <= {MAX_SUB_MARKETS_PER_EVENT}")
    print(f"  clarity >= 2/5")
    print()

    raw = fetch_open_markets()
    print(f"fetched {len(raw)} open markets")
    df = process_markets(raw)
    print(f"after filters: {len(df)} candidates")
    if df.empty:
        return

    # rank by combined score: clarity + liquidity proxy
    df["rank_score"] = df["clarity"] * 2 + (df["volume"] / 50_000).clip(upper=5)
    df = df.sort_values(["category", "rank_score"], ascending=[True, False])

    print("\nBy category:")
    print(df.groupby("category").size().to_string())

    print("\nTop 3 per category (rank_score):")
    for cat, sub in df.groupby("category"):
        print(f"\n--- {cat} ---")
        for _, r in sub.head(3).iterrows():
            mid_display = r["mid"]
            print(f"  [{r['hours_to_close']:>5.1f}h] mid={mid_display:.3f} "
                  f"spread={r['spread']:.3f} vol=${r['volume']:>7,} "
                  f"clarity={r['clarity']}/5  {r['question'][:80]}")

    df.to_csv(OUT, index=False)
    print(f"\nSaved {len(df)} candidates to {OUT}")


if __name__ == "__main__":
    main()

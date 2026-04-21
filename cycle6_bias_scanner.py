"""Track C: Live bias scanner — flag open markets in statistically-biased pockets.

Unlike Oracle scanner which relies on Claude judgment, this scanner:
  1. Loads pre-computed bias table (from historical data)
  2. Scans current open markets
  3. Flags those matching (category × price_bucket) with strong historical edge

No Claude subjective step. Pure statistics.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

GAMMA = "https://gamma-api.polymarket.com/markets"
OUT = Path("data/results/bias_candidates.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

# Bias pockets refined through:
# 1) pattern_calibration.py (original rank by EV)
# 2) cycle6_stability.py (must survive all 3 sub-windows with same sign)
# 3) cycle6_esports_deepdive.py (LoL-specific isolation)
#
# Tier A = survived cross-window stability test
# Tier B = strong bias but untested stability (use with caution)
# Tier C = deep-dive confirmed but small sample
BIAS_POCKETS = [
    # (category_key, price_lo, price_hi, best_side, expected_ev_pct, tier, source_n)
    # Tier A (stable across 3 sub-windows)
    ("weather",         0.25, 0.40, "YES", 28.0, "A", 413),
    ("sports_global",   0.50, 0.60, "YES", 13.4, "A", 115),
    # Tier C (deep-dive isolated, watch sample size)
    ("lol",             0.50, 0.60, "NO",  18.4, "C", 247),  # LoL-specific from esports
    # Tier B (strong raw bias, not cross-window stable but large n)
    ("other",           0.70, 0.80, "NO",  21.7, "B", 209),
    ("tweet_count",     0.10, 0.25, "NO",  16.0, "B", 22),
]


def categorize(slug):
    s = (slug or "").lower()
    # more specific first
    if "lol-" in s or "-lol-" in s or s.startswith("lol-"):
        return "lol"
    if any(k in s for k in ["nba-", "mlb-", "nhl-", "ncaa", "cbb-", "cfb-"]):
        return "sports_us"
    if any(k in s for k in ["ufc-", "atp-", "wta-", "fif-", "fl1-", "bun-",
                             "ucl-", "uel-", "epl-", "euroleague", "kbo-", "pga"]):
        return "sports_global"
    if any(k in s for k in ["cs2-", "val-", "dota", "rocket-league",
                             "-esports-", "blast-", "iem-"]):
        return "esports"
    if any(k in s for k in ["tweets", "tweet-", "-of-posts-", "-of-tweets-"]):
        return "tweet_count"
    if "highest-temperature" in s or "temperature-in-" in s:
        return "weather"
    return "other"


def fetch_open_markets(limit_pages: int = 20) -> list[dict]:
    out = []
    for offset in range(0, limit_pages * 500, 500):
        try:
            r = requests.get(GAMMA, params={
                "closed": "false", "active": "true",
                "limit": 500, "offset": offset,
                "volume_num_min": 2000,
                "order": "volume", "ascending": "false",
            }, timeout=30)
            data = r.json()
            if not isinstance(data, list) or not data:
                break
            out.extend(data)
            time.sleep(0.2)
        except Exception:
            break
    return out


def match_market(m: dict) -> list[dict]:
    try:
        outcomes = json.loads(m.get("outcomes") or "[]")
        tokens = json.loads(m.get("clobTokenIds") or "[]")
    except Exception:
        return []
    if len(outcomes) != 2 or len(tokens) != 2:
        return []

    try:
        ask = float(m.get("bestAsk") or 0)
        bid = float(m.get("bestBid") or 0)
    except Exception:
        return []
    if ask <= 0 or bid <= 0:
        return []
    mid = (ask + bid) / 2

    cat = categorize(m.get("slug"))
    results = []
    for pocket in BIAS_POCKETS:
        pc_cat, lo, hi, best_side, ev_pct, tier, src_n = pocket
        if cat != pc_cat:
            continue
        if not (lo <= mid < hi):
            continue

        # You want to bet best_side. Entry is ask of that side
        if best_side == "YES":
            entry = ask
        else:
            entry = 1 - bid  # NO ask ≈ 1 - YES bid
        results.append({
            "category": cat,
            "pocket": f"{lo:.2f}-{hi:.2f}",
            "best_side": best_side,
            "entry_price": round(entry, 4),
            "expected_ev_pct": ev_pct,
            "tier": tier,
            "historical_n": src_n,
            "slug": m.get("slug"),
            "question": (m.get("question") or "")[:90],
            "mid": round(mid, 4),
            "spread": round(ask-bid, 4),
            "volume": round(float(m.get("volumeNum") or 0)),
            "end_date": m.get("endDate"),
        })
    return results


def main():
    print("Cycle 6 Bias Scanner — statistical pockets only, no Claude judgment")
    print()
    for pc in BIAS_POCKETS:
        cat, lo, hi, side, ev, tier, src_n = pc
        print(f"  [{tier}] {cat:<18} {lo:.2f}-{hi:.2f}  side={side}  "
              f"expected EV={ev:+.1f}%  (historical n={src_n})")
    print()

    raw = fetch_open_markets()
    print(f"Fetched {len(raw)} open markets")

    hits = []
    for m in raw:
        hits.extend(match_market(m))

    if not hits:
        print("No current matches.")
        return

    df = pd.DataFrame(hits).sort_values("expected_ev_pct", ascending=False)
    print(f"\nFound {len(df)} current candidates:\n")
    for _, r in df.iterrows():
        ed = (r["end_date"] or "")[:10]
        print(f"  [{r['tier']}] [{r['category']:<14}] {r['pocket']}  side={r['best_side']:<3}  "
              f"entry={r['entry_price']:.3f}  vol=${r['volume']:>7,}  {ed}  "
              f"{r['question'][:60]}")

    df.to_csv(OUT, index=False)
    print(f"\nSaved to {OUT}")


if __name__ == "__main__":
    main()

"""Live scanner: find current Polymarket opportunities matching statistically
significant FLB edges (validated via bootstrap 95% CI on 12.4k markets)."""
import json
import time
from datetime import datetime, timezone

import pandas as pd
import requests

GAMMA = "https://gamma-api.polymarket.com/markets"


# Three validated strategies (bootstrap CI_95_low > 0)
STRATEGIES = [
    {
        "name": "A_mid_favorite",
        "price_lo": 0.88, "price_hi": 0.96,
        "vol_lo": 5_000, "vol_hi": 10_000,
        "hours_to_close_min": 24, "hours_to_close_max": 96,  # ~3d window around 72h
        "expected_edge": 0.036, "win_rate_est": 0.966,
        "label": "Fav 0.88-0.96, vol $5-10k, ~3d out",
    },
    {
        "name": "B_tail_arb",
        "price_lo": 0.95, "price_hi": 0.99,
        "vol_lo": 5_000, "vol_hi": 50_000,
        "hours_to_close_min": 120, "hours_to_close_max": 216,  # ~7d window
        "expected_edge": 0.011, "win_rate_est": 0.992,
        "label": "Fav 0.95-0.99, vol $5-50k, ~7d out",
    },
    {
        "name": "C_moderate_fav",
        "price_lo": 0.70, "price_hi": 0.88,
        "vol_lo": 5_000, "vol_hi": 20_000,
        "hours_to_close_min": 120, "hours_to_close_max": 216,
        "expected_edge": 0.061, "win_rate_est": 0.825,
        "label": "Fav 0.70-0.88, vol $5-20k, ~7d out",
    },
]


def fetch_open_markets(limit=500, offset=0) -> list[dict]:
    r = requests.get(GAMMA, params={
        "closed": "false", "active": "true",
        "limit": limit, "offset": offset,
        "volume_num_min": 5000,
        "order": "volume", "ascending": "true",
    }, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, list) else []


def match_strategies(m: dict) -> list[dict]:
    try:
        outcomes = json.loads(m.get("outcomes") or "[]")
        tokens = json.loads(m.get("clobTokenIds") or "[]")
    except Exception:
        return []
    if len(outcomes) != 2 or len(tokens) != 2:
        return []

    volume = float(m.get("volumeNum") or 0)
    liquidity = float(m.get("liquidityClob") or 0)
    if liquidity < 300:
        return []

    end_date = m.get("endDate")
    if not end_date:
        return []
    try:
        end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    except Exception:
        return []
    h_to_close = (end_dt - datetime.now(timezone.utc)).total_seconds() / 3600

    best_ask = m.get("bestAsk")
    best_bid = m.get("bestBid")
    if best_ask is None or best_bid is None:
        return []
    try:
        ask = float(best_ask); bid = float(best_bid)
    except Exception:
        return []
    if ask <= 0 or bid <= 0 or ask <= bid:
        return []
    mid = (ask + bid) / 2
    spread = ask - bid
    if spread > 0.03:
        return []

    # favorite side
    if mid >= 0.5:
        fav_side = outcomes[0]; fav_price = mid; fav_ask = ask
    else:
        fav_side = outcomes[1]; fav_price = 1 - mid; fav_ask = 1 - bid

    matches = []
    for s in STRATEGIES:
        if not (s["price_lo"] <= fav_price <= s["price_hi"]): continue
        if not (s["vol_lo"] <= volume <= s["vol_hi"]): continue
        if not (s["hours_to_close_min"] <= h_to_close <= s["hours_to_close_max"]): continue
        matches.append({
            "strategy": s["name"],
            "strategy_label": s["label"],
            "slug": m.get("slug"),
            "question": m.get("question"),
            "fav_side": fav_side,
            "fav_price": round(fav_price, 4),
            "fav_ask": round(fav_ask, 4),
            "spread": round(spread, 4),
            "volume": round(volume),
            "liquidity_clob": round(liquidity),
            "hours_to_close": round(h_to_close, 1),
            "expected_edge": s["expected_edge"],
            "est_win_rate": s["win_rate_est"],
            "end_date": end_date,
        })
    return matches


def main():
    print("Live FLB Scanner (statistically validated strategies)")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")
    print()
    for s in STRATEGIES:
        print(f"  {s['name']}: {s['label']}")
        print(f"    expected +{s['expected_edge']*100:.1f}% per bet, "
              f"~{s['win_rate_est']*100:.0f}% win rate")
    print()

    hits = []
    for offset in range(0, 8000, 500):
        batch = fetch_open_markets(limit=500, offset=offset)
        if not batch:
            break
        for m in batch:
            hits.extend(match_strategies(m))
        time.sleep(0.3)

    if not hits:
        print("No matching markets right now.")
        return

    df = pd.DataFrame(hits).sort_values(["strategy", "hours_to_close"])
    print(f"Found {len(df)} opportunities:\n")
    for strat in df["strategy"].unique():
        print(f"\n=== {strat} ===")
        sub = df[df["strategy"] == strat]
        cols = ["question", "fav_side", "fav_price", "fav_ask", "spread",
                "volume", "hours_to_close"]
        for _, r in sub.iterrows():
            q = (r["question"] or "")[:70]
            print(f"  [{r['hours_to_close']:>5.1f}h] {r['fav_side']:<4} @ {r['fav_price']:.3f} "
                  f"(ask {r['fav_ask']:.3f}, vol ${r['volume']:>6,})  {q}")

    df.to_csv("data/results/live_candidates.csv", index=False)
    print(f"\nSaved to data/results/live_candidates.csv ({len(df)} rows)")


if __name__ == "__main__":
    main()

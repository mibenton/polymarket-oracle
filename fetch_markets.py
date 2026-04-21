"""Fetch all closed Polymarket markets via Gamma API, save to parquet."""
import json
import time
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

GAMMA = "https://gamma-api.polymarket.com/markets"
OUT = Path("data/markets.parquet")
OUT.parent.mkdir(exist_ok=True)

PAGE_SIZE = 500
MAX_PAGES = 200  # 500 * 200 = 100k cap


def fetch_page(offset: int) -> list[dict]:
    for attempt in range(5):
        try:
            r = requests.get(
                GAMMA,
                params={
                    "closed": "true",
                    "limit": PAGE_SIZE,
                    "offset": offset,
                    "order": "closedTime",
                    "ascending": "false",
                },
                timeout=30,
            )
            if r.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)
    return []


def simplify(m: dict) -> dict | None:
    # parse JSON-string fields
    try:
        outcomes = json.loads(m.get("outcomes") or "[]")
        prices = json.loads(m.get("outcomePrices") or "[]")
        tokens = json.loads(m.get("clobTokenIds") or "[]")
    except Exception:
        return None
    if len(outcomes) != 2 or len(tokens) != 2 or len(prices) != 2:
        return None
    # resolution: outcomePrices are "1" for winner, "0" for loser
    try:
        p0, p1 = float(prices[0]), float(prices[1])
    except Exception:
        return None
    if not ((p0 == 1 and p1 == 0) or (p0 == 0 and p1 == 1)):
        return None  # skip non-binary-resolved (partial / void)
    yes_idx = 0 if outcomes[0].lower() in ("yes", "over") else (1 if outcomes[1].lower() in ("yes", "over") else 0)
    # We treat outcomes[0] as the "base" side for consistency
    return {
        "id": m.get("id"),
        "slug": m.get("slug"),
        "question": m.get("question"),
        "conditionId": m.get("conditionId"),
        "yes_token": tokens[0],
        "no_token": tokens[1],
        "yes_outcome": outcomes[0],
        "no_outcome": outcomes[1],
        "yes_won": p0 == 1,
        "volume": float(m.get("volumeNum") or 0),
        "liquidity": float(m.get("liquidityNum") or 0),
        "closed_time": m.get("closedTime"),
        "end_date": m.get("endDate"),
        "start_date": m.get("startDate"),
        "uma_status": m.get("umaResolutionStatus"),
        "neg_risk": bool(m.get("negRisk")),
        "category": (m.get("events") or [{}])[0].get("category") if m.get("events") else None,
    }


def main():
    rows = []
    seen_ids = set()
    empty_streak = 0
    for page in tqdm(range(MAX_PAGES), desc="pages"):
        data = fetch_page(page * PAGE_SIZE)
        if not data:
            empty_streak += 1
            if empty_streak >= 2:
                break
            continue
        empty_streak = 0
        new = 0
        for m in data:
            if m.get("id") in seen_ids:
                continue
            seen_ids.add(m.get("id"))
            simp = simplify(m)
            if simp:
                rows.append(simp)
                new += 1
        if new == 0 and len(data) < PAGE_SIZE:
            break
        time.sleep(0.3)  # respect rate limit

    df = pd.DataFrame(rows)
    df["closed_time"] = pd.to_datetime(df["closed_time"], utc=True, errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], utc=True, errors="coerce")
    df["start_date"] = pd.to_datetime(df["start_date"], utc=True, errors="coerce")
    df.to_parquet(OUT, index=False)
    print(f"\nsaved {len(df)} markets to {OUT}")
    print(df[["volume", "liquidity"]].describe())
    print("\nresolved/disputed breakdown:")
    print(df["uma_status"].value_counts(dropna=False))


if __name__ == "__main__":
    main()

"""Extended fetch: go 12+ months back, server-side volume filter to speed up."""
import json
import time
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

GAMMA = "https://gamma-api.polymarket.com/markets"
OUT = Path("data/markets_ext.parquet")
OUT.parent.mkdir(exist_ok=True)

PAGE_SIZE = 500
MAX_PAGES = 1500  # ~750k filtered markets
MIN_VOLUME_FILTER = 5000  # server-side filter
TARGET_MIN_DATE = pd.Timestamp("2025-04-18", tz="UTC")  # 12 months back


def fetch_page(offset: int) -> list[dict]:
    for attempt in range(5):
        try:
            r = requests.get(
                GAMMA,
                params={
                    "closed": "true",
                    "limit": PAGE_SIZE,
                    "offset": offset,
                    "volume_num_min": MIN_VOLUME_FILTER,
                    "order": "closedTime",
                    "ascending": "false",
                },
                timeout=30,
            )
            if r.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            data = r.json()
            if isinstance(data, dict):  # error response
                return []
            return data
        except Exception:
            if attempt == 4:
                return []
            time.sleep(1 + attempt)
    return []


def simplify(m: dict) -> dict | None:
    try:
        outcomes = json.loads(m.get("outcomes") or "[]")
        prices = json.loads(m.get("outcomePrices") or "[]")
        tokens = json.loads(m.get("clobTokenIds") or "[]")
    except Exception:
        return None
    if len(outcomes) != 2 or len(tokens) != 2 or len(prices) != 2:
        return None
    try:
        p0, p1 = float(prices[0]), float(prices[1])
    except Exception:
        return None
    if not ((p0 == 1 and p1 == 0) or (p0 == 0 and p1 == 1)):
        return None
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
    }


def main():
    rows = []
    seen_ids = set()
    earliest = None
    empty_streak = 0
    pbar = tqdm(range(MAX_PAGES), desc="pages")
    for page in pbar:
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
                try:
                    ct = pd.Timestamp(simp["closed_time"], tz="UTC")
                    earliest = ct if earliest is None or ct < earliest else earliest
                except Exception:
                    pass
        if earliest:
            pbar.set_postfix({"earliest": earliest.date().isoformat(), "rows": len(rows)})
            if earliest < TARGET_MIN_DATE:
                print(f"\nreached target date {TARGET_MIN_DATE.date()}, stopping")
                break
        if new == 0 and len(data) < PAGE_SIZE:
            break
        # incremental save every 50 pages
        if (page + 1) % 50 == 0:
            pd.DataFrame(rows).to_parquet(OUT, index=False)
        time.sleep(0.3)

    df = pd.DataFrame(rows)
    df["closed_time"] = pd.to_datetime(df["closed_time"], utc=True, errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], utc=True, errors="coerce")
    df["start_date"] = pd.to_datetime(df["start_date"], utc=True, errors="coerce")
    df.to_parquet(OUT, index=False)
    print(f"\nsaved {len(df)} markets to {OUT}")
    print(f"time range: {df['closed_time'].min()} -> {df['closed_time'].max()}")


if __name__ == "__main__":
    main()

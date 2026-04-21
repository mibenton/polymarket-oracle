"""Fetch prices for extended target set (20k-100k vol, dur>=72h, missing only)."""
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from tqdm import tqdm

CLOB = "https://clob.polymarket.com/prices-history"
MARKETS_EXT = Path("data/markets_ext.parquet")
PRICES_IN = Path("data/prices.parquet")
PRICES_OUT = Path("data/prices_ext.parquet")

FIDELITY = 60
WORKERS = 8
SLEEP = 0.04
BATCH_SAVE = 1000


def fetch_one(token: str) -> list[dict]:
    for attempt in range(3):
        try:
            r = requests.get(
                CLOB,
                params={"market": token, "interval": "max", "fidelity": FIDELITY},
                timeout=30,
            )
            if r.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            return r.json().get("history", [])
        except Exception:
            if attempt == 2:
                return []
            time.sleep(1 + attempt)
    return []


def main():
    ext = pd.read_parquet(MARKETS_EXT)
    ext["closed_time"] = pd.to_datetime(ext["closed_time"], utc=True, errors="coerce")
    ext["start_date"] = pd.to_datetime(ext["start_date"], utc=True, errors="coerce")
    ext["duration_h"] = (ext["closed_time"] - ext["start_date"]).dt.total_seconds() / 3600

    # target: FLB sweet spot
    target = ext[(ext["volume"] >= 20000) & (ext["volume"] <= 100000) &
                 (ext["duration_h"] >= 72)].copy()
    print(f"target markets: {len(target):,}")

    # resume if partial
    done = set()
    if PRICES_OUT.exists():
        prev = pd.read_parquet(PRICES_OUT)
        done = set(prev["market_id"].unique())
    # also count as "done" anything we have in the original prices.parquet
    if PRICES_IN.exists():
        prev_in = pd.read_parquet(PRICES_IN)
        done |= set(prev_in["market_id"].unique())
    print(f"already done (in either file): {len(done):,}")

    todo = target[~target["id"].isin(done)]
    print(f"to fetch: {len(todo):,}")

    results = []

    def task(row):
        hist = fetch_one(row["yes_token"])
        return row["id"], hist

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(task, row): row for _, row in todo.iterrows()}
        for i, fut in enumerate(tqdm(as_completed(futs), total=len(futs), desc="prices")):
            mid, hist = fut.result()
            for pt in hist:
                results.append({"market_id": mid, "t": pt["t"], "p": pt["p"]})
            if (i + 1) % BATCH_SAVE == 0:
                partial = pd.DataFrame(results)
                if PRICES_OUT.exists():
                    prev = pd.read_parquet(PRICES_OUT)
                    partial = pd.concat([prev, partial], ignore_index=True)
                partial.to_parquet(PRICES_OUT, index=False)
                results = []
            time.sleep(SLEEP)

    if results:
        partial = pd.DataFrame(results)
        if PRICES_OUT.exists():
            prev = pd.read_parquet(PRICES_OUT)
            partial = pd.concat([prev, partial], ignore_index=True)
        partial.to_parquet(PRICES_OUT, index=False)

    final = pd.read_parquet(PRICES_OUT)
    print(f"\ntotal price points: {len(final):,}")
    print(f"unique markets: {final['market_id'].nunique():,}")


if __name__ == "__main__":
    main()

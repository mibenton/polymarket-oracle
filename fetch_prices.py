"""Fetch CLOB price history for each market's YES token. Incremental save."""
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
from tqdm import tqdm

CLOB = "https://clob.polymarket.com/prices-history"
MARKETS = Path("data/markets.parquet")
OUT = Path("data/prices.parquet")

# filters
MIN_VOLUME = 5000
MIN_DURATION_H = 72

# fetch config
FIDELITY = 60  # 60-min bars
WORKERS = 8
SLEEP = 0.05


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
    df = pd.read_parquet(MARKETS)
    df["duration_h"] = (df["closed_time"] - df["start_date"]).dt.total_seconds() / 3600
    mask = (df["volume"] >= MIN_VOLUME) & (df["duration_h"] >= MIN_DURATION_H)
    sub = df[mask].reset_index(drop=True)
    print(f"targets: {len(sub)} markets")

    # resume if partial
    done = set()
    if OUT.exists():
        prev = pd.read_parquet(OUT)
        done = set(prev["market_id"].unique())
        print(f"already done: {len(done)}")
    todo = sub[~sub["id"].isin(done)]
    print(f"to fetch: {len(todo)}")

    results = []
    batch_save = 500

    def task(row):
        hist = fetch_one(row["yes_token"])
        return row["id"], hist

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(task, row): row for _, row in todo.iterrows()}
        for i, fut in enumerate(tqdm(as_completed(futs), total=len(futs), desc="prices")):
            mid, hist = fut.result()
            for pt in hist:
                results.append({"market_id": mid, "t": pt["t"], "p": pt["p"]})
            # incremental save
            if (i + 1) % batch_save == 0:
                partial = pd.DataFrame(results)
                if OUT.exists():
                    prev = pd.read_parquet(OUT)
                    partial = pd.concat([prev, partial], ignore_index=True)
                partial.to_parquet(OUT, index=False)
                results = []
            time.sleep(SLEEP)

    if results:
        partial = pd.DataFrame(results)
        if OUT.exists():
            prev = pd.read_parquet(OUT)
            partial = pd.concat([prev, partial], ignore_index=True)
        partial.to_parquet(OUT, index=False)

    final = pd.read_parquet(OUT)
    print(f"\ntotal price points: {len(final)}")
    print(f"unique markets: {final['market_id'].nunique()}")


if __name__ == "__main__":
    main()

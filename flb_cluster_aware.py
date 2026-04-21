"""Cluster-aware FLB re-test: one position per event_id."""
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

TAKER_FEE = 0.01
SEED = 42


def load_trades():
    """Reload Strategy A trades with market_id."""
    ext = pd.read_parquet("data/markets_ext.parquet")
    orig = pd.read_parquet("data/markets.parquet")
    markets = pd.concat([ext, orig], ignore_index=True).drop_duplicates("id")
    markets["closed_time"] = pd.to_datetime(markets["closed_time"], utc=True, errors="coerce")
    markets["start_date"] = pd.to_datetime(markets["start_date"], utc=True, errors="coerce")
    frames = []
    for p in ["data/prices.parquet", "data/prices_ext.parquet"]:
        if Path(p).exists():
            frames.append(pd.read_parquet(p))
    prices = pd.concat(frames).drop_duplicates(["market_id", "t"])

    markets = markets[markets["id"].isin(prices["market_id"].unique())]
    m = markets[["id", "closed_time", "yes_won", "volume", "slug"]].rename(
        columns={"id": "market_id"})
    m["target_ts"] = (m["closed_time"] - pd.Timedelta(hours=72)).astype("int64") // 10**9
    merged = pd.merge_asof(
        m.sort_values("target_ts"), prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6 * 3600),
    )
    entries = merged.dropna(subset=["p"]).copy()
    entries["fav_price"] = np.where(entries["p"] >= 0.5, entries["p"], 1 - entries["p"])
    entries["fav_won"] = np.where(entries["p"] >= 0.5,
                                   entries["yes_won"].astype(bool),
                                   ~entries["yes_won"].astype(bool))
    sub = entries[(entries["fav_price"] >= 0.88) & (entries["fav_price"] <= 0.96) &
                  (entries["volume"] >= 5_000) & (entries["volume"] <= 10_000)].copy()
    b = 1 / sub["fav_price"].values - 1
    sub["pnl"] = np.where(sub["fav_won"], b, -1) - TAKER_FEE
    return sub.reset_index(drop=True)


def fetch_event_id(market_id: str) -> str | None:
    try:
        r = requests.get("https://gamma-api.polymarket.com/markets",
                         params={"id": market_id, "limit": 1}, timeout=15)
        data = r.json()
        if not data:
            return None
        events = data[0].get("events") or []
        if events:
            return str(events[0].get("id"))
    except Exception:
        return None
    return None


def annotate_events(trades: pd.DataFrame) -> pd.DataFrame:
    cache = Path("data/event_ids.parquet")
    if cache.exists():
        prev = pd.read_parquet(cache)
        trades = trades.merge(prev, on="market_id", how="left")
    else:
        trades["event_id"] = None

    missing = trades[trades["event_id"].isna()]
    if len(missing) > 0:
        print(f"fetching event_id for {len(missing)} markets...")
        results = {}
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs = {ex.submit(fetch_event_id, mid): mid
                    for mid in missing["market_id"].unique()}
            for fut in tqdm(as_completed(futs), total=len(futs)):
                mid = futs[fut]
                eid = fut.result()
                if eid:
                    results[mid] = eid
                time.sleep(0.03)
        new_df = pd.DataFrame(list(results.items()), columns=["market_id", "event_id"])
        trades = trades.drop(columns=["event_id"]).merge(new_df, on="market_id", how="left")
        new_df.to_parquet(cache, index=False)

    return trades


def cluster_stats(pnl: np.ndarray, label: str = "") -> dict:
    if len(pnl) < 3:
        return {"n": len(pnl), "label": label}
    mean = pnl.mean()
    se = pnl.std(ddof=1) / np.sqrt(len(pnl))
    rng = np.random.default_rng(SEED)
    bs = np.array([pnl[rng.integers(0, len(pnl), len(pnl))].mean() for _ in range(3000)])
    return {
        "label": label,
        "n": len(pnl),
        "mean": mean,
        "se": se,
        "t": mean / se if se > 0 else 0,
        "ci_low": np.percentile(bs, 2.5),
        "ci_high": np.percentile(bs, 97.5),
        "pos_rate": (pnl > 0).mean(),
    }


def analyze_clusters(trades: pd.DataFrame):
    print("\n" + "="*80)
    print("CLUSTER-AWARE STRATEGY A ANALYSIS")
    print("="*80)

    trades = trades.copy()
    # fallback for missing event_id: use slug prefix
    trades["event_id"] = trades["event_id"].fillna(
        trades["slug"].str.split("-").str[:6].str.join("-")
    )

    print(f"\nMarket-level: n={len(trades)}, unique events={trades['event_id'].nunique()}")

    # Method 1: One representative per event (by market_id modulo — deterministic)
    representative = trades.sort_values(["event_id", "market_id"]).groupby(
        "event_id", as_index=False).first()
    s1 = cluster_stats(representative["pnl"].values, "1 rep per event (first)")

    # Method 2: Average PnL per event (equal dollar per event)
    per_event = trades.groupby("event_id").agg(
        pnl=("pnl", "mean"),
        n_sub=("pnl", "size"),
    ).reset_index()
    s2 = cluster_stats(per_event["pnl"].values, "equal-weight avg per event")

    # Method 3: Median PnL per event
    per_event_med = trades.groupby("event_id")["pnl"].median().values
    s3 = cluster_stats(per_event_med, "median per event")

    # Market-level (flawed baseline)
    s0 = cluster_stats(trades["pnl"].values, "market-level (original, flawed)")

    print("\n" + "-"*80)
    for s in [s0, s1, s2, s3]:
        if s.get("n", 0) < 3:
            continue
        sig = " SIGNIFICANT" if s["t"] > 1.96 else " not sig"
        print(f"  {s['label']:<38} n={s['n']:>4}  mean={s['mean']:+.4f}  "
              f"t={s['t']:+.2f}  CI=[{s['ci_low']:+.4f},{s['ci_high']:+.4f}]  {sig}")

    # Cluster size distribution
    print("\nCluster size distribution:")
    clust_sizes = trades.groupby("event_id").size()
    print(clust_sizes.describe())

    print("\nTop 10 clusters by size:")
    top = clust_sizes.sort_values(ascending=False).head(10)
    for eid, sz in top.items():
        evt_pnl = trades[trades["event_id"] == eid]["pnl"]
        slug_sample = trades[trades["event_id"] == eid]["slug"].iloc[0]
        print(f"  event={eid}  n={sz}  mean_pnl={evt_pnl.mean():+.4f}  "
              f"sum={evt_pnl.sum():+.2f}  e.g.={slug_sample[:55]}")

    # Check if a >3x cluster filter saves any edge
    print("\n--- FILTER: remove events with >=3 sub-markets (suspected bucket-spam) ---")
    small_clusters = clust_sizes[clust_sizes < 3].index
    filtered = trades[trades["event_id"].isin(small_clusters)]
    s4 = cluster_stats(filtered["pnl"].values, "market-level, only events w/ <3 sub-markets")
    print(f"  {s4['label']}: n={s4['n']}, mean={s4['mean']:+.4f}, "
          f"t={s4['t']:+.2f}, CI=[{s4['ci_low']:+.4f},{s4['ci_high']:+.4f}]")

    return trades


def main():
    trades = load_trades()
    print(f"Strategy A trades: {len(trades)}")
    trades = annotate_events(trades)
    have_eid = trades["event_id"].notna().sum()
    print(f"With event_id: {have_eid} / {len(trades)}")
    analyze_clusters(trades)


if __name__ == "__main__":
    main()

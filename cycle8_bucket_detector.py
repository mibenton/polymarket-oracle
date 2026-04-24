"""Cycle 8: Find exact-bucket markets with near-mean underpricing (weather-like).

Method:
1. Group markets by event_id (parent event).
2. Keep events with >= 5 child markets (true bucket structure).
3. For each event, sort child markets by implied probability (fav_price at T-72h).
4. Identify the "peak bucket" (highest implied prob = market's favored outcome).
5. Check: do near-peak buckets resolve YES more than their implied prob?
6. Cross-window stability on the identified pattern.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd

TAKER_FEE = 0.01


def load():
    ext = pd.read_parquet("data/markets_ext.parquet")
    orig = pd.read_parquet("data/markets.parquet")
    markets = pd.concat([ext, orig], ignore_index=True).drop_duplicates("id")
    markets["closed_time"] = pd.to_datetime(markets["closed_time"], utc=True, errors="coerce")
    markets["start_date"] = pd.to_datetime(markets["start_date"], utc=True, errors="coerce")
    markets["duration_h"] = (markets["closed_time"] - markets["start_date"]).dt.total_seconds()/3600

    frames = []
    for p in ["data/prices.parquet", "data/prices_ext.parquet"]:
        if Path(p).exists():
            frames.append(pd.read_parquet(p))
    prices = pd.concat(frames).drop_duplicates(["market_id","t"])

    have = markets[markets["id"].isin(prices["market_id"].unique())].copy()
    have = have[have["duration_h"] >= 72].copy()
    have["target_ts"] = (have["closed_time"] - pd.Timedelta(hours=72)).astype("int64") // 10**9

    m = have[["id","slug","question","closed_time","yes_won","yes_outcome",
              "no_outcome","volume","duration_h","target_ts"]].rename(columns={"id":"market_id"})
    merged = pd.merge_asof(
        m.sort_values("target_ts"),
        prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6*3600),
    ).dropna(subset=["p"])
    merged["yes_won_int"] = merged["yes_won"].astype(int)
    return merged


def event_key(slug: str) -> str:
    """Strip numeric suffix / thresholds to group by event.
    e.g. 'highest-temperature-in-tokyo-on-april-24-2026-19c' -> 'highest-temperature-in-tokyo-on-april-24-2026'
    """
    if not isinstance(slug, str):
        return "unknown"
    # Remove trailing '-<number><optional unit>' and range indicators
    s = re.sub(r'-[0-9]+(pt[0-9]+)?(c|f|k|m|b|corhigher|corabove|corbelow|corlower|pct)?$',
               '', slug.lower())
    # Remove range like '180-199' or '0pt25-0pt30'
    s = re.sub(r'-[0-9]+(pt[0-9]+)?(-[0-9]+(pt[0-9]+)?)?$', '', s)
    return s


def detect_bucket_events(df: pd.DataFrame, min_children: int = 5):
    """Find event families with >= min_children child markets."""
    df = df.copy()
    df["event_key"] = df["slug"].apply(event_key)
    counts = df["event_key"].value_counts()
    multi = counts[counts >= min_children]
    print(f"\nEvents with >= {min_children} child markets: {len(multi)}")
    print(f"Top 20 by child count:")
    print(multi.head(20).to_string())
    return df[df["event_key"].isin(multi.index)]


def categorize_event(slug: str) -> str:
    s = slug.lower()
    if "highest-temperature" in s or "temperature-in-" in s:
        return "weather"
    if "tweets" in s or "-of-posts-" in s:
        return "tweet_count"
    if "opening-weekend" in s or "box-office" in s:
        return "box_office"
    if any(k in s for k in ["bitcoin", "ethereum", "solana", "btc-", "eth-"]):
        if "above" in s or "dip" in s:
            return "crypto_threshold"
        return "crypto_other"
    if any(k in s for k in ["cpi", "fomc", "-rate-"]):
        return "macro_exact"
    if any(k in s for k in ["nfl-draft", "pick-", "first-round"]):
        return "draft_pick"
    if any(k in s for k in ["will-", "-win-", "primary"]):
        return "politics_or_sports"
    return "other_bucket"


def test_near_peak_edge(df: pd.DataFrame):
    """For each category × price bucket, compute if bias exists."""
    df = df.copy()
    df["category"] = df["slug"].apply(categorize_event)
    df["yes_won_int"] = df["yes_won"].astype(int)
    # focus on low-implied YES buckets (typical for bucket markets: retail undervalues near-peak)
    bins = [0, 0.05, 0.1, 0.15, 0.20, 0.30, 0.40, 0.5, 0.7, 1.0]
    df["p_bucket"] = pd.cut(df["p"], bins=bins, include_lowest=True)

    print(f"\n{'='*80}")
    print("CATEGORY x PRICE-BUCKET CALIBRATION (bucket markets only)")
    print(f"{'='*80}")
    rows = []
    for (cat, bkt), sub in df.groupby(["category", "p_bucket"], observed=True):
        if len(sub) < 20:
            continue
        implied = sub["p"].mean()
        actual = sub["yes_won_int"].mean()
        bias = (actual - implied) * 100
        # Only flag YES-underpricing (which is what weather showed)
        if actual > implied:
            gross_ev = (actual / implied - 1) * 100
            net_ev = gross_ev - 1.5  # conservative fee
            side = "YES"
        else:
            gross_ev = ((1-actual) / (1-implied) - 1) * 100
            net_ev = gross_ev - 1.5
            side = "NO"
        rows.append({
            "category": cat,
            "price_bucket": str(bkt),
            "n": len(sub),
            "implied_p": round(implied, 3),
            "actual_p": round(actual, 3),
            "bias_pp": round(bias, 1),
            "best_side": side,
            "net_ev_pct": round(net_ev, 1),
        })

    out = pd.DataFrame(rows).sort_values("net_ev_pct", ascending=False)
    print(out.to_string(index=False))
    out.to_csv("data/results/cycle8_bucket_calibration.csv", index=False)
    return out


def cross_window_stability(df: pd.DataFrame, top_pockets):
    """For top pockets, split window into 3 parts, check consistency."""
    df = df.copy()
    df["category"] = df["slug"].apply(categorize_event)
    df["yes_won_int"] = df["yes_won"].astype(int)

    df = df.sort_values("closed_time").reset_index(drop=True)
    t_min = df["closed_time"].min()
    t_max = df["closed_time"].max()
    third = (t_max - t_min) / 3
    df["window"] = pd.cut(
        df["closed_time"],
        bins=[t_min, t_min + third, t_min + 2*third, t_max + pd.Timedelta(seconds=1)],
        labels=["W1", "W2", "W3"], include_lowest=True,
    )

    print(f"\n{'='*80}")
    print("CROSS-WINDOW STABILITY on top pockets")
    print(f"{'='*80}")

    for _, pocket in top_pockets.head(15).iterrows():
        cat = pocket["category"]
        bkt_str = pocket["price_bucket"]
        # parse bucket
        m = re.match(r'\(([-\d.]+),\s*([\d.]+)\]', bkt_str)
        if not m:
            continue
        lo, hi = float(m.group(1)), float(m.group(2))
        sub = df[(df["category"] == cat) & (df["p"] > lo) & (df["p"] <= hi)]
        per_window = sub.groupby("window", observed=True).agg(
            n=("yes_won_int","size"),
            implied=("p","mean"),
            actual=("yes_won_int","mean"),
        )
        per_window["bias_pp"] = (per_window["actual"] - per_window["implied"]) * 100
        if len(per_window) < 3 or (per_window["n"] < 10).any():
            continue
        signs = per_window["bias_pp"].apply(lambda x: 1 if x > 3 else (-1 if x < -3 else 0))
        same_sign = (signs != 0).all() and (signs.iloc[0] * signs.iloc[1] > 0) \
                    and (signs.iloc[0] * signs.iloc[2] > 0)
        marker = "[STABLE]" if same_sign else "         "
        print(f"{marker} {cat:<20} {bkt_str:<18}  "
              f"W1 bias={per_window['bias_pp'].iloc[0]:+.1f}pp "
              f"W2={per_window['bias_pp'].iloc[1]:+.1f}pp "
              f"W3={per_window['bias_pp'].iloc[2]:+.1f}pp  "
              f"(n={per_window['n'].sum()})")


def main():
    df = load()
    print(f"Loaded {len(df):,} markets with prices")

    # Detect bucket events
    bucket_df = detect_bucket_events(df, min_children=5)
    print(f"\nBucket-market observations: {len(bucket_df):,}")

    # Test calibration by category
    pockets = test_near_peak_edge(bucket_df)

    # Cross-window stability
    positive_pockets = pockets[pockets["net_ev_pct"] > 5]
    cross_window_stability(bucket_df, positive_pockets)


if __name__ == "__main__":
    main()

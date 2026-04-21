"""Track A: Cross-window stability — split 30 day sample into 3 sub-windows.

If top bias persists in all 3 windows → structural edge
If only present in 1 or 2 → artifact
"""
from pathlib import Path
import numpy as np
import pandas as pd

TAKER_FEE = 0.01


def categorize(slug):
    s = (slug or "").lower()
    if any(k in s for k in ["nba-", "mlb-", "nhl-", "ncaa", "cbb-", "cfb-"]):
        return "sports_us"
    if any(k in s for k in ["ufc-", "atp-", "wta-", "fif-", "fl1-", "bun-",
                             "ucl-", "uel-", "epl-", "euroleague", "kbo-", "pga"]):
        return "sports_global"
    if any(k in s for k in ["cs2-", "val-", "lol-", "dota", "rocket-league",
                             "-esports-", "blast-", "iem-"]):
        return "esports"
    if "updown" in s or "up-or-down" in s or "upordown" in s:
        return "short_term_price_direction"
    if any(k in s for k in ["bitcoin-above-", "btc-above-", "ethereum-above-",
                             "eth-above-", "solana-above-", "sol-above-"]):
        return "crypto_price_threshold"
    if "dip-to-" in s or "hit-" in s:
        return "price_touch_threshold"
    if any(k in s for k in ["tweets", "tweet-", "-of-posts-", "-of-tweets-"]):
        return "tweet_count"
    if any(k in s for k in ["-election", "-primary", "-senate", "-governor",
                             "-president", "-parliament", "-nominee"]):
        return "politics_election"
    if "highest-temperature" in s or "temperature-in-" in s:
        return "weather"
    return "other"


def load_priced():
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

    m = have[["id","closed_time","yes_won","slug","duration_h","target_ts"]].rename(columns={"id":"market_id"})
    merged = pd.merge_asof(
        m.sort_values("target_ts"),
        prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6*3600),
    ).dropna(subset=["p"])
    merged["category"] = merged["slug"].apply(categorize)
    merged["yes_won_int"] = merged["yes_won"].astype(int)
    return merged


def split_windows(df):
    df = df.sort_values("closed_time").reset_index(drop=True)
    t_min = df["closed_time"].min()
    t_max = df["closed_time"].max()
    span = t_max - t_min
    third = span / 3
    boundaries = [t_min, t_min + third, t_min + 2*third, t_max + pd.Timedelta(seconds=1)]
    df["window"] = pd.cut(df["closed_time"], bins=boundaries,
                           labels=["W1", "W2", "W3"], include_lowest=True)
    return df


def stable_biases(df, min_n=20, bias_thresh=3):
    """Find (category, price bucket) where bias > threshold in all 3 windows."""
    bins = [0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 1.0]
    df = df.copy()
    df["bucket"] = pd.cut(df["p"], bins=bins, include_lowest=True)

    # Compute per (cat, bucket, window)
    g = df.groupby(["category", "bucket", "window"], observed=True).agg(
        n=("yes_won_int", "size"),
        implied=("p", "mean"),
        actual=("yes_won_int", "mean"),
    ).reset_index()
    g["bias_pp"] = (g["actual"] - g["implied"]) * 100

    # Pivot to see all 3 windows side by side
    print(f"\n{'='*95}")
    print("STABILITY CHECK: category × bucket × sub-window")
    print("Only showing cells where n >= 20 AND same sign in all 3 windows")
    print(f"{'='*95}")

    stable = []
    for (cat, buc), sub in g.groupby(["category", "bucket"], observed=True):
        if len(sub) < 3:
            continue
        if (sub["n"] < min_n).any():
            continue
        biases = sub.sort_values("window")["bias_pp"].values
        if all(b > bias_thresh for b in biases) or all(b < -bias_thresh for b in biases):
            stable.append({
                "category": cat,
                "bucket": str(buc),
                "n_total": sub["n"].sum(),
                "W1_bias": round(biases[0], 1),
                "W2_bias": round(biases[1], 1),
                "W3_bias": round(biases[2], 1),
                "avg_bias": round(biases.mean(), 1),
            })

    out = pd.DataFrame(stable).sort_values("avg_bias", key=abs, ascending=False)
    print(out.to_string(index=False))

    # Contrast: show Cycle-5 top findings and see if they survive
    print(f"\n{'='*95}")
    print("RE-CHECK: Cycle-5 top biases across 3 windows")
    print(f"{'='*95}")
    focus = [
        ("sports_global", "(0.6, 0.75]"),
        ("esports", "(0.5, 0.6]"),
        ("weather", "(0.25, 0.4]"),
        ("sports_global", "(0.25, 0.4]"),
        ("other", "(0.6, 0.75]"),
        ("sports_us", "(0.4, 0.5]"),
        ("tweet_count", "(0.1, 0.25]"),
    ]
    rows = []
    for cat, buc in focus:
        sub = g[(g["category"]==cat) & (g["bucket"].astype(str)==buc)]
        if len(sub) == 0:
            continue
        sub = sub.sort_values("window")
        r = {"category": cat, "bucket": buc}
        for _, rr in sub.iterrows():
            w = rr["window"]
            r[f"{w}_n"] = int(rr["n"])
            r[f"{w}_bias"] = round(rr["bias_pp"], 1)
            r[f"{w}_act"] = round(rr["actual"], 3)
        rows.append(r)
    print(pd.DataFrame(rows).to_string(index=False))


def main():
    df = load_priced()
    df = split_windows(df)
    print(f"Markets: {len(df):,}")
    print(f"Windows:")
    for w, sub in df.groupby("window", observed=True):
        if len(sub) > 0:
            print(f"  {w}: {sub['closed_time'].min().date()} -> "
                  f"{sub['closed_time'].max().date()}  n={len(sub)}")
    stable_biases(df)


if __name__ == "__main__":
    main()

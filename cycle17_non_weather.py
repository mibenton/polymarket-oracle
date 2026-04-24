"""Cycle 17: Look beyond weather for similar exact-bucket mispricings.

Candidates:
- Sports exact score buckets
- Crypto exact price on date
- Tweet count buckets
- Box office ranges
- Political vote %
- Economic data exact ranges
"""
import re
from pathlib import Path
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

    m = have[["id","slug","question","closed_time","yes_won","volume","target_ts"]].rename(columns={"id":"market_id"})
    merged = pd.merge_asof(
        m.sort_values("target_ts"),
        prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6*3600),
    ).dropna(subset=["p"])
    merged["yes_won_int"] = merged["yes_won"].astype(int)
    merged["pnl"] = np.where(merged["yes_won"], 1/merged["p"]-1-TAKER_FEE, -1-TAKER_FEE)
    return merged


def categorize(slug: str, question: str) -> str:
    s = (slug or "").lower()
    q = (question or "").lower()
    # tweet count range
    if re.search(r'-[0-9]+-[0-9]+$', s) and ("tweet" in s or "post" in s):
        return "tweet_count_range"
    # "between X-Y"
    if "between" in q and ("score" in q or "points" in q or "goals" in q):
        return "sports_score_range"
    if "between" in q and ("box-office" in s or "opening" in q):
        return "box_office_range"
    # crypto exact on date
    if ("bitcoin" in s or "btc-" in s or "ethereum" in s or "solana" in s) and "above" in s:
        return "crypto_above"
    # crypto between
    if "between" in q and any(k in s for k in ["bitcoin","btc","eth","ethereum","solana","sol"]):
        return "crypto_range"
    # political percent
    if re.search(r'[0-9]+pct', s) or ("margin" in q or "vote" in q):
        return "political_range"
    return None


def main():
    df = load()
    df["cat"] = df.apply(lambda r: categorize(r["slug"], r["question"]), axis=1)
    df = df[df["cat"].notna()].copy()
    print(f"Non-weather bucket-like markets: {len(df):,}")

    print(f"\n=== By category ===")
    g = df.groupby("cat").agg(
        n=("pnl","size"),
        win=("yes_won","mean"),
        mean_pnl=("pnl","mean"),
    )
    g["win_pct"] = (g["win"]*100).round(0)
    g["mean_pnl_pct"] = (g["mean_pnl"]*100).round(1)
    g = g.drop(columns=["win","mean_pnl"])
    print(g.sort_values("mean_pnl_pct", ascending=False).to_string())

    # Calibration by price bucket within each category
    print(f"\n=== Category x Price bucket ===")
    bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
    df["pb"] = pd.cut(df["p"], bins=bins, include_lowest=True)
    gx = df.groupby(["cat","pb"], observed=True).agg(
        n=("pnl","size"),
        mean_pnl=("pnl","mean"),
        implied=("p","mean"),
        actual=("yes_won","mean"),
    )
    gx = gx[gx["n"] >= 30].copy()
    gx["bias_pp"] = ((gx["actual"] - gx["implied"])*100).round(1)
    gx["mean_pnl_pct"] = (gx["mean_pnl"]*100).round(1)
    gx = gx[["n","bias_pp","mean_pnl_pct"]]
    print(gx.sort_values("mean_pnl_pct", ascending=False).to_string())


if __name__ == "__main__":
    main()

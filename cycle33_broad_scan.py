"""Cycle 33: Broad scan of ALL bucket-like markets for hidden edges.

Goal: find pockets similar to weather/crypto_range that we haven't discovered.
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


def fine_categorize(slug, question):
    s = (slug or "").lower()
    q = (question or "").lower()

    # Weather
    if "highest-temperature" in s or "temperature-in-" in s:
        if any(k in s for k in ["orhigher","orabove","orbelow","orlower"]):
            return "weather_cumulative"
        return "weather_exact"

    # Snow
    if "snowfall" in s or "snow" in s:
        return "snow"

    # Tweet counts
    if any(k in s for k in ["tweets","-of-tweets-","-of-posts-"]):
        return "tweet_count"

    # Crypto
    if any(k in s for k in ["bitcoin","btc-","ethereum","eth-","solana","sol-",
                             "xrp","ripple","dogecoin","doge","cardano","ada"]):
        if "between" in s:
            return "crypto_between"
        if "above" in s:
            return "crypto_above"
        if "dip" in s or "dip-to" in s:
            return "crypto_dip"
        return "crypto_other"

    # Stock range
    if any(k in s for k in ["earnings","eps","quarterly","revenue"]):
        if "between" in q:
            return "earnings_range"
        return "earnings_binary"

    # Elections
    if any(k in s for k in ["election","primary","nominee","senate","governor","president"]):
        return "political"

    # Sports
    if any(k in s for k in ["nba-","nfl-","mlb-","nhl-","ufc-","atp-","wta-","cs2-","val-","lol-"]):
        if any(k in s for k in ["spread","total","o-u","ou-"]):
            return "sports_totals"
        return "sports_match"

    # Box office
    if "box-office" in s or "opening-weekend" in s:
        return "box_office"

    # Will X happen by date
    if "will" in s and ("by-" in s or "-before-" in s):
        return "will_by_date"

    return None


def main():
    df = load()
    df["cat"] = df.apply(lambda r: fine_categorize(r["slug"], r["question"]), axis=1)
    df = df[df["cat"].notna()].copy()
    print(f"Categorized markets: {len(df):,}")

    # Overall per category
    print(f"\n=== Per category ===")
    g = df.groupby("cat").agg(
        n=("pnl","size"),
        win=("yes_won","mean"),
        mean_pnl=("pnl","mean"),
    )
    g["win_pct"] = (g["win"]*100).round(0)
    g["mean_pnl_pct"] = (g["mean_pnl"]*100).round(1)
    print(g.drop(columns=["win","mean_pnl"]).sort_values("mean_pnl_pct", ascending=False).to_string())

    # Category × price bucket (find pockets)
    print(f"\n=== Category x Price bucket (n>=30, sorted by EV) ===")
    bins = [0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.70, 1.0]
    df["pb"] = pd.cut(df["p"], bins=bins, include_lowest=True)
    gx = df.groupby(["cat","pb"], observed=True).agg(
        n=("pnl","size"),
        mean_pnl=("pnl","mean"),
        win=("yes_won","mean"),
        implied=("p","mean"),
    )
    gx["bias_pp"] = ((gx["win"] - gx["implied"])*100).round(1)
    gx["mean_pnl_pct"] = (gx["mean_pnl"]*100).round(1)
    gx = gx[gx["n"]>=30][["n","bias_pp","mean_pnl_pct"]]
    print(gx.sort_values("mean_pnl_pct", ascending=False).to_string())


if __name__ == "__main__":
    main()

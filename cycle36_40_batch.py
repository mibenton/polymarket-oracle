"""Cycle 36-40 batch analysis.

C36: Volume momentum — does volume growth between start and close correlate with edge?
C37: Bucket-within-event price ratio — is an outlier-priced bucket a signal?
C38: Post-drawdown sizing — after 5+ losses, does edge recover?
C39: Per-tier time-of-week patterns
C40: Per-city edge momentum (recent weeks vs older)
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '.')
from cycle9_weather_segment import load
from cycle6_bias_scanner import CITY_TZ_OFFSET, is_good_close_hour

TAKER_FEE = 0.01


def event_key(slug):
    s = re.sub(r'-[0-9]+(pt[0-9]+)?(c|f)?(orhigher|orabove|orbelow|orlower)?$',
               '', (slug or '').lower())
    s = re.sub(r'-[0-9]+(-[0-9]+)?(f|c)?$', '', s)
    return s


def main():
    df = load()
    df["pnl"] = np.where(df["yes_won"], 1/df["p"]-1-TAKER_FEE, -1-TAKER_FEE)
    df["event"] = df["slug"].apply(event_key)
    df["local_hour"] = df.apply(
        lambda r: (r["closed_time"].hour + CITY_TZ_OFFSET.get(r["city"], 0)) % 24,
        axis=1
    )

    # C36: Volume momentum (we only have end volume. Use volume vs peer buckets)
    print("=" * 80)
    print("C36: Is volume higher than other buckets in same event?")
    print("=" * 80)
    sub = df[(df["p"]>=0.25) & (df["p"]<=0.36) & (df["volume"]>=10000)].copy()
    event_max_vol = sub.groupby("event")["volume"].max().rename("event_max_vol")
    sub = sub.merge(event_max_vol, on="event")
    sub["vol_ratio"] = sub["volume"] / sub["event_max_vol"]
    bins = [0, 0.3, 0.6, 0.9, 1.01]
    labels = ["<0.3","0.3-0.6","0.6-0.9","≥0.9 (max)"]
    sub["vol_tier"] = pd.cut(sub["vol_ratio"], bins=bins, labels=labels)
    g = sub.groupby("vol_tier", observed=True).agg(
        n=("pnl","size"), mean_pnl=("pnl","mean"), win=("yes_won","mean")
    )
    g["mean_pnl_pct"]=(g["mean_pnl"]*100).round(1); g["win_pct"]=(g["win"]*100).round(0)
    print(g.drop(columns=["mean_pnl","win"]).to_string())

    # C37: Bucket price rank within event
    print("\n" + "=" * 80)
    print("C37: Bucket's price rank (1 = highest, N = lowest) within event")
    print("=" * 80)
    sub2 = df[(df["p"]>=0.05) & (df["p"]<=0.50)].copy()
    sub2["p_rank"] = sub2.groupby("event")["p"].rank(ascending=False).astype(int)
    sub2["event_n"] = sub2.groupby("event")["slug"].transform("count")
    sub2 = sub2[sub2["event_n"] >= 5]
    g = sub2.groupby("p_rank").agg(
        n=("pnl","size"), mean_pnl=("pnl","mean")
    )
    g["mean_pnl_pct"]=(g["mean_pnl"]*100).round(1)
    print(g.drop(columns=["mean_pnl"]).head(10).to_string())

    # C38: Post-drawdown analysis — after 3+ consecutive losses, does next bet recover?
    print("\n" + "=" * 80)
    print("C38: Edge recovery after drawdown")
    print("=" * 80)
    chronological = df[(df["p"]>=0.25) & (df["p"]<=0.36)].copy().sort_values("closed_time").reset_index(drop=True)
    losses = 0
    bins = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[]}
    for _, r in chronological.iterrows():
        if losses in bins:
            bins[losses].append(r["pnl"])
        if r["yes_won"]:
            losses = 0
        else:
            losses += 1
    for k, v in bins.items():
        if len(v) < 5: continue
        mean_p = np.mean(v)*100
        print(f"  After {k} consecutive losses: n={len(v)}, next-bet mean PnL={mean_p:+.1f}%")

    # C39: Per-tier weekly performance (is one tier decaying faster?)
    print("\n" + "=" * 80)
    print("C39: Weekly PnL by tier")
    print("=" * 80)
    df["week"] = df["closed_time"].dt.to_period("W").astype(str)
    for tier_name, cond in [
        ("S (p 0.25-0.36)", (df["p"]>=0.25)&(df["p"]<=0.36)),
        ("B (p 0.10-0.15)", (df["p"]>=0.10)&(df["p"]<=0.15)),
    ]:
        sub = df[cond & (df["volume"]>=10000) & df["local_hour"].apply(is_good_close_hour)]
        g = sub.groupby("week").agg(n=("pnl","size"), m=("pnl","mean"))
        g["m_pct"] = (g["m"]*100).round(1)
        print(f"\n{tier_name}:")
        print(g.drop(columns=["m"]).to_string())

    # C40: Top cities stability across weeks
    print("\n" + "=" * 80)
    print("C40: Top 5 cities consistency across weeks")
    print("=" * 80)
    sub = df[(df["p"]>=0.25) & (df["p"]<=0.36) & (df["volume"]>=10000)]
    city_week = sub.groupby(["city","week"]).agg(n=("pnl","size"), m=("pnl","mean"))
    city_week["m_pct"] = (city_week["m"]*100).round(1)
    # Check which cities are positive across multiple weeks
    city_weekly_count = sub.groupby("city")["week"].nunique()
    top_cities = city_weekly_count[city_weekly_count >= 3].index
    results = []
    for city in top_cities:
        sub_c = sub[sub["city"]==city]
        weekly_means = sub_c.groupby("week")["pnl"].mean()
        pos_weeks = (weekly_means > 0).sum()
        total_weeks = len(weekly_means)
        results.append({
            "city": city, "n": len(sub_c),
            "pos_weeks": pos_weeks, "total_weeks": total_weeks,
            "pos_pct": round(pos_weeks/total_weeks*100, 0),
            "overall_mean_pct": round(sub_c["pnl"].mean()*100, 1),
        })
    pr = pd.DataFrame(results).sort_values("pos_pct", ascending=False)
    print(pr.to_string(index=False))


if __name__ == "__main__":
    main()

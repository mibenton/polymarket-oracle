"""Cycle 30: Use within-event unity constraint as signal.

For each weather event (city-date), sum of all bucket implied probs should ≈ 1.
If sum < 0.95 → market systematically under-pricing the event → EDGE
If sum > 1.05 → market over-pricing → NO side better

This is self-referential (no external data) and untested.
"""
import re
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '.')
from cycle9_weather_segment import load

TAKER_FEE = 0.01


def event_key(slug: str) -> str:
    s = re.sub(r'-[0-9]+(pt[0-9]+)?(c|f)?(orhigher|orabove|orbelow|orlower)?$',
               '', (slug or '').lower())
    s = re.sub(r'-[0-9]+(-[0-9]+)?(f|c)?$', '', s)
    return s


def main():
    df = load()
    df["event"] = df["slug"].apply(event_key)
    df["pnl"] = np.where(df["yes_won"], 1/df["p"]-1-TAKER_FEE, -1-TAKER_FEE)

    # For each event, sum all child bucket implied probs
    sums = df.groupby("event")["p"].sum().rename("event_sum")
    counts = df.groupby("event")["slug"].count().rename("event_count")
    df = df.merge(sums, on="event").merge(counts, on="event")

    # Filter: events with at least 5 children
    df = df[df["event_count"] >= 5].copy()
    print(f"Events with 5+ children: {df['event'].nunique()}, markets: {len(df)}")
    print(f"\nDistribution of event_sum (should be ~1.0):")
    print(df.groupby("event")["event_sum"].first().describe())

    # Analyze: does low event_sum correlate with positive edge?
    print(f"\n=== Event sum buckets ===")
    bins = [0, 0.85, 0.95, 1.0, 1.05, 1.15, 2.0]
    labels = ["<0.85 (under)","0.85-0.95","0.95-1.0","1.0-1.05","1.05-1.15",">1.15 (over)"]
    df["sum_bucket"] = pd.cut(df["event_sum"], bins=bins, labels=labels, include_lowest=True)
    g = df.groupby("sum_bucket", observed=True).agg(
        n=("pnl","size"),
        n_events=("event","nunique"),
        mean_pnl=("pnl","mean"),
        win=("yes_won","mean"),
    )
    g["win_pct"] = (g["win"]*100).round(0)
    g["mean_pnl_pct"] = (g["mean_pnl"]*100).round(1)
    g = g.drop(columns=["mean_pnl","win"])
    print(g.to_string())

    # Specifically at price bucket 0.25-0.36 (Tier S range), does low sum help more?
    print(f"\n=== At Tier S price (0.25-0.36) x event_sum ===")
    sub = df[(df["p"]>=0.25) & (df["p"]<=0.36)]
    gx = sub.groupby("sum_bucket", observed=True).agg(
        n=("pnl","size"),
        mean_pnl=("pnl","mean"),
        win=("yes_won","mean"),
    )
    gx["win_pct"] = (gx["win"]*100).round(0)
    gx["mean_pnl_pct"] = (gx["mean_pnl"]*100).round(1)
    gx = gx.drop(columns=["mean_pnl","win"])
    print(gx[gx["n"]>=15].to_string())

    # Top low-sum events
    print(f"\n=== Top under-priced events (event_sum < 0.95) ===")
    low = df[df["event_sum"] < 0.95].copy()
    if len(low):
        evt_summary = low.groupby("event").agg(
            n_buckets=("pnl","size"),
            sum=("event_sum","first"),
            n_won=("yes_won","sum"),
            total_pnl=("pnl","sum"),
        ).sort_values("total_pnl", ascending=False).head(10)
        print(evt_summary.to_string())


if __name__ == "__main__":
    main()

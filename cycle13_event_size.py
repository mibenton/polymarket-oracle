"""Cycle 13: Does number of child buckets per event matter?

An event with 15 temperature buckets spreads probability thinly across each.
An event with 5 buckets concentrates. Hypothesis: more buckets = more retail
under-pricing of central bucket (because each gets <1/N probability intuitively).
"""
import re
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '.')
from cycle9_weather_segment import load

TAKER_FEE = 0.01


def event_key(slug: str) -> str:
    if not isinstance(slug, str):
        return ""
    # strip trailing temperature tag like -17c, -65-66f, -corhigher
    s = re.sub(r'-[0-9]+(pt[0-9]+)?(c|f)?(orhigher|orabove|orbelow|orlower)?$',
               '', slug.lower())
    s = re.sub(r'-[0-9]+(-[0-9]+)?(f|c)?$', '', s)
    return s


def main():
    df = load()
    df["event"] = df["slug"].apply(event_key)
    child_count = df.groupby("event")["slug"].nunique()
    df["event_size"] = df["event"].map(child_count)

    print(f"Event size distribution:")
    print(child_count.describe())

    sub = df[(df["p"] >= 0.20) & (df["p"] <= 0.40)].copy()
    sub["pnl"] = np.where(sub["yes_won"], 1/sub["p"]-1-TAKER_FEE, -1-TAKER_FEE)

    print(f"\n=== Weather 0.20-0.40 by event size ===")
    bins = [0, 3, 5, 8, 12, 20, 200]
    labels = ["1-3","4-5","6-8","9-12","13-20",">20"]
    sub["esb"] = pd.cut(sub["event_size"], bins=bins, labels=labels)
    g = sub.groupby("esb", observed=True).agg(
        n=("pnl","size"),
        win=("yes_won","mean"),
        mean_pnl=("pnl","mean"),
    )
    g["win_pct"] = (g["win"]*100).round(0)
    g["mean_pnl_pct"] = (g["mean_pnl"]*100).round(1)
    g = g.drop(columns=["win","mean_pnl"])
    print(g.to_string())

    # Combined with price tier
    print(f"\n=== Event size x Price bucket ===")
    sub["pb"] = pd.cut(sub["p"], bins=[0.20,0.25,0.30,0.36,0.40], labels=["0.20-0.25","0.25-0.30","0.30-0.36","0.36-0.40"])
    gx = sub.groupby(["esb","pb"], observed=True).agg(
        n=("pnl","size"),
        mean_pnl=("pnl","mean"),
    )
    gx["mean_pnl_pct"] = (gx["mean_pnl"]*100).round(1)
    gx = gx.drop(columns=["mean_pnl"])
    gx = gx[gx["n"] >= 15]
    print(gx.to_string())


if __name__ == "__main__":
    main()

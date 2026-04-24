"""Cycle 12: Fine-grained volume analysis.

Cycle 9 found volume >$100k had +110% PnL (but n=6). Drill down:
- $20k-$50k vs $50k-$100k vs $100k-$250k vs >$250k
- Within each, check win rate and mean PnL
"""
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '.')
from cycle9_weather_segment import load

TAKER_FEE = 0.01

def main():
    df = load()
    sub = df[(df["p"] >= 0.20) & (df["p"] <= 0.40)].copy()
    sub["pnl"] = np.where(sub["yes_won"], 1/sub["p"]-1-TAKER_FEE, -1-TAKER_FEE)
    print(f"Weather 0.20-0.40 n={len(sub)}")

    print(f"\n=== Fine volume tiers ===")
    bins = [0, 5000, 10000, 20000, 50000, 100000, 250000, 1e9]
    labels = ["<5k","5-10k","10-20k","20-50k","50-100k","100-250k",">250k"]
    sub["vol"] = pd.cut(sub["volume"], bins=bins, labels=labels)
    g = sub.groupby("vol", observed=True).agg(
        n=("pnl","size"),
        win=("yes_won","mean"),
        mean_pnl=("pnl","mean"),
        total_pnl=("pnl","sum"),
    )
    g["win_pct"] = (g["win"]*100).round(0)
    g["mean_pnl_pct"] = (g["mean_pnl"]*100).round(1)
    g["total_pnl"] = g["total_pnl"].round(1)
    g = g.drop(columns=["win","mean_pnl"])
    print(g.to_string())

    # Cross: volume x price bucket
    print(f"\n=== Volume x Price bucket ===")
    sub["pb"] = pd.cut(sub["p"], bins=[0.20,0.25,0.30,0.36,0.40], labels=["0.20-0.25","0.25-0.30","0.30-0.36","0.36-0.40"])
    gx = sub.groupby(["vol","pb"], observed=True).agg(
        n=("pnl","size"),
        mean_pnl=("pnl","mean"),
    )
    gx["mean_pnl_pct"] = (gx["mean_pnl"]*100).round(1)
    gx = gx.drop(columns=["mean_pnl"])
    print(gx[gx["n"]>=20].to_string())


if __name__ == "__main__":
    main()

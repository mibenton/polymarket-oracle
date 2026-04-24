"""Cycle 76: Sports totals (over/under, spread) — 43k markets unexplored.

Cycle 7 killed sports match-winner. But totals are structurally different:
- Match: ternary information (team A strength, team B, matchup)
- Total: continuous line-based bet
Might have different retail bias profile.
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

    m = have[["id","slug","question","closed_time","yes_won","yes_outcome",
              "no_outcome","volume","target_ts"]].rename(columns={"id":"market_id"})
    merged = pd.merge_asof(
        m.sort_values("target_ts"),
        prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6*3600),
    ).dropna(subset=["p"])
    merged["yes_won_int"] = merged["yes_won"].astype(int)
    merged["pnl"] = np.where(merged["yes_won"], 1/merged["p"]-1-TAKER_FEE, -1-TAKER_FEE)
    return merged


def categorize_total(slug, question):
    s = (slug or "").lower()
    q = (question or "").lower()
    # Only totals-like
    has_total = any(k in s for k in ["total","-ou-","o-u","over-under","spread"]) or \
                any(k in q for k in [" o/u ","over/under","total runs","total goals",
                                      "total points","total sets"])
    if not has_total:
        return None
    # Sport breakdown
    if "mlb-" in s or "mlb_" in s: return "mlb_total"
    if "nba-" in s: return "nba_total"
    if "nfl-" in s: return "nfl_total"
    if "nhl-" in s: return "nhl_total"
    if "ncaa" in s or "cbb-" in s or "cfb-" in s: return "ncaa_total"
    if "ufc-" in s: return "ufc_total"
    if "atp-" in s or "wta-" in s: return "tennis_total"
    if "fif-" in s or "epl-" in s or "ucl-" in s or "uel-" in s or \
       "bun-" in s or "fl1-" in s or "sai-" in s: return "soccer_total"
    if any(k in s for k in ["cs2-","val-","lol-","dota"]): return "esports_total"
    return "other_total"


def main():
    df = load()
    df["cat"] = df.apply(lambda r: categorize_total(r["slug"], r["question"]), axis=1)
    totals = df[df["cat"].notna()].copy()
    print(f"Sports totals with prices: {len(totals):,}")

    # Overall
    print(f"\n=== Per sport ===")
    g = totals.groupby("cat").agg(
        n=("pnl","size"),
        win=("yes_won","mean"),
        mean_pnl=("pnl","mean"),
    )
    g["win_pct"] = (g["win"]*100).round(0)
    g["mean_pnl_pct"] = (g["mean_pnl"]*100).round(1)
    g = g.drop(columns=["win","mean_pnl"]).sort_values("mean_pnl_pct", ascending=False)
    print(g.to_string())

    # By price bucket × sport
    print(f"\n=== Price bucket x sport (n>=30) ===")
    totals["pb"] = pd.cut(totals["p"], bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    gx = totals.groupby(["cat","pb"], observed=True).agg(
        n=("pnl","size"),
        mean_pnl=("pnl","mean"),
        win=("yes_won","mean"),
    )
    gx["mean_pnl_pct"] = (gx["mean_pnl"]*100).round(1)
    gx["win_pct"] = (gx["win"]*100).round(0)
    gx = gx[gx["n"] >= 30].drop(columns=["mean_pnl","win"])
    gx = gx.sort_values("mean_pnl_pct", ascending=False)
    print(gx.to_string())

    # Best cells
    print(f"\n=== TOP 10 pockets (mean PnL >0 and n>=30) ===")
    top = gx[gx["mean_pnl_pct"] > 0].head(10)
    print(top.to_string())


if __name__ == "__main__":
    main()

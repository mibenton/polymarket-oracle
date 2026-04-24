"""Cycle 14: Multi-bucket portfolio — bet on multiple adjacent buckets simultaneously.

Hypothesis: When forecast is for a specific value, buying 3-5 buckets covering
±2°C captures the distribution with less variance than single-bucket bet.

Test: For each event (city-date), what would happen if we bought ALL buckets
in the 0.25-0.36 range? vs. cherry-picking single best bucket?
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
    df["pnl_1"] = np.where(df["yes_won"], 1/df["p"]-1-TAKER_FEE, -1-TAKER_FEE)

    # For each event, find buckets in 0.25-0.36 range and simulate
    # "bet $1 per bucket that qualifies"
    print(f"\n=== Multi-bucket portfolio test ===")
    qualifying = df[(df["p"] >= 0.25) & (df["p"] <= 0.36)].copy()
    print(f"Buckets in 0.25-0.36: {len(qualifying):,}")

    by_event = qualifying.groupby("event").agg(
        n_buckets=("slug","count"),
        total_pnl=("pnl_1","sum"),
        any_won=("yes_won","any"),
    )
    print(f"\nEvents with at least 1 qualifying bucket: {len(by_event)}")
    by_event["avg_pnl_per_bucket"] = by_event["total_pnl"] / by_event["n_buckets"]

    print(f"\n=== Multi-bucket strategy: bet $1 on each qualifying bucket per event ===")
    print(f"Mean n_buckets per event: {by_event['n_buckets'].mean():.2f}")
    print(f"Mean total pnl per event: ${by_event['total_pnl'].mean():.2f}")
    print(f"Pct events with at least one winner: {by_event['any_won'].mean()*100:.1f}%")

    # Distribution of events
    print(f"\n=== Events by number of qualifying buckets ===")
    dist = by_event.groupby("n_buckets").agg(
        n_events=("total_pnl","size"),
        mean_total_pnl=("total_pnl","mean"),
        pct_winner=("any_won","mean"),
    )
    dist["mean_total_pnl"] = dist["mean_total_pnl"].round(2)
    dist["pct_winner"] = (dist["pct_winner"]*100).round(0)
    print(dist.to_string())

    # Key metric: portfolio sharpe vs single-bet sharpe
    single_bets = qualifying["pnl_1"]
    print(f"\n=== Single vs Portfolio ===")
    print(f"Single bucket:")
    print(f"  mean = ${single_bets.mean():+.2f}  std = ${single_bets.std():.2f}")
    print(f"  sharpe = {single_bets.mean()/single_bets.std():+.3f}")

    # Portfolio: sum of pnl within event, then average across events
    evt_pnl = by_event["total_pnl"]
    # normalize to per-bucket so comparable
    evt_pnl_norm = by_event["total_pnl"] / by_event["n_buckets"]
    print(f"\nPortfolio (avg per-event-bucket):")
    print(f"  mean = ${evt_pnl_norm.mean():+.2f}  std = ${evt_pnl_norm.std():.2f}")
    print(f"  sharpe = {evt_pnl_norm.mean()/evt_pnl_norm.std():+.3f}")


if __name__ == "__main__":
    main()

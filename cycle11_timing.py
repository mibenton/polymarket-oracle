"""Cycle 11: Which entry timing gives best edge?

Compare T-24h / T-48h / T-72h / T-120h / T-168h for weather exact-bucket at various
price buckets. Hypothesis: later entry (T-24) has more information → edge might shrink
OR grow (if market still irrational at last moment).
"""
from pathlib import Path
import numpy as np
import pandas as pd

TAKER_FEE = 0.01


def build_entries(markets, prices, offset_h):
    have = markets[markets["id"].isin(prices["market_id"].unique())].copy()
    have = have[have["duration_h"] >= offset_h + 6].copy()  # need buffer
    have["target_ts"] = (have["closed_time"] - pd.Timedelta(hours=offset_h)).astype("int64") // 10**9

    m = have[["id","slug","closed_time","yes_won","volume","target_ts"]].rename(columns={"id":"market_id"})
    merged = pd.merge_asof(
        m.sort_values("target_ts"),
        prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6*3600),
    ).dropna(subset=["p"])
    merged["yes_won_int"] = merged["yes_won"].astype(int)
    merged = merged[
        merged["slug"].str.contains("highest-temperature-in-", case=False, na=False) &
        ~merged["slug"].str.contains("orhigher|orabove|orbelow|orlower",
                                      case=False, regex=True, na=False)
    ]
    merged["pnl"] = np.where(
        merged["yes_won"], 1/merged["p"]-1-TAKER_FEE, -1-TAKER_FEE
    )
    return merged


def main():
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

    offsets = [12, 24, 48, 72, 120, 168]
    buckets = [(0.10, 0.15, "B"), (0.20, 0.30, "A+"), (0.30, 0.36, "S"), (0.36, 0.40, "A")]

    print(f"\n{'='*70}")
    print("TIMING COMPARISON: entry at T-Nh before close, weather exact")
    print(f"{'='*70}")
    rows = []
    for offset in offsets:
        ent = build_entries(markets, prices, offset)
        for lo, hi, tier in buckets:
            sub = ent[(ent["p"] >= lo) & (ent["p"] <= hi)]
            if len(sub) < 30:
                continue
            rows.append({
                "offset_h": offset,
                "tier": tier,
                "bucket": f"{lo:.2f}-{hi:.2f}",
                "n": len(sub),
                "win_rate_pct": round(sub["yes_won_int"].mean()*100, 1),
                "mean_pnl_pct": round(sub["pnl"].mean()*100, 1),
                "sum_pnl": round(sub["pnl"].sum(), 1),
            })
    df = pd.DataFrame(rows).sort_values(["tier","offset_h"])
    print(df.to_string(index=False))

    # Find best offset per bucket
    print(f"\n{'='*70}")
    print("BEST OFFSET per bucket (by mean_pnl_pct)")
    print(f"{'='*70}")
    for tier in ["S","A+","A","B"]:
        sub = df[df["tier"] == tier]
        if sub.empty:
            continue
        best = sub.loc[sub["mean_pnl_pct"].idxmax()]
        print(f"  Tier {tier:<3}: T-{best['offset_h']:>3}h  →  {best['mean_pnl_pct']:+.1f}%  (n={best['n']})")

    df.to_csv("data/results/cycle11_timing.csv", index=False)


if __name__ == "__main__":
    main()

"""Final robust analysis: 12k markets, weekly out-of-sample splits + bootstrap CI."""
from pathlib import Path
import numpy as np
import pandas as pd

TAKER_FEE = 0.01


def load_data():
    ext = pd.read_parquet("data/markets_ext.parquet")
    orig = pd.read_parquet("data/markets.parquet")
    markets = pd.concat([ext, orig], ignore_index=True).drop_duplicates("id")
    markets["closed_time"] = pd.to_datetime(markets["closed_time"], utc=True, errors="coerce")
    markets["start_date"] = pd.to_datetime(markets["start_date"], utc=True, errors="coerce")
    markets["duration_h"] = (markets["closed_time"] - markets["start_date"]).dt.total_seconds() / 3600

    frames = []
    for path in ["data/prices.parquet", "data/prices_ext.parquet"]:
        if Path(path).exists():
            frames.append(pd.read_parquet(path))
    prices = pd.concat(frames, ignore_index=True).drop_duplicates(["market_id", "t"])
    return markets, prices


def load_entries(markets, prices, offset_h):
    markets = markets[markets["id"].isin(prices["market_id"].unique())]
    m = markets[["id", "closed_time", "yes_won", "volume", "slug"]].rename(columns={"id": "market_id"})
    m["target_ts"] = (m["closed_time"] - pd.Timedelta(hours=offset_h)).astype("int64") // 10**9
    m_sorted = m.sort_values("target_ts")
    p_sorted = prices.sort_values("t")
    merged = pd.merge_asof(
        m_sorted, p_sorted, left_on="target_ts", right_on="t",
        by="market_id", direction="backward", tolerance=int(6 * 3600),
    )
    return merged.dropna(subset=["p"])


def compute_pnl(df):
    df = df.copy()
    df["fav_price"] = np.where(df["p"] >= 0.5, df["p"], 1 - df["p"])
    df["fav_won"] = np.where(df["p"] >= 0.5, df["yes_won"].astype(bool),
                             ~df["yes_won"].astype(bool))
    b = 1 / df["fav_price"].values - 1
    df["pnl"] = np.where(df["fav_won"], b, -1) - TAKER_FEE
    return df


def bootstrap_ci(pnl: np.ndarray, n_boot: int = 5000, seed: int = 42) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    means = [pnl[rng.integers(0, len(pnl), len(pnl))].mean() for _ in range(n_boot)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def weekly_analysis(df: pd.DataFrame, lo: float, hi: float,
                    vol_lo: float, vol_hi: float, label: str) -> pd.DataFrame:
    sub = df[(df["fav_price"] >= lo) & (df["fav_price"] <= hi) &
             (df["volume"] >= vol_lo) & (df["volume"] <= vol_hi)].copy()
    sub["week"] = sub["closed_time"].dt.to_period("W").astype(str)
    g = sub.groupby("week").agg(
        n=("pnl", "size"),
        mean_pnl=("pnl", "mean"),
        win_rate=("fav_won", lambda x: x.astype(int).mean()),
    ).reset_index()
    g["strategy"] = label
    return g


def test_strategy(df: pd.DataFrame, lo: float, hi: float,
                  vol_lo: float, vol_hi: float, label: str) -> dict:
    sub = df[(df["fav_price"] >= lo) & (df["fav_price"] <= hi) &
             (df["volume"] >= vol_lo) & (df["volume"] <= vol_hi)]
    if len(sub) < 20:
        return {"label": label, "n": len(sub)}
    pnl = sub["pnl"].values
    ci_low, ci_high = bootstrap_ci(pnl)
    # t-stat for mean > 0
    mean = pnl.mean()
    se = pnl.std(ddof=1) / np.sqrt(len(pnl))
    t_stat = mean / se if se > 0 else 0
    return {
        "label": label,
        "n": len(sub),
        "mean_pnl": float(mean),
        "ci_95_low": ci_low,
        "ci_95_high": ci_high,
        "win_rate": float(sub["fav_won"].astype(int).mean()),
        "sharpe": float(mean / pnl.std(ddof=1)) if pnl.std() > 0 else 0,
        "t_stat": float(t_stat),
        "significant": ci_low > 0,
    }


def main():
    markets, prices = load_data()
    print(f"Data: {len(prices):,} price points, {prices['market_id'].nunique():,} markets")
    print(f"      time window: {markets['closed_time'].min()} -> {markets['closed_time'].max()}")

    print("\n" + "="*80)
    print("CANDIDATE STRATEGIES: 95% bootstrap CI on mean PnL (after 1% fee)")
    print("="*80)

    results_72 = []
    for offset_h in [24, 72, 168]:
        df = compute_pnl(load_entries(markets, prices, offset_h))

        candidates = [
            # (price lo, hi, vol lo, vol hi, label)
            (0.88, 0.96, 5_000, 10_000, "Fav 0.88-0.96, vol 5-10k"),
            (0.88, 0.96, 10_000, 20_000, "Fav 0.88-0.96, vol 10-20k"),
            (0.88, 0.96, 20_000, 50_000, "Fav 0.88-0.96, vol 20-50k"),
            (0.88, 0.96, 50_000, 100_000, "Fav 0.88-0.96, vol 50-100k"),
            (0.88, 0.96, 100_000, 1e7, "Fav 0.88-0.96, vol 100k+"),
            (0.90, 0.96, 5_000, 20_000, "Fav 0.90-0.96, vol 5-20k"),
            (0.95, 0.99, 5_000, 50_000, "Fav 0.95-0.99, vol 5-50k"),
            (0.95, 0.99, 20_000, 100_000, "Fav 0.95-0.99, vol 20-100k"),
            (0.70, 0.88, 5_000, 20_000, "Fav 0.70-0.88, vol 5-20k"),
        ]
        print(f"\n--- ENTRY OFFSET: {offset_h}h ---")
        print(f"{'strategy':<38} {'n':>5} {'mean':>8} {'CI_low':>8} {'CI_hi':>8} "
              f"{'win%':>6} {'sharpe':>8} {'sig':>4}")
        for args in candidates:
            r = test_strategy(df, *args)
            if r.get("n", 0) < 20:
                continue
            print(f"{r['label']:<38} {r['n']:>5} {r['mean_pnl']:>+7.3%} "
                  f"{r['ci_95_low']:>+7.3%} {r['ci_95_high']:>+7.3%} "
                  f"{r['win_rate']*100:>5.1f}% {r['sharpe']:>+8.3f} "
                  f"{'YES' if r['significant'] else 'NO':>4}")
            if offset_h == 72:
                results_72.append(r)

    # Weekly stability test for winners at 72h
    df72 = compute_pnl(load_entries(markets, prices, 72))
    print("\n" + "="*80)
    print("WEEKLY STABILITY TEST (72h offset, top 3 candidates)")
    print("="*80)
    top = sorted(
        [r for r in results_72 if r.get("n", 0) >= 20],
        key=lambda x: x.get("mean_pnl", -9), reverse=True
    )[:3]
    for r in top:
        label = r["label"]
        print(f"\n{label}:")
        lo, hi, vol_lo, vol_hi = next(
            (c[0], c[1], c[2], c[3]) for c in [
                (0.88, 0.96, 5_000, 10_000, "Fav 0.88-0.96, vol 5-10k"),
                (0.88, 0.96, 10_000, 20_000, "Fav 0.88-0.96, vol 10-20k"),
                (0.88, 0.96, 20_000, 50_000, "Fav 0.88-0.96, vol 20-50k"),
                (0.88, 0.96, 50_000, 100_000, "Fav 0.88-0.96, vol 50-100k"),
                (0.88, 0.96, 100_000, 1e7, "Fav 0.88-0.96, vol 100k+"),
                (0.90, 0.96, 5_000, 20_000, "Fav 0.90-0.96, vol 5-20k"),
                (0.95, 0.99, 5_000, 50_000, "Fav 0.95-0.99, vol 5-50k"),
                (0.95, 0.99, 20_000, 100_000, "Fav 0.95-0.99, vol 20-100k"),
                (0.70, 0.88, 5_000, 20_000, "Fav 0.70-0.88, vol 5-20k"),
            ] if c[4] == label
        )
        wk = weekly_analysis(df72, lo, hi, vol_lo, vol_hi, label)
        print(wk.to_string(index=False))

    print("\n" + "="*80)
    print("CONCLUSIONS")
    print("="*80)
    sig = [r for r in results_72 if r.get("significant", False)]
    print(f"Strategies with CI_95_low > 0 at 72h: {len(sig)}")
    for r in sig:
        print(f"  * {r['label']}: mean {r['mean_pnl']:+.2%} "
              f"(CI [{r['ci_95_low']:+.2%}, {r['ci_95_high']:+.2%}])")


if __name__ == "__main__":
    main()

"""Analyze extended dataset: combine markets_ext.parquet + both price files.
Test edge persistence across months."""
from pathlib import Path
import numpy as np
import pandas as pd

TAKER_FEE = 0.01


def load_combined() -> tuple[pd.DataFrame, pd.DataFrame]:
    # combine market metadata (ext is the superset)
    ext = pd.read_parquet("data/markets_ext.parquet")
    orig = pd.read_parquet("data/markets.parquet")
    markets = pd.concat([ext, orig], ignore_index=True).drop_duplicates("id")
    markets["closed_time"] = pd.to_datetime(markets["closed_time"], utc=True, errors="coerce")
    markets["start_date"] = pd.to_datetime(markets["start_date"], utc=True, errors="coerce")
    markets["duration_h"] = (markets["closed_time"] - markets["start_date"]).dt.total_seconds() / 3600

    # combine prices
    frames = []
    for path in ["data/prices.parquet", "data/prices_ext.parquet"]:
        if Path(path).exists():
            frames.append(pd.read_parquet(path))
    prices = pd.concat(frames, ignore_index=True).drop_duplicates(["market_id", "t"])
    return markets, prices


def load_entries(markets: pd.DataFrame, prices: pd.DataFrame, offset_h: int) -> pd.DataFrame:
    markets = markets[markets["id"].isin(prices["market_id"].unique())]
    m = markets[["id", "closed_time", "start_date", "yes_won", "volume", "slug"]].rename(
        columns={"id": "market_id"}
    )
    m["target_ts"] = (m["closed_time"] - pd.Timedelta(hours=offset_h)).astype("int64") // 10**9
    m_sorted = m.sort_values("target_ts")
    p_sorted = prices.sort_values("t")
    merged = pd.merge_asof(
        m_sorted, p_sorted, left_on="target_ts", right_on="t",
        by="market_id", direction="backward", tolerance=int(6 * 3600),
    )
    return merged.dropna(subset=["p"])


def favorite(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["fav_price"] = np.where(df["p"] >= 0.5, df["p"], 1 - df["p"])
    df["fav_won"] = np.where(df["p"] >= 0.5, df["yes_won"].astype(bool),
                             ~df["yes_won"].astype(bool))
    return df


def strat_pnl(df: pd.DataFrame, lo: float, hi: float, vol_lo: float, vol_hi: float) -> dict:
    df = favorite(df)
    sub = df[(df["fav_price"] >= lo) & (df["fav_price"] <= hi) &
             (df["volume"] >= vol_lo) & (df["volume"] <= vol_hi)].copy()
    if len(sub) < 10:
        return {"n": len(sub)}
    b = 1 / sub["fav_price"].values - 1
    wins = sub["fav_won"].astype(bool).values
    pnl = np.where(wins, b, -1) - TAKER_FEE
    return {
        "n": len(sub),
        "mean_pnl": float(pnl.mean()),
        "std": float(pnl.std()),
        "win_rate": float(wins.mean()),
        "sharpe": float(pnl.mean() / pnl.std()) if pnl.std() > 0 else 0,
    }


def monthly_edge(df: pd.DataFrame, lo: float, hi: float, vol_lo: float, vol_hi: float) -> pd.DataFrame:
    df = favorite(df)
    sub = df[(df["fav_price"] >= lo) & (df["fav_price"] <= hi) &
             (df["volume"] >= vol_lo) & (df["volume"] <= vol_hi)].copy()
    b = 1 / sub["fav_price"].values - 1
    wins = sub["fav_won"].astype(bool).values
    sub["pnl"] = np.where(wins, b, -1) - TAKER_FEE
    sub["month"] = sub["closed_time"].dt.tz_convert("UTC").dt.to_period("M").astype(str)
    g = sub.groupby("month").agg(
        n=("pnl", "size"),
        mean_pnl=("pnl", "mean"),
        win_rate=("fav_won", lambda x: x.astype(int).mean()),
    ).reset_index()
    return g


def volume_band_scan(df: pd.DataFrame, lo: float, hi: float) -> pd.DataFrame:
    df = favorite(df)
    sub = df[(df["fav_price"] >= lo) & (df["fav_price"] <= hi)].copy()
    b = 1 / sub["fav_price"].values - 1
    wins = sub["fav_won"].astype(bool).values
    sub["pnl"] = np.where(wins, b, -1) - TAKER_FEE
    bands = [(5_000, 10_000), (10_000, 20_000), (20_000, 50_000),
             (50_000, 100_000), (100_000, 500_000), (500_000, 1e7)]
    rows = []
    for lo_v, hi_v in bands:
        m = (sub["volume"] >= lo_v) & (sub["volume"] < hi_v)
        if m.sum() < 20:
            continue
        rows.append({
            "band": f"${lo_v//1000}k-${int(hi_v//1000)}k",
            "n": int(m.sum()),
            "mean_pnl": float(sub.loc[m, "pnl"].mean()),
            "win_rate": float(sub.loc[m, "fav_won"].astype(int).mean()),
        })
    return pd.DataFrame(rows)


def main():
    markets, prices = load_combined()
    print(f"combined markets: {len(markets):,}")
    print(f"combined price points: {len(prices):,}")
    print(f"markets with prices: {prices['market_id'].nunique():,}")
    print(f"time range: {markets['closed_time'].min()} -> {markets['closed_time'].max()}")

    for offset_h in [24, 72, 168]:
        print(f"\n{'='*70}\nENTRY OFFSET: {offset_h}h\n{'='*70}")
        entries = load_entries(markets, prices, offset_h)
        print(f"entries: {len(entries):,}")

        # Core strategy at various bands
        print(f"\nCORE STRATEGY: favorite 0.88-0.96, by volume band:")
        print(volume_band_scan(entries, 0.88, 0.96).to_string(index=False))

        print(f"\nSTRATEGY COMPARISONS (vol $20k-$100k):")
        for lo, hi, label in [
            (0.88, 0.96, "Fav 0.88-0.96"),
            (0.90, 0.96, "Fav 0.90-0.96"),
            (0.92, 0.98, "Fav 0.92-0.98"),
            (0.95, 0.99, "Fav 0.95-0.99"),
            (0.70, 0.88, "Fav 0.70-0.88"),
        ]:
            r = strat_pnl(entries, lo, hi, 20_000, 100_000)
            if r["n"] >= 10:
                print(f"  {label}: n={r['n']:>5}  mean={r['mean_pnl']:+.4f}  "
                      f"win={r['win_rate']*100:.1f}%  sharpe={r['sharpe']:+.3f}")

    # Time series: monthly edge for core strategy
    print(f"\n{'='*70}\nMONTHLY EDGE: Fav 0.88-0.96, vol $20k-$100k, 72h out\n{'='*70}")
    entries = load_entries(markets, prices, 72)
    monthly = monthly_edge(entries, 0.88, 0.96, 20_000, 100_000)
    print(monthly.to_string(index=False))


if __name__ == "__main__":
    main()

"""Validation cycle: favorite-side analysis, category breakdown, time-weighted return."""
from pathlib import Path
import numpy as np
import pandas as pd

MARKETS = Path("data/markets.parquet")
PRICES = Path("data/prices.parquet")
TAKER_FEE = 0.01


def load_entries(offset_h: int) -> pd.DataFrame:
    markets = pd.read_parquet(MARKETS)
    prices = pd.read_parquet(PRICES)
    markets = markets[markets["id"].isin(prices["market_id"].unique())]
    m = markets[["id", "closed_time", "start_date", "yes_won", "volume",
                 "neg_risk", "question", "slug"]].rename(columns={"id": "market_id"})
    m["target_ts"] = (m["closed_time"] - pd.Timedelta(hours=offset_h)).astype("int64") // 10**9
    m_sorted = m.sort_values("target_ts")
    p_sorted = prices.sort_values("t")
    merged = pd.merge_asof(
        m_sorted, p_sorted, left_on="target_ts", right_on="t",
        by="market_id", direction="backward", tolerance=int(6 * 3600),
    )
    return merged.dropna(subset=["p"])


def favorite_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """For each market, bet on the FAVORITE side (higher implied prob)."""
    df = df.copy()
    # favorite = side with higher prob; if p>=0.5 favorite=YES, else favorite=NO
    df["fav_side"] = np.where(df["p"] >= 0.5, "YES", "NO")
    df["fav_price"] = np.where(df["p"] >= 0.5, df["p"], 1 - df["p"])
    df["fav_won"] = np.where(df["p"] >= 0.5, df["yes_won"], ~df["yes_won"].astype(bool))
    return df


def scan_favorite(df: pd.DataFrame, step: float = 0.02) -> pd.DataFrame:
    df = favorite_analysis(df)
    rows = []
    for lo in np.arange(0.50, 0.99, step):
        for hi in np.arange(lo + 0.02, 1.01, step):
            sub = df[(df["fav_price"] >= lo) & (df["fav_price"] <= hi)]
            if len(sub) < 30:
                continue
            b = 1 / sub["fav_price"].values - 1
            wins = sub["fav_won"].astype(bool).values
            pnl = np.where(wins, b, -1) - TAKER_FEE
            rows.append({
                "lo": round(lo, 2), "hi": round(hi, 2),
                "n": len(sub),
                "mean_pnl": pnl.mean(),
                "std": pnl.std(),
                "sharpe": pnl.mean() / pnl.std() if pnl.std() > 0 else 0,
                "win_rate": wins.mean(),
            })
    return pd.DataFrame(rows).sort_values("mean_pnl", ascending=False)


def category_breakdown(df: pd.DataFrame, lo: float, hi: float) -> pd.DataFrame:
    """Break down best strategy by slug prefix (proxy for category)."""
    df = favorite_analysis(df)
    sub = df[(df["fav_price"] >= lo) & (df["fav_price"] <= hi)].copy()
    # extract category from slug (first token)
    sub["cat"] = sub["slug"].str.split("-").str[0]
    # PnL
    b = 1 / sub["fav_price"].values - 1
    wins = sub["fav_won"].astype(bool).values
    sub["pnl"] = np.where(wins, b, -1) - TAKER_FEE

    g = sub.groupby("cat").agg(
        n=("pnl", "size"),
        mean_pnl=("pnl", "mean"),
        win_rate=("fav_won", lambda x: x.astype(int).mean()),
    ).reset_index()
    return g[g["n"] >= 10].sort_values("mean_pnl", ascending=False)


def time_weighted_return(df: pd.DataFrame, lo: float, hi: float, offset_h: int) -> dict:
    """Annualized return accounting for hold time = offset_h."""
    df = favorite_analysis(df)
    sub = df[(df["fav_price"] >= lo) & (df["fav_price"] <= hi)].copy()
    b = 1 / sub["fav_price"].values - 1
    wins = sub["fav_won"].astype(bool).values
    pnl = np.where(wins, b, -1) - TAKER_FEE
    mean_bet_return = pnl.mean()
    hold_days = offset_h / 24
    # if capital can rotate every hold_days (bets are independent, parallel possible)
    # simplified: treat each bet as one slot of capital for hold_days
    annual_cycles = 365 / hold_days
    annual_return = (1 + mean_bet_return) ** annual_cycles - 1
    return {
        "n": int(len(sub)),
        "mean_bet_return": float(mean_bet_return),
        "hold_days": hold_days,
        "annual_cycles": annual_cycles,
        "annual_return_per_slot": float(annual_return),
    }


def check_volume_effect(df: pd.DataFrame, lo: float, hi: float) -> pd.DataFrame:
    """Does edge persist in high-volume (real) markets vs low-volume (zombie)?"""
    df = favorite_analysis(df)
    sub = df[(df["fav_price"] >= lo) & (df["fav_price"] <= hi)].copy()
    b = 1 / sub["fav_price"].values - 1
    wins = sub["fav_won"].astype(bool).values
    sub["pnl"] = np.where(wins, b, -1) - TAKER_FEE
    sub["vol_bucket"] = pd.cut(
        sub["volume"],
        bins=[0, 5000, 20000, 100000, 1e12],
        labels=["5-20k", "20-100k", "100k-1M", ">1M"],
    )
    g = sub.groupby("vol_bucket", observed=True).agg(
        n=("pnl", "size"),
        mean_pnl=("pnl", "mean"),
        win_rate=("fav_won", lambda x: x.astype(int).mean()),
    ).reset_index()
    return g


def main():
    print("=" * 70)
    print("VALIDATION CYCLE: bet-on-FAVORITE analysis")
    print("=" * 70)

    for offset_h in [24, 72, 168]:
        print(f"\n--- offset {offset_h}h ---")
        df = load_entries(offset_h)

        scan = scan_favorite(df)
        print("\nTop 10 favorite-side windows by mean PnL (n>=30):")
        print(scan.head(10).to_string(index=False))

        # Time-weighted return for top candidate
        best = scan.iloc[0]
        twr = time_weighted_return(df, best["lo"], best["hi"], offset_h)
        print(f"\nTime-weighted annualized return (per capital slot):")
        print(f"  window {best['lo']}-{best['hi']}: {twr['annual_return_per_slot']*100:+.1f}%/yr per slot")

        # Volume breakdown on 0.88-0.96 window (the FLB sweet spot)
        vol_eff = check_volume_effect(df, 0.88, 0.96)
        print(f"\nVolume effect on 0.88-0.96 window @ {offset_h}h:")
        print(vol_eff.to_string(index=False))

    # Category breakdown on best strategy (3d out, 0.88-0.96)
    print("\n" + "=" * 70)
    print("CATEGORY BREAKDOWN (72h offset, favorite 0.88-0.96, n>=10)")
    print("=" * 70)
    df = load_entries(72)
    cat = category_breakdown(df, 0.88, 0.96)
    print(cat.head(25).to_string(index=False))


if __name__ == "__main__":
    main()

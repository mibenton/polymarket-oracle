"""FLB backtest: calibration + PnL by probability bucket."""
from pathlib import Path

import numpy as np
import pandas as pd

MARKETS = Path("data/markets.parquet")
PRICES = Path("data/prices.parquet")
OUT_DIR = Path("data/results")
OUT_DIR.mkdir(exist_ok=True)

# Polymarket taker fees (2026 Q1) - use a conservative blended 1%
TAKER_FEE = 0.01
ENTRY_OFFSETS_H = [24, 72, 168]  # 1d, 3d, 7d before close


def load_entry_prices(prices: pd.DataFrame, markets: pd.DataFrame, offset_h: int) -> pd.DataFrame:
    """For each market, find the price at (closed_time - offset_h)."""
    m = markets[["id", "closed_time", "yes_won"]].rename(columns={"id": "market_id"})
    m["target_ts"] = (m["closed_time"] - pd.Timedelta(hours=offset_h)).astype("int64") // 10**9

    prices = prices.sort_values(["market_id", "t"])
    rows = []
    # vectorized per market via merge_asof
    m_sorted = m.sort_values("target_ts")
    p_sorted = prices.sort_values("t")
    # merge asof backward: last price at or before target_ts
    merged = pd.merge_asof(
        m_sorted, p_sorted, left_on="target_ts", right_on="t",
        by="market_id", direction="backward", tolerance=int(6 * 3600),
    )
    return merged.dropna(subset=["p"])


def calibration(df: pd.DataFrame, n_bins: int = 20) -> pd.DataFrame:
    """Bucket by entry price, compute actual win rate."""
    df = df.copy()
    df["bucket"] = pd.cut(df["p"], bins=np.linspace(0, 1, n_bins + 1), include_lowest=True)
    g = df.groupby("bucket", observed=True).agg(
        n=("yes_won", "size"),
        implied=("p", "mean"),
        actual=("yes_won", lambda x: x.astype(int).mean()),
    ).reset_index()
    g["edge"] = g["actual"] - g["implied"]
    # Wilson-ish 95% CI
    g["se"] = np.sqrt(g["actual"] * (1 - g["actual"]) / g["n"].clip(lower=1))
    g["ci_low"] = g["actual"] - 1.96 * g["se"]
    g["ci_high"] = g["actual"] + 1.96 * g["se"]
    return g


def strategy_pnl(df: pd.DataFrame, lo: float, hi: float, side: str = "yes") -> dict:
    """Buy YES at entry price if lo <= p <= hi, hold to resolution.
       side='yes' = buy YES; side='no' = buy NO (bet against favorite)."""
    sub = df[(df["p"] >= lo) & (df["p"] <= hi)].copy()
    if len(sub) == 0:
        return {"n": 0}
    if side == "yes":
        # profit per $1 stake = (1/p - 1) if win else -1
        sub["pnl"] = np.where(sub["yes_won"], (1 / sub["p"]) - 1, -1)
    else:  # bet NO
        no_p = 1 - sub["p"]
        sub["pnl"] = np.where(~sub["yes_won"], (1 / no_p) - 1, -1)
    # apply taker fee on entry
    sub["pnl"] -= TAKER_FEE
    return {
        "n": len(sub),
        "mean_pnl": sub["pnl"].mean(),
        "std_pnl": sub["pnl"].std(),
        "win_rate": (sub["pnl"] > 0).mean(),
        "total_pnl_per_$1": sub["pnl"].sum(),
        "sharpe_per_bet": sub["pnl"].mean() / sub["pnl"].std() if sub["pnl"].std() > 0 else 0,
    }


def main():
    markets = pd.read_parquet(MARKETS)
    prices = pd.read_parquet(PRICES)
    print(f"markets: {len(markets)}  prices: {len(prices)}  unique: {prices['market_id'].nunique()}")

    # keep only markets we have prices for
    markets = markets[markets["id"].isin(prices["market_id"].unique())]
    print(f"markets with prices: {len(markets)}")

    report_lines = []
    for offset_h in ENTRY_OFFSETS_H:
        print(f"\n{'='*60}\nENTRY OFFSET: {offset_h}h before close\n{'='*60}")
        entries = load_entry_prices(prices, markets, offset_h)
        entries["yes_won"] = entries["yes_won"].astype(bool)
        print(f"entries with valid price: {len(entries)}")

        cal = calibration(entries, n_bins=20)
        print("\nCALIBRATION (implied vs actual):")
        print(cal[["bucket", "n", "implied", "actual", "edge", "ci_low", "ci_high"]].to_string(index=False))

        cal.to_csv(OUT_DIR / f"calibration_{offset_h}h.csv", index=False)

        print("\nSTRATEGY PnL per $1 stake (after 1% taker fee):")
        strategies = [
            ("Buy YES 0.50-0.70", 0.50, 0.70, "yes"),
            ("Buy YES 0.55-0.75", 0.55, 0.75, "yes"),
            ("Buy YES 0.60-0.80", 0.60, 0.80, "yes"),
            ("Buy YES 0.70-0.90", 0.70, 0.90, "yes"),
            ("Buy NO  0.05-0.20", 0.05, 0.20, "no"),
            ("Buy NO  0.10-0.30", 0.10, 0.30, "no"),
            ("Buy NO  0.20-0.40", 0.20, 0.40, "no"),
            ("Buy YES 0.90-0.97", 0.90, 0.97, "yes"),
            ("Buy YES 0.97-1.00", 0.97, 1.00, "yes"),
        ]
        print(f"{'strategy':<25} {'n':>6} {'mean':>8} {'std':>8} {'win%':>6} {'sharpe':>8}")
        for name, lo, hi, side in strategies:
            r = strategy_pnl(entries, lo, hi, side)
            if r["n"] == 0:
                continue
            print(f"{name:<25} {r['n']:>6} {r['mean_pnl']:>+8.4f} {r['std_pnl']:>8.4f} "
                  f"{r['win_rate']*100:>5.1f}% {r['sharpe_per_bet']:>+8.4f}")

    print("\nresults saved to data/results/")


if __name__ == "__main__":
    main()

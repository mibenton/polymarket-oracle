"""Deep-dive: best strategy parameters + compound growth simulation."""
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

    m = markets[["id", "closed_time", "yes_won", "volume", "neg_risk", "question"]].rename(
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


def pnl_per_bet(df: pd.DataFrame, side: str = "yes") -> pd.Series:
    if side == "yes":
        return np.where(df["yes_won"], (1 / df["p"]) - 1, -1) - TAKER_FEE
    else:
        no_p = 1 - df["p"]
        return np.where(~df["yes_won"], (1 / no_p) - 1, -1) - TAKER_FEE


def scan_thresholds(df: pd.DataFrame, step: float = 0.02) -> pd.DataFrame:
    """Scan all [lo, hi] windows for YES side."""
    rows = []
    for lo in np.arange(0.50, 0.99, step):
        for hi in np.arange(lo + 0.02, 1.01, step):
            sub = df[(df["p"] >= lo) & (df["p"] <= hi)]
            if len(sub) < 30:
                continue
            pnl = pnl_per_bet(sub, "yes")
            rows.append({
                "lo": round(lo, 2), "hi": round(hi, 2),
                "n": len(sub),
                "mean": pnl.mean(),
                "std": pnl.std(),
                "sharpe": pnl.mean() / pnl.std() if pnl.std() > 0 else 0,
                "win_rate": (pnl > 0).mean(),
            })
    return pd.DataFrame(rows).sort_values("sharpe", ascending=False)


def compound_sim(df: pd.DataFrame, lo: float, hi: float, side: str,
                 kelly_frac: float = 0.25, cap: float = 0.05,
                 start: float = 1000.0, n_sims: int = 1000) -> dict:
    """Monte-Carlo compound growth: each bet sized by Kelly × fraction, capped."""
    sub = df[(df["p"] >= lo) & (df["p"] <= hi)].sort_values("closed_time").reset_index(drop=True)
    if len(sub) == 0:
        return {"n": 0}

    # Kelly: f* = (p·b − q) / b where b = (1/entry_p - 1) for YES
    if side == "yes":
        entry_p = sub["p"].values
        b = 1 / entry_p - 1
        # estimated p = empirical win rate in bucket (use overall actual rate for this strategy)
        p_win = sub["yes_won"].mean()  # global estimate
        f_kelly = (p_win * b - (1 - p_win)) / b
        wins = sub["yes_won"].astype(bool).values
    else:
        entry_p = 1 - sub["p"].values
        b = 1 / entry_p - 1
        p_win = (~sub["yes_won"]).mean()
        f_kelly = (p_win * b - (1 - p_win)) / b
        wins = (~sub["yes_won"].astype(bool)).values

    # fractional Kelly, capped
    stake_frac = np.clip(f_kelly * kelly_frac, 0, cap)
    # PnL per $1 staked
    pnl_per_dollar = np.where(wins, b, -1) - TAKER_FEE

    # Deterministic path (order of bets by closed_time)
    bal = start
    path = [bal]
    for i in range(len(sub)):
        stake = bal * stake_frac[i]
        bal += stake * pnl_per_dollar[i]
        path.append(bal)
    deterministic_final = bal

    # Monte Carlo: shuffle order
    rng = np.random.default_rng(42)
    finals = []
    max_dd = []
    for _ in range(n_sims):
        idx = rng.permutation(len(sub))
        bal = start
        peak = start
        dd = 0
        for i in idx:
            stake = bal * stake_frac[i]
            bal += stake * pnl_per_dollar[i]
            peak = max(peak, bal)
            dd = min(dd, (bal - peak) / peak)
        finals.append(bal)
        max_dd.append(dd)
    finals = np.array(finals)

    return {
        "n": len(sub),
        "p_win_empirical": float(p_win),
        "avg_stake_frac": float(stake_frac.mean()),
        "deterministic_final": float(deterministic_final),
        "mc_mean_final": float(finals.mean()),
        "mc_median_final": float(np.median(finals)),
        "mc_p5": float(np.percentile(finals, 5)),
        "mc_p95": float(np.percentile(finals, 95)),
        "mc_worst_dd": float(np.min(max_dd)),
        "start": start,
    }


def main():
    print("=" * 70)
    print("DEEP ANALYSIS: FLB on Polymarket (sample ~12 days of recent closed markets)")
    print("=" * 70)

    for offset_h in [24, 72, 168]:
        print(f"\n--- offset {offset_h}h ---")
        df = load_entries(offset_h)
        print(f"entries: {len(df)}")

        # Scan thresholds
        scan = scan_thresholds(df)
        print(f"\nTop 15 [lo, hi] windows by Sharpe (YES side, n>=30):")
        print(scan.head(15).to_string(index=False))

        scan.to_csv(f"data/results/scan_{offset_h}h.csv", index=False)

    # Compound simulation on the best candidates
    print("\n" + "=" * 70)
    print("COMPOUND GROWTH SIMULATION ($1000 start, 1/4 Kelly, cap 5%/bet)")
    print("=" * 70)

    candidates = [
        (168, 0.90, 0.97, "yes", "YES 0.90-0.97 @ 7d out"),
        (168, 0.70, 0.90, "yes", "YES 0.70-0.90 @ 7d out"),
        (72,  0.90, 0.97, "yes", "YES 0.90-0.97 @ 3d out"),
        (24,  0.90, 0.97, "yes", "YES 0.90-0.97 @ 1d out"),
        (72,  0.97, 1.00, "yes", "YES 0.97-1.00 @ 3d out (tail arb)"),
        (24,  0.97, 1.00, "yes", "YES 0.97-1.00 @ 1d out (tail arb)"),
    ]
    for offset_h, lo, hi, side, label in candidates:
        df = load_entries(offset_h)
        r = compound_sim(df, lo, hi, side)
        if r["n"] == 0:
            continue
        print(f"\n{label}")
        print(f"  trades: {r['n']},  empirical p_win: {r['p_win_empirical']:.3f}")
        print(f"  avg stake: {r['avg_stake_frac']*100:.2f}% of bankroll")
        print(f"  deterministic final: ${r['deterministic_final']:,.0f}  "
              f"({r['deterministic_final']/r['start']-1:+.1%})")
        print(f"  MC median: ${r['mc_median_final']:,.0f}  "
              f"p5: ${r['mc_p5']:,.0f}  p95: ${r['mc_p95']:,.0f}")
        print(f"  worst drawdown: {r['mc_worst_dd']*100:.1f}%")


if __name__ == "__main__":
    main()

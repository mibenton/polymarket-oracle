"""Cycle 20: Ostracism test on weather 0.25-0.36 sweet spot.

Drop top-N winning trades, see if edge survives. Answers: "is our +55% EV real
or concentrated in 5-10 lucky trades?"
"""
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '.')
from cycle9_weather_segment import load

TAKER_FEE = 0.01


def stats(pnl, label):
    n = len(pnl)
    if n < 5:
        return None
    m = pnl.mean()
    s = pnl.std(ddof=1) if n > 1 else 0
    t = m / (s / np.sqrt(n)) if s > 0 else 0
    return {
        "label": label,
        "n": n,
        "mean_pnl_pct": round(m*100, 2),
        "sum_pnl": round(pnl.sum(), 1),
        "win_rate_pct": round((pnl > 0).mean()*100, 0),
        "t_stat": round(t, 2),
        "std": round(s, 3),
    }


def main():
    df = load()
    sub = df[(df["p"] >= 0.25) & (df["p"] <= 0.36)].copy()
    sub["pnl"] = np.where(sub["yes_won"], 1/sub["p"]-1-TAKER_FEE, -1-TAKER_FEE)

    print(f"\n=== Ostracism on weather 0.25-0.36 (n={len(sub)}) ===")
    print(f"{'scenario':<30} {'n':>5} {'mean%':>7} {'sum':>8} {'win%':>5} {'t':>6}")
    print("-" * 75)

    # baseline
    s = stats(sub["pnl"], "Baseline")
    print(f"{s['label']:<30} {s['n']:>5} {s['mean_pnl_pct']:>+6.2f} {s['sum_pnl']:>+8.1f} {s['win_rate_pct']:>4.0f} {s['t_stat']:>+6.2f}")

    # drop top winners by absolute PnL
    sorted_desc = sub.sort_values("pnl", ascending=False)
    for pct in [0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50]:
        k = max(1, int(len(sorted_desc) * pct))
        remaining = sorted_desc.iloc[k:]["pnl"]
        s = stats(remaining, f"Drop top {int(pct*100)}% ({k})")
        marker = "" if s["t_stat"] > 1.96 else " [ins t<1.96]"
        print(f"{s['label']:<30} {s['n']:>5} {s['mean_pnl_pct']:>+6.2f} {s['sum_pnl']:>+8.1f} {s['win_rate_pct']:>4.0f} {s['t_stat']:>+6.2f}{marker}")

    # drop losers
    print("")
    sorted_asc = sub.sort_values("pnl", ascending=True)
    for pct in [0.05, 0.10, 0.20]:
        k = max(1, int(len(sorted_asc) * pct))
        remaining = sorted_asc.iloc[k:]["pnl"]
        s = stats(remaining, f"Drop bottom {int(pct*100)}% ({k})")
        print(f"{s['label']:<30} {s['n']:>5} {s['mean_pnl_pct']:>+6.2f} {s['sum_pnl']:>+8.1f} {s['win_rate_pct']:>4.0f} {s['t_stat']:>+6.2f}")

    # random drop baseline
    print("")
    rng = np.random.default_rng(42)
    for pct in [0.10, 0.20]:
        k = max(1, int(len(sub) * pct))
        means = []
        for _ in range(200):
            idx = rng.choice(len(sub), size=len(sub)-k, replace=False)
            means.append(sub.iloc[idx]["pnl"].mean())
        avg = np.mean(means)*100
        p95 = np.percentile(means, 97.5)*100
        p5 = np.percentile(means, 2.5)*100
        print(f"Random drop {int(pct*100)}% (200 sims)    mean_mean%={avg:+.2f}  [95% band: {p5:+.1f} to {p95:+.1f}]")

    # Event-level ostracism (kill top 5 contributing cities)
    print(f"\n=== Drop top winning cities ===")
    city_pnl = sub.groupby("city")["pnl"].sum().sort_values(ascending=False)
    print(f"Top 5 city contributions: ${city_pnl.head(5).sum():.1f}")
    for n_drop in [1, 3, 5, 10]:
        dropped_cities = city_pnl.head(n_drop).index.tolist()
        remaining = sub[~sub["city"].isin(dropped_cities)]["pnl"]
        s = stats(remaining, f"Drop top {n_drop} cities")
        print(f"{s['label']:<30} {s['n']:>5} {s['mean_pnl_pct']:>+6.2f} {s['sum_pnl']:>+8.1f} {s['win_rate_pct']:>4.0f} {s['t_stat']:>+6.2f}")


if __name__ == "__main__":
    main()

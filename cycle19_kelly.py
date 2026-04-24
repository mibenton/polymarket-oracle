"""Cycle 19: Kelly sizing optimization.

For each tier, compute optimal bet fraction using observed edge & win rate.
Compare to current flat % sizing.
"""
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '.')
from cycle9_weather_segment import load

TAKER_FEE = 0.01


def kelly(p_win, entry_price, fraction=0.25):
    """Kelly fraction for YES bet at entry_price with win prob p_win."""
    if entry_price <= 0 or entry_price >= 1:
        return 0
    b = (1.0 / entry_price) - 1.0  # payoff ratio
    q = 1 - p_win
    f = (p_win * b - q) / b
    return max(0, f * fraction)


def main():
    df = load()
    tiers = [
        ("S",  0.25, 0.36),
        ("A+ (low)", 0.22, 0.25),
        ("A+ (high)", 0.36, 0.40),
        ("B",  0.10, 0.15),
    ]

    print(f"\n{'='*80}")
    print("KELLY SIZING per tier")
    print(f"{'='*80}")
    print(f"{'tier':<12} {'n':>5} {'p_win':>7} {'entry':>7} {'full Kelly':>11} {'1/4 Kelly':>10} {'1/2 Kelly':>10}")

    for name, lo, hi in tiers:
        sub = df[(df["p"] >= lo) & (df["p"] <= hi)].copy()
        if len(sub) < 20:
            continue
        p_win = sub["yes_won"].mean()
        avg_entry = sub["p"].mean()
        k_full = kelly(p_win, avg_entry, 1.0)
        k_quarter = kelly(p_win, avg_entry, 0.25)
        k_half = kelly(p_win, avg_entry, 0.5)
        print(f"{name:<12} {len(sub):>5} {p_win:>7.3f} {avg_entry:>7.3f} "
              f"{k_full*100:>10.1f}% {k_quarter*100:>9.1f}% {k_half*100:>9.1f}%")

    # Compare with current flat sizing
    print(f"\n{'='*80}")
    print("CURRENT vs RECOMMENDED sizing")
    print(f"{'='*80}")
    # Current STAKE_PCT: S=3%, A+=2%, A=1.5%, B=1%
    current = {"S": 0.03, "A+ (low)": 0.02, "A+ (high)": 0.02, "B": 0.01}
    print(f"{'tier':<12} {'current':>8} {'1/4 Kelly':>11} {'change':>10}")
    for name, lo, hi in tiers:
        sub = df[(df["p"] >= lo) & (df["p"] <= hi)].copy()
        if len(sub) < 20:
            continue
        p_win = sub["yes_won"].mean()
        avg_entry = sub["p"].mean()
        k_q = kelly(p_win, avg_entry, 0.25)
        cur = current.get(name, 0.02)
        change = (k_q - cur) / cur * 100 if cur > 0 else 0
        print(f"{name:<12} {cur*100:>7.1f}% {k_q*100:>10.1f}% {change:>+9.0f}%")

    # Compute expected growth per Kelly regime
    print(f"\n{'='*80}")
    print("EXPECTED growth per bet (approximation)")
    print(f"{'='*80}")
    print(f"Formula: g = f * (p*b + q*(-1) - fee) where fee=1%")
    for name, lo, hi in tiers:
        sub = df[(df["p"] >= lo) & (df["p"] <= hi)].copy()
        if len(sub) < 20:
            continue
        p_win = sub["yes_won"].mean()
        avg_entry = sub["p"].mean()
        b = (1/avg_entry) - 1
        mean_ret = p_win * b - (1-p_win) - TAKER_FEE
        cur = current.get(name, 0.02)
        k_q = kelly(p_win, avg_entry, 0.25)
        g_cur = cur * mean_ret
        g_kelly = k_q * mean_ret
        print(f"  {name}: mean_ret={mean_ret*100:+.1f}%/$  growth@{cur*100:.1f}%={g_cur*100:+.2f}%  "
              f"growth@Kelly25={g_kelly*100:+.2f}%")


if __name__ == "__main__":
    main()

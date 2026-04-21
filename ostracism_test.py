"""Ostracism Test on Strategy A: 驗證 edge 是否由少數樣本撐出.

策略 A: Favorite 0.88-0.96, vol $5k-$10k, 72h out, hold to resolution.

Since this is a market-screen strategy (no signal substitution possible after
removal), we adapt the classical Ostracism Test to:
  - Part A: Drop top N winners, recompute stats.
  - Part B: Drop worst N losers (symmetric control).
  - Part C: Drop random N (baseline).
  - Part D: Event clustering to estimate effective n.
"""
from pathlib import Path
import numpy as np
import pandas as pd

TAKER_FEE = 0.01
SEED = 42


def load():
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


def strategy_A_trades(markets, prices):
    """Replicate strategy A and return per-trade table with pnl."""
    markets = markets[markets["id"].isin(prices["market_id"].unique())]
    offset_h = 72
    m = markets[["id", "closed_time", "start_date", "yes_won",
                 "volume", "slug", "question"]].rename(columns={"id": "market_id"})
    m["target_ts"] = (m["closed_time"] - pd.Timedelta(hours=offset_h)).astype("int64") // 10**9
    m_sorted = m.sort_values("target_ts")
    p_sorted = prices.sort_values("t")
    merged = pd.merge_asof(
        m_sorted, p_sorted, left_on="target_ts", right_on="t",
        by="market_id", direction="backward", tolerance=int(6 * 3600),
    )
    entries = merged.dropna(subset=["p"]).copy()

    # favorite transform
    entries["fav_price"] = np.where(entries["p"] >= 0.5, entries["p"], 1 - entries["p"])
    entries["fav_won"] = np.where(entries["p"] >= 0.5,
                                   entries["yes_won"].astype(bool),
                                   ~entries["yes_won"].astype(bool))

    # strategy A filter
    sub = entries[(entries["fav_price"] >= 0.88) & (entries["fav_price"] <= 0.96) &
                  (entries["volume"] >= 5_000) & (entries["volume"] <= 10_000)].copy()

    # pnl per $1 stake
    b = 1 / sub["fav_price"].values - 1
    wins = sub["fav_won"].astype(bool).values
    sub["pnl"] = np.where(wins, b, -1) - TAKER_FEE
    return sub.reset_index(drop=True)


def stats(pnl: np.ndarray) -> dict:
    if len(pnl) < 3:
        return {"n": len(pnl)}
    mean = pnl.mean()
    se = pnl.std(ddof=1) / np.sqrt(len(pnl))
    # bootstrap CI
    rng = np.random.default_rng(SEED)
    bs = np.array([pnl[rng.integers(0, len(pnl), len(pnl))].mean() for _ in range(2000)])
    return {
        "n": int(len(pnl)),
        "mean": float(mean),
        "se": float(se),
        "t": float(mean / se) if se > 0 else 0,
        "ci_low": float(np.percentile(bs, 2.5)),
        "ci_high": float(np.percentile(bs, 97.5)),
        "win_rate": float((pnl > 0).mean()),
        "sum_pnl": float(pnl.sum()),
    }


def fmt(s: dict) -> str:
    if s.get("n", 0) < 3:
        return f"n={s.get('n',0)} (too small)"
    return (f"n={s['n']:>3}  mean={s['mean']:+.4f}  t={s['t']:+.2f}  "
            f"CI=[{s['ci_low']:+.4f},{s['ci_high']:+.4f}]  "
            f"win={s['win_rate']*100:.1f}%  sum=${s['sum_pnl']:+.2f}")


def part_A_intensity_sweep(trades: pd.DataFrame):
    print("\n" + "="*80)
    print("PART A: INTENSITY SWEEP — 放逐前 N% 最賺筆")
    print("="*80)
    # rank trades by pnl desc, then cumulatively exclude top X%
    sorted_trades = trades.sort_values("pnl", ascending=False).reset_index(drop=True)
    base = stats(trades["pnl"].values)
    print(f"  Baseline:        {fmt(base)}")
    for pct in [0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50]:
        k = max(1, int(len(sorted_trades) * pct))
        remaining = sorted_trades.iloc[k:]["pnl"].values
        s = stats(remaining)
        marker = "" if s.get("t", 0) > 1.96 else " [WARN t<1.96]"
        print(f"  Drop top {int(pct*100):>3}%  ({k:>3}): {fmt(s)}{marker}")
    # drop ALL positive pnl (pure losers only)
    all_pos_dropped = trades[trades["pnl"] <= 0]["pnl"].values
    s = stats(all_pos_dropped)
    print(f"  Drop ALL winners: {fmt(s)}")


def part_B_symmetric(trades: pd.DataFrame):
    print("\n" + "="*80)
    print("PART B: SYMMETRIC CONTROL — 放逐前 N% 最虧筆（應讓 edge 上升）")
    print("="*80)
    sorted_losers = trades.sort_values("pnl", ascending=True).reset_index(drop=True)
    for pct in [0.01, 0.02, 0.05, 0.10, 0.20]:
        k = max(1, int(len(sorted_losers) * pct))
        remaining = sorted_losers.iloc[k:]["pnl"].values
        s = stats(remaining)
        print(f"  Drop bot {int(pct*100):>3}%  ({k:>3}): {fmt(s)}")


def part_C_random_baseline(trades: pd.DataFrame):
    print("\n" + "="*80)
    print("PART C: RANDOM BASELINE — 相同強度隨機放逐（測試 mask side-effect）")
    print("="*80)
    rng = np.random.default_rng(SEED)
    for pct in [0.05, 0.10, 0.20]:
        k = max(1, int(len(trades) * pct))
        # 200 random draws
        means = []
        for _ in range(200):
            idx = rng.choice(len(trades), size=len(trades) - k, replace=False)
            means.append(trades.iloc[idx]["pnl"].mean())
        means = np.array(means)
        s_drop_top = stats(
            trades.sort_values("pnl", ascending=False).iloc[k:]["pnl"].values
        )
        print(f"  Drop {int(pct*100):>3}% random (200 sims): "
              f"mean of means={means.mean():+.4f}  "
              f"95% band=[{np.percentile(means,2.5):+.4f},{np.percentile(means,97.5):+.4f}]")
        print(f"        vs drop top {int(pct*100):>3}%: {s_drop_top['mean']:+.4f}  "
              f"→ asymmetry={means.mean()-s_drop_top['mean']:+.4f}")


def part_D_event_clustering(trades: pd.DataFrame):
    print("\n" + "="*80)
    print("PART D: EVENT CLUSTERING — 單 event 貢獻 + 有效樣本數")
    print("="*80)
    # event = slug prefix (remove trailing numeric/market-type suffix)
    # e.g. "nba-phx-okc-2026-04-19-spread-home-1pt5" → "nba-phx-okc-2026-04-19"
    def event_key(slug):
        if not isinstance(slug, str):
            return "unknown"
        parts = slug.split("-")
        # heuristic: keep through first date-like token
        out = []
        for p in parts:
            out.append(p)
            # stop after a year-like token + month + day
            if len(out) >= 3 and any(c.isdigit() for c in p) and len(p) <= 2:
                break
        return "-".join(out[:6])

    trades = trades.copy()
    trades["event"] = trades["slug"].apply(event_key)

    # top events by absolute pnl contribution
    evt = trades.groupby("event").agg(
        n_markets=("pnl", "size"),
        sum_pnl=("pnl", "sum"),
        mean_pnl=("pnl", "mean"),
    ).sort_values("sum_pnl", ascending=False).reset_index()

    total = trades["pnl"].sum()
    evt["pct_of_total"] = evt["sum_pnl"] / total * 100
    print(f"\n  Total PnL: ${total:+.2f}   n_trades: {len(trades)}   n_events: {len(evt)}")
    print(f"  Effective n (unique events): {len(evt)}")
    print(f"  Avg markets per event: {len(trades)/len(evt):.2f}")
    print("\n  Top 10 events by absolute PnL contribution:")
    print(evt.head(10).to_string(index=False))

    print("\n  Concentration:")
    for k in [1, 3, 5, 10]:
        pct = evt.head(k)["sum_pnl"].sum() / total * 100
        print(f"    top {k:>2} events: {pct:>5.1f}% of total PnL")

    # cluster-aware se: assume iid within event fails → use event-level means
    event_means = trades.groupby("event")["pnl"].mean().values
    n_eff = len(event_means)
    if n_eff >= 3:
        cluster_mean = event_means.mean()
        cluster_se = event_means.std(ddof=1) / np.sqrt(n_eff)
        cluster_t = cluster_mean / cluster_se if cluster_se > 0 else 0
        print(f"\n  Cluster-robust stats (treat each event as 1 obs):")
        print(f"    n_eff = {n_eff},  mean of event means = {cluster_mean:+.4f}")
        print(f"    cluster SE = {cluster_se:.4f},  t = {cluster_t:+.2f}")
        if cluster_t < 1.96:
            print(f"    [WARN]  Cluster-robust t < 1.96 → edge NOT significant after clustering")
        else:
            print(f"    [OK] Cluster-robust t ≥ 1.96 → edge survives clustering")


def verdict(trades: pd.DataFrame):
    print("\n" + "="*80)
    print("🏛️  JUDGEMENT")
    print("="*80)
    base = stats(trades["pnl"].values)

    # drop top 10%
    k10 = int(len(trades) * 0.10)
    after_10 = stats(
        trades.sort_values("pnl", ascending=False).iloc[k10:]["pnl"].values
    )
    impact_10 = (after_10["mean"] - base["mean"]) / abs(base["mean"]) * 100

    # drop top 20%
    k20 = int(len(trades) * 0.20)
    after_20 = stats(
        trades.sort_values("pnl", ascending=False).iloc[k20:]["pnl"].values
    )

    # drop all winners
    losers = trades[trades["pnl"] <= 0]["pnl"].values
    all_win_dropped = stats(losers)

    print(f"\n  Baseline:                 mean={base['mean']:+.4f}  t={base['t']:+.2f}")
    print(f"  After drop top 10%:       mean={after_10['mean']:+.4f}  t={after_10['t']:+.2f}  ({impact_10:+.1f}% shift)")
    print(f"  After drop top 20%:       mean={after_20['mean']:+.4f}  t={after_20['t']:+.2f}")
    print(f"  After drop ALL winners:   mean={all_win_dropped.get('mean','?'):.4f} "
          f"(only losers remain, sanity check)")

    print("\n  Verdict:")
    if after_10["ci_low"] <= 0 and after_10["t"] < 1.96:
        print("  [FAIL] 放逐前 10% 後顯著性已消失 → edge 高度依賴少數樣本")
    elif after_20["ci_low"] <= 0 and after_20["t"] < 1.96:
        print("  [WARN]  放逐前 20% 後顯著性消失 → edge 淺，樣本量邊緣")
    else:
        print("  [OK] 撐過 20% 放逐仍顯著 → edge 結構性較強")


def main():
    markets, prices = load()
    trades = strategy_A_trades(markets, prices)
    print(f"Strategy A trades loaded: n={len(trades)}")
    print(f"Baseline: mean={trades['pnl'].mean():+.4f}  "
          f"win_rate={(trades['pnl']>0).mean()*100:.1f}%  "
          f"sum=${trades['pnl'].sum():+.2f}")

    part_A_intensity_sweep(trades)
    part_B_symmetric(trades)
    part_C_random_baseline(trades)
    part_D_event_clustering(trades)
    verdict(trades)

    # save trade list
    out = Path("data/results/ostracism_strategy_A_trades.csv")
    trades[["slug", "question", "fav_price", "fav_won", "pnl", "volume",
            "closed_time"]].sort_values("pnl", ascending=False).to_csv(out, index=False)
    print(f"\n  Trade list saved to {out}")


if __name__ == "__main__":
    main()

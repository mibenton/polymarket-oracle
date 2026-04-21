"""Market calibration by category: does market price match actual outcome rate?

If yes → no edge. If no → we found systematic mispricing.
"""
from pathlib import Path
import numpy as np
import pandas as pd

TAKER_FEE = 0.01


def categorize(slug, question, y, n):
    s = (slug or "").lower()
    if any(k in s for k in ["nba-", "mlb-", "nhl-", "ncaa", "cbb-", "cfb-"]):
        return "sports_us"
    if any(k in s for k in ["ufc-", "atp-", "wta-", "fif-", "fl1-", "bun-",
                             "ucl-", "uel-", "epl-", "euroleague", "kbo-", "pga"]):
        return "sports_global"
    if any(k in s for k in ["cs2-", "val-", "lol-", "dota", "rocket-league",
                             "-esports-", "blast-", "iem-"]):
        return "esports"
    if "updown" in s or "up-or-down" in s or "upordown" in s:
        return "short_term_price_direction"
    if any(k in s for k in ["bitcoin-above-", "btc-above-", "ethereum-above-",
                             "eth-above-", "solana-above-", "sol-above-"]):
        return "crypto_price_threshold"
    if "dip-to-" in s or "hit-" in s:
        return "price_touch_threshold"
    if any(k in s for k in ["tweets", "tweet-", "-of-posts-", "-of-tweets-"]):
        return "tweet_count"
    if any(k in s for k in ["-election", "-primary", "-senate", "-governor",
                             "-president", "-parliament", "-nominee"]):
        return "politics_election"
    if any(k in s for k in ["fed-", "fomc", "cpi", "ecb-", "-rate-",
                             "-key-rate", "bank-of-"]):
        return "macro_rates"
    if any(k in s for k in ["earnings", "quarterly", "beat-"]):
        return "earnings"
    if "ipo" in s:
        return "ipo"
    if "highest-temperature" in s or "temperature-in-" in s:
        return "weather"
    if any(k in s for k in ["oscar", "box-office", "opening-weekend"]):
        return "entertainment"
    if any(k in s for k in ["will-trump-", "will-musk-", "-publicly-",
                             "-insult", "-mention-"]):
        return "public_figure_behavior"
    if any(k in s for k in ["russia-", "ukraine-", "iran-", "israel-",
                             "gaza-", "hamas-", "putin-"]):
        return "geopolitics"
    return "other"


def load():
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
    prices = pd.concat(frames).drop_duplicates(["market_id", "t"])

    # For each market, get price at T-72h
    have = markets[markets["id"].isin(prices["market_id"].unique())].copy()
    have = have[have["duration_h"] >= 72].copy()
    have["target_ts"] = (have["closed_time"] - pd.Timedelta(hours=72)).astype("int64") // 10**9

    m = have[["id", "closed_time", "yes_won", "volume", "slug", "question",
              "yes_outcome", "no_outcome", "duration_h", "target_ts"]].rename(columns={"id":"market_id"})
    merged = pd.merge_asof(
        m.sort_values("target_ts"),
        prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6*3600),
    ).dropna(subset=["p"])
    merged["category"] = merged.apply(
        lambda r: categorize(r["slug"], r["question"], r["yes_outcome"], r["no_outcome"]),
        axis=1,
    )
    return merged


def calibrate_by_category(df):
    """For each category, bucket by market price at T-72h and compute actual win rate."""
    bins = [0, 0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9, 1.0]
    df = df.copy()
    df["p_bucket"] = pd.cut(df["p"], bins=bins, include_lowest=True)
    df["yes_won_int"] = df["yes_won"].astype(int)

    print(f"\n{'='*80}")
    print("MARKET CALIBRATION: price at T-72h vs actual yes_won, by category")
    print("(columns: [market_p_range] n  implied_p  actual_p  bias  bet_edge_bps)")
    print(f"{'='*80}")

    for cat, sub in df.groupby("category"):
        if len(sub) < 100:
            continue
        print(f"\n--- {cat} (n={len(sub):,}, overall P(YES)={sub['yes_won_int'].mean()*100:.1f}%) ---")
        g = sub.groupby("p_bucket", observed=True).agg(
            n=("yes_won_int", "size"),
            implied_p=("p", "mean"),
            actual_p=("yes_won_int", "mean"),
        ).reset_index()
        g["bias_pp"] = (g["actual_p"] - g["implied_p"]) * 100

        # Estimated edge after fee if you "bet the correct side"
        # If actual > implied, buy YES. Edge per $ = (actual/implied) - 1 - fee
        def est_edge(row):
            if row["n"] < 10:
                return np.nan
            if row["actual_p"] > row["implied_p"]:
                # buy YES at ~implied_p (assume you can get mid)
                return (row["actual_p"] / row["implied_p"] - 1 - TAKER_FEE) * 10000
            else:
                # buy NO at 1-implied_p
                return ((1 - row["actual_p"]) / (1 - row["implied_p"]) - 1 - TAKER_FEE) * 10000

        g["edge_bps"] = g.apply(est_edge, axis=1)
        print(g.to_string(index=False))


def flag_opportunities(df):
    """Find (category × price-bucket) where bias is large AND n is sufficient."""
    bins = [0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0]
    df = df.copy()
    df["p_bucket"] = pd.cut(df["p"], bins=bins, include_lowest=True)
    df["yes_won_int"] = df["yes_won"].astype(int)

    print(f"\n{'='*80}")
    print("TOP MISPRICING OPPORTUNITIES (|bias| > 5pp, n >= 30)")
    print(f"{'='*80}")
    rows = []
    for (cat, bucket), sub in df.groupby(["category", "p_bucket"], observed=True):
        if len(sub) < 30:
            continue
        implied = sub["p"].mean()
        actual = sub["yes_won_int"].mean()
        bias = (actual - implied) * 100
        # EV after fee — best side
        if actual > implied:
            ev = (actual / implied - 1 - TAKER_FEE) * 100  # buy YES
            side = "YES"
        else:
            ev = ((1-actual) / (1-implied) - 1 - TAKER_FEE) * 100  # buy NO
            side = "NO"
        rows.append({
            "category": cat,
            "p_range": str(bucket),
            "n": len(sub),
            "implied_p": round(implied, 3),
            "actual_p": round(actual, 3),
            "bias_pp": round(bias, 2),
            "best_side": side,
            "ev_pct": round(ev, 2),
        })

    out = pd.DataFrame(rows)
    out = out[out["bias_pp"].abs() >= 5].sort_values("ev_pct", ascending=False)
    print(out.to_string(index=False))

    # Save full table
    out_full = pd.DataFrame(rows).sort_values("ev_pct", ascending=False)
    out_full.to_csv("data/results/patterns/calibration_by_cat_bucket.csv", index=False)
    print(f"\nSaved full table to data/results/patterns/calibration_by_cat_bucket.csv")


def main():
    df = load()
    print(f"Loaded {len(df):,} markets with price at T-72h")
    print(f"Time window: {df['closed_time'].min()} -> {df['closed_time'].max()}")

    calibrate_by_category(df)
    flag_opportunities(df)


if __name__ == "__main__":
    main()

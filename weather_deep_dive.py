"""Deep-dive on weather bias: structural vs noise."""
from pathlib import Path
import numpy as np
import pandas as pd

TAKER_FEE = 0.01


def load_priced_weather():
    ext = pd.read_parquet("data/markets_ext.parquet")
    orig = pd.read_parquet("data/markets.parquet")
    m = pd.concat([ext, orig], ignore_index=True).drop_duplicates("id")
    m["closed_time"] = pd.to_datetime(m["closed_time"], utc=True, errors="coerce")
    m["start_date"] = pd.to_datetime(m["start_date"], utc=True, errors="coerce")
    m["duration_h"] = (m["closed_time"] - m["start_date"]).dt.total_seconds() / 3600

    # weather only
    weather = m[m["slug"].str.lower().str.contains(
        "highest-temperature|temperature-in-", regex=True, na=False
    )].copy()

    # pull prices
    frames = []
    for p in ["data/prices.parquet", "data/prices_ext.parquet"]:
        if Path(p).exists():
            frames.append(pd.read_parquet(p))
    prices = pd.concat(frames).drop_duplicates(["market_id", "t"])

    weather = weather[weather["id"].isin(prices["market_id"].unique())]
    weather = weather[weather["duration_h"] >= 72].copy()
    weather["target_ts"] = (weather["closed_time"] - pd.Timedelta(hours=72)).astype("int64") // 10**9

    w = weather[["id", "slug", "question", "closed_time", "yes_won",
                 "yes_outcome", "duration_h", "target_ts"]].rename(columns={"id": "market_id"})
    merged = pd.merge_asof(
        w.sort_values("target_ts"),
        prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6 * 3600),
    ).dropna(subset=["p"])

    merged["yes_won_int"] = merged["yes_won"].astype(int)
    return merged


def classify_weather(slug: str) -> str:
    """Classify weather market structure."""
    s = slug.lower()
    if "orhigher" in s or "orabove" in s:
        return "cumulative_at_or_above"
    if "orbelow" in s or "orlower" in s:
        return "cumulative_at_or_below"
    return "exact_bucket"  # "X°C" (default)


def extract_city(slug: str) -> str:
    """Extract city token."""
    s = slug.lower()
    # pattern: highest-temperature-in-<city>-on-<date>-<value>
    parts = s.split("-")
    # find "in" marker
    try:
        i = parts.index("in")
        return parts[i + 1]
    except (ValueError, IndexError):
        return "unknown"


def main():
    df = load_priced_weather()
    print(f"Weather markets with T-72h price: {len(df)}")
    print(f"Overall YES rate: {df['yes_won_int'].mean()*100:.1f}%")
    print(f"Time span: {df['closed_time'].min()} → {df['closed_time'].max()}")

    df["kind"] = df["slug"].apply(classify_weather)
    df["city"] = df["slug"].apply(extract_city)

    print("\n=== By question structure ===")
    g = df.groupby("kind").agg(
        n=("yes_won_int", "size"),
        yes_rate=("yes_won_int", "mean"),
    )
    g["yes_rate"] = (g["yes_rate"] * 100).round(1)
    print(g.to_string())

    print("\n=== Focus on 0.25-0.40 price bucket (our Tier-A pocket) ===")
    focus = df[(df["p"] >= 0.25) & (df["p"] <= 0.40)].copy()
    print(f"n={len(focus)}, implied mean={focus['p'].mean():.3f}, "
          f"actual YES={focus['yes_won_int'].mean()*100:.1f}%, "
          f"bias={((focus['yes_won_int'].mean() - focus['p'].mean()) * 100):+.1f}pp")

    print("\n  By structure:")
    g = focus.groupby("kind").agg(
        n=("yes_won_int", "size"),
        implied=("p", "mean"),
        actual=("yes_won_int", "mean"),
    )
    g["bias_pp"] = (g["actual"] - g["implied"]) * 100
    g = g.round({"implied": 3, "actual": 3, "bias_pp": 1})
    print(g.to_string())

    print("\n=== EV after fee by structure (0.25-0.40 bucket) ===")
    for k, sub in focus.groupby("kind"):
        b = 1 / sub["p"].values - 1
        wins = sub["yes_won_int"].values
        pnl = np.where(wins, b, -1) - TAKER_FEE
        mean_pnl = pnl.mean()
        n = len(sub)
        se = pnl.std(ddof=1) / np.sqrt(n) if n > 1 else 0
        print(f"  {k}: n={n}, mean PnL = {mean_pnl*100:+.2f}% "
              f"± {se*100:.2f}% (1σ), t={mean_pnl/se if se>0 else 0:+.2f}")

    print("\n=== Top cities by count ===")
    city_counts = focus["city"].value_counts().head(15)
    print(city_counts.to_string())

    print("\n=== Monthly split (to see if bias is stable) ===")
    focus["month"] = focus["closed_time"].dt.to_period("M").astype(str)
    monthly = focus.groupby(["month", "kind"]).agg(
        n=("yes_won_int", "size"),
        actual=("yes_won_int", "mean"),
    )
    monthly["actual"] = (monthly["actual"] * 100).round(1)
    print(monthly.to_string())

    # Now compare: exact_bucket on 0.25-0.40 should be mispriced (retail
    # undervalues the bucket nearest forecast mean)
    print("\n=== KEY TEST: exact_bucket only ===")
    bucket_only = focus[focus["kind"] == "exact_bucket"]
    if len(bucket_only) > 0:
        b = 1 / bucket_only["p"].values - 1
        wins = bucket_only["yes_won_int"].values
        pnl = np.where(wins, b, -1) - TAKER_FEE
        print(f"  n={len(bucket_only)}")
        print(f"  implied = {bucket_only['p'].mean():.3f}")
        print(f"  actual YES = {bucket_only['yes_won_int'].mean()*100:.1f}%")
        print(f"  mean PnL per $1 stake = {pnl.mean()*100:+.2f}%")
        # Bootstrap CI
        rng = np.random.default_rng(42)
        bs = [pnl[rng.integers(0, len(pnl), len(pnl))].mean() for _ in range(5000)]
        ci_low = np.percentile(bs, 2.5) * 100
        ci_high = np.percentile(bs, 97.5) * 100
        print(f"  Bootstrap 95% CI: [{ci_low:+.2f}%, {ci_high:+.2f}%]")

    print("\n=== Cumulative (at-or-above) comparison ===")
    cum = focus[focus["kind"] == "cumulative_at_or_above"]
    if len(cum) > 0:
        b = 1 / cum["p"].values - 1
        wins = cum["yes_won_int"].values
        pnl = np.where(wins, b, -1) - TAKER_FEE
        print(f"  n={len(cum)}")
        print(f"  implied = {cum['p'].mean():.3f}")
        print(f"  actual YES = {cum['yes_won_int'].mean()*100:.1f}%")
        print(f"  mean PnL per $1 stake = {pnl.mean()*100:+.2f}%")
        rng = np.random.default_rng(42)
        bs = [pnl[rng.integers(0, len(pnl), len(pnl))].mean() for _ in range(5000)]
        ci_low = np.percentile(bs, 2.5) * 100
        ci_high = np.percentile(bs, 97.5) * 100
        print(f"  Bootstrap 95% CI: [{ci_low:+.2f}%, {ci_high:+.2f}%]")


if __name__ == "__main__":
    main()

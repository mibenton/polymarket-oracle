"""Cycle 9A: Within-weather segmentation.

Break the weather 0.20-0.40 YES edge down by:
- City climate zone (tropical/temperate/cold/continental/coastal)
- Temperature band (hot cities vs cold cities)
- Day of week
- Month/season
- Weekday vs weekend
- Bucket position relative to event set (center vs edge of bucket range)
- Volume bucket

Goal: find sub-populations with 2-3x the base edge.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd

TAKER_FEE = 0.01

CITY_CLIMATE = {
    # Tropical (equator, hot year-round)
    "singapore": "tropical", "jakarta": "tropical", "bangkok": "tropical",
    "kuala-lumpur": "tropical", "manila": "tropical", "ho-chi-minh": "tropical",
    "rio": "tropical", "sao-paulo": "tropical",
    # Desert
    "dubai": "desert", "riyadh": "desert", "cairo": "desert",
    # Tropical-temperate mix
    "hong-kong": "subtropical", "taipei": "subtropical",
    "tel-aviv": "subtropical", "miami": "subtropical",
    # Temperate (seasonal)
    "london": "temperate", "paris": "temperate", "berlin": "temperate",
    "madrid": "temperate", "rome": "temperate", "istanbul": "temperate",
    "ankara": "temperate", "milan": "temperate", "munich": "temperate",
    "warsaw": "temperate", "vienna": "temperate", "athens": "temperate",
    "helsinki": "cold", "oslo": "cold", "stockholm": "cold",
    # East Asia temperate/continental
    "tokyo": "temperate", "seoul": "continental", "beijing": "continental",
    "shanghai": "subtropical", "shenzhen": "subtropical",
    "chengdu": "subtropical", "chongqing": "subtropical", "wuhan": "subtropical",
    # US
    "nyc": "continental", "new-york-city": "continental",
    "chicago": "continental", "denver": "continental",
    "atlanta": "subtropical", "los-angeles": "mediterranean",
    "san-francisco": "mediterranean", "seattle": "temperate",
    "houston": "subtropical", "phoenix": "desert", "dallas": "subtropical",
    # Canada
    "toronto": "continental", "vancouver": "temperate", "montreal": "cold",
    # South Asia
    "lucknow": "subtropical", "delhi": "subtropical", "mumbai": "tropical",
    # Oceania
    "sydney": "temperate", "melbourne": "temperate", "wellington": "temperate",
    "auckland": "temperate",
    # Russia
    "moscow": "cold",
    # Latin America
    "mexico-city": "subtropical", "buenos-aires": "temperate", "lima": "subtropical",
}


def extract_city(slug: str) -> str:
    m = re.match(r'highest-temperature-in-([a-z-]+?)-on-', slug.lower())
    if not m:
        return "unknown"
    city = m.group(1).rstrip("-")
    return city


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
    prices = pd.concat(frames).drop_duplicates(["market_id","t"])

    have = markets[markets["id"].isin(prices["market_id"].unique())].copy()
    have = have[have["duration_h"] >= 72].copy()
    have["target_ts"] = (have["closed_time"] - pd.Timedelta(hours=72)).astype("int64") // 10**9

    m = have[["id","slug","closed_time","yes_won","volume","target_ts"]].rename(columns={"id":"market_id"})
    merged = pd.merge_asof(
        m.sort_values("target_ts"),
        prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6*3600),
    ).dropna(subset=["p"])
    merged["yes_won_int"] = merged["yes_won"].astype(int)
    # weather only (exact-bucket, no orhigher/orbelow)
    merged = merged[
        merged["slug"].str.contains("highest-temperature-in-", case=False, na=False) &
        ~merged["slug"].str.contains("orhigher|orabove|orbelow|orlower",
                                      case=False, regex=True, na=False)
    ].copy()
    merged["city"] = merged["slug"].apply(extract_city)
    merged["climate"] = merged["city"].map(CITY_CLIMATE).fillna("unknown")
    merged["fav_price"] = np.where(merged["p"] >= 0.5, merged["p"], 1 - merged["p"])
    return merged


def pnl_yes_bet(entry, won):
    """PnL per $1 stake if we BUY YES at entry."""
    return ((1.0 / entry) - 1.0 - TAKER_FEE) if won else -1.0 - TAKER_FEE


def analyze(df: pd.DataFrame, focus_lo=0.20, focus_hi=0.40):
    df = df.copy()
    # focus on 0.20-0.40 where we trade
    sub = df[(df["p"] >= focus_lo) & (df["p"] <= focus_hi)].copy()
    sub["pnl"] = sub.apply(lambda r: pnl_yes_bet(r["p"], bool(r["yes_won"])), axis=1)

    print(f"\n=== Focus: weather 0.20-0.40 ({len(sub):,} markets) ===")
    print(f"Overall win rate: {sub['yes_won_int'].mean()*100:.1f}%")
    print(f"Overall mean PnL/$1: {sub['pnl'].mean()*100:+.2f}%")
    print(f"Overall total PnL if $1 per bet: ${sub['pnl'].sum():+.2f}")

    # By climate zone
    print(f"\n--- By climate zone ---")
    g = sub.groupby("climate").agg(
        n=("pnl","size"),
        win_rate=("yes_won_int","mean"),
        mean_pnl=("pnl","mean"),
        sum_pnl=("pnl","sum"),
    )
    g["mean_pnl_pct"] = (g["mean_pnl"]*100).round(1)
    g["win_rate_pct"] = (g["win_rate"]*100).round(0)
    g["sum_pnl"] = g["sum_pnl"].round(1)
    g = g.drop(columns=["mean_pnl","win_rate"])
    print(g.sort_values("mean_pnl_pct", ascending=False).to_string())

    # By city (n>=10 only)
    print(f"\n--- By city (n>=10) ---")
    gc = sub.groupby("city").agg(
        n=("pnl","size"),
        win_rate=("yes_won_int","mean"),
        mean_pnl=("pnl","mean"),
    )
    gc = gc[gc["n"] >= 10].copy()
    gc["mean_pnl_pct"] = (gc["mean_pnl"]*100).round(1)
    gc["win_rate_pct"] = (gc["win_rate"]*100).round(0)
    gc = gc.drop(columns=["mean_pnl","win_rate"]).sort_values("mean_pnl_pct", ascending=False)
    print(gc.to_string())

    # By day of week
    print(f"\n--- By day of week ---")
    sub["dow"] = sub["closed_time"].dt.day_name()
    gd = sub.groupby("dow").agg(
        n=("pnl","size"),
        mean_pnl=("pnl","mean"),
    )
    gd["mean_pnl_pct"] = (gd["mean_pnl"]*100).round(1)
    gd = gd.drop(columns=["mean_pnl"])
    print(gd.to_string())

    # By entry price bucket (fine-grained within 0.20-0.40)
    print(f"\n--- Fine-grained entry price (0.20-0.40) ---")
    sub["pb"] = pd.cut(sub["p"], bins=np.arange(0.20, 0.41, 0.02), include_lowest=True)
    gp = sub.groupby("pb", observed=True).agg(
        n=("pnl","size"),
        win_rate=("yes_won_int","mean"),
        mean_pnl=("pnl","mean"),
    )
    gp["mean_pnl_pct"] = (gp["mean_pnl"]*100).round(1)
    gp["win_rate_pct"] = (gp["win_rate"]*100).round(0)
    gp = gp.drop(columns=["mean_pnl","win_rate"])
    print(gp.to_string())

    # By volume
    print(f"\n--- By volume tier ---")
    sub["vt"] = pd.cut(sub["volume"],
                        bins=[0, 5_000, 20_000, 100_000, 1e8],
                        labels=["<5k","5k-20k","20k-100k",">100k"])
    gv = sub.groupby("vt", observed=True).agg(
        n=("pnl","size"),
        mean_pnl=("pnl","mean"),
    )
    gv["mean_pnl_pct"] = (gv["mean_pnl"]*100).round(1)
    gv = gv.drop(columns=["mean_pnl"])
    print(gv.to_string())

    # Save top cities and top climate for scanner
    out_path = Path("data/results/cycle9_weather_segments.csv")
    out_path.parent.mkdir(exist_ok=True)
    combined = []
    for segment_type, group_df in [("climate", g), ("city", gc), ("dow", gd), ("price", gp), ("volume", gv)]:
        tmp = group_df.reset_index()
        tmp["segment_type"] = segment_type
        tmp = tmp.rename(columns={tmp.columns[0]: "segment_value"})
        combined.append(tmp)
    pd.concat(combined, ignore_index=True).to_csv(out_path, index=False)
    print(f"\nSaved segments to {out_path}")


def main():
    df = load()
    print(f"Loaded {len(df):,} exact-bucket weather markets with price at T-72h")
    analyze(df)


if __name__ == "__main__":
    main()

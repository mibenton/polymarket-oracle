"""Track B: Deep-dive esports 0.5-0.6 NO edge.

Question: Why does the 'slight favorite' (0.5-0.6) lose 44.1% vs market 52.4%?
Hypotheses to test:
  H1: Specific game (CS2 / LoL / Valorant / Dota) drives it
  H2: Specific tournament type
  H3: BO1 vs BO3 vs BO5
  H4: outcome[0] (first-listed team) bias
  H5: Time-of-day effect (fan-heavy timezones)
"""
from pathlib import Path
import numpy as np
import pandas as pd

TAKER_FEE = 0.01


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

    m = have[["id","slug","question","closed_time","yes_won","yes_outcome",
              "no_outcome","volume","duration_h","target_ts"]].rename(columns={"id":"market_id"})
    merged = pd.merge_asof(
        m.sort_values("target_ts"),
        prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6*3600),
    ).dropna(subset=["p"])
    merged["yes_won_int"] = merged["yes_won"].astype(int)
    return merged


def parse_game(slug):
    s = slug.lower()
    for game in ["cs2-", "val-", "lol-", "dota", "rocket-league"]:
        if game in s:
            return game.rstrip("-")
    return "other"


def parse_tournament(slug):
    """Heuristic: tokens between game marker and date look like tournament."""
    s = slug.lower()
    # Looks for patterns like "cs2-<tourney>-<team1>-<team2>-<date>"
    parts = s.split("-")
    if len(parts) < 5:
        return "unknown"
    # simplistic: take token 1 (after game prefix)
    return parts[1] if len(parts) > 1 else "unknown"


def parse_bo_format(question):
    q = (question or "").lower()
    if "bo3" in q or "(bo3)" in q:
        return "BO3"
    if "bo5" in q or "(bo5)" in q:
        return "BO5"
    if "bo1" in q or "(bo1)" in q:
        return "BO1"
    if "bo7" in q:
        return "BO7"
    return "unknown"


def main():
    df = load()
    # esports only
    df = df[df["slug"].str.lower().str.contains(
        r"cs2-|val-|lol-|dota|-esports-|blast-|iem-", regex=True, na=False
    )].copy()
    print(f"Esports markets with prices: {len(df)}")

    df["game"] = df["slug"].apply(parse_game)
    df["tournament"] = df["slug"].apply(parse_tournament)
    df["bo"] = df["question"].apply(parse_bo_format)

    # 0.5-0.6 bucket
    focus = df[(df["p"] >= 0.5) & (df["p"] < 0.6)].copy()
    print(f"\n0.5-0.6 bucket: n={len(focus)}")
    print(f"  Overall P(YES win): {focus['yes_won_int'].mean()*100:.1f}%")
    print(f"  Market implied avg: {focus['p'].mean()*100:.1f}%")
    print(f"  Bias: {(focus['yes_won_int'].mean() - focus['p'].mean())*100:+.1f}pp")

    print(f"\n--- BY GAME ---")
    g = focus.groupby("game").agg(
        n=("yes_won_int","size"),
        impl=("p","mean"),
        actual=("yes_won_int","mean"),
    )
    g["bias_pp"] = (g["actual"] - g["impl"]) * 100
    g[["impl","actual"]] = g[["impl","actual"]].round(3)
    g["bias_pp"] = g["bias_pp"].round(1)
    print(g.sort_values("n", ascending=False).to_string())

    print(f"\n--- BY BO FORMAT ---")
    g = focus.groupby("bo").agg(
        n=("yes_won_int","size"),
        impl=("p","mean"),
        actual=("yes_won_int","mean"),
    )
    g["bias_pp"] = (g["actual"] - g["impl"]) * 100
    print(g.round({"impl":3,"actual":3,"bias_pp":1}).to_string())

    print(f"\n--- BY TOURNAMENT (n>=15) ---")
    g = focus.groupby("tournament").agg(
        n=("yes_won_int","size"),
        impl=("p","mean"),
        actual=("yes_won_int","mean"),
    )
    g["bias_pp"] = (g["actual"] - g["impl"]) * 100
    g = g[g["n"] >= 15]
    print(g.round({"impl":3,"actual":3,"bias_pp":1}).sort_values("n", ascending=False).to_string())

    print(f"\n--- DAY OF WEEK (closed_time day) ---")
    focus["dow"] = focus["closed_time"].dt.day_name()
    g = focus.groupby("dow").agg(
        n=("yes_won_int","size"),
        actual=("yes_won_int","mean"),
    )
    print(g.round({"actual":3}).to_string())

    print(f"\n--- VOLUME TERTILES ---")
    focus["vol_tier"] = pd.qcut(focus["volume"], q=3, labels=["low","mid","high"])
    g = focus.groupby("vol_tier", observed=True).agg(
        n=("yes_won_int","size"),
        impl=("p","mean"),
        actual=("yes_won_int","mean"),
    )
    g["bias_pp"] = (g["actual"] - g["impl"]) * 100
    print(g.round({"impl":3,"actual":3,"bias_pp":1}).to_string())

    # Also: how many of these had yes_outcome being a specific side
    # In Polymarket esports, outcome[0] is usually alphabetical by team name
    # If bias is in outcome[0] winning less than expected, we could bet outcome[1]
    # But our bucket already filters 0.5-0.6 so YES is already the favorite
    # Interpretation: slight favorite at 0.55 wins only 44% → 6pp NO bias


if __name__ == "__main__":
    main()

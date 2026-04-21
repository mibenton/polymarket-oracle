"""Comprehensive pattern analysis: 318k Polymarket markets.

研究目的：找出「什麼類型的題目在什麼情況下比較容易 YES/NO」
目標是純 descriptive — 不做交易建議，先找規律。

分析維度：
  1. Question structure patterns (Will X, by date, etc.)
  2. Outcome naming conventions (Yes/No, Over/Under, team names)
  3. Category (sports, crypto, politics, weather, etc.)
  4. Price buckets (base rate by implied probability)
  5. Duration effect (short-lived vs long markets)
  6. Volume regime (retail vs sharp)
  7. Conditional tables (given X, P(YES))
"""
import re
from pathlib import Path
import numpy as np
import pandas as pd

OUT_DIR = Path("data/results/patterns")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_all():
    ext = pd.read_parquet("data/markets_ext.parquet")
    orig = pd.read_parquet("data/markets.parquet")
    m = pd.concat([ext, orig], ignore_index=True).drop_duplicates("id")
    m["closed_time"] = pd.to_datetime(m["closed_time"], utc=True, errors="coerce")
    m["start_date"] = pd.to_datetime(m["start_date"], utc=True, errors="coerce")
    m["duration_h"] = (m["closed_time"] - m["start_date"]).dt.total_seconds() / 3600
    m = m[m["duration_h"] >= 0]  # clean
    return m


# ==================== categorization ====================
def categorize(slug: str, question: str, y_out: str, n_out: str) -> str:
    s = (slug or "").lower()
    q = (question or "").lower()
    # prefix-based heuristics (most specific first)
    if any(k in s for k in ["nba-", "mlb-", "nhl-", "ncaa", "cbb-", "cfb-"]):
        return "sports_us"
    if any(k in s for k in ["ufc-", "atp-", "wta-", "fif-", "fl1-", "bun-",
                             "ucl-", "uel-", "epl-", "euroleague", "kbo-",
                             "mlb-", "pga", "wgp"]):
        return "sports_global"
    if any(k in s for k in ["cs2-", "val-", "lol-", "dota", "rocket-league",
                             "-esports-", "blast-", "iem-"]):
        return "esports"
    if "updown" in s or "up-or-down" in s or "upordown" in s:
        return "short_term_price_direction"
    if any(k in s for k in ["bitcoin-above-", "btc-above-", "ethereum-above-",
                             "eth-above-", "solana-above-", "sol-above-"]):
        return "crypto_price_threshold"
    if "dip-to-" in s or "hit-" in s or "reach-" in s:
        return "price_touch_threshold"
    if any(k in s for k in ["tweets", "tweet-", "-of-posts-", "-of-tweets-"]):
        return "tweet_count"
    if any(k in s for k in ["-election", "-primary", "-senate", "-governor",
                             "-president", "-parliament", "-nominee"]):
        return "politics_election"
    if any(k in s for k in ["fed-", "fomc", "cpi", "ecb-", "boj-",
                             "-rate-", "-key-rate", "bank-of-"]):
        return "macro_rates"
    if any(k in s for k in ["earnings", "quarterly", "beat-"]):
        return "earnings"
    if "ipo" in s:
        return "ipo"
    if any(k in s for k in ["highest-temperature", "temperature-in-",
                             "-weather-", "snowfall"]):
        return "weather"
    if any(k in s for k in ["oscar", "grammy", "box-office", "opening-weekend",
                             "gross", "movie"]):
        return "entertainment"
    if any(k in s for k in ["will-trump-", "will-biden-", "will-musk-",
                             "-publicly-", "-insult", "-mention-"]):
        return "public_figure_behavior"
    if any(k in s for k in ["russia-", "ukraine-", "iran-", "israel-",
                             "gaza-", "hamas-", "putin-"]):
        return "geopolitics"
    return "other"


def question_pattern(question: str) -> str:
    """Classify by question structure."""
    q = (question or "").lower().strip()
    if q.startswith("will ") and " by " in q:
        return "will_X_by_date"
    if q.startswith("will ") and " win " in q:
        return "will_X_win"
    if " vs. " in q or " vs " in q:
        return "vs_matchup"
    if q.endswith("?") and ("above" in q or "greater than" in q or "hit" in q):
        return "threshold_above"
    if q.endswith("?") and ("below" in q or "under" in q or "dip" in q):
        return "threshold_below"
    if " draw?" in q:
        return "draw_question"
    if q.startswith("can "):
        return "can_X_happen"
    if " between " in q:
        return "range_question"
    return "other_structure"


def outcome_type(y: str, n: str) -> str:
    """Classify outcome naming."""
    y_low = (y or "").lower()
    n_low = (n or "").lower()
    pair = f"{y_low}|{n_low}"
    if pair == "yes|no":
        return "yes_no"
    if pair == "over|under" or pair == "under|over":
        return "over_under"
    if pair == "up|down" or pair == "down|up":
        return "up_down"
    if pair == "draw|no" or pair == "no|draw":
        return "draw_pair"
    return "team_or_named"


# ==================== analysis ====================
def print_section(title):
    print(f"\n{'='*80}\n{title}\n{'='*80}")


def analyze(df: pd.DataFrame):
    df = df.copy()
    df["category"] = df.apply(
        lambda r: categorize(r["slug"], r["question"], r["yes_outcome"], r["no_outcome"]),
        axis=1,
    )
    df["q_pattern"] = df["question"].apply(question_pattern)
    df["outcome_type"] = df.apply(
        lambda r: outcome_type(r["yes_outcome"], r["no_outcome"]), axis=1
    )
    df["yes_won_int"] = df["yes_won"].astype(int)

    # ---- Category base rates ----
    print_section("1. BASE RATE P(YES WINS) BY CATEGORY")
    g = df.groupby("category").agg(
        n=("yes_won_int", "size"),
        p_yes=("yes_won_int", "mean"),
        med_vol=("volume", "median"),
        med_dur_h=("duration_h", "median"),
    ).sort_values("n", ascending=False)
    g["p_yes"] = (g["p_yes"] * 100).round(1)
    g["med_vol"] = g["med_vol"].round(0)
    g["med_dur_h"] = g["med_dur_h"].round(0)
    print(g.to_string())

    # ---- Question pattern base rates ----
    print_section("2. BASE RATE P(YES) BY QUESTION PATTERN")
    g = df.groupby("q_pattern").agg(
        n=("yes_won_int", "size"),
        p_yes=("yes_won_int", "mean"),
    ).sort_values("n", ascending=False)
    g["p_yes"] = (g["p_yes"] * 100).round(1)
    print(g.to_string())

    # ---- Outcome type ----
    print_section("3. BASE RATE P(YES) BY OUTCOME NAMING")
    g = df.groupby("outcome_type").agg(
        n=("yes_won_int", "size"),
        p_yes=("yes_won_int", "mean"),
    ).sort_values("n", ascending=False)
    g["p_yes"] = (g["p_yes"] * 100).round(1)
    print(g.to_string())

    # ---- "Will X by Y" markets specifically ----
    print_section('4. "Will X by [date]" MARKETS — STRONGLY NO-BIASED?')
    sub = df[df["q_pattern"] == "will_X_by_date"]
    print(f"  n = {len(sub):,}")
    print(f"  P(YES) = {sub['yes_won_int'].mean()*100:.1f}%")
    print(f"  Interpretation: '{sub['yes_won_int'].mean()*100:.0f}%' of the time the "
          f"described event did happen by the deadline.")
    # break down by category
    print("\n  By category:")
    g = sub.groupby("category").agg(n=("yes_won_int","size"), p_yes=("yes_won_int","mean"))
    g["p_yes"] = (g["p_yes"]*100).round(1)
    print(g.sort_values("n", ascending=False).head(10).to_string())

    # ---- Conditional: category × outcome_type ----
    print_section("5. P(YES) BY CATEGORY × OUTCOME_TYPE")
    ct = df.groupby(["category", "outcome_type"]).agg(
        n=("yes_won_int","size"), p_yes=("yes_won_int","mean")
    ).reset_index()
    ct["p_yes"] = (ct["p_yes"]*100).round(1)
    ct = ct[ct["n"] >= 100].sort_values(["category", "n"], ascending=[True, False])
    print(ct.to_string(index=False))


def analyze_named_markets(df: pd.DataFrame):
    """Deep dive into categories with enough samples."""
    df = df.copy()
    df["category"] = df.apply(
        lambda r: categorize(r["slug"], r["question"], r["yes_outcome"], r["no_outcome"]),
        axis=1,
    )
    df["yes_won_int"] = df["yes_won"].astype(int)

    # --- Short term price direction: up/down ---
    print_section("6. SHORT-TERM PRICE DIRECTION (UP/DOWN)")
    sub = df[df["category"] == "short_term_price_direction"].copy()
    if len(sub) > 100:
        # For up/down markets: outcome[0] is always "Up"?
        sub["up_side_is_yes_outcome"] = sub["yes_outcome"].str.lower().isin(["up"])
        # Actual Up % = yes_won if yes_outcome=Up else 1-yes_won
        sub["up_won"] = np.where(sub["up_side_is_yes_outcome"],
                                  sub["yes_won_int"], 1 - sub["yes_won_int"])
        print(f"  n={len(sub):,}, P(UP wins) = {sub['up_won'].mean()*100:.1f}%")
        # Break down by asset type
        for asset in ["bitcoin", "ethereum", "solana", "btc", "eth", "sol",
                      "xagusd", "eurusd", "dxy", "hood", "tsla", "nvda", "spy"]:
            a = sub[sub["slug"].str.contains(asset, case=False, na=False)]
            if len(a) >= 30:
                print(f"    {asset:<10}: n={len(a):>4}  P(UP)={a['up_won'].mean()*100:.1f}%")

    # --- Tweet count markets ---
    print_section("7. TWEET COUNT MARKETS")
    sub = df[df["category"] == "tweet_count"].copy()
    if len(sub) > 100:
        print(f"  n={len(sub):,}, P(YES) = {sub['yes_won_int'].mean()*100:.1f}%")
        # slug often has "-N-M" form for ranges; YES ≈ did actual count fall in range
        # so P(YES) low means narrow ranges usually miss
        print(f"  Interpretation: most tweet-count bucket markets resolve NO because the")
        print(f"  specific bucket rarely matches actual. That's why tail NO bets are 'safe'.")

    # --- Weather (highest temperature) ---
    print_section("8. WEATHER (HIGHEST TEMPERATURE) MARKETS")
    sub = df[df["category"] == "weather"].copy()
    if len(sub) > 100:
        print(f"  n={len(sub):,}, P(YES) = {sub['yes_won_int'].mean()*100:.1f}%")
        # Extract threshold + orhigher/orbelow from slug
        def classify_weather(slug):
            s = slug.lower()
            if "orhigher" in s or "orabove" in s:
                return "YES_means_at_or_above"
            if "orbelow" in s or "orlower" in s:
                return "YES_means_at_or_below"
            return "other"
        sub["kind"] = sub["slug"].apply(classify_weather)
        print(sub.groupby("kind").agg(
            n=("yes_won_int","size"), p_yes=("yes_won_int","mean")
        ).to_string())

    # --- Crypto price threshold ---
    print_section("9. CRYPTO PRICE THRESHOLD (above / dip to) MARKETS")
    sub = df[df["category"].isin(["crypto_price_threshold", "price_touch_threshold"])].copy()
    if len(sub) > 100:
        print(f"  n={len(sub):,}, P(YES) = {sub['yes_won_int'].mean()*100:.1f}%")

    # --- Sports matchups: does home/first side win? ---
    print_section("10. SPORTS MATCHUPS: P(OUTCOME_0 WINS)")
    sub = df[df["category"].str.startswith("sports")].copy()
    if len(sub) > 100:
        print(f"  Total sports n={len(sub):,}")
        # outcome_0 in Polymarket sports is usually away / first-listed team
        # yes_won = outcome_0 won
        print(f"  P(outcome_0 wins) = {sub['yes_won_int'].mean()*100:.1f}%")
        # Sports subcats
        for cat in ["sports_us", "sports_global", "esports"]:
            ss = df[df["category"] == cat]
            if len(ss) >= 100:
                print(f"    {cat:<15}: n={len(ss):>5}  P(outcome_0)={ss['yes_won_int'].mean()*100:.1f}%")

    # --- Politics/elections ---
    print_section("11. POLITICS / ELECTIONS")
    sub = df[df["category"] == "politics_election"].copy()
    if len(sub) > 50:
        print(f"  n={len(sub):,}, P(YES) = {sub['yes_won_int'].mean()*100:.1f}%")
        print(f"  (Mostly 'Will X win primary/election?' — most candidates lose → YES rare)")

    # --- Geopolitics ---
    print_section("12. GEOPOLITICS (Russia/Ukraine/Iran/Israel)")
    sub = df[df["category"] == "geopolitics"].copy()
    if len(sub) > 50:
        print(f"  n={len(sub):,}, P(YES) = {sub['yes_won_int'].mean()*100:.1f}%")
        # break by keyword
        for kw in ["russia", "ukraine", "iran", "israel", "gaza", "hamas"]:
            a = sub[sub["slug"].str.contains(kw, case=False, na=False)]
            if len(a) >= 30:
                print(f"    {kw:<10}: n={len(a):>4}  P(YES)={a['yes_won_int'].mean()*100:.1f}%")

    # --- Public figure behavior ---
    print_section("13. PUBLIC FIGURE BEHAVIOR (Trump/Musk/Biden ...)")
    sub = df[df["category"] == "public_figure_behavior"].copy()
    if len(sub) > 50:
        print(f"  n={len(sub):,}, P(YES) = {sub['yes_won_int'].mean()*100:.1f}%")


def time_effects(df: pd.DataFrame):
    print_section("14. DURATION EFFECT")
    df = df.copy()
    df["yes_won_int"] = df["yes_won"].astype(int)
    df["dur_bucket"] = pd.cut(df["duration_h"],
                               bins=[0, 6, 24, 72, 168, 720, 1e6],
                               labels=["<6h", "6-24h", "1-3d", "3-7d", "1-4w", ">4w"])
    g = df.groupby("dur_bucket", observed=True).agg(
        n=("yes_won_int","size"), p_yes=("yes_won_int","mean")
    )
    g["p_yes"] = (g["p_yes"]*100).round(1)
    print(g.to_string())


def volume_effects(df: pd.DataFrame):
    print_section("15. VOLUME EFFECT ON P(YES)")
    df = df.copy()
    df["yes_won_int"] = df["yes_won"].astype(int)
    df["vol_bucket"] = pd.cut(df["volume"],
                               bins=[0, 100, 1000, 10000, 100000, 1e6, 1e10],
                               labels=["<$100", "$100-1k", "$1k-10k",
                                       "$10k-100k", "$100k-1M", ">$1M"])
    g = df.groupby("vol_bucket", observed=True).agg(
        n=("yes_won_int","size"), p_yes=("yes_won_int","mean")
    )
    g["p_yes"] = (g["p_yes"]*100).round(1)
    print(g.to_string())


def main():
    df = load_all()
    print(f"Loaded {len(df):,} markets")
    print(f"Time range: {df['closed_time'].min()} -> {df['closed_time'].max()}")
    print(f"Overall P(YES wins) = {df['yes_won'].astype(int).mean()*100:.1f}%")

    analyze(df)
    analyze_named_markets(df)
    time_effects(df)
    volume_effects(df)


if __name__ == "__main__":
    main()

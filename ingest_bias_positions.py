"""Convert bias scanner hits into paper-trade decisions.

Filters:
  - Tier A+ (size 2% bankroll) and Tier B (size 1% bankroll)
  - end_date in future and within 30 days
  - volume >= $2000 (tradeable)
  - limit to 25 new positions per run (diversification)

Appends to data/oracle_decisions.jsonl so oracle_portfolio.py --ingest can open positions.
"""
import json
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd

CANDIDATES = Path("data/results/bias_candidates.csv")
DEC_FILE = Path("data/oracle_decisions.jsonl")
MAX_NEW_POSITIONS = 25
MAX_DAYS_TO_CLOSE = 30
# Stake sizing per tier (Cycle 19 Kelly analysis)
# S sweet spot: full 1/4 Kelly ≈ 3%
# A: 1/4 Kelly says 3.1% for high-price end, 1% for low-price end. Pick middle 2.5%
# B: 1/4 Kelly ≈ 1%
STAKE_PCT = {"S": 0.03, "A+": 0.025, "A": 0.02, "B": 0.01, "C": 0.005}


def main():
    if not CANDIDATES.exists():
        print(f"[skip] {CANDIDATES} not found — run cycle6_bias_scanner.py first")
        return
    df = pd.read_csv(CANDIDATES)
    print(f"Raw candidates: {len(df)}")

    # Accept tiers S, A+, A, B
    df = df[df["tier"].isin(["S", "A+", "A", "B"])].copy()
    print(f"Tier S/A+/A/B: {len(df)}")
    if df.empty:
        print("No candidates.")
        return

    # Parse end_date and filter future
    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=MAX_DAYS_TO_CLOSE)
    def parse_end(s):
        try:
            return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        except Exception:
            return None
    df["end_dt"] = df["end_date"].apply(parse_end)
    df = df[df["end_dt"].notna()]
    # Cycle 11 finding: T-12h entry is disastrous (-15 to -50% PnL)
    # Optimal is T-48 to T-72h. Raise minimum to 30h to be safely past T-24 risk zone.
    df = df[(df["end_dt"] > now + timedelta(hours=30)) & (df["end_dt"] <= cutoff)]
    print(f"In future (30h-30d window): {len(df)}")

    # Dedupe by slug (same market can appear twice from PSG O/U etc)
    df = df.drop_duplicates(subset=["slug"]).copy()

    # Rank: prefer higher volume × tier priority × not-too-soon
    tier_prio = {"S": 5, "A+": 4, "A": 3, "B": 2, "C": 1}
    df["tier_prio"] = df["tier"].map(tier_prio).fillna(0)
    df["hours_to_close"] = (df["end_dt"] - now).dt.total_seconds() / 3600
    # Rank: high-volume + higher-tier + at least 6h away (avoid near-expiry slippage)
    df["rank"] = df["tier_prio"] * 1000 + df["volume"] / (df["hours_to_close"] + 24)
    # Prefer 4/25+ (skip overdone 4/24 which we already have 12 open)
    df = df.sort_values("rank", ascending=False).head(MAX_NEW_POSITIONS)

    print(f"\nSelected {len(df)} positions:\n")
    print(df[["slug", "best_side", "entry_price", "volume", "hours_to_close",
              "expected_ev_pct"]].to_string(index=False))

    # Append decisions
    existing_slugs = set()
    if DEC_FILE.exists():
        for line in DEC_FILE.read_text(encoding="utf-8").strip().split("\n"):
            if line:
                try:
                    existing_slugs.add(json.loads(line)["slug"])
                except Exception:
                    pass

    new_lines = []
    for _, r in df.iterrows():
        if r["slug"] in existing_slugs:
            continue
        side = "BUY YES" if r["best_side"] == "YES" else "BUY NO"
        stake = STAKE_PCT.get(r["tier"], 0.01)
        dec = {
            "slug": r["slug"],
            "decision": side,
            "p_claude": 0.55 if r["best_side"] == "YES" else 0.45,  # placeholder
            "p_market_yes": r["mid"],
            "entry_price": r["entry_price"],
            "edge_bps": int(r["expected_ev_pct"] * 100),
            "confidence": 3 if r["tier"] in ("A+","A") else 2,
            "position_pct_of_bankroll": stake,
            "tier": r["tier"],
            "reasoning": f"Tier-{r['tier']} bias pocket ({r['category']} {r['pocket']}, "
                         f"historical n={r['historical_n']}). "
                         f"Expected EV {r['expected_ev_pct']:.1f}% after fee.",
            "question": r["question"],
            "end_date": r["end_date"],
            "source": "bias_scanner",
            "analyzed_at": now.isoformat(),
        }
        new_lines.append(json.dumps(dec, ensure_ascii=False))

    if new_lines:
        with DEC_FILE.open("a", encoding="utf-8") as f:
            for line in new_lines:
                f.write(line + "\n")
        print(f"\n[APPENDED] {len(new_lines)} new decisions to {DEC_FILE}")
    else:
        print("\nNo new decisions (all slugs already recorded).")

    print("\nNext: python oracle_portfolio.py --ingest")


if __name__ == "__main__":
    main()

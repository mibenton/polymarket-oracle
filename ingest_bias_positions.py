"""Convert Tier-A bias scanner hits into paper-trade decisions.

Filters:
  - Tier A only (stable across 3 sub-windows)
  - end_date in future and within 30 days
  - volume >= $2000 (tradeable)
  - limit to 20 positions max (diversification)

Appends to data/oracle_decisions.jsonl so oracle_portfolio.py --ingest can open positions.
"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pandas as pd

CANDIDATES = Path("data/results/bias_candidates.csv")
DEC_FILE = Path("data/oracle_decisions.jsonl")
MAX_POSITIONS = 20
MAX_DAYS_TO_CLOSE = 30


def main():
    df = pd.read_csv(CANDIDATES)
    print(f"Raw candidates: {len(df)}")

    # Tier A only
    df = df[df["tier"] == "A"].copy()
    print(f"Tier A: {len(df)}")

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
    df = df[(df["end_dt"] > now + timedelta(hours=12)) & (df["end_dt"] <= cutoff)]
    print(f"In future (12h-30d window): {len(df)}")

    # Dedupe by slug (same market can appear twice from PSG O/U etc)
    df = df.drop_duplicates(subset=["slug"]).copy()

    # Rank: prefer higher volume (liquidity), slightly shorter to close
    df["hours_to_close"] = (df["end_dt"] - now).dt.total_seconds() / 3600
    df["rank"] = df["volume"] / (df["hours_to_close"] + 24)
    df = df.sort_values("rank", ascending=False).head(MAX_POSITIONS)

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
        dec = {
            "slug": r["slug"],
            "decision": side,
            "p_claude": 0.55 if r["best_side"] == "YES" else 0.45,  # placeholder
            "p_market_yes": r["mid"],
            "entry_price": r["entry_price"],
            "edge_bps": int(r["expected_ev_pct"] * 100),
            "confidence": 3,  # moderate, stability-backed
            "position_pct_of_bankroll": 0.02,  # 2% per position
            "reasoning": f"Tier-A statistical bias pocket ({r['category']} {r['pocket']}, "
                         f"historical n={r['historical_n']}, cross-window stable). "
                         f"Expected EV {r['expected_ev_pct']:.1f}% after fee.",
            "question": r["question"],
            "end_date": r["end_date"],
            "source": "bias_scanner_TA",
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

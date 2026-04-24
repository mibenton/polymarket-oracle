"""Cycle 9B: Auto-tier adjustment based on closed positions.

Rule:
- Take all closed positions tagged by tier.
- For each tier, compute win_rate and mean PnL.
- If PnL < -5% after n>=10 → DEMOTE 1 level
- If PnL > +15% after n>=10 → PROMOTE 1 level (up to S)
- Write a suggestion report (does NOT auto-modify scanner, user confirms)
"""
import json
from pathlib import Path
import pandas as pd

POS_FILE = Path("data/oracle_positions.csv")
DEC_FILE = Path("data/oracle_decisions.jsonl")
OUT = Path("data/results/tier_adjustment_report.md")

TIER_ORDER = ["C", "B", "A", "A+", "S"]
MIN_N_FOR_DECISION = 8


def load_closed_with_tier():
    if not POS_FILE.exists():
        return pd.DataFrame()
    pos = pd.read_csv(POS_FILE)
    closed = pos[pos["status"] == "CLOSED"].copy()
    if closed.empty:
        return closed

    # Map decisions → slug → (tier, pocket_category)
    tier_map = {}
    cat_map = {}
    if DEC_FILE.exists():
        with DEC_FILE.open(encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    tier = d.get("tier")
                    if not tier:
                        tier = infer_tier_from_reasoning(d.get("reasoning", ""))
                    tier_map[d["slug"]] = tier
                    # infer pocket category
                    r = (d.get("reasoning","") + " " + d.get("slug","")).lower()
                    if "weather" in r or "temperature" in r:
                        cat_map[d["slug"]] = "weather"
                    elif "sports_global" in r or "atp-" in r or "wta-" in r or \
                         "kbo-" in r or "epl-" in r or "ufc-" in r or "bun-" in r or \
                         "fl1-" in r or "fif-" in r:
                        cat_map[d["slug"]] = "sports"
                    elif "lol" in r:
                        cat_map[d["slug"]] = "lol"
                    else:
                        cat_map[d["slug"]] = "other"
                except Exception:
                    continue
    closed["tier"] = closed["slug"].map(tier_map).fillna("unknown")
    closed["pocket"] = closed["slug"].map(cat_map).fillna("other")
    return closed


def infer_tier_from_reasoning(reason: str) -> str:
    """Legacy: pre-tier decisions tagged via reasoning string."""
    r = (reason or "").lower()
    if "tier-s" in r or "sweet spot" in r:
        return "S"
    if "tier-a+" in r:
        return "A+"
    if "tier-a" in r:
        return "A"
    if "tier-b" in r:
        return "B"
    if "tier-c" in r:
        return "C"
    return "unknown"


def analyze():
    closed = load_closed_with_tier()
    if closed.empty:
        return "No closed positions to analyze."

    # Compute per (pocket, tier) stats
    stats = []
    for (pocket, tier), sub in closed.groupby(["pocket", "tier"]):
        if tier == "unknown":
            continue
        n = len(sub)
        total_stake = sub["stake_usd"].sum()
        total_pnl = sub["pnl_usd"].sum()
        mean_ret = total_pnl / total_stake if total_stake > 0 else 0
        win_rate = (sub["pnl_usd"] > 0).mean()
        stats.append({
            "pocket": pocket,
            "tier": tier,
            "n": n,
            "total_stake": round(total_stake, 2),
            "total_pnl": round(total_pnl, 2),
            "mean_return_pct": round(mean_ret * 100, 1),
            "win_rate_pct": round(win_rate * 100, 0),
        })
    df = pd.DataFrame(stats)

    # Recommend adjustments
    recs = []
    for _, row in df.iterrows():
        tier = row["tier"]
        n = row["n"]
        mean_ret = row["mean_return_pct"]
        if n < MIN_N_FOR_DECISION:
            rec = "HOLD (insufficient n)"
        elif mean_ret < -5:
            rec = "DEMOTE (mean return < -5%)"
        elif mean_ret > 15:
            rec = "PROMOTE (mean return > 15%)"
        else:
            rec = "HOLD (within expected range)"
        recs.append(rec)
    df["recommendation"] = recs

    # Write report
    OUT.parent.mkdir(exist_ok=True)
    report = [
        "# Auto-Tier Adjustment Report",
        "",
        f"Generated from {len(closed)} closed positions.",
        "",
        "## Tier Performance",
        "",
        df.to_markdown(index=False),
        "",
        "## Decisions",
        "",
    ]
    for _, r in df.iterrows():
        report.append(f"- **Tier {r['tier']}**: {r['recommendation']}  "
                       f"(n={r['n']}, return={r['mean_return_pct']}%, "
                       f"pnl=${r['total_pnl']})")

    report.append("\n## Rule")
    report.append("- Demote if mean return < -5% with n>=8")
    report.append("- Promote if mean return > 15% with n>=8")
    report.append("- Hold otherwise")
    report.append("")

    OUT.write_text("\n".join(report), encoding="utf-8")

    # Print
    print("\n" + "="*70)
    print("TIER PERFORMANCE")
    print("="*70)
    print(df.to_string(index=False))
    print(f"\nReport written to {OUT}")
    return df


if __name__ == "__main__":
    analyze()

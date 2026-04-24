"""Cycle 65: Strategy health monitor.

Checks:
1. Are closed positions tracking historical EV?
2. Is any tier under-performing by > 50%?
3. Edge decay week-over-week
4. Drawdown status
5. Recommends adjustments
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

POS_FILE = Path("data/oracle_positions.csv")
DEC_FILE = Path("data/oracle_decisions.jsonl")
OUT = Path("data/results/health_report.md")

# Historical EV expectations from evolution
EXPECTED_EV = {
    "S++": 2.07, "S+": 1.76, "S": 1.23,
    "A+": 0.25, "A": 0.80,
    "B++": 2.81, "B+": 1.75, "B": 0.19,
    "C": 1.00,
}


def load_closed_with_tier():
    if not POS_FILE.exists():
        return pd.DataFrame()
    pos = pd.read_csv(POS_FILE)
    closed = pos[pos["status"] == "CLOSED"].copy()
    tier_map = {}
    if DEC_FILE.exists():
        text = DEC_FILE.read_text(encoding="utf-8")
        for line in text.strip().split("\n"):
            if not line: continue
            try:
                d = json.loads(line)
                tier = d.get("tier")
                if not tier:
                    r = d.get("reasoning", "").lower()
                    for t in ["s++", "s+", "s", "a+", "a", "b++", "b+", "b", "c"]:
                        if f"tier-{t}" in r or f"tier {t}" in r:
                            tier = t.upper(); break
                tier_map[d["slug"]] = tier or "unknown"
            except Exception:
                continue
    closed["tier"] = closed["slug"].map(tier_map).fillna("unknown")
    return closed


def health_check():
    closed = load_closed_with_tier()
    report = ["# Strategy Health Report", ""]

    if closed.empty:
        report.append("No closed positions yet.")
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text("\n".join(report))
        return

    report.append(f"Closed positions: {len(closed)}")
    report.append(f"Time window: recent paper trades")
    report.append("")

    # Per-tier actual vs expected
    report.append("## Tier Performance (actual vs expected)")
    report.append("")
    report.append("| Tier | n | Actual Ret | Expected | Delta | Status |")
    report.append("|------|---|-----------|----------|-------|--------|")

    overall_delta = 0
    count_weighted = 0
    for tier, sub in closed.groupby("tier"):
        if tier == "unknown" or tier not in EXPECTED_EV:
            continue
        n = len(sub)
        total_stake = sub["stake_usd"].sum()
        total_pnl = sub["pnl_usd"].sum()
        actual_ret = total_pnl / total_stake if total_stake > 0 else 0
        expected = EXPECTED_EV[tier]
        delta = actual_ret - expected
        overall_delta += delta * n
        count_weighted += n

        status = "🟢 OK" if delta > -0.3 else ("🟡 WATCH" if delta > -0.7 else "🔴 ALERT")
        report.append(f"| {tier} | {n} | {actual_ret:+.2f} | +{expected:.2f} | {delta:+.2f} | {status} |")

    if count_weighted > 0:
        avg_delta = overall_delta / count_weighted
        report.append("")
        report.append(f"**Weighted average delta**: {avg_delta:+.2f}")
        if avg_delta < -0.5:
            report.append("\n🔴 **Overall alert**: strategy under-performing by >50%. Consider pause/review.")
        elif avg_delta < -0.2:
            report.append("\n🟡 **Watch**: strategy slightly under-performing. Continue monitoring.")
        else:
            report.append("\n🟢 **Healthy**: strategy tracking expectations.")

    # Recent vs older performance
    if "closed_at" in closed.columns:
        closed["closed_at"] = pd.to_datetime(closed["closed_at"], utc=True, errors="coerce")
        recent_cut = closed["closed_at"].max() - pd.Timedelta(days=7)
        recent = closed[closed["closed_at"] >= recent_cut]
        older = closed[closed["closed_at"] < recent_cut]
        if len(recent) > 0 and len(older) > 0:
            recent_ret = recent["pnl_usd"].sum() / recent["stake_usd"].sum()
            older_ret = older["pnl_usd"].sum() / older["stake_usd"].sum()
            report.append("")
            report.append(f"## Recent (last 7d) vs Older")
            report.append(f"- Recent: n={len(recent)}, return={recent_ret*100:+.1f}%")
            report.append(f"- Older:  n={len(older)}, return={older_ret*100:+.1f}%")
            if recent_ret < older_ret - 0.3:
                report.append("\n⚠️ Recent performance significantly worse — possible edge decay")

    # Drawdown check
    report.append("")
    report.append("## Drawdown")
    bankroll_starting = 10000
    cumulative_pnl = closed["pnl_usd"].sum()
    current_bankroll = bankroll_starting + cumulative_pnl
    # Simple running max
    chronological = closed.sort_values("closed_at") if "closed_at" in closed.columns else closed
    balances = [bankroll_starting]
    b = bankroll_starting
    for _, r in chronological.iterrows():
        b += r["pnl_usd"]
        balances.append(b)
    peak = max(balances)
    trough = min(balances[balances.index(peak):] if peak in balances else balances)
    dd = (trough - peak) / peak if peak > 0 else 0
    report.append(f"- Starting: ${bankroll_starting:,}")
    report.append(f"- Current:  ${current_bankroll:,.0f}")
    report.append(f"- Peak:     ${peak:,.0f}")
    report.append(f"- Max DD from peak: {dd*100:.1f}%")
    if dd < -0.30:
        report.append("\n🔴 Drawdown > 30%. Consider pause + reset.")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    print(f"\nReport saved to {OUT}")


if __name__ == "__main__":
    health_check()

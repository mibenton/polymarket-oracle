"""Oracle Portfolio — paper-trade ledger.

Data files:
  data/oracle_decisions.jsonl    — per-analysis JSON outputs (append-only)
  data/oracle_positions.csv      — active + closed paper positions
  data/oracle_pnl.csv            — per-position realized PnL

Usage:
  python oracle_portfolio.py --ingest           # read decisions, open paper positions
  python oracle_portfolio.py --status           # show current positions + unrealized
  python oracle_portfolio.py --settle           # check closed markets & realize PnL
  python oracle_portfolio.py --report           # overall stats
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

GAMMA = "https://gamma-api.polymarket.com/markets"
DEC_FILE = Path("data/oracle_decisions.jsonl")
POS_FILE = Path("data/oracle_positions.csv")
PNL_FILE = Path("data/oracle_pnl.csv")

BANKROLL_START = 10_000.0  # paper bankroll

# Realistic UA to bypass Cloudflare bot detection on cloud IPs
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def load_decisions() -> list[dict]:
    if not DEC_FILE.exists():
        return []
    text = DEC_FILE.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.strip().split("\n") if line]


def load_positions() -> pd.DataFrame:
    if POS_FILE.exists():
        return pd.read_csv(POS_FILE)
    return pd.DataFrame(columns=[
        "slug", "question", "side", "entry_price", "stake_usd",
        "p_claude", "confidence", "edge_bps", "opened_at",
        "end_date", "status", "resolution_outcome", "pnl_usd", "closed_at",
    ])


def save_positions(df: pd.DataFrame):
    df.to_csv(POS_FILE, index=False)


def ingest():
    """Turn new BUY decisions into paper positions."""
    decisions = load_decisions()
    if not decisions:
        print("No decisions in oracle_decisions.jsonl")
        return

    positions = load_positions()
    existing_slugs = set(positions["slug"].tolist()) if not positions.empty else set()

    new_rows = []
    for d in decisions:
        if d.get("decision") not in ("BUY YES", "BUY NO"):
            continue
        if d.get("slug") in existing_slugs:
            continue

        side = "YES" if d["decision"] == "BUY YES" else "NO"
        # entry price: use p_market_yes for YES, (1 - p_market_yes) for NO
        # but better: caller should have put actual ask in entry_price if available
        entry = d.get("entry_price") or d.get("p_market_yes", 0.5)
        if side == "NO":
            entry = 1 - entry
        stake_pct = d.get("position_pct_of_bankroll", 0.02)
        stake_usd = BANKROLL_START * stake_pct

        new_rows.append({
            "slug": d["slug"],
            "question": d.get("question", ""),
            "side": side,
            "entry_price": entry,
            "stake_usd": stake_usd,
            "p_claude": d.get("p_claude"),
            "confidence": d.get("confidence"),
            "edge_bps": d.get("edge_bps"),
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "end_date": d.get("end_date", ""),
            "status": "OPEN",
            "resolution_outcome": "",
            "pnl_usd": 0.0,
            "closed_at": "",
        })

    if not new_rows:
        print("No new BUY decisions to ingest.")
        return

    positions = pd.concat([positions, pd.DataFrame(new_rows)], ignore_index=True)
    save_positions(positions)
    print(f"Opened {len(new_rows)} new paper positions.")
    for r in new_rows:
        print(f"  [{r['side']}] ${r['stake_usd']:.0f} @ {r['entry_price']:.3f}  "
              f"edge={r['edge_bps']}bps  {r['question'][:70]}")


def fetch_market_state(slug: str) -> dict | None:
    """Query gamma-api. Default returns only open markets, so retry with closed=true if empty."""
    for closed in ("false", "true"):
        try:
            r = requests.get(
                GAMMA,
                params={"slug": slug, "limit": 1, "closed": closed},
                headers=HEADERS, timeout=15,
            )
            if r.status_code != 200:
                print(f"    [warn {slug}] status {r.status_code}: {r.text[:80]}")
                return None
            data = r.json()
            if data and isinstance(data, list):
                return data[0]
        except Exception as e:
            print(f"    [exc {slug}] {type(e).__name__}: {e}")
            return None
    return None


def settle():
    """Check each OPEN position's current status and realize if closed."""
    positions = load_positions()
    if positions.empty:
        print("No positions.")
        return
    open_pos = positions[positions["status"] == "OPEN"]
    if open_pos.empty:
        print("No open positions.")
        return

    print(f"Checking {len(open_pos)} open positions...")
    for idx, row in open_pos.iterrows():
        state = fetch_market_state(row["slug"])
        if not state:
            print(f"  {row['slug']}: fetch failed")
            continue
        closed = state.get("closed")
        if not closed:
            # still open; compute unrealized
            try:
                mid = (float(state.get("bestAsk", 0)) + float(state.get("bestBid", 0))) / 2
            except Exception:
                mid = None
            if mid:
                side = row["side"]
                cur_price = mid if side == "YES" else (1 - mid)
                unreal = (cur_price / row["entry_price"] - 1) * row["stake_usd"]
                print(f"  [OPEN]    {row['slug'][:50]}  unrealized=${unreal:+.1f}")
            continue

        # closed → realize
        try:
            outcome_prices = json.loads(state.get("outcomePrices") or "[]")
        except Exception:
            outcome_prices = []
        if len(outcome_prices) != 2:
            continue
        yes_won = float(outcome_prices[0]) == 1
        side_won = yes_won if row["side"] == "YES" else not yes_won
        if side_won:
            payout = row["stake_usd"] / row["entry_price"]  # share count × $1
            pnl = payout - row["stake_usd"]
        else:
            pnl = -row["stake_usd"]

        positions.at[idx, "status"] = "CLOSED"
        positions.at[idx, "resolution_outcome"] = "YES" if yes_won else "NO"
        positions.at[idx, "pnl_usd"] = pnl
        positions.at[idx, "closed_at"] = datetime.now(timezone.utc).isoformat()
        print(f"  [CLOSED]  {row['slug'][:50]}  side={row['side']} "
              f"won={side_won}  pnl=${pnl:+.1f}")

    save_positions(positions)


def status():
    positions = load_positions()
    if positions.empty:
        print("No positions.")
        return
    print(f"Bankroll start: ${BANKROLL_START:,.0f}")
    print()
    open_pos = positions[positions["status"] == "OPEN"]
    closed_pos = positions[positions["status"] == "CLOSED"]
    print(f"OPEN positions: {len(open_pos)}")
    if not open_pos.empty:
        for _, r in open_pos.iterrows():
            print(f"  [{r['side']:<3}] ${r['stake_usd']:>6.0f} @ {r['entry_price']:.3f}  "
                  f"edge={r['edge_bps']}bps conf={r['confidence']}/5  "
                  f"{(r['question'] or '')[:60]}")

    print(f"\nCLOSED positions: {len(closed_pos)}")
    if not closed_pos.empty:
        wins = (closed_pos["pnl_usd"] > 0).sum()
        total_pnl = closed_pos["pnl_usd"].sum()
        print(f"  win rate: {wins}/{len(closed_pos)} = {wins/len(closed_pos)*100:.0f}%")
        print(f"  total realized PnL: ${total_pnl:+,.2f}")
        print(f"  bankroll change: {total_pnl/BANKROLL_START*100:+.2f}%")

    # total stake at risk
    at_risk = open_pos["stake_usd"].sum() if not open_pos.empty else 0
    print(f"\nCapital at risk (open): ${at_risk:,.0f} ({at_risk/BANKROLL_START*100:.1f}% of bankroll)")


def report():
    positions = load_positions()
    if positions.empty:
        print("No positions.")
        return
    closed = positions[positions["status"] == "CLOSED"]
    if closed.empty:
        print("No closed positions yet.")
        return

    wins = (closed["pnl_usd"] > 0).sum()
    n = len(closed)
    total_pnl = closed["pnl_usd"].sum()
    mean_pnl = closed["pnl_usd"].mean()
    mean_ret = (closed["pnl_usd"] / closed["stake_usd"]).mean() * 100

    print(f"ORACLE PORTFOLIO REPORT")
    print(f"=" * 60)
    print(f"  closed positions:  {n}")
    print(f"  wins:              {wins} ({wins/n*100:.0f}%)")
    print(f"  total realized:    ${total_pnl:+,.2f}")
    print(f"  mean pnl/trade:    ${mean_pnl:+.2f}")
    print(f"  mean return/stake: {mean_ret:+.1f}%")

    # by confidence
    print(f"\n  By confidence:")
    for c in sorted(closed["confidence"].unique()):
        sub = closed[closed["confidence"] == c]
        wr = (sub["pnl_usd"] > 0).mean() * 100
        pnl = sub["pnl_usd"].sum()
        print(f"    conf={c}: n={len(sub)}, win%={wr:.0f}, pnl=${pnl:+.1f}")

    # by edge size
    print(f"\n  By edge size:")
    edge_bins = [0, 500, 1000, 2000, 5000, 1e9]
    edge_labels = ["<500bps", "500-1000", "1000-2000", "2000-5000", ">5000"]
    closed["edge_bin"] = pd.cut(closed["edge_bps"].abs(), bins=edge_bins, labels=edge_labels)
    for label, sub in closed.groupby("edge_bin", observed=True):
        wr = (sub["pnl_usd"] > 0).mean() * 100
        pnl = sub["pnl_usd"].sum()
        print(f"    {label}: n={len(sub)}, win%={wr:.0f}, pnl=${pnl:+.1f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ingest", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--settle", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    if args.ingest:
        ingest()
    elif args.settle:
        settle()
    elif args.report:
        report()
    else:
        status()


if __name__ == "__main__":
    main()

"""Grade student answers against hidden answer key — 100-question edition."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

KEY = Path("data/workbook/answer_key.parquet")
BATCH_DIR = Path("data/workbook")
TAKER_FEE = 0.01
BANKROLL = 10_000


def brier(p, actual):
    return np.asarray((p - actual) ** 2)


def load_all_answers() -> pd.DataFrame:
    """Merge all answer batches (answers_batch_N.json) + any legacy student_answers.json."""
    records = []
    for path in sorted(BATCH_DIR.glob("answers_batch_*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                records.extend(data)
        except Exception as e:
            print(f"  failed to parse {path}: {e}")
    # fallback
    legacy = BATCH_DIR / "student_answers.json"
    if legacy.exists() and not records:
        data = json.loads(legacy.read_text(encoding="utf-8"))
        if isinstance(data, list):
            records.extend(data)
    return pd.DataFrame(records)


def categorize(slug: str) -> str:
    s = (slug or "").lower()
    if any(k in s for k in ["nba-", "mlb-", "nhl-", "ncaa", "cbb-", "ufc-",
                             "atp-", "wta-", "cs2-", "val-", "lol-", "ucl-",
                             "uel-", "epl-", "bun-", "fl1-", "fif-", "euroleague"]):
        return "sports_esports"
    if any(k in s for k in ["bitcoin", "btc-", "ethereum", "eth-", "solana",
                             "updown", "above-", "dip-", "xagusd", "hood-"]):
        return "crypto_fx"
    if any(k in s for k in ["election", "primary", "senate", "president",
                             "minister", "parliament"]):
        return "politics"
    if any(k in s for k in ["fed-", "rate", "fomc", "cpi"]):
        return "macro"
    if any(k in s for k in ["tweet", "post", "cruz", "trump", "musk", "starmer"]):
        return "behavior"
    if any(k in s for k in ["ipo", "earnings", "quarterly"]):
        return "corporate"
    if "temperature" in s or "weather" in s or "snow" in s:
        return "weather"
    return "other"


def grade():
    ans = load_all_answers()
    key = pd.read_parquet(KEY)

    print("="*80)
    print(f"WORKBOOK GRADE REPORT — {len(ans)} answers on {len(key)} questions")
    print("="*80)

    if len(ans) == 0:
        print("No answers.")
        return

    merged = ans.merge(
        key[["q_id", "slug", "yes_won", "p", "fav_won", "fav_price",
             "yes_outcome", "no_outcome", "bucket", "question", "volume"]],
        on="q_id", how="left", suffixes=("_ans", "_key")
    )
    # use key's slug as canonical
    merged["slug"] = merged["slug_key"].fillna(merged.get("slug_ans"))
    merged["category"] = merged["slug"].apply(categorize)

    # ============== Decision distribution ==============
    print(f"\nDecision distribution:")
    print(merged["decision"].value_counts().to_string())
    skip_rate = (merged["decision"] == "SKIP").mean() * 100
    print(f"SKIP rate: {skip_rate:.0f}% (target 70-80%)")

    # possible_leakage
    if "possible_leakage" in merged.columns:
        leak_count = merged["possible_leakage"].fillna(False).sum()
        print(f"Self-flagged possible leakage: {leak_count}")

    # ============== BUY decisions: PnL ==============
    bets = merged[merged["decision"].isin(["BUY YES", "BUY NO"])].copy()
    if len(bets) == 0:
        print("\nNo BUY decisions (100% SKIP).")
    else:
        def compute_pnl(r):
            won = bool(r["yes_won"]) if r["decision"] == "BUY YES" else not bool(r["yes_won"])
            entry = r["entry_price"]
            gross = (1.0 / entry) - 1 if won else -1.0
            net = gross - TAKER_FEE
            stake = BANKROLL * r["position_pct_of_bankroll"]
            pnl = stake * net
            return won, gross, net, stake, pnl

        bets[["won", "gross_pct", "net_pct", "stake_usd", "pnl_usd"]] = bets.apply(
            lambda r: pd.Series(compute_pnl(r)), axis=1
        )

        print(f"\n--- BUY decisions ({len(bets)}) ---")
        for _, r in bets.iterrows():
            flag = "LEAK" if r.get("possible_leakage") else "    "
            print(f"  Q{int(r['q_id']):>3} [{flag}] {r['decision']:<8} "
                  f"entry={r['entry_price']:.3f} won={str(r['won']):<5} "
                  f"net={r['net_pct']*100:+6.2f}% "
                  f"stake=${r['stake_usd']:>6,.0f} pnl=${r['pnl_usd']:+7,.2f}  "
                  f"{(r['reasoning'] or '')[:40]}")

        print(f"\n  Total bets: {len(bets)}")
        print(f"  Win rate:   {bets['won'].mean()*100:.0f}%")
        print(f"  Total PnL:  ${bets['pnl_usd'].sum():+,.2f}")
        print(f"  vs bankroll: {bets['pnl_usd'].sum()/BANKROLL*100:+.3f}%")

        # Strip out leakage-flagged trades
        clean = bets[~bets.get("possible_leakage", pd.Series(False, index=bets.index)).fillna(False)]
        if len(clean) > 0 and len(clean) < len(bets):
            print(f"\n  If exclude leakage-flagged: n={len(clean)}, "
                  f"win={clean['won'].mean()*100:.0f}%, "
                  f"pnl=${clean['pnl_usd'].sum():+,.2f}")

    # ============== Calibration ==============
    print(f"\n{'='*80}")
    print("CALIBRATION")
    print("="*80)
    fav_won = merged["fav_won"].astype(int).values
    yes_won = merged["yes_won"].astype(int).values
    p_claude = merged["p_claude"].astype(float).values

    brier_as_yes = brier(p_claude, yes_won).mean()
    brier_as_fav = brier(p_claude, fav_won).mean()
    brier_baseline = brier(0.5, yes_won).mean()
    brier_market = brier(merged["p"].values, yes_won).mean()

    # Interpret p_claude per-row (if question's YES outcome was favorite, p_claude prob means
    # p of YES; if NO was favorite, likely they meant p_fav = p_NO)
    # Actually agents gave p_claude consistently on YES per instructions. Use as yes.
    print(f"Brier vs actual yes:  Claude={brier_as_yes:.4f}  Market={brier_market:.4f}  "
          f"Baseline(0.5)={brier_baseline:.4f}")
    print(f"Lower is better. Claude beats market: {brier_as_yes < brier_market}")

    # Claude's directional calls (if p_claude > 0.5 means predicting YES)
    claude_yes_pred = (p_claude >= 0.5).astype(int)
    claude_dir_acc = (claude_yes_pred == yes_won).mean() * 100
    market_yes_pred = (merged["p"] >= 0.5).astype(int)
    market_dir_acc = (market_yes_pred == yes_won).mean() * 100
    print(f"Directional accuracy: Claude={claude_dir_acc:.1f}%  Market={market_dir_acc:.1f}%")

    # ============== Market baseline PnL (always bet favorite) ==============
    print(f"\n{'='*80}")
    print("MARKET BASELINE (bet favorite $200 every time)")
    print("="*80)
    base = merged.copy()
    base["fav_ask"] = np.minimum(base["fav_price"] + 0.01, 0.999)
    base["bet_gross"] = np.where(
        base["fav_won"], (1 / base["fav_ask"]) - 1, -1.0
    )
    base["bet_net"] = base["bet_gross"] - TAKER_FEE
    wins = base["fav_won"].sum()
    total_net = base["bet_net"].sum() * 200  # $200 per bet
    print(f"  fav win rate: {wins}/{len(base)} = {wins/len(base)*100:.0f}%")
    print(f"  mean net / $1: {base['bet_net'].mean()*100:+.2f}%")
    print(f"  total PnL if $200/bet: ${total_net:+,.2f}")

    # ============== By bucket breakdown ==============
    print(f"\n{'='*80}")
    print("BY PRICE BUCKET")
    print("="*80)
    for b, sub in merged.groupby("bucket", observed=True):
        n = len(sub)
        n_bet = (sub["decision"] != "SKIP").sum()
        fav_wr = sub["fav_won"].mean() * 100
        p_c = sub["p_claude"].mean()
        p_m = sub["p"].mean()
        print(f"  {b:<10}  n={n:>3}  BUY={n_bet}  fav_won={fav_wr:.0f}%  "
              f"avg p_claude={p_c:.2f}  avg p_market={p_m:.2f}")

    # ============== By category breakdown ==============
    print(f"\n{'='*80}")
    print("BY CATEGORY")
    print("="*80)
    for cat, sub in merged.groupby("category"):
        n = len(sub)
        n_bet = (sub["decision"] != "SKIP").sum()
        fav_wr = sub["fav_won"].mean() * 100
        p_c = sub["p_claude"].mean()
        p_m = sub["p"].mean()
        b_c = brier(sub["p_claude"], sub["yes_won"].astype(int)).mean()
        b_m = brier(sub["p"], sub["yes_won"].astype(int)).mean()
        print(f"  {cat:<15}  n={n:>3}  BUY={n_bet}  "
              f"fav_won={fav_wr:.0f}%  Brier(C)={b_c:.3f} Brier(M)={b_m:.3f}")

    # ============== Confidence-calibration ==============
    print(f"\n{'='*80}")
    print("CONFIDENCE vs WIN RATE (only BUY decisions)")
    print("="*80)
    if len(bets) > 0:
        for c in sorted(bets["confidence"].unique()):
            sub = bets[bets["confidence"] == c]
            wr = sub["won"].mean() * 100
            pnl = sub["pnl_usd"].sum()
            print(f"  confidence={c}: n={len(sub)}  win%={wr:.0f}  pnl=${pnl:+,.2f}")


if __name__ == "__main__":
    grade()

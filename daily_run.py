"""Daily routine — one command to rule them all.

Runs in order:
1. Settle closed positions (realize PnL)
2. Scan current market for bias pockets
3. Ingest new Tier-S+/S/A+/A/B candidates (with size limits)
4. Status snapshot
5. Auto-tier adjustment suggestions (cycle9_auto_tier)
6. Commit + push if changes

Usage:
  python daily_run.py
  python daily_run.py --dry          # skip git push
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd, capture=False):
    print(f"\n$ {cmd}")
    if capture:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return subprocess.run(cmd, shell=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="skip git commit/push")
    args = ap.parse_args()

    py = sys.executable + " -X utf8"

    print("="*70)
    print("STEP 1: Settle closed positions")
    print("="*70)
    run(f"{py} oracle_portfolio.py --settle")

    print("\n" + "="*70)
    print("STEP 2: Scan current markets")
    print("="*70)
    run(f"{py} cycle6_bias_scanner.py")

    print("\n" + "="*70)
    print("STEP 3: Generate ingest decisions (deduped)")
    print("="*70)
    run(f"{py} ingest_bias_positions.py")

    print("\n" + "="*70)
    print("STEP 4: Open paper positions for new decisions")
    print("="*70)
    run(f"{py} oracle_portfolio.py --ingest")

    print("\n" + "="*70)
    print("STEP 5: Status snapshot")
    print("="*70)
    run(f"{py} oracle_portfolio.py --status")

    print("\n" + "="*70)
    print("STEP 6: Tier performance report")
    print("="*70)
    run(f"{py} cycle9_auto_tier.py")

    if args.dry:
        print("\n[dry mode] skipping git push")
        return

    print("\n" + "="*70)
    print("STEP 7: Commit + push")
    print("="*70)
    run("git add -A data/")
    r = run("git diff --cached --quiet", capture=True)
    if r.returncode == 0:
        print("(no changes to commit)")
    else:
        from datetime import datetime
        stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        run(f'git commit -m "daily_run {stamp}"')
        run("git push origin main")


if __name__ == "__main__":
    main()

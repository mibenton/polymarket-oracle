"""Track C: Live bias scanner — flag open markets in statistically-biased pockets.

Unlike Oracle scanner which relies on Claude judgment, this scanner:
  1. Loads pre-computed bias table (from historical data)
  2. Scans current open markets
  3. Flags those matching (category × price_bucket) with strong historical edge

No Claude subjective step. Pure statistics.
"""
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

GAMMA = "https://gamma-api.polymarket.com/markets"
OUT = Path("data/results/bias_candidates.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

# Use a realistic browser UA to bypass Cloudflare bot challenges on cloud IPs
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# Bias pockets refined through:
# 1) pattern_calibration.py (original rank by EV)
# 2) cycle6_stability.py (must survive all 3 sub-windows with same sign)
# 3) cycle6_esports_deepdive.py (LoL-specific isolation)
#
# Tier A = survived cross-window stability test
# Tier B = strong bias but untested stability (use with caution)
# Tier C = deep-dive confirmed but small sample
BIAS_POCKETS = [
    # (category_key, price_lo, price_hi, best_side, expected_ev_pct, tier, source_n)
    # Cycle 21 stacked-filter strongest: price 0.25-0.36 + vol>=20k + preferred cities
    # → +122% mean PnL, 63% win, t=+5.31 (n=57). Marked as Tier "S+".
    # The S+ filter check is done in match_market via PER_POCKET_RULES.preferred.
    ("weather_exact",   0.25, 0.36, "YES", 90.0, "S+", 57),
    # Tier S wider (keep for good cities that aren't in top-16)
    ("weather_exact",   0.25, 0.36, "YES", 55.0, "S",  221),
    # Tier A+ (wider price band, still positive when vol>=20k)
    ("weather_exact",   0.22, 0.25, "YES", 25.0, "A+", 170),
    ("weather_exact",   0.36, 0.40, "YES", 20.0, "A+", 75),
    # Tier B (low-prob, different city dynamics per C10)
    ("weather_exact",   0.10, 0.15, "YES", 19.0, "B",  347),
    # Cycle 17: crypto "between X-Y" range markets
    ("crypto_range",    0.10, 0.20, "YES", 40.0, "A",   40),
    # === STRATEGIES BELOW ARE NOW EXCLUDED ===
    # Disabled after paper-trade failure 4/22-4/24:
    # Sports (12 bets, 17% win vs expected 55%, -$1710 PnL)
    # ("sports_global", 0.50, 0.60, "YES", 13.4, "A", 115),
    # LoL (untested in paper trade, sample small)
    # ("lol", 0.50, 0.60, "NO", 18.4, "C", 247),
    # Other (inconsistent, tier B)
    # ("other", 0.70, 0.80, "NO", 21.7, "B", 209),
    # Tweet count (sample too small)
    # ("tweet_count", 0.10, 0.25, "NO", 16.0, "B", 22),
]


def categorize(slug):
    s = (slug or "").lower()
    # more specific first
    if "lol-" in s or "-lol-" in s or s.startswith("lol-"):
        return "lol"
    if any(k in s for k in ["nba-", "mlb-", "nhl-", "ncaa", "cbb-", "cfb-"]):
        return "sports_us"
    if any(k in s for k in ["ufc-", "atp-", "wta-", "fif-", "fl1-", "bun-",
                             "ucl-", "uel-", "epl-", "euroleague", "kbo-", "pga"]):
        return "sports_global"
    if any(k in s for k in ["cs2-", "val-", "dota", "rocket-league",
                             "-esports-", "blast-", "iem-"]):
        return "esports"
    if any(k in s for k in ["tweets", "tweet-", "-of-posts-", "-of-tweets-"]):
        return "tweet_count"
    # Cycle 17: crypto "between X-Y" range markets at 0.10-0.20 price → +61% EV (n=40)
    # Strict: must contain "between" (excludes "reach"/"dip to" threshold markets)
    has_crypto = any(k in s for k in ["bitcoin", "btc-", "ethereum", "eth-",
                                       "solana", "sol-"])
    if has_crypto and "between" in s:
        return "crypto_range"
    # Weather: exact-bucket only (not cumulative). Cycle 9 segmentation found:
    # - Tropical climate: edge ~0 → EXCLUDE
    # - East-Asian capitals (Beijing/Taipei/Shanghai/Seoul/Singapore): negative → EXCLUDE
    if ("highest-temperature" in s or "temperature-in-" in s) and \
       not any(k in s for k in ["orhigher", "orabove", "orbelow", "orlower"]):
        # Cycle 9 banned cities (n>=15, mean PnL < -10%)
        banned_cities = ["beijing", "taipei", "shanghai", "seoul", "singapore",
                         "jakarta", "bangkok", "manila", "ho-chi-minh",
                         "kuala-lumpur", "hong-kong", "warsaw", "ankara"]
        if any(f"temperature-in-{c}-" in s for c in banned_cities):
            return "weather_banned"
        return "weather_exact"
    return "other"


def fetch_open_markets(limit_pages: int = 20) -> list[dict]:
    out = []
    for offset in range(0, limit_pages * 500, 500):
        try:
            r = requests.get(GAMMA, params={
                "closed": "false", "active": "true",
                "limit": 500, "offset": offset,
                "volume_num_min": 10000,  # C12 confirmed: vol 5-10k = -62% PnL (disaster)
                "order": "volume", "ascending": "false",
            }, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"  [warn] status {r.status_code} at offset {offset}: {r.text[:100]}")
                break
            data = r.json()
            if not isinstance(data, list) or not data:
                print(f"  [warn] non-list or empty response at offset {offset}: {str(data)[:100]}")
                break
            out.extend(data)
            time.sleep(0.2)
        except Exception as e:
            print(f"  [exc] offset {offset}: {type(e).__name__}: {e}")
            break
    return out


def extract_city(slug: str) -> str:
    m = re.match(r'highest-temperature-in-([a-z-]+?)-on-', (slug or '').lower())
    if not m:
        return ""
    return m.group(1).rstrip("-")


# Cycle 10: per-pocket banlist + Cycle 21 preferred list
PER_POCKET_RULES = {
    # S+ = strictest filter = ONLY cities from C21 +122% mean PnL sample
    "S+": {
        "banned": [],
        "preferred": ["dallas","austin","moscow","madrid","wellington","miami","tel-aviv",
                      "milan","los-angeles","lucknow","san-francisco","denver","wuhan",
                      "toronto","nyc","chongqing"],
        "require_preferred": True,  # S+ ONLY accepts preferred cities
    },
    "S":  {"banned": [], "preferred": ["london"]},
    "A+": {
        "banned": ["atlanta","ankara","london","amsterdam","hong-kong","warsaw","beijing",
                   "taipei","seoul","singapore","shanghai"],
        "preferred": ["dallas","austin","moscow","madrid","wellington","miami","tel-aviv",
                      "milan","los-angeles","lucknow","san-francisco","denver","wuhan",
                      "toronto","nyc","chongqing"],
    },
    "A":  {"banned": [], "preferred": []},
    "B":  {
        "banned": ["miami","shenzhen","madrid","seoul","moscow","buenos-aires","atlanta",
                   "london"],
        "preferred": ["beijing","taipei","dallas","milan","wellington","nyc","chicago",
                      "shanghai","paris"],
    },
}


def match_market(m: dict) -> list[dict]:
    import re as _re
    try:
        outcomes = json.loads(m.get("outcomes") or "[]")
        tokens = json.loads(m.get("clobTokenIds") or "[]")
    except Exception:
        return []
    if len(outcomes) != 2 or len(tokens) != 2:
        return []

    try:
        ask = float(m.get("bestAsk") or 0)
        bid = float(m.get("bestBid") or 0)
    except Exception:
        return []
    if ask <= 0 or bid <= 0:
        return []
    mid = (ask + bid) / 2

    cat = categorize(m.get("slug"))
    slug = m.get("slug") or ""
    city = extract_city(slug)

    results = []
    for pocket in BIAS_POCKETS:
        pc_cat, lo, hi, best_side, ev_pct, tier, src_n = pocket
        if cat != pc_cat:
            continue
        if not (lo <= mid < hi):
            continue

        # Per-pocket banlist (Cycle 10) + S+ preferred-only (Cycle 21)
        rules = PER_POCKET_RULES.get(tier, {})
        if city and city in rules.get("banned", []):
            continue
        is_preferred = bool(city and city in rules.get("preferred", []))
        # S+ tier requires city in preferred list
        if rules.get("require_preferred") and not is_preferred:
            continue
        # S+ tier also requires volume >=20k
        if tier == "S+" and float(m.get("volumeNum") or 0) < 20_000:
            continue

        # You want to bet best_side. Entry is ask of that side
        if best_side == "YES":
            entry = ask
        else:
            entry = 1 - bid  # NO ask ≈ 1 - YES bid
        results.append({
            "city": city,
            "preferred_city": is_preferred,
            "category": cat,
            "pocket": f"{lo:.2f}-{hi:.2f}",
            "best_side": best_side,
            "entry_price": round(entry, 4),
            "expected_ev_pct": ev_pct,
            "tier": tier,
            "historical_n": src_n,
            "slug": m.get("slug"),
            "question": (m.get("question") or "")[:90],
            "mid": round(mid, 4),
            "spread": round(ask-bid, 4),
            "volume": round(float(m.get("volumeNum") or 0)),
            "end_date": m.get("endDate"),
        })
    return results


def main():
    print("Cycle 6 Bias Scanner — statistical pockets only, no Claude judgment")
    print()
    for pc in BIAS_POCKETS:
        cat, lo, hi, side, ev, tier, src_n = pc
        print(f"  [{tier}] {cat:<18} {lo:.2f}-{hi:.2f}  side={side}  "
              f"expected EV={ev:+.1f}%  (historical n={src_n})")
    print()

    raw = fetch_open_markets()
    print(f"Fetched {len(raw)} open markets")

    hits = []
    for m in raw:
        hits.extend(match_market(m))

    if not hits:
        print("No current matches.")
        return

    df = pd.DataFrame(hits).sort_values("expected_ev_pct", ascending=False)
    print(f"\nFound {len(df)} current candidates:\n")
    for _, r in df.iterrows():
        ed = (r["end_date"] or "")[:10]
        print(f"  [{r['tier']}] [{r['category']:<14}] {r['pocket']}  side={r['best_side']:<3}  "
              f"entry={r['entry_price']:.3f}  vol=${r['volume']:>7,}  {ed}  "
              f"{r['question'][:60]}")

    df.to_csv(OUT, index=False)
    print(f"\nSaved to {OUT}")


if __name__ == "__main__":
    main()

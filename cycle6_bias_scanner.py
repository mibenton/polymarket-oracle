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
    # Cycle 29: B+ strict (preferred cities + vol>=20k) = +175% mean PnL (n=63)
    ("weather_exact",   0.10, 0.15, "YES", 130.0, "B+", 63),
    # Tier B (low-prob, different city dynamics per C10)
    ("weather_exact",   0.10, 0.15, "YES", 19.0, "B",  347),
    # Cycle 82 refined: weather tail 0.02-0.05 + vol>=20k + morning close
    # = +238% mean PnL, 13% win (n=103). Upgraded from C to A tier due to massive EV.
    # Note: 87% loss rate but 20-30x payouts when winning. Keep stake small (high variance).
    ("weather_exact",   0.02, 0.05, "YES", 150.0, "A",  103),
    # Cycle 80: weather_exact 0.30-0.35 narrow band = +46% (n=70, 47% win)
    ("weather_exact",   0.30, 0.35, "YES", 46.0, "A+", 70),
    # Cycle 42 refined: crypto "between X-Y" 0.10-0.15 is real sweet spot (n=26, +81%)
    ("crypto_range",    0.10, 0.15, "YES", 80.0, "A",   26),
    # Cycle 34/42: Box office 0.02-0.10 high-variance tail (big payoffs)
    # Keep but lower stake (C limit); also tighten 0-0.02 is excluded (all lose)
    ("box_office",      0.03, 0.10, "YES", 100.0, "C",  22),
    # Cycle 76: Soccer O/U totals 0.50-0.60 YES → +30% mean, 70% win (n=44)
    # +46% with vol>100k (n=10)
    ("soccer_total",    0.50, 0.60, "YES", 30.0, "A",  44),
    # Cycle 88/91/101: Sports match 0.60-0.80 YES → BUY NO has +12% edge (n=187)
    # Cycle 101: 0.65-0.70 + vol>=100k = +49% (n=20) — volume upgrades
    # Split into sub-pockets:
    ("sports_global",   0.65, 0.80, "NO",  22.0, "A",  85),   # tighter narrow + higher price
    ("sports_global",   0.60, 0.65, "NO",  10.0, "B", 67),    # wider low-band
    # Cycle 93: Non-weather non-crypto 0.60-0.70 → NO has +12.6% edge (n=431 broad)
    # Universal "heavy favorite" over-pricing
    ("sports_us",       0.60, 0.80, "NO",  12.0, "B", 100),
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
    # Cycle 88: sports match at 0.6-0.8 YES → BUY NO has edge (+12% PnL, 36% win)
    # Different from 0.5-0.6 which we killed as YES-side in Cycle 7.
    if any(k in s for k in ["ufc-", "atp-", "wta-", "fif-", "fl1-", "bun-",
                             "ucl-", "uel-", "epl-", "euroleague", "kbo-", "pga"]):
        return "sports_global"
    if any(k in s for k in ["cs2-", "val-", "dota", "rocket-league",
                             "-esports-", "blast-", "iem-"]):
        return "esports"
    if any(k in s for k in ["tweets", "tweet-", "-of-posts-", "-of-tweets-"]):
        return "tweet_count"
    # Cycle 17: crypto "between X-Y" range markets at 0.10-0.20 price → +61% EV (n=40)
    has_crypto = any(k in s for k in ["bitcoin", "btc-", "ethereum", "eth-",
                                       "solana", "sol-"])
    if has_crypto and "between" in s:
        return "crypto_range"
    # Cycle 34: box office opening/ 2nd/3rd weekend markets → low price bucket +224% (n=22)
    if "box-office" in s or "opening-weekend" in s:
        return "box_office"
    # Cycle 76: Soccer totals 0.50-0.60 YES = +30%, 70% win
    if any(k in s for k in ["fif-","epl-","ucl-","uel-","bun-","fl1-","es2-","aus-",
                             "bra-","efa-","lal-","sai-"]) and \
       any(k in s for k in ["-total-", "total-"]):
        return "soccer_total"
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


# Cycle 32 finding: local close hour matters heavily
# 0-6h local = +117.6% PnL, 12-18h = -77.3%, 18-24h = -34.5%
# Offsets for common cities (hours from UTC)
CITY_TZ_OFFSET = {
    'nyc': -4, 'miami': -4, 'atlanta': -4, 'chicago': -5, 'dallas': -5,
    'austin': -5, 'denver': -6, 'los-angeles': -7, 'san-francisco': -7,
    'seattle': -7, 'houston': -5, 'phoenix': -7, 'vancouver': -7,
    'montreal': -4, 'toronto': -4,
    'london': 1, 'paris': 2, 'madrid': 2, 'rome': 2, 'milan': 2,
    'berlin': 2, 'munich': 2, 'amsterdam': 2, 'warsaw': 2, 'vienna': 2,
    'moscow': 3, 'istanbul': 3, 'tel-aviv': 3, 'ankara': 3, 'athens': 3,
    'helsinki': 3, 'oslo': 2, 'stockholm': 2,
    'dubai': 4, 'riyadh': 3, 'cairo': 3,
    'delhi': 5, 'mumbai': 5, 'lucknow': 5,
    'beijing': 8, 'shanghai': 8, 'hong-kong': 8, 'chengdu': 8,
    'chongqing': 8, 'wuhan': 8, 'shenzhen': 8, 'taipei': 8,
    'seoul': 9, 'tokyo': 9,
    'singapore': 8, 'jakarta': 7, 'bangkok': 7, 'kuala-lumpur': 8,
    'manila': 8, 'ho-chi-minh': 7,
    'sydney': 10, 'melbourne': 10, 'wellington': 12, 'auckland': 12,
    'sao-paulo': -3, 'buenos-aires': -3, 'lima': -5, 'mexico-city': -6,
}


def local_close_hour(end_date_iso: str, city: str) -> int:
    """Return local-time hour (0-23) of close for city."""
    if not end_date_iso:
        return -1
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(end_date_iso.replace("Z", "+00:00"))
        offset = CITY_TZ_OFFSET.get(city, 0)
        return (dt.hour + offset) % 24
    except Exception:
        return -1


def is_good_close_hour(hour: int) -> bool:
    """Cycle 32: 0-6h local close = +117% PnL, 6-12h OK, 12-24h NEGATIVE."""
    if hour < 0:
        return True  # unknown, don't filter
    return 0 <= hour < 12  # before local noon only


# Cycles 10, 21, 40: per-pocket banlist + preferred cities
# Cycle 40: cities with 100% positive-week consistency get extra weight
ULTRA_PREFERRED = ["san-francisco","paris","madrid","lucknow","tel-aviv","sao-paulo"]
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
    # B+ same preferred as B but require_preferred and vol>=20k
    "B+": {
        "banned": [],
        "preferred": ["beijing","taipei","dallas","milan","wellington","nyc","chicago",
                      "shanghai","paris"],
        "require_preferred": True,
    },
}


def event_key_for_scan(slug: str) -> str:
    """Strip trailing temp/range to group buckets of same event (city-date)."""
    s = re.sub(r'-[0-9]+(pt[0-9]+)?(c|f)?(orhigher|orabove|orbelow|orlower)?$',
               '', (slug or '').lower())
    s = re.sub(r'-[0-9]+(-[0-9]+)?(f|c)?$', '', s)
    return s


def match_market(m: dict, event_vol_max: dict | None = None) -> list[dict]:
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
        # S+ and B+ also require volume >=20k
        # Cycle 82: weather_exact 0.02-0.05 tail pocket also requires vol>=20k
        if tier in ("S+", "B+") and float(m.get("volumeNum") or 0) < 20_000:
            continue
        if pc_cat == "weather_exact" and lo == 0.02 and hi == 0.05:
            if float(m.get("volumeNum") or 0) < 20_000:
                continue
        # Cycle 32: reject markets closing in city local afternoon/evening (12-24h)
        # Applies to ALL weather tiers (universal edge uplift)
        local_h = local_close_hour(m.get("endDate"), city) if city else -1
        if pc_cat == "weather_exact" and not is_good_close_hour(local_h):
            continue

        # Cycle 41: volume ratio within event (S+/B+ boost if vol >= 60% of event max)
        vol_ratio = 1.0
        if event_vol_max is not None and pc_cat == "weather_exact":
            evt = event_key_for_scan(m.get("slug") or "")
            max_v = event_vol_max.get(evt, 0)
            my_v = float(m.get("volumeNum") or 0)
            if max_v > 0:
                vol_ratio = my_v / max_v
        # S++ / B++ pseudo-tiers: same as S+/B+ but vol_ratio >= 0.6
        tier_label = tier
        if tier == "S+" and vol_ratio >= 0.6:
            tier_label = "S++"
        elif tier == "B+" and vol_ratio >= 0.6:
            tier_label = "B++"

        # You want to bet best_side. Entry is ask of that side
        if best_side == "YES":
            entry = ask
        else:
            entry = 1 - bid  # NO ask ≈ 1 - YES bid
        # ev uplift if tier upgraded to ++
        ev_final = ev_pct * 1.5 if tier_label.endswith("++") else ev_pct
        results.append({
            "city": city,
            "preferred_city": is_preferred,
            "category": cat,
            "pocket": f"{lo:.2f}-{hi:.2f}",
            "best_side": best_side,
            "entry_price": round(entry, 4),
            "expected_ev_pct": ev_final,
            "tier": tier_label,
            "vol_ratio": round(vol_ratio, 2),
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

    # Cycle 41: compute event_vol_max for vol_ratio filter
    event_vol_max = {}
    for m in raw:
        slug = m.get("slug") or ""
        if "temperature-in-" in slug.lower():
            evt = event_key_for_scan(slug)
            v = float(m.get("volumeNum") or 0)
            if v > event_vol_max.get(evt, 0):
                event_vol_max[evt] = v

    hits = []
    for m in raw:
        hits.extend(match_market(m, event_vol_max))

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

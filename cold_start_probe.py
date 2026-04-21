"""Probe newly-listed Polymarket markets for Unity constraint violations (YES+NO != 1).

If YES_ask + NO_ask < 1:  arb — buy both → guaranteed +1 per pair - fees
If YES_bid + NO_bid > 1:  arb — sell both → guaranteed +fees

Reference: arXiv 2508.03474 shows 41% of markets had such anomalies historically,
but bots catch them in <3s. Checking if small windows still exist for manual exec.
"""
import json
import time
from datetime import datetime, timezone

import pandas as pd
import requests

GAMMA = "https://gamma-api.polymarket.com/markets"
CLOB_BOOK = "https://clob.polymarket.com/book"
TAKER_FEE_BY_CAT = {"crypto": 0.018, "sports": 0.0075, "politics": 0.01,
                    "economics": 0.015, "tech": 0.01, "geopolitics": 0.0}
DEFAULT_FEE = 0.015


def fetch_recent_markets(hours_age_max: int = 48, limit: int = 500) -> list[dict]:
    """Get recently-created active markets."""
    out = []
    for offset in range(0, 3000, 500):
        r = requests.get(GAMMA, params={
            "closed": "false", "active": "true",
            "limit": 500, "offset": offset,
            "order": "createdAt", "ascending": "false",
        }, timeout=30)
        data = r.json()
        if not isinstance(data, list) or not data:
            break
        for m in data:
            created = m.get("createdAt") or ""
            try:
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                age_h = (datetime.now(timezone.utc) - created_dt).total_seconds() / 3600
            except Exception:
                continue
            if age_h > hours_age_max:
                break
            out.append(m)
        if len(out) >= limit:
            break
        time.sleep(0.2)
    return out[:limit]


def fetch_book(token_id: str) -> dict | None:
    try:
        r = requests.get(CLOB_BOOK, params={"token_id": token_id}, timeout=15)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def best_levels(book: dict | None) -> tuple[float, float, float, float]:
    """Return (best_bid, bid_size, best_ask, ask_size)."""
    if not book:
        return 0, 0, 0, 0
    bids = book.get("bids", []) or []
    asks = book.get("asks", []) or []
    # Polymarket CLOB returns bids sorted asc, asks sorted desc (check)
    # best bid = highest price, best ask = lowest price
    def bpick(lst, fn):
        if not lst:
            return 0, 0
        best = fn(lst, key=lambda x: float(x.get("price", 0)))
        return float(best.get("price", 0)), float(best.get("size", 0))
    bb, bb_sz = bpick(bids, max)
    ba, ba_sz = bpick(asks, min)
    return bb, bb_sz, ba, ba_sz


def probe_market(m: dict, fee: float) -> dict | None:
    try:
        tokens = json.loads(m.get("clobTokenIds") or "[]")
        outcomes = json.loads(m.get("outcomes") or "[]")
    except Exception:
        return None
    if len(tokens) != 2:
        return None

    yes_book = fetch_book(tokens[0])
    no_book = fetch_book(tokens[1])
    y_bid, y_bid_sz, y_ask, y_ask_sz = best_levels(yes_book)
    n_bid, n_bid_sz, n_ask, n_ask_sz = best_levels(no_book)

    # Arb 1: buy YES ask + NO ask < 1 → pair pays $1 regardless
    ask_sum = y_ask + n_ask if (y_ask > 0 and n_ask > 0) else None
    buy_arb_gross = (1 - ask_sum) if ask_sum else None
    buy_arb_net = (buy_arb_gross - 2 * fee * (y_ask + n_ask) / 2) if buy_arb_gross else None

    # Arb 2: sell YES bid + NO bid > 1
    bid_sum = y_bid + n_bid if (y_bid > 0 and n_bid > 0) else None
    sell_arb_gross = (bid_sum - 1) if bid_sum else None

    max_pair_size = min(y_ask_sz, n_ask_sz) if (y_ask_sz and n_ask_sz) else 0

    created = m.get("createdAt", "")
    end = m.get("endDate", "")
    try:
        age_h = (datetime.now(timezone.utc) -
                 datetime.fromisoformat(created.replace("Z", "+00:00"))
                ).total_seconds() / 3600
    except Exception:
        age_h = None

    return {
        "slug": m.get("slug"),
        "question": (m.get("question") or "")[:80],
        "age_h": round(age_h, 2) if age_h else None,
        "volume": float(m.get("volumeNum") or 0),
        "y_bid": y_bid, "y_ask": y_ask,
        "n_bid": n_bid, "n_ask": n_ask,
        "ask_sum": round(ask_sum, 4) if ask_sum else None,
        "bid_sum": round(bid_sum, 4) if bid_sum else None,
        "buy_arb_gross": round(buy_arb_gross, 4) if buy_arb_gross else None,
        "buy_arb_net": round(buy_arb_net, 4) if buy_arb_net else None,
        "sell_arb_gross": round(sell_arb_gross, 4) if sell_arb_gross else None,
        "max_pair_size": max_pair_size,
        "end_date": end,
    }


def main():
    print("Fetching recent markets (created last 48h)...")
    markets = fetch_recent_markets(hours_age_max=48, limit=200)
    print(f"got {len(markets)} markets")

    results = []
    for i, m in enumerate(markets):
        fee = DEFAULT_FEE  # conservative
        r = probe_market(m, fee)
        if r:
            results.append(r)
        if (i + 1) % 20 == 0:
            print(f"  probed {i+1}/{len(markets)}")
        time.sleep(0.15)

    df = pd.DataFrame(results)
    if df.empty:
        print("no probe results")
        return

    print(f"\nTotal probed: {len(df)}")
    print(f"Has both-side orderbook: {df['ask_sum'].notna().sum()}")

    # Find violations
    buy_arbs = df[df["buy_arb_gross"].fillna(0) > 0.005].sort_values(
        "buy_arb_gross", ascending=False)
    sell_arbs = df[df["sell_arb_gross"].fillna(0) > 0.005].sort_values(
        "sell_arb_gross", ascending=False)
    buy_profitable = df[df["buy_arb_net"].fillna(-1) > 0].sort_values(
        "buy_arb_net", ascending=False)

    print(f"\nBuy-arb (ask_sum < 1, gross > 0.5%): {len(buy_arbs)}")
    print(f"Sell-arb (bid_sum > 1, gross > 0.5%): {len(sell_arbs)}")
    print(f"Buy-arb NET profitable (after fees): {len(buy_profitable)}")

    if len(buy_arbs):
        print("\n--- Top 10 buy-arb candidates ---")
        cols = ["slug", "age_h", "volume", "y_ask", "n_ask", "ask_sum",
                "buy_arb_gross", "buy_arb_net", "max_pair_size"]
        print(buy_arbs[cols].head(10).to_string(index=False))

    if len(sell_arbs):
        print("\n--- Top 10 sell-arb candidates ---")
        cols = ["slug", "age_h", "volume", "y_bid", "n_bid", "bid_sum",
                "sell_arb_gross", "max_pair_size"]
        print(sell_arbs[cols].head(10).to_string(index=False))

    # Sum distribution
    print(f"\nAsk-sum distribution (ideally near 1.00):")
    print(df["ask_sum"].describe())
    print(f"\nBid-sum distribution:")
    print(df["bid_sum"].describe())

    df.to_csv("data/results/cold_start_probe.csv", index=False)
    print(f"\nSaved to data/results/cold_start_probe.csv")


if __name__ == "__main__":
    main()

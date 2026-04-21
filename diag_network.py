"""Diagnose network access to Polymarket APIs from current host."""
import json
import sys
import requests

print(f"Python: {sys.version.split()[0]}")
print(f"requests: {requests.__version__}")

# Test 1: Plain gamma-api
print("\n--- Test 1: gamma-api markets?limit=1 ---")
try:
    r = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={"limit": 1}, timeout=15,
    )
    print(f"status: {r.status_code}")
    print(f"headers (partial): {dict((k, v) for k, v in list(r.headers.items())[:5])}")
    print(f"body[:200]: {r.text[:200]}")
except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")

# Test 2: gamma-api with User-Agent
print("\n--- Test 2: gamma-api + explicit User-Agent ---")
try:
    r = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={"limit": 1}, timeout=15,
        headers={"User-Agent": "Mozilla/5.0 (polymarket-oracle-bot)"},
    )
    print(f"status: {r.status_code}")
    print(f"body[:200]: {r.text[:200]}")
except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")

# Test 3: CLOB prices-history
print("\n--- Test 3: CLOB markets?limit=1 ---")
try:
    r = requests.get("https://clob.polymarket.com/markets", params={"limit": 1}, timeout=15)
    print(f"status: {r.status_code}")
    print(f"body[:200]: {r.text[:200]}")
except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")

# Test 4: A generic cloudflare site (to isolate Polymarket-specific blocking)
print("\n--- Test 4: httpbin.org (control) ---")
try:
    r = requests.get("https://httpbin.org/ip", timeout=15)
    print(f"status: {r.status_code}")
    print(f"body: {r.text[:200]}")
except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")

# Test 5: IP we're running from
print("\n--- Test 5: detect outgoing IP ---")
try:
    r = requests.get("https://api.ipify.org?format=json", timeout=15)
    print(f"IP: {r.text}")
except Exception as e:
    print(f"EXCEPTION: {type(e).__name__}: {e}")

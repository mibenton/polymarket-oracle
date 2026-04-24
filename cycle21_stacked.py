"""Cycle 21: Stack all filters and measure cumulative edge improvement.

Start from raw weather exact-bucket, progressively apply filters:
1. Base: weather exact, any price any city
2. + Price 0.20-0.40
3. + Price 0.25-0.36
4. + Vol >= 10k
5. + Vol >= 20k
6. + Ban losing cities (per-pocket from C10)
7. + Prefer top-10 cities
"""
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '.')
from cycle9_weather_segment import load

TAKER_FEE = 0.01


def stats_label(df, label):
    df = df.copy()
    df["pnl"] = np.where(df["yes_won"], 1/df["p"]-1-TAKER_FEE, -1-TAKER_FEE)
    n = len(df)
    if n < 5:
        return dict(label=label, n=n, mean=0, t=0)
    m = df["pnl"].mean()
    s = df["pnl"].std(ddof=1)
    t = m / (s/np.sqrt(n)) if s > 0 else 0
    return dict(label=label, n=n, mean_pct=round(m*100, 1),
                sum_pnl=round(df["pnl"].sum(),1),
                win_pct=round((df["pnl"]>0).mean()*100,0),
                t=round(t,2))


BANNED_A_PLUS = ["atlanta","ankara","london","amsterdam","hong-kong","warsaw","beijing",
                  "taipei","seoul","singapore","shanghai","miami","tropical"]
TOP_CITIES_A_PLUS = ["dallas","austin","moscow","madrid","wellington","miami","tel-aviv",
                      "milan","los-angeles","lucknow","san-francisco","denver","wuhan",
                      "toronto","nyc","chongqing"]


def main():
    df = load()
    results = []

    # Base
    results.append(stats_label(df, "1. All weather exact"))
    results.append(stats_label(df[(df["p"]>=0.20) & (df["p"]<=0.40)], "2. + price 0.20-0.40"))
    results.append(stats_label(df[(df["p"]>=0.25) & (df["p"]<=0.36)], "3. + price 0.25-0.36"))

    sub = df[(df["p"]>=0.25) & (df["p"]<=0.36)]
    results.append(stats_label(sub[sub["volume"]>=10_000], "4. + vol >= 10k"))
    results.append(stats_label(sub[sub["volume"]>=20_000], "5. + vol >= 20k"))
    results.append(stats_label(sub[sub["volume"]>=50_000], "6. + vol >= 50k"))

    sub2 = sub[sub["volume"]>=20_000]
    results.append(stats_label(
        sub2[~sub2["city"].isin(BANNED_A_PLUS)], "7. + ban losers (C10)"
    ))
    results.append(stats_label(
        sub2[sub2["city"].isin(TOP_CITIES_A_PLUS)], "8. + ONLY preferred cities"
    ))

    # Add deviation filter from C16: 3-5C off city median
    sub3 = sub2[~sub2["city"].isin(BANNED_A_PLUS)]
    city_median = sub3.groupby("city")["p"].median()  # proxy
    # Actually we need temp. Skip here for simplicity.

    # DoW filter from C15: Tue/Sun/Fri/Thu
    sub3["dow"] = sub3["closed_time"].dt.day_name()
    good_dow = ["Tuesday","Sunday","Friday","Thursday","Wednesday"]
    results.append(stats_label(
        sub3[sub3["dow"].isin(good_dow)], "9. + good DoW (Tue/Sun/Fri/Thu/Wed)"
    ))

    # Event size from C13: 1-3 or 6-8 or 13-20
    import re
    def event_key(slug):
        s = re.sub(r'-[0-9]+(pt[0-9]+)?(c|f)?(orhigher|orabove|orbelow|orlower)?$',
                   '', (slug or '').lower())
        s = re.sub(r'-[0-9]+(-[0-9]+)?(f|c)?$', '', s)
        return s
    df["event"] = df["slug"].apply(event_key)
    event_size = df.groupby("event")["slug"].nunique()
    sub4 = sub3.copy()
    sub4["event"] = sub4["slug"].apply(event_key)
    sub4["event_size"] = sub4["event"].map(event_size)
    results.append(stats_label(
        sub4[sub4["event_size"].between(6,20)], "10. + event size 6-20"
    ))

    # Print table
    print(f"\n{'='*85}")
    print("STACKED FILTER PROGRESSION")
    print(f"{'='*85}")
    print(f"{'filter':<50} {'n':>5} {'mean%':>7} {'sum':>8} {'win%':>5} {'t':>6}")
    print("-" * 85)
    for r in results:
        print(f"{r['label']:<50} {r['n']:>5} {r.get('mean_pct',0):>+6.1f} "
              f"{r.get('sum_pnl',0):>+8.1f} {r.get('win_pct',0):>4.0f} {r.get('t',0):>+6.2f}")


if __name__ == "__main__":
    main()

"""Cycle 16: Is target temperature within city's seasonal norm?

Hypothesis: If asked "Will Miami be 70°F on April 24?" and Miami's April normal
is 82°F, this target is an OUTLIER. Outlier-target markets should behave
differently from on-normal markets.
"""
import re
import numpy as np
import pandas as pd
import sys
sys.path.insert(0, '.')
from cycle9_weather_segment import load

TAKER_FEE = 0.01


def extract_temp(slug: str) -> tuple[float, str]:
    """Return (temperature_value, unit)."""
    if not isinstance(slug, str):
        return (None, None)
    # match patterns like -18c / -65-66f / -78corhigher
    m = re.search(r'-([0-9]+)(pt([0-9]+))?(c|f)(?:orhigher|orabove|orbelow|orlower)?$',
                  slug.lower())
    if m:
        whole = float(m.group(1))
        frac = float(m.group(3))/10 if m.group(3) else 0
        return (whole + frac, m.group(4))
    # range patterns: -65-66f
    m2 = re.search(r'-([0-9]+)-([0-9]+)(c|f)$', slug.lower())
    if m2:
        avg = (float(m2.group(1)) + float(m2.group(2))) / 2
        return (avg, m2.group(3))
    return (None, None)


def main():
    df = load()
    df["target_temp"], df["unit"] = zip(*df["slug"].apply(extract_temp))
    df = df[df["target_temp"].notna()].copy()

    # Convert all to Celsius
    df["target_c"] = np.where(df["unit"] == "f",
                               (df["target_temp"] - 32) * 5/9,
                               df["target_temp"])

    # Compute per-city median target (proxy for seasonal norm in dataset)
    city_norm = df.groupby("city")["target_c"].median().rename("city_median_c")
    df = df.merge(city_norm, on="city")
    df["deviation_c"] = df["target_c"] - df["city_median_c"]
    df["abs_dev"] = df["deviation_c"].abs()

    sub = df[(df["p"] >= 0.25) & (df["p"] <= 0.36)].copy()
    sub["pnl"] = np.where(sub["yes_won"], 1/sub["p"]-1-TAKER_FEE, -1-TAKER_FEE)

    print(f"\n=== Weather 0.25-0.36 by target deviation from city median ===")
    bins = [0, 1, 2, 3, 5, 100]
    labels = ["0-1°C","1-2°C","2-3°C","3-5°C",">5°C"]
    sub["dev_bucket"] = pd.cut(sub["abs_dev"], bins=bins, labels=labels, include_lowest=True)
    g = sub.groupby("dev_bucket", observed=True).agg(
        n=("pnl","size"),
        win=("yes_won","mean"),
        mean_pnl=("pnl","mean"),
    )
    g["win_pct"] = (g["win"]*100).round(0)
    g["mean_pnl_pct"] = (g["mean_pnl"]*100).round(1)
    g = g.drop(columns=["win","mean_pnl"])
    print(g.to_string())

    # Direction of deviation
    print(f"\n=== Direction of deviation ===")
    sub["dev_sign"] = np.sign(sub["deviation_c"])
    sub["dir"] = sub["dev_sign"].map({-1:"below-norm", 0:"at-norm", 1:"above-norm"})
    g = sub.groupby("dir").agg(n=("pnl","size"), mean_pnl=("pnl","mean"), win=("yes_won","mean"))
    g["win_pct"] = (g["win"]*100).round(0)
    g["mean_pnl_pct"] = (g["mean_pnl"]*100).round(1)
    g = g.drop(columns=["win","mean_pnl"])
    print(g.to_string())


if __name__ == "__main__":
    main()

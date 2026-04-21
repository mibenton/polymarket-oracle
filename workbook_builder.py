"""Build a workbook (questions without answers) + hidden answer key.

思路：從歷史已結算市場抽 N 題。每題展示「T-72h 的市場快照」但隱藏結果。
Claude 在不能 WebSearch 的條件下分析，完成後用 answer_key 對答案。

這是 Cycle 5 Oracle 框架的真正回測方式（用戶的「作業本」類比）。
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

WORKBOOK = Path("data/workbook/questions.md")
ANSWER_KEY = Path("data/workbook/answer_key.parquet")
WORKBOOK.parent.mkdir(parents=True, exist_ok=True)

N_QUESTIONS = 100
BATCH_SIZE = 20  # questions per agent
SEED = 2026
MIN_VOLUME = 10_000
MIN_DURATION_H = 72


def load():
    ext = pd.read_parquet("data/markets_ext.parquet")
    orig = pd.read_parquet("data/markets.parquet")
    markets = pd.concat([ext, orig], ignore_index=True).drop_duplicates("id")
    markets["closed_time"] = pd.to_datetime(markets["closed_time"], utc=True, errors="coerce")
    markets["start_date"] = pd.to_datetime(markets["start_date"], utc=True, errors="coerce")
    markets["duration_h"] = (markets["closed_time"] - markets["start_date"]).dt.total_seconds() / 3600
    frames = []
    for p in ["data/prices.parquet", "data/prices_ext.parquet"]:
        if Path(p).exists():
            frames.append(pd.read_parquet(p))
    prices = pd.concat(frames).drop_duplicates(["market_id", "t"])
    return markets, prices


def build_entries(markets, prices):
    markets = markets[markets["id"].isin(prices["market_id"].unique())]
    m = markets[["id", "question", "slug", "closed_time", "start_date", "yes_won",
                 "yes_outcome", "no_outcome", "volume", "duration_h"]].rename(
        columns={"id": "market_id"})
    m = m[(m["volume"] >= MIN_VOLUME) & (m["duration_h"] >= MIN_DURATION_H)]
    m["target_ts"] = (m["closed_time"] - pd.Timedelta(hours=72)).astype("int64") // 10**9

    merged = pd.merge_asof(
        m.sort_values("target_ts"),
        prices.sort_values("t"),
        left_on="target_ts", right_on="t", by="market_id",
        direction="backward", tolerance=int(6 * 3600),
    ).dropna(subset=["p"])
    return merged


def remove_bucket_spam(df):
    """Remove markets where slug shares prefix with many others (bucket-spam)."""
    df = df.copy()
    df["event_prefix"] = df["slug"].str.split("-").str[:5].str.join("-")
    counts = df["event_prefix"].value_counts()
    keep_prefix = counts[counts < 3].index
    return df[df["event_prefix"].isin(keep_prefix)]


def sample_workbook(df, n=N_QUESTIONS, seed=SEED):
    """Stratified sample: mix of prob ranges + categories."""
    # add price buckets
    df = df.copy()
    df["fav_price"] = np.where(df["p"] >= 0.5, df["p"], 1 - df["p"])
    df["bucket"] = pd.cut(df["fav_price"], bins=[0.5, 0.65, 0.80, 0.92, 1.0],
                          labels=["close", "moderate", "strong", "tail"])

    # take roughly equal from each bucket
    rng = np.random.default_rng(seed)
    per_bucket = max(1, n // 4)
    samples = []
    for b in df["bucket"].unique():
        sub = df[df["bucket"] == b]
        if len(sub) == 0:
            continue
        take = min(per_bucket + 2, len(sub))
        idx = rng.choice(len(sub), size=take, replace=False)
        samples.append(sub.iloc[idx])
    out = pd.concat(samples).sample(n=min(n, len(pd.concat(samples))),
                                     random_state=seed).reset_index(drop=True)
    return out


def write_workbook(sample, batch_no=None, out_path=None):
    """Write questions file (no answers). If batch_no given, write a batch file."""
    title = "Oracle Backtest Workbook"
    if batch_no is not None:
        title += f" — Batch {batch_no}"
    lines = [f"# {title}",
             "",
             f"**Task**: 分析以下 {len(sample)} 題。每題只給你 T-72h 前的市場快照和題目，"
             "不告訴你結果。你的任務是給出 Decision JSON。",
             "",
             "**規則**：",
             "- 禁止使用 WebSearch 或 WebFetch 查結果",
             "- 只能用你的訓練知識 + 題目提供的資訊",
             "- 誠實估 p_claude。如果你完全不知道，寫 confidence=1 然後 SKIP",
             "- SKIP 率高沒關係，這正是框架目標",
             "",
             "**Decision JSON 格式**（每題一個）：",
             "```json",
             "{",
             '  "q_id": 整數,',
             '  "slug": "...",',
             '  "decision": "BUY YES" | "BUY NO" | "SKIP",',
             '  "p_claude": 0.00,',
             '  "entry_price": 0.00,',
             '  "edge_bps": 整數,',
             '  "confidence": 1-5,',
             '  "reasoning": "簡短"',
             "}",
             "```",
             ""]

    for _, row in sample.iterrows():
        i = row["q_id"] - 1
        # Reconstruct T-72h snapshot
        fav_outcome = row["yes_outcome"] if row["p"] >= 0.5 else row["no_outcome"]
        fav_price = row["fav_price"]
        other_price = 1 - fav_price
        other_outcome = row["no_outcome"] if row["p"] >= 0.5 else row["yes_outcome"]

        # assume typical 0.02 spread
        ask = min(fav_price + 0.01, 0.999)
        bid = max(fav_price - 0.01, 0.001)

        lines += [
            f"## Q{i+1}",
            f"",
            f"- **slug**: `{row['slug']}`",
            f"- **question**: {row['question']}",
            f"- **outcomes**: {row['yes_outcome']} / {row['no_outcome']}",
            f"- **favorite at T-72h**: {fav_outcome} @ mid {fav_price:.3f} (ask {ask:.3f}, bid {bid:.3f})",
            f"- **other side**: {other_outcome} @ mid {other_price:.3f}",
            f"- **volume at close**: ${row['volume']:,.0f}",
            f"- **duration**: {row['duration_h']:.0f}h",
            f"- **close date**: {row['closed_time'].date()}",
            "",
            "→ 你的 Decision JSON:",
            "```json",
            "{",
            f'  "q_id": {i+1},',
            f'  "slug": "{row["slug"]}",',
            '  ...',
            "}",
            "```",
            "",
        ]

    target = out_path or WORKBOOK
    target.write_text("\n".join(lines), encoding="utf-8")


def write_answer_key(sample):
    """Save hidden answer key. q_id → actual outcome."""
    key = sample[["slug", "question", "yes_won", "p", "fav_won",
                  "yes_outcome", "no_outcome", "volume",
                  "fav_price", "bucket"]].copy()
    key["q_id"] = range(1, len(key) + 1)
    key.to_parquet(ANSWER_KEY, index=False)


def main():
    markets, prices = load()
    entries = build_entries(markets, prices)
    print(f"Candidate pool: {len(entries)}")
    entries = remove_bucket_spam(entries)
    print(f"After bucket-spam filter: {len(entries)}")

    sample = sample_workbook(entries, n=N_QUESTIONS, seed=SEED)
    print(f"Sampled: {len(sample)}")
    print(f"\nBucket distribution:")
    print(sample["bucket"].value_counts())

    # compute fav_won before writing (used in both workbook + answer_key)
    sample = sample.copy()
    sample["fav_won"] = np.where(sample["p"] >= 0.5,
                                  sample["yes_won"].astype(bool),
                                  ~sample["yes_won"].astype(bool))
    # assign q_id and reset index
    sample = sample.reset_index(drop=True)
    sample["q_id"] = range(1, len(sample) + 1)

    # write full workbook
    write_workbook(sample)
    write_answer_key(sample)
    print(f"[WRITTEN] {WORKBOOK}")
    print(f"[WRITTEN] {ANSWER_KEY} (hidden from analyst)")

    # write per-batch files
    n_batches = (len(sample) + BATCH_SIZE - 1) // BATCH_SIZE
    for b in range(n_batches):
        lo = b * BATCH_SIZE
        hi = min(lo + BATCH_SIZE, len(sample))
        batch = sample.iloc[lo:hi].reset_index(drop=True)
        # keep q_id from full workbook (don't renumber)
        batch_path = WORKBOOK.parent / f"questions_batch_{b+1}.md"
        write_workbook(batch, batch_no=b+1, out_path=batch_path)
        print(f"[WRITTEN] {batch_path}  (Q{batch['q_id'].min()}-Q{batch['q_id'].max()})")

    print(f"\nFavorite win rate (baseline): {sample['fav_won'].mean()*100:.1f}%  "
          f"(if you just bet on favorite every time)")


if __name__ == "__main__":
    main()

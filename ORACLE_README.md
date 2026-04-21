# Polymarket Oracle — 方向 A 工作流

## 為什麼不再做量化 FLB

經過四輪回測循環的誠實結論：

1. **Cycle 1** (12 天樣本)：發現 +2.1% FLB edge
2. **Cycle 2** (30 天 + bootstrap CI)：修正為 +3.61% (策略 A)
3. **Cycle 3** (DSR + Ostracism)：**Deflated Sharpe 0.41 不過；t_cluster = +0.23 不顯著**
4. **Cycle 4** (cluster-aware + 跨平台 + cold-start)：三路並行全部 **無 edge**

核心發現：Polymarket 個人可執行的**統計/套利 edge 在 2026 已不存在**。

唯一還有可能的是 **資訊整合 edge**。這是 Claude 的 comparative advantage。

---

## 三層決策框架（保留）

```
Layer 1  事件品質過濾器   oracle_scanner.py
         ↓
Layer 2  Claude 主觀分析   subagent × WebSearch/WebFetch
Layer 3  客觀資料驗證      同一 agent 在 brief 的 checklist 裡
         ↓
JSON 決策 (BUY YES / BUY NO / SKIP)
         ↓
       Paper Portfolio    oracle_portfolio.py
```

---

## 每日工作流

```bash
# 1. 掃事件品質 (每早跑一次)
python oracle_scanner.py
# → data/results/oracle_candidates.csv (≈150 events)

# 2. 挑前 6-10 個生成 briefs
python oracle_analyze.py --top 8
# → data/oracle_briefs/*.md

# 3. 把每個 brief 派 subagent 執行（主 agent 手動）
#    每 agent 回傳嚴格 JSON，append 到 data/oracle_decisions.jsonl

# 4. 把 BUY 決策寫入 paper portfolio
python oracle_portfolio.py --ingest

# 5. 每日結算
python oracle_portfolio.py --settle

# 6. 月報
python oracle_portfolio.py --report
```

---

## 決策規則（硬性）

- `|edge_bps| < 500` → **SKIP**（資訊優勢不足）
- `confidence < 3/5` → **SKIP**
- 題目模糊 / UMA 爭議先例 → **SKIP**
- **healthy ratio: 10 個候選 SKIP 7 個是正常的**

倉位公式（bankroll × cap）：
- edge 500-1000 bps → 2% cap
- edge 1000-2000 bps → 3% cap
- edge > 2000 bps → 5% cap，但要反省「為什麼市場這麼笨？」

---

## 成敗驗收

paper trade 4 週後檢視：

| 指標 | 及格 | 優秀 |
|---|---|---|
| 勝率 vs `p_claude` 校準誤差 | < 10pp | < 5pp |
| 月度實現 PnL | > 0 | > 2% bankroll |
| SKIP 比例 | 60-80% | 70-80% |
| 單倉最大虧損 | < 5% bankroll | < 3% |

**若 8 週後未達「及格」 → 確認方向 A 也不成立，停手。**

---

## 既有檔案

### 新 (Cycle 5 保留)
- `oracle_scanner.py` — Layer 1 事件品質過濾
- `oracle_analyze.py` — Layer 2+3 brief 生成
- `oracle_portfolio.py` — paper-trade ledger

### 舊 (已證偽、僅歷史參考)
- `live_scanner.py` — 舊的 FLB profile 掃描器（**不要用**）
- `backtest_flb.py` / `deep_analysis.py` / `validate.py` / `final_analysis.py` — FLB 回測鏈
- `ostracism_test.py` / `flb_cluster_aware.py` / `cold_start_probe.py` — Cycle 3+4 證偽工具

### 資料
- `data/markets*.parquet` — 318k 歷史市場元資料（可再利用做其他分析）
- `data/prices*.parquet` — 12k 市場價格歷史（CLOB 30 天限制）
- `data/oracle_briefs/` — 當日待分析 brief
- `data/oracle_decisions.jsonl` — append-only 決策紀錄
- `data/oracle_positions.csv` — 當前/歷史 paper 倉位

---

## 關鍵紀律

1. **信心不夠寧願 SKIP**。賺錢不靠數量，靠 edge × 正確決策。
2. **entry price = ask**（YES 邊）或 **1 - bid**（NO 邊）。不要用 mid 算 edge（會高估）。
3. **每週覆核**：若連續 2 週 BUY 決策 > 40%，強制把 `edge` 門檻從 500bps 調高到 800bps。
4. **結算源可疑 = SKIP**。UMA 爭議一次可吃掉 3 個月利潤。
5. **規模化陷阱**：單個 Polymarket 市場不吃太多單，吃 > 5% orderbook 會推價。

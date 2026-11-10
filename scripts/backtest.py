# scripts/backtest.py —— 月度动量回测（P19 时序纪律的代码化）
# 铁律：第 t 日收盘后算信号（只用 ≤t 的数据），第 t→t+1 日才产生收益
import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "cases" / "case-001" / "data.csv"
OUT = ROOT / "evidence" / "case-001-results.json"

LOOKBACK = 20  # 动量回看窗口（20 日）

# 1. 读数据：整理成 {品种: [(日期, 收盘), ...]}
prices = {}
with DATA.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        prices.setdefault(row["ticker"], []).append((row["date"], float(row["close"])))

tickers = sorted(prices)
dates = [d for d, _ in prices[tickers[0]]]

# 2. 回测主循环
strategy_total = 0.0
benchmark_total = 0.0
last_signal_date = None
n_trades = 0

for t in range(LOOKBACK, len(dates) - 1):  # 留一天给收益计算
    day_t, day_next = dates[t], dates[t + 1]
    # 信号：用 ≤ day_t 的过去 20 日涨幅排名
    momentum = {
        tk: prices[tk][t][1] / prices[tk][t - LOOKBACK][1] - 1
        for tk in tickers
    }
    best = max(momentum, key=momentum.get)  # 买涨幅最强的
    last_signal_date = day_t
    # 收益：只在 day_t → day_next 这一段产生（信号之后！）
    strategy_total += prices[best][t + 1][1] / prices[best][t][1] - 1
    benchmark_total += sum(
        prices[tk][t + 1][1] / prices[tk][t][1] - 1 for tk in tickers
    ) / len(tickers)
    n_trades += 1

# 3. 结果入 evidence/（出生证明：时点、口径、数值一次记全）
result = {
    "case_id": "case-001",
    "strategy": f"momentum_top1_lookback{LOOKBACK}",
    "as_of": dates[-1],                      # 数据快照截止日
    "n_trades": n_trades,
    "signal_timing_check": "全部信号 ≤ as_of，收益发生在信号之后（P19）",
    "last_signal_date": last_signal_date,
    "strategy_total_return_pct": round(strategy_total * 100, 2),
    "benchmark_equal_weight_pct": round(benchmark_total * 100, 2),
    "excess_pct": round((strategy_total - benchmark_total) * 100, 2),
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"回测完成：{n_trades} 次交易")
print(f"策略累计收益：{result['strategy_total_return_pct']}%")
print(f"基准（等权）收益：{result['benchmark_equal_weight_pct']}%")
print(f"超额：{result['excess_pct']}%  → 结果已存 {OUT.name}")
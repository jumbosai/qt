# scripts/make_data.py —— 生成合成价格数据
# 种子固定 = 每次运行生成的数据一模一样（P20/P44：确定性可复现）
import csv
import random
from pathlib import Path

random.seed(42)  # 种子：随机世界的定海神针

OUT = Path(__file__).parent.parent / "cases" / "case-001" / "data.csv"

TICKERS = ["SYN-A", "SYN-B", "SYN-C"]  # 三只合成品种
DAYS = 120                              # 120 天
START_PRICE = 100.0

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["date", "ticker", "close"])  # 表头
    prices = {t: START_PRICE for t in TICKERS}
    for day in range(DAYS):
        date = f"2026-06-{day + 1:02d}"           # 从 6 月 1 日起
        for t in TICKERS:
            change = random.gauss(0, 1.5)         # 每天随机涨跌（平均0，波动1.5%）
            prices[t] = round(prices[t] * (1 + change / 100), 2)
            writer.writerow([date, t, prices[t]])

print(f"已生成 data.csv：{DAYS} 天 × {len(TICKERS)} 只品种（种子42，可复现）")
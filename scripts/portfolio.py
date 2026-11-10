# scripts/portfolio.py —— case-002 目标组合权重表生成（核心-卫星，brief P13 目标组合）
# 核心仓 70% 写死；卫星仓 30% 取 evidence 里已生效的 satellite_candidates 前5等权
# 确定性：输出只依赖 evidence/case-002-results.json，同一快照重跑产出一致（P15 可盖章）
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
RESULTS = ROOT / "evidence" / "case-002-results.json"
OUT = ROOT / "evidence" / "portfolio-target.md"

# 核心仓（事先写死，改动须走演进流程 P27-33）：(代码, 目标权重%)
CORE = [("510300", 40.0), ("511010", 20.0), ("518880", 10.0)]
CORE_TOTAL = 70.0
SAT_TOTAL = 30.0
SAT_PER = 6.0  # Top5 等权：30% / 5

COMMISSION = 0.0003  # 佣金万三（0.03%），ETF 免印花税


def w(s):
    """显示宽度：CJK 记 2，其余记 1（终端对齐用）"""
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in str(s))


def pad(s, width):
    return str(s) + " " * max(0, width - w(s))


def main():
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    if not results.get("satellite_candidates_confirmed"):
        raise SystemExit("satellite_candidates 未生效（规模复核未通过），禁止生成目标组合（P26）")

    names = {e["code"]: e["name"] for e in results["screen"]}
    satellites = results["satellite_candidates"][:5]
    if len(satellites) != 5:
        raise SystemExit(f"卫星候选不足 5 只（实际 {len(satellites)}），等权配置无法凑满 30%")

    rows = [(c, names[c], "核心", f"{p:.0f}%") for c, p in CORE]
    rows += [(c, names[c], "卫星", f"{SAT_PER:.0f}%") for c in satellites]

    core_sum = sum(p for _, p in CORE)
    sat_sum = SAT_PER * len(satellites)
    assert abs(core_sum - CORE_TOTAL) < 1e-9, f"核心仓合计 {core_sum}% ≠ {CORE_TOTAL}%"
    assert abs(sat_sum - SAT_TOTAL) < 1e-9, f"卫星仓合计 {sat_sum}% ≠ {SAT_TOTAL}%"

    as_of = results["data"]["as_of"]
    cost_per_10k = 10000 * COMMISSION  # 单边

    header = ["代码", "名称", "角色", "目标权重"]
    widths = [max(w(h), *(w(r[i]) for r in rows + [["合计", "", "", "100%"]]))
              for i, h in enumerate(header)]

    def fmt_row(r):
        return "  ".join(pad(c, widths[i]) for i, c in enumerate(r))

    lines = [
        "# case-002 目标组合权重表",
        "",
        f"数据 as_of：{as_of}（行情快照）｜卫星名单来源：evidence/case-002-results.json"
        f"（satellite_candidates，confirmed={results['satellite_candidates_confirmed']}）",
        f"核心仓 {CORE_TOTAL:.0f}%（长期持有，偏离 ±5% 再平衡）＋ 卫星仓 {SAT_TOTAL:.0f}%（Top5 等权，各 {SAT_PER:.0f}%）",
        "",
        "| 代码 | 名称 | 角色 | 目标权重 |",
        "|---|---|---|---|",
    ]
    lines += [f"| {c} | {n} | {r} | {p} |" for c, n, r, p in rows]
    lines += [
        "| 合计 | | | 100% |",
        "",
        "## 交易成本提示",
        "",
        f"若从全仓现金一次性买入，按佣金万三（0.03%）+ ETF 无印花税估算："
        f"每 1 万元成交额单边约 {cost_per_10k:.1f} 元成本（一买一卖双边约 {cost_per_10k * 2:.1f} 元；"
        f"若券商有单笔最低 5 元佣金，小额单笔按 5 元计）。",
        "这只是估算，实际费率、最低收费与美股 ETF 佣金结构以你的券商为准。",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"数据 as_of={as_of}，核心 {CORE_TOTAL:.0f}% + 卫星 {SAT_TOTAL:.0f}%（Top5 各 {SAT_PER:.0f}%）")
    print(fmt_row(header))
    print("-" * w(fmt_row(header)))
    for r in rows:
        print(fmt_row(r))
    print(fmt_row(["合计", "", "", "100%"]))
    print(f"\n交易成本提示：1 万元一次性买入，万三佣金 + ETF 无印花税，单边约 {cost_per_10k:.1f} 元"
          f"（估算，实际以券商为准；详见 {OUT.relative_to(ROOT)}）")


if __name__ == "__main__":
    main()

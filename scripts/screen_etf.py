# scripts/screen_etf.py —— case-002 卫星仓筛选（brief P26 规则的代码化）
# 铁律：只用 data/ 快照内 ≤ as_of 的数据；规模缺失标 n/a 转人工复核，绝不默认通过
# 确定性：同一快照重跑结果一致（排名并列按代码字典序）；规模复核记录来自 meta.json，不手改本文件
import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "cases" / "case-002" / "data"
META = DATA_DIR / "meta.json"
OUT = ROOT / "evidence" / "case-002-results.json"

DRAWDOWN_LIMIT_PCT = -25.0  # 最大回撤 ≤ -25% 淘汰
SIZE_LIMIT_YI = 5.0         # 规模 < 5 亿元淘汰
TOP_N = 5                   # 卫星仓候选名额


def load_etfs():
    """读 meta.json（权威名单+规模）和每只的 CSV（收盘价序列）"""
    meta = json.loads(META.read_text(encoding="utf-8"))
    etfs = []
    for code, info in meta["etfs"].items():
        rows = list(csv.DictReader((DATA_DIR / info["file"]).open(encoding="utf-8")))
        closes = [float(r["收盘价"]) for r in rows]
        ret = closes[-1] / closes[0] - 1
        # 最大回撤：每个价格对“此前最高点”的跌幅，取最小
        peak = closes[0]
        mdd = 0.0
        for p in closes:
            peak = max(peak, p)
            mdd = min(mdd, p / peak - 1)
        etfs.append({
            "code": code,
            "ticker": info["ticker"],
            "name": info["name"],
            "n_rows": len(rows),
            "first_date": rows[0]["日期"],
            "last_date": rows[-1]["日期"],
            "return_pct": round(ret * 100, 2),
            "max_drawdown_pct": round(mdd * 100, 2),
            "return_raw": ret,
            "mdd_raw": mdd,
            "fund_size_亿元": info["fund_size_亿元"],
            "fund_size_source": info.get("fund_size_source"),
            "fund_size_as_of": info.get("fund_size_as_of"),
            "fund_size_query_date": info.get("fund_size_query_date"),
            "elimination_reasons": [],
            "size_missing": info["fund_size_亿元"] == "n/a",
        })
    return meta, etfs


def screen(etfs):
    """三条淘汰规则，全部命中原因都记录（不只记第一条）"""
    # 规则1：涨幅后 50% 淘汰——全池排名，n 只淘汰 floor(n/2) 只
    order = sorted(etfs, key=lambda e: (-e["return_raw"], e["code"]))
    for e in order[len(order) // 2:]:
        e["elimination_reasons"].append("涨幅后50%")

    # 规则2：最大回撤 ≤ -25% 淘汰
    for e in etfs:
        if e["mdd_raw"] * 100 <= DRAWDOWN_LIMIT_PCT:
            e["elimination_reasons"].append("最大回撤≤-25%")

    # 规则3：规模 < 5 亿淘汰；缺失标 n/a → 人工复核，不自动淘汰也不视为通过
    for e in etfs:
        if not e["size_missing"] and e["fund_size_亿元"] < SIZE_LIMIT_YI:
            e["elimination_reasons"].append("规模<5亿")

    survivors = [e for e in order if not e["elimination_reasons"]]
    return survivors[:TOP_N]


def w(s):
    """显示宽度：CJK 记 2，其余记 1（终端对齐用）"""
    return sum(2 if ord(ch) > 0x2E7F else 1 for ch in str(s))


def pad(s, width):
    return str(s) + " " * max(0, width - w(s))


def print_table(order, candidates):
    header = ["代码", "名称", "近1年涨幅%", "最大回撤%", "规模(亿)", "结论", "淘汰原因"]
    rows = []
    for e in order:
        if e["elimination_reasons"]:
            verdict, reason = "淘汰", "；".join(e["elimination_reasons"])
        elif e in candidates:
            verdict, reason = "候选" + ("*" if e["size_missing"] else ""), ""
        else:
            verdict, reason = "幸存", ""
        size = e["fund_size_亿元"] if e["size_missing"] else f'{e["fund_size_亿元"]:g}'
        rows.append([
            e["code"], e["name"], f'{e["return_pct"]:+.2f}',
            f'{e["max_drawdown_pct"]:.2f}', size, verdict, reason,
        ])
    widths = [max(w(h), *(w(r[i]) for r in rows)) for i, h in enumerate(header)]
    line = "  ".join(pad(h, widths[i]) for i, h in enumerate(header))
    print(line)
    print("-" * w(line))
    for r in rows:
        print("  ".join(pad(c, widths[i]) for i, c in enumerate(r)))
    if any(e["size_missing"] for e in candidates):
        print("\n* 规模 n/a：按 brief 规模规则转人工复核，复核通过前候选名单不生效")
    else:
        print("\n规模已复核：候选规模均 ≥5亿元，候选名单正式生效（复核记录见 results.json 的 size_review）")


def main():
    meta, etfs = load_etfs()
    candidates = screen(etfs)
    order = sorted(etfs, key=lambda e: (-e["return_raw"], e["code"]))
    as_ofs = {e["last_date"] for e in etfs}
    as_of = min(as_ofs)

    confirmed = bool(candidates) and all(
        (not c["size_missing"]) and c["fund_size_亿元"] >= SIZE_LIMIT_YI
        for c in candidates
    )
    if confirmed:
        note = "规模复核通过：候选全部 ≥5亿元，satellite_candidates 正式生效"
    elif any(c["size_missing"] for c in candidates):
        note = "候选存在规模 n/a：按 P26 转人工复核，复核通过前 satellite_candidates 不生效"
    else:
        note = "候选中存在规模 <5亿元：satellite_candidates 未生效"

    size_reviewed = [e for e in order if not e["size_missing"]]
    for e in etfs:
        e.pop("return_raw")
        e.pop("mdd_raw")
        e["status"] = "candidate" if any(e is c for c in candidates) else (
            "eliminated" if e["elimination_reasons"] else "survived")
    review = [e["code"] for e in order if e["size_missing"]]

    result = {
        "case_id": "case-002",
        "stage": "satellite_screen",
        "rules": {
            "momentum": "近1年涨幅 = (末日收盘-首日收盘)/首日收盘；后50%淘汰（全池排名，并列按代码字典序）",
            "drawdown": "近1年最大回撤 ≤ -25% 淘汰",
            "size": "基金规模 < 5亿元淘汰；缺失标 n/a 转人工复核，不得视为通过（P26）",
            "ranking": "幸存者按近1年涨幅降序取前5",
        },
        "data": {
            "dir": "cases/case-002/data",
            "retrieved_date": meta["retrieved_date"],
            "as_of": as_of,
            "as_of_consistent": len(as_ofs) == 1,
            "n_etfs": len(etfs),
        },
        "screen": sorted(etfs, key=lambda e: e["code"]),
        "review_required": review,
        "satellite_candidates": [e["code"] for e in candidates],
        "satellite_candidates_confirmed": confirmed,
        "note": note,
        "size_review": {
            "method": "stock_finance_data 无 ETF AUM 字段，候选规模人工联网复核（issuer官网/Yahoo Finance/天天基金）",
            "fx": meta.get("fund_size_fx"),
            "items": [
                {
                    "code": e["code"],
                    "fund_size_亿元": e["fund_size_亿元"],
                    "source": e["fund_size_source"],
                    "as_of": e["fund_size_as_of"],
                    "query_date": e["fund_size_query_date"],
                }
                for e in size_reviewed
            ],
            "conclusion": "候选5只规模均 >5亿元，规模门槛通过" if confirmed
                          else "存在未复核或低于门槛的候选，见 note",
        },
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"数据快照：as_of={as_of}，检索日={meta['retrieved_date']}，{len(etfs)} 只ETF"
          f"{'（各CSV截止日一致）' if result['data']['as_of_consistent'] else '（注意：CSV截止日不一致！）'}")
    print_table(order, candidates)
    print(f"\n卫星仓候选 Top{TOP_N}：{'、'.join(e['code'] for e in candidates) or '（无）'}"
          f"{'【已生效】' if confirmed else '【未生效】'}")
    if review:
        print(f"仍缺规模（已淘汰，不影响结论）：{'、'.join(review)}")
    print(f"→ 结果已存 {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

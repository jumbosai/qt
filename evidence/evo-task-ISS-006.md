# 演进任务包：ISS-006（跨市场收益口径不一致）

- 生成：2026-11-10 ｜ 流程：/qt:evo

## 问题描述
A 股 CSV 为前复权价（含分红再投资），美股 CSV 为不复权价（不含股息约 0.45%~1.3%）。动量排名跨市场比较时系统性低估美股约 1 个百分点；brief 未规定价格口径，存在逐月漂移风险。

## 责任角色
generator（取数与脚本）

## 修复方案
美股 `adjust=forward` 实测返回 EMPTY_DATA（该源不支持美股前复权），故改为**全市场统一不复权（price return）**：重取 7 只 A 股 ETF `adjust=none`，美股 CSV 保持不变（本就不复权），口径对齐。收益口径写入 meta.json 与 results.json 的 data 块，钉死口径防漂移。

## 验收标准
1. meta.json `price_params.adjust` 与 results.json `data.adjust` 均为 none 并注明理由
2. Critic 独立重算 10 只涨幅/回撤与 results.json 一致（重算脚本不复用筛选代码）
3. 同一快照重跑 screen_etf.py 产物字节一致（确定性不破）

## 关联产物及当前哈希（修复前）
- cases/case-002/data/*.csv（7 只 A 股）：510300 `4f5870d7e16aa84e`(SPY)/`9bb005ac8ee2bbee`(QQQ)/`121bee6f6bbc1623`(VTI) 美股三只不变；A 股七只待重取后变更
- cases/case-002/data/meta.json `f4a693a2f6b55b97`
- scripts/screen_etf.py `e01f6f0036188a44`
- evidence/case-002-results.json `5456acb7b648951c`（重跑后必然变更）

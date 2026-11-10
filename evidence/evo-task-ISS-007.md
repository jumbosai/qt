# 演进任务包：ISS-007（无调仓单，成本提示缺换手率×费率口径）

- 生成：2026-11-10 ｜ 流程：/qt:evo

## 问题描述
brief 验收#5 要求"调仓单含交易成本提示（卫星换手率 × 预估费率）"。现有 portfolio-target.md 是目标权重表而非调仓单（无买卖明细与金额），成本提示为通用万三，未按换手率×费率口径计算；本期首次建仓换手率=100%，应显式给出。

## 责任角色
generator（scripts/portfolio.py）

## 修复方案
portfolio.py 增加产出 evidence/case-002-trade-order.md：当前持仓=现金 → 买入明细（权重、示例金额），换手率=100%，成本 = 本金 × 换手率 × 费率（单边万三无印花税），卫星仓单独列示 30%×100%×0.03%。

## 验收标准
1. evidence/case-002-trade-order.md 存在，含买卖明细/金额、换手率×费率成本式
2. 同一快照重跑 portfolio.py，portfolio-target.md 与 trade-order 字节一致
3. portfolio-target.md 未被破坏（权重表原样保留）

## 关联产物及当前哈希（修复前）
- scripts/portfolio.py `40aca52769c73d1a`
- evidence/portfolio-target.md `b3d3236fb74b0aef`
- evidence/case-002-trade-order.md（新建，无哈希）

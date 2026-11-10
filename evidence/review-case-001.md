# case-001 审查报告（Critic 出具 · 对应课件 P9/P19/P20）

## 审查对象
evidence/case-001-results.json（由 scripts/backtest.py 确定性生成）

## 时点与证据检查
- [x] 信号时点全部 ≤ as_of（last_signal_date ≤ as_of）✅ 通过
- [x] 收益发生在信号之后（t→t+1，无未来泄露）✅ 通过
- [x] 结果文件带日期与口径说明 ✅ 通过

## 问题项台账
| 编号 | 描述 | 责任角色 | 状态 |
|---|---|---|---|
| ISS-001 | 回测未扣除交易成本与滑点，收益高估 | generator | open |
| ISS-002 | 样本仅 120 天 × 3 只品种，统计意义弱 | generator | open |
| ISS-003 | 仅用种子 42，未做参数扰动/子样本稳健性检验（P20）| generator | open |

## Critic 结论
候选策略不予验收，按 P18 修订循环发回 Generator 修复（继续/结束决策权在 Orchestrator 与人类）。

## 备注
超额 +0.48% 在扣除交易成本后预计转负（呼应 ISS-001）；合成数据无真实动量效应，该结果为预期现象。
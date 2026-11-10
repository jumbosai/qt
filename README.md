# qt-practice：长程智能体工作流练习

> 复旦 FMBA《金融人工智能编程》第 3 讲「长程工作流」实操
> 按课件 P4「完整架构」搭建的迷你量化研究工作流

## 工作流图（P4 骨架的实体化）

```
用户想法(brief.md) ──授权+边界──→ Orchestrator(qt.py 状态机)
                                      │ 读/写 state.json（请求ID·产物·哈希·问题项·版本）
                    ┌─────────────────┴──────────────────┐
                    ▼                                    ▼
        Generator 负责人(角色卡)              Critic 负责人(角色卡)
        数据(make_data)                      数据与证据/稳健性/执行风险
        特征+回测(backtest) ──候选+测试──→   问题项台账(ISS-xxx) ──未通过──┐
                    │←──────────── 修复任务包（P19）←───────────────────┘
                    ▼
        检查关卡(P20)：数值检查+完整审查+两轮通过
                    ▼
        人类批准(P5) → 演进(P27-33)：改动提案→评估→批准/回滚（Git 版本）
```

## 目录结构

| 路径 | 作用 | 课件页 |
|---|---|---|
| `roles/generator.md` | Generator 角色契约（职责/工具/边界） | P10 |
| `roles/critic.md` | Critic 角色契约（每轮全新审查） | P9 |
| `state/state.json` | 共享状态台账（问题项/版本/批准权） | P14/P24 |
| `cases/case-001/brief.md` | 任务简报（时点证据+验收标准） | P3/P43 |
| `cases/case-001/data.csv` | 合成数据快照（种子42可复现） | P44 |
| `evidence/case-001-results.json` | 回测结果（出生证明） | P15 |
| `evidence/review-case-001.md` | Critic 审查报告（3 问题项） | P19/P20 |
| `scripts/qt.py` | Orchestrator：状态机+条件路由+自动盖章 | P14/P26 |
| `scripts/make_data.py` / `backtest.py` | 确定性计算（可复跑） | P10/P44 |

## 如何复现（任何人跑出相同结果）

```bash
python3 scripts/make_data.py   # ① 生成合成数据（种子42，人人相同）
python3 scripts/backtest.py    # ② 回测 → 结果+时点检查入 evidence/
python3 scripts/qt.py          # ③ Orchestrator：盖章 + 条件路由
```

## 当前案例结论（case-001）

动量策略超额 +0.48%（99 次交易），扣费后预计转负；Critic 开 3 个问题项（ISS-001~003），
状态推进至 `review`，待修复循环。详见 `evidence/review-case-001.md`。

## 已知边界 / 作业扩展方向

- 修复循环分支（review → 修复任务包）待实现
- 稳健性检验（多种子/子样本）待实现
- 自动 git push Hook（待安装）
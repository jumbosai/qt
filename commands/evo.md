---
description: 演进：把 status=open 的 issues 逐条转成修复任务包，Generator 修复后 Critic 复核，全程留痕 commit
---

你在 qt 工作流中扮演 Orchestrator，执行演进流程（P27-33）：

1. 读取 state/state.json 中所有 status=open 的 issues（$ARGUMENTS 可指定单条如 ISS-004，留空处理全部），逐条生成修复任务包写入 evidence/evo-task-<ISS-xxx>.md，包含：问题描述 → 责任角色（owner）→ 验收标准（可检查、可复现）→ 关联产物清单及当前哈希指纹（从 artifacts 取）
2. 分派 Generator 按任务包修复；修复涉及 scripts/ 时，要求同一快照重跑结果一致（P47 确定性）
3. 每修完一条先运行 python3 scripts/qt.py 验货（verify_seal）：若关联产物被误改（TAMPERED），提示人类用 git 回滚该产物后重试，禁止带着脏产物继续
4. 交 Critic 独立复核（复核不修改产物），报告写入 evidence/；通过则该 issue 标 resolved，未通过保持 open 并记录原因
5. 所有决定、任务包、复核报告记入 evidence/ 并 commit；任务包中如需改动 brief 的写死规则，必须先取得人类批准（P27-33）

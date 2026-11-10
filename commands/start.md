---
description: 开新 case：读 brief 建台账、运行 qt.py 路由分派 Generator、提醒人类设定验收口径
---

你在 qt 工作流中扮演 Orchestrator，执行开案流程：

1. 确定新案件目录：优先用 $ARGUMENTS 作为 cases/ 下的目录名；未提供则先列出 cases/ 下尚无 evidence 产物的目录让人类确认。读取该目录的 brief.md 作为唯一需求来源
2. 在 state/state.json 建立台账：request_id（格式 req-YYYYMMDD-NNN）、case_id、version 0.1.0、status 初始为 pending、artifacts 与 issues 为空列表、approvals.human_required=true
3. 运行 python3 scripts/qt.py 触发 P26 路由：状态推进到 generator_working，输出原样记入 evidence/
4. 最后提醒人类：开案完成，请设定验收口径（产出格式、阈值、检查关卡），验收标准确认后写入 evidence/ 并 commit

纪律：brief 里写死的规则在人工修改前视为冻结；所有决定记入 evidence/；每步操作前说明你在执行哪一步。

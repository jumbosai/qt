# 演进任务包：ISS-008（换血规则缺结构化基线）

- 生成：2026-11-10 ｜ 流程：/qt:evo

## 问题描述
brief 卫星再平衡规则"Top5 与上月相比换血 >2 只才整体更换"。state.json 未结构化记录本期 Top5 名单（仅存于 portfolio-target.md 表格），下月无法程序化判定换血数。

## 责任角色
generator（台账维护）

## 修复方案
state.json 新增 `current_satellite: {as_of, list, basis, set_at}`，以本期 satellite_candidates 为基线。

## 验收标准
1. state.json 含 current_satellite，list 与 results.json satellite_candidates 一致
2. qt.py verify_seal 通过（含变更后产物重新盖章）
3. 其余 open issues 保持 open 且各有处理计划

## 关联产物及当前哈希（修复前）
- state/state.json（台账本体）
- evidence/case-002-results.json `5456acb7b648951c`（ISS-006 修复后会变更，以最新为准）

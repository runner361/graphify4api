# Implementation Tasks — add-scenario-capability-gloss

## Spec

- [ ] 1. 撰写 openspec 变更:proposal / design / tasks / specs delta / .openspec.yaml
- [ ] 2. `openspec validate add-scenario-capability-gloss` 通过

## 实现

- [ ] 3. 读 `tools/skillgen/fragments/core/core.md` Step 3 Part B prompt,定位 schema 与规则段
- [ ] 4. 扩展 Part B prompt:合法 `file_type` 增 `feature`(仅操作页);节点可选字段 `capability`(英文动名 gloss)、`scenario_kind`(operation);给"离散操作"判定规则 + gloss 正反例
- [ ] 5. 同步 `references/extraction-spec.md`(若 schema 权威定义在此)
- [ ] 6. `python -m tools.skillgen` regen 14 split 产物
- [ ] 7. `python -m tools.skillgen --bless` 更新 expected 快照
- [ ] 8. `python -m tools.skillgen --check` 绿(无 drift)
- [ ] 9. `python -m graphify install`(windows 平台)同步 installed skill

## 验证

- [x] 10. 重跑 Part B 子代理于 iotdm 语料子集(实例标签管理 4 篇),确认操作级页面产出带 `capability` 的 `file_type:"feature"` 节点 ✓(删除标签→`delete tag`、添加标签→`add tag`、使用标签检索资源→`search resource by tag`)
- [x] 11. 确认类目页/概述页不产场景节点 ✓(标签概述→不产)
- [x] 12. 确认目录层 dir-feature + `contains` 不受影响(回归) ✓(单元测试 109 绿)
- [x] 13. 既有 feature-link/build 测试全绿 ✓(109 passed)

## 收尾(待用户决定)

- [ ] 14. 是否 archive(依赖乙落地后一并 archive 更合理)
- [x] 15. **已知设计 bug(端到端暴露)→ 已修复**:子代理给 scenario 节点 label=页面名、source_file=同一 .md → 与 sibling document page 节点 label+source_file 全同 → `build()` exact 去重吞 feature 节点。**根因**:dedup pass 1 按 `_norm(label)` 分组、组内按 source_file 分区合并(label+source_file 全同即合并)。**修复**:extraction-spec(甲)+ extraction-spec-compact 规定 scenario 节点 `label` = 英文 capability gloss 本身(如 "delete tag"),与 page 节点的中文文件名 label 天然不同 → 不同 `_norm(label)` 组 → 不合并。实证:注入 3 scenario 节点,build 去重后 39 feature 存活(36 dir-feature + 3 scenario),scenario 全部存活。见 `scenario-linking-e2e-blockers` 记忆 blocker #1(已标 RESOLVED)。


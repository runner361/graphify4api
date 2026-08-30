# Implementation Tasks — add-scenario-api-linking-via-gloss

## Spec

- [x] 1. 撰写 openspec 变更:proposal / design / tasks / specs delta(MODIFIED 确定性候选预筛 + ADDED 操作场景节点预筛绕过)/ .openspec.yaml
- [x] 2. `openspec validate add-scenario-api-linking-via-gloss` 通过

## 实现

- [x] 3. 读 `graphify/feature_link.py` 的 `_feature_text`(line ~228)+ `run_feature_linking` 循环(line ~548-577)+ early-return(line ~498)
- [x] 4. `_feature_text`:`parts` 纳入 `feature.get("capability")`(英文 gloss);docstring 注明跨语言桥
- [x] 5. `run_feature_linking`:`unmapped` 计数(语义扩展为"评过但 0 边":预筛饿死 OR LLM 拒判);返回摘要 + early-return + cache + LLM/degrade 路径同步增 `unmapped`
- [x] 6. `_prescreen` + `_degrade` 打分双侧 `.lower()`(大小写不敏感;实测 34→75 命中),不改 `_english_terms`/`_op_text`/`_entity_text` 构造
- [x] 7. 不动 `generate_feature_nodes`/`_is_md_file_node`/裁决 prompt/缓存
- [x] 7a. **scenario 预筛 bypass(D5)**:`_prescreen` 加 `min_prescreen` 参数;`run_feature_linking` 按 `feat.get("capability")` 选阈值(`_SCENARIO_MIN_PRESCREEN=0.0` vs `_MIN_PRESCREEN=60.0`);dir-feature 无 `capability` 走 strict 60 不变

## 验证

- [x] 8. 单测:带 `capability` 的 scenario 节点 + 英文 op 候选(大写 method)→ prescreen 命中 → 边生成(`implemented_by`)
- [x] 9. 单测:scenario 节点无匹配 API → `unmapped` +1、0 边、不伪造
- [x] 10. 单测:无 `capability` 的 dir-feature 节点行为零回归(与既有测试一致)
- [x] 11. 单测:`_prescreen` 大小写不敏感(大写 method vs 小写 gloss 命中)
- [x] 11a. 单测:scenario 动词差 bypass strict 预筛(`add tag`↔`tagDevice` ~22 分 < 60,strict 0 候选;bypass 进 LLM → `implemented_by` 边)
- [x] 11b. 单测:无 `capability` 的 feature 节点 strict 60 不走 bypass(LLM 不被调,0 边,`unmapped` +1)
- [x] 12. `tests/test_feature_link.py` + `tests/test_build.py` 全绿(111 feature_link/build 测试通过;130 test_wiki 失败为既有 GBK slug 问题,与本变更无关)

## 收尾(待用户决定)

- [ ] 13. 是否 archive(与变更甲 + add-feature-link-backend 一并 archive 更合理)
- [x] 14. 端到端验证(task #22,iotda+iotdm 合并图谱):全语料 strict 60 = 7 边;**shipped 代码(无 monkeypatch)重跑 = 109 条 feature→API/entity 边(70 implemented_by + 5 uses_entity + 其余,console GBK 截断打印但 `len(impl)==109` 为权威计数)**。bypass 逻辑被真实执行(`_prescreen` 在 cache 前跑,scenario 走 0.0 阈值返回 top-N),LLM/缓存裁决产出边。详见 `scenario-linking-e2e-blockers` 记忆(blocker #1 dedup 已修,blocker #2 已修)。

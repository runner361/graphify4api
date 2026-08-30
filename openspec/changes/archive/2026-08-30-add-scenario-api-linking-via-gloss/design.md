## Context

变更甲让 Part B 子代理为操作级 `.md` 页面吐 `file_type:"feature"` 场景节点,带英文 `capability` gloss。但 `run_feature_linking` 的 `_feature_text`(`feature_link.py:228`)此刻不读 `capability`——它组装 `[label, 文件名 stem, heading labels, _english_terms(正文)]`。对 scenario 节点:

- `fdir = feat.get("feature_dir") or feat.get("source_file","").rstrip("/")` → scenario 节点无 `feature_dir`,`fdir` 退化为 `.md` 文件路径本身
- `files_by_dir.get(fdir, [])` → `[]`(`files_by_dir` 键是目录,非 `.md` 路径)→ 无 page 节点 → 正文不刮
- → `_feature_text` 退化成纯中文 label(如"删除标签")
- `_prescreen` 的 `bridge = _english_terms(纯中文)` → 空串 → 返回 `[]` → 0 候选 → 无边

跨语言桥断在最后一公里:gloss 已在节点上,但 prescreen 没用它。本变更把 `capability` 纳入 `_feature_text` 的 parts,让英文 gloss 经 `_english_terms` 进 `bridge`,与英文 op_text 命中。

## Goals

- 带 `capability` 的 scenario 节点 → prescreen 在 gloss ↔ 英文 op_text 上命中 top-N → 进 LLM 裁决(或降级名称匹配)→ `implemented_by`/`uses_entity` 边生成
- 无 `capability` 的 feature 节点(目录类目层、旧产物)行为逐字节不变(零回归)
- 无匹配 API 的 scenario → 0 边、不伪造,且 `unmapped` 计数可量(诚实空)
- 零新增 LLM pass、零新增依赖、零 key

## Non-Goals

- **不**改 `_english_terms` / `_op_text` / `_entity_text` 的文本构造(gloss 只是新输入;小写化在打分 call-site 做,不污染 prompt/显示用的原始文本)
- **不**改 LLM 裁决 prompt / `_build_prompt` / `_parse_adjudication`(裁决层不变,只让它真正被调用)
- **不**改 `generate_feature_nodes` / `_is_md_file_node`(目录层不变)
- **不**改 `build()` 签名或调用(返回值仍丢弃;`unmapped` forward-compatible,本次不接报告)
- **不**改 Part B prompt(gloss 产出属变更甲)
- **不**改 skillgen 报告层/Step 5(`unmapped` 接入 GRAPH_REPORT 是后续 follow-up,本变更只让数据可得)
- **不**改 aider/devin monolith fragments(split-only)
- **不**解决 gloss 质量(gloss 选词不准如 `create amqp queue` 对 `amqp-queues` 仍可能排序偏低;本变更解决"gloss 没被用上" + "大小写击垮桥" + "动词汇差/单复数/复合词 bypass",gloss 质量是变更甲的天花板)

## Decisions

### D1: 在 `_feature_text` 加 `capability`,而非改 `_prescreen`

把 `feat.get("capability")` 加进 `_feature_text` 的 parts,而非在 `_prescreen` 里特判。理由:
- `_prescreen` 已对 `feature_text` 统一 `_english_terms` 抽英文词打分——gloss 是英文,自然进 bridge,无需特判
- `capability` 是节点级属性,放 `_feature_text`(以 `feature` 节点为输入)语义最贴;`_prescreen` 只认字符串,不认节点
- 一处改动,scenario 与 dir-feature 走同一条 `_feature_text`,dir-feature 无 `capability` 字段 → `feat.get("capability")` 为 None → 不追加 → 零回归

### D2: scenario 节点正文不额外刮

scenario 节点的 `fdir` 退化为 `.md` 路径,正文当前不刮(`files_by_dir.get(fdir)` 空)。本变更**不**为 scenario 节点额外 Read `.md` 正文刮词——`capability` gloss 是变更甲子代理读完整页后的一次跨语言概括,是正文英文词的精炼替代品,设计上就是为替代"正文刮词"这道失效机制。只读 gloss,最小、最忠实于变更甲的设计意图。若 gloss 召回不足,follow-up 可再刮正文,本变更不做(YAGNI)。

### D3: `unmapped` 计数入返回摘要

`run_feature_linking` 返回 `{features, edges, llm}`。新增 `unmapped`:预筛后 `not cand_ids` 的 feature 数。理由:
- "诚实空"要求能区分"未映射"(评了、无 API)与"未处理"(没评)。当前 `continue` 静默跳过,两者在返回里不可分
- `build()` 当前丢弃返回,但计数 forward-compatible:测试可断言、未来报告层可接入,无破坏
- 2 行改动,零风险

### D4: `_prescreen`/`_degrade` 打分大小写不敏感(实测驱动)

实测 `rapidfuzz.fuzz.token_set_ratio`(无 processor)大小写敏感:
- `("delete tag", "DELETE iot instances tags")` = **34.3** < 60 → 0 候选
- `("delete tag", "delete iot instances tags")` = 75.0 ≥ 60(双侧小写后)

HTTP 方法约定大写(`DELETE`/`POST`)、capability gloss 小写、路径段小写。大小写敏感的打分使 gloss 桥在"动词取自 gloss(小写)对 method(大写)"这一最常见情形下 0 命中——桥断在打分层。修法:在两处打分 call-site(`_prescreen` 与 `_degrade`)对 `bridge` 与 `ctxt` 各 `.lower()`,不改 `_english_terms`/`_op_text`/`_entity_text` 的构造(保持 prompt/显示用原始文本)。理由:
- 这是 prescreen 的**潜在健壮性缺陷**,独立于 gloss 也存在:老 body-term 桥仅靠 doc 正文里"POST"与 op_text"POST"恰好大小写一致才命中;若 doc 写小写"post"即失效。gloss 桥只是让它暴露
- 不用 `processor=utils.default_process`(会去标点,"amqp-queues"→"amqp queues"改 token 结构,行为变化大);`.lower()` 最小、可预测
- 零回归:既有"同形大小写一致"命中,双侧小写后仍等(100→100);既有"无重叠"仍无重叠

### D5: scenario 节点预筛 bypass(全语料端到端实测驱动)

D1+D4 修了"gloss 没被用上"和"大小写击垮桥",但全语料端到端(56 scenario × 173 ops)暴露 **strict 60 阈值仍饿死大部分 scenario 节点**——case-insensitive + gloss 只在 gloss 与 op_text **共享精确 token** 时桥通(如 `delete tag`↔`DELETE...tags` 因 `delete` 精确匹配 method);而最常见的动词语义差桥不了:

- `add tag`↔`tagDevice`(POST /tags):实测 `token_set_ratio` = **21.7** < 60。三重 token 级失配:(a) 动词差 `add` vs API 隐含动词(`tagDevice` 里没有 `add`),(b) 单复数 `tag` vs `tags`,(c) camelCase 复合名不分词(`tagDevice` 是一个 token,不分裂为 `tag`+`device`)。
- strict 60 全语料仅出 **7** 条 feature→API 边(2 条 scenario `implemented_by` + 5 entity);54/56 scenario 被饿死。

`token_set_ratio` 的 token 级精确匹配本质无法桥接语义等价但词素异的对——这是 fuzz 启发式的固有局限,不是 gloss 质量问题。但 **LLM 裁决器能**(它读语义:`add tag` ≡ 给设备打标签 ≡ `tagDevice`)。

**修法**:对带 `capability` 的 scenario 节点,prescreen 用 0.0 最低阈值(退化为"仅排序不硬滤",返回 top-N 不滤分),让候选总进 LLM 语义裁决;无 `capability` 的 dir-feature 仍走 strict 60(无 gloss,fuzz 是其唯一信号,阈值避免每 feature→全 op 淹没 LLM)。`_prescreen` 加 `min_prescreen` 参数,`run_feature_linking` 按 `feat.get("capability")` 选阈值。

**实测验证(全语料 iotdm 130 文档 + iotda 173 API)**:
- strict 60:7 边。
- scenario bypass(0.0):**92** 条 scenario→API/entity 边,几乎全正确(`add tag`→tagDevice、`send command`→createCommand、`register device`→addDevice ×5、`upgrade firmware`→OTA package/module、`create product`→createProduct、`configure forwarding`→routingFlowControlPolicy 全 CRUD…)。
- LLM 对无匹配 API 的 ~9 个 scenario(`delete tag`/`deploy plugin`/`reset credential`)诚实返 0 边,不伪造——bypass 放宽候选但 LLM 是合格守门人。
- dir-feature 层不受影响(strict 60 不变)。

**`unmapped` 语义随之扩展**:从"预筛 0 候选"扩展为"评过但 0 边"(预筛饿死 或 LLM 拒判),作为统一诚实空计数。early-return(有 feature 无 op)也返 `unmapped=len(features)`。

**成本权衡**:bypass 使每个 scenario 节点都调 1 次 LLM(56 次/本语料),换 92 条真实边。scenario 节点数有界(仅操作页产,变更甲限定),一次性 build 成本可接受。dir-feature 不付此成本(仍 strict)。未来优化:候选 max 得分=0(零重叠)时跳过 LLM,但当前 bypass 已验证且边数正确,先 ship 简单版。

## Risks / Trade-offs

- **gloss 质量是天花板**(同变更甲 Risks):gloss 不准则 prescreen 排序失准。但 bypass 下 LLM 见 top-N 仍能裁决正确项;gloss 只影响"对 op 是否进 top-N",影响召回上限,不影响已入候选的裁决正确性。
- **scenario 与 dir-feature 双层指向相近 API**:类目层(目录)与操作层(场景)可能都指向同一组 API。这是有意的两层;裁决 LLM 可在操作层建 `implemented_by`、类目层建更粗的关联,不冲突。
- **`unmapped` 不入报告**:本变更只让数据可得,不接入 GRAPH_REPORT。用户暂不可见。明确列为 follow-up,避免 skillgen 报告层 scope 膨胀。
- **bypass 增 LLM 调用量**:scenario 节点每节点 1 次 LLM 调用(含无匹配的诚实空调用)。scenario 数有界(操作页),可接受;若超大语料成本敏感,follow-up 加"max 得分 0 跳过"优化。

## Migration Plan

1. 纯加法 + 返回字段扩展。无 `capability` 的 feature 节点:`_feature_text` 不追加 gloss,`feat.get("capability")` 为 None → 行为与变更前逐字节一致。
2. 有 `capability` 的 scenario 节点:从"悬空"(0 候选、无边)变为"可链接"(gloss 进 bridge → 候选 → 边)。这是修 bug,不是 break。
3. `unmapped` 字段新增,`build()` 丢弃返回 → 无调用方受影响。
4. 无数据/配置迁移。

## Open Questions

- `unmapped` 何时接入 GRAPH_REPORT?暂不,列为 follow-up。接入需改 skillgen Step 5 报告 + `build` 传递摘要,独立变更。
- scenario 节点是否也刮 `.md` 正文英文词(双保险)?暂不(D2),gloss 即精炼替代;召回不足再扩。

## Why

`feature-api-linking` 现行的 feature 节点**唯一来源是产品文档的目录结构**(`generate_feature_nodes`,`feature_link.py:103`):每个直接含 `.md` 的目录→一个 feature 节点。这在真实语料(iotdm 130 篇 .md)上暴露两个问题:

1. **粒度太粗**:目录是产品能力的**类目层**("实例标签管理/"下 4 篇操作文档共用一个 feature 节点),而真正能和单个 API 方法 1:1 映射的是**操作级场景**("删除标签"、"添加标签")。类目粒度下,一个 feature 要对应一组 CRUD API,映射糊、evidence 空。
2. **目录结构不可靠**:扁平语料(根目录散置 .md)或目录缺失时,0 个 feature 节点,feature-link 直接早退,0 边。

更关键的是**跨语言缺口**(`feature-link-prescreen-language-gap` 记忆):`_prescreen` 用 `fuzz.token_set_ratio(feature_text, op_text)`,iotdm 文档纯中文、iotda API 路径纯英文,`_english_terms` 从中文正文刮不到英文路径段 → 36 feature 全部 0 候选 → LLM 从不被调用 → 0 边。

本变更**不替换目录来源,而是加一层操作级场景来源**:Part B 语义子代理(此刻就在用 Claude Code 订阅跑、读每篇 .md)顺带给每个操作级页面吐一个 `file_type:"feature"` 场景节点,带一个**英文 `capability` gloss**(如"删除标签"→`delete tag`)。这个 gloss 是跨语言桥——它让现有 fuzz prescreen 在英 gloss ↔ 英 op_text 上直接命中,无需嵌入模型、无需 API key、无需翻译 pass。

## What Changes

- Part B 语义抽取子代理 prompt 扩展:对每篇描述一个**离散产品操作**(用户在 UI 上执行的一个任务)的 `.md` 页面,在正常 concept 节点之外,**额外吐一个场景节点**:
  - `file_type: "feature"`(使其成为可被 `run_feature_linking` 链接的 feature 节点,与 `document` page 节点区分)
  - `scenario_kind: "operation"`(类目页/概述页/纯 UI 无 API 页 → 不吐,或标 `scenario_kind:"category"` 但不参与链接)
  - `capability: "<动词+名词英文 gloss>"`(如 `delete tag`、`create amqp queue`、`send command`)—— 跨语言桥的核心字段
  - `source_file`:该 `.md` 路径
  - `label`:操作的可读名(可用中文页面名)
  - 其余 concept/edges 抽取不变
- `generate_feature_nodes` **不改**:目录类目层保留(目录→feature 节点 + `contains`→page),Part B 操作级 feature 节点因不是 `_is_md_file_node` 而自然 passthrough,两层层级清晰(类目 contains→操作场景 implemented_by→API)
- `_is_md_file_node` 不改(Part B feature 节点 `file_type:"feature"` ≠ `"document"`,本就不被误当 page 节点)
- 抽取 prompt 的 JSON schema 扩展:`file_type` 合法值增 `feature`(仅当页面描述一个离散操作时),节点可选字段增 `capability`、`scenario_kind`

## Capabilities

### Modified Capabilities

- `feature-api-linking`:新增"从文档语义抽取生成操作级场景节点(带英文 capability gloss)"需求——feature 节点除目录来源外,可由 Part B 子代理从文档内容抽取,粒度为操作级,携带跨语言 gloss。既有"从功能文档目录结构生成功能节点"(类目层)保留不变。

### New Capabilities

(无)

## Impact

- 修改:`tools/skillgen/fragments/core/core.md`(Step 3 Part B 子代理 prompt:扩展 schema 说明 + 何时吐操作场景节点 + capability 字段),随之 `python -m tools.skillgen` regen 14 个 split 产物 + `--bless` + `--check`
- 修改:`references/extraction-spec.md`(若 Part B prompt 的 schema 权威定义在此,同步 `file_type:"feature"` + `capability` + `scenario_kind` 字段说明)
- 不变:`graphify/feature_link.py` 的 `generate_feature_nodes`/`_is_md_file_node`(passthrough 不需改);`run_feature_linking` 的链接逻辑(属变更乙)
- 不变:`graphify/llm.py`、`detect_backend()`
- 不变:默认行为(Part B 子代理若不吐 capability 节点,一切如旧——目录层照常工作,链接层零回归)
- 依赖:独立。变更乙(`add-scenario-api-linking-via-gloss`)依赖本变更产出 `capability` 字段才能跨语言命中
- 验证:重跑 Part B 子代理于 iotdm 语料,确认操作级页面产出带 `capability` 的 `file_type:"feature"` 节点;类目页/纯 UI 页不产

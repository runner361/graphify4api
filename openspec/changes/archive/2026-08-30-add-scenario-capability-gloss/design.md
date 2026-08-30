## Context

Part B 语义子代理(`tools/skillgen/fragments/core/core.md` Step 3 Part B)此刻对每篇 `.md` 抽取 concept 节点(`file_type:"document"`/`"rationale"`)。它**已经在读文档全文、已在跑**(用 Claude Code 订阅,与本环境一致)。本变更让它顺手多吐一个字段——`capability` 英文 gloss——把"这页描述什么产品操作"这个跨语言信号固化进节点,供 `run_feature_linking` 的 prescreen 在英↔英上命中。

这与目录来源**不冲突**:`generate_feature_nodes` 只对 `_is_md_file_node`(`file_type=="document"` 且 label=文件名)的 page 节点按目录分组建 dir-feature。Part B 吐的 `file_type:"feature"` 节点不是 page 节点,既不被 dir 逻辑误归组,也不会被重复建——它自然 passthrough,作为操作层与目录类目层共存。

## Goals

- 每个描述离散产品操作的 `.md` 页面 → 一个 `file_type:"feature"` 场景节点,带英文 `capability` gloss
- gloss 是动词+名词英文短语,语义贴近对应 API 资源/动作(如"删除标签"→`delete tag`,"消息下发"→`send message`),使现有 fuzz prescreen(英↔英 op_text)可命中
- 类目页/概述页/纯 UI 无 API 页不吐场景节点(或吐 `scenario_kind:"category"` 但不参与链接),避免类目粒度污染操作级映射
- 零新增 LLM pass:复用已在跑的 Part B 子代理;零新增依赖、零 key
- 默认零回归:子代理不吐 capability 时,目录层与链接层行为不变

## Non-Goals

- **不**改 `run_feature_linking` 的链接逻辑(用 gloss 做匹配属变更乙)
- **不**改 `generate_feature_nodes` / `_is_md_file_node`(passthrough 不需改)
- **不**引入嵌入模型 / 翻译 API / 任何新依赖
- **不**抽 UI 操作步骤(用户明确不要;`capability` 只是一个 gloss 短语,不是步骤列表)
- **不**做 op-vs-category 的显式分类 pass——是否操作由子代理在抽取时判断(吐或不吐场景节点),无 API 的页面在链接期(乙)由裁决 LLM 判空、不建边
- **不**改 aider/devin monolith fragments(同 `add-feature-link-backend` 的 Non-Goals,split-only)

## Decisions

### D1: 场景节点 `file_type:"feature"`,与 page 节点区分

Part B 对操作页**额外**吐一个 `file_type:"feature"` 节点,而非把 page 节点(`file_type:"document"`)retype。理由:
- page 节点是"文件"语义,被 `_is_md_file_node` 识别、被 dir-feature `contains` 挂载;retype 会破坏这两条
- 场景节点是"产品操作"语义,与文件本身是两个概念(一页文档描述一个操作),独立节点 + 同 `source_file` 隐式关联,语义清晰
- `run_feature_linking` 已按 `file_type=="feature"` 迭代,无需改迭代条件

### D2: `capability` 为英文动词+名词 gloss

格式:小写动词 + 名词短语,如 `delete tag`、`create amqp queue`、`send command`、`register device`。理由:
- 与 op_text(`POST /v5/iot/{project_id}/amqp-queues iot amqp-queues`)在英文词素上重叠 → fuzz `token_set_ratio` 命中
- gloss 是子代理读完整页后的一次跨语言概括,等价于嵌入模型要做的那次判断,但由已在跑的子代理顺带做
- 不要求 gloss 精确等于 op 路径段;只要求语义近到让 prescreen 进 top-N,精确裁决交给 LLM(乙)

### D3: 类目/概述/纯 UI 页不吐场景节点

子代理判断:页面描述一个离散、可映射到 API 的操作 → 吐 `scenario_kind:"operation"` 节点;页面是类目索引/概述/纯 UI 计费流程(如"购买实例"、"访问受限"、"实例管理"类目页)→ 不吐场景节点。理由:
- 避免类目粒度污染操作级 1:1 映射
- 无 API 的页面不吐场景节点,天然在链接期不建边(满足"无 API 不建边")

### D4: 复用 Part B,不加新 pass

`capability` 由 Part B 子代理在现有抽取调用内顺带产出,不新增 LLM 调用、不新增 pass。代价 = 子代理 prompt 略长 + 输出多几字段,边际成本近零。

### D5: 抽取 prompt schema 扩展点

在 Part B prompt 的 JSON schema 与规则段:合法 `file_type` 增 `feature`(仅操作页),节点可选字段增 `capability`、`scenario_kind`;并给判定规则(何为"离散操作")与 gloss 示例。改 `fragments/core/core.md` → skillgen regen 14 split 产物。

## Risks / Trade-offs

- **gloss 质量是天花板**:子代理 gloss 不准则 prescreen 仍 0 命中。缓解:gloss 只需进 top-N,不需精确;且乙的 LLM 裁决兜底。若大规模不准,后续可升级到嵌入(变更预留)。
- **节点数增加**:每个操作页多一个 feature 节点。dedup/clustering 已能处理 feature 节点(既有目录 feature 节点证明),无新机制。
- **prompt 复杂度**:Part B prompt 已较长,加规则可能影响子代理对其它字段的注意力。缓解:规则写紧凑、给正反例。
- **与目录层共存的语义重叠**:dir-feature(类目)与操作 feature 可能指向相近 API。这是有意的两层(类目 vs 操作),链接期乙可决定只在操作层建 `implemented_by`、类目层不建。

## Migration Plan

1. 纯加法。子代理不吐 `capability` 时,输出与变更前逐字节一致(目录层 + concept 节点不变)。
2. 吐了 `capability` 的场景节点:在乙落地前是"悬空"feature 节点(无链接边,因 `_feature_text` 还没读 gloss)——不破坏,只是暂时无边。
3. 无数据/配置迁移。

## Open Questions

- `capability` 是否需要多 gloss(一个操作映射多个资源)?暂定单 gloss,YAGNI;若 prescreen 召回不足再扩。
- 概述页"消息通信概述"是否吐 `scenario_kind:"category"` 节点参与类目层?暂不(目录层已覆盖类目),保持操作层纯净。

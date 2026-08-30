# feature-api-linking Specification

## Purpose
TBD - created by archiving change add-feature-api-linking. Update Purpose after archive.
## Requirements
### Requirement: 从功能文档目录结构生成功能节点
系统 SHALL 为功能文档路径下**每个直接包含说明文档的目录**(任意层级)生成一个 feature 节点(`file_type: feature`),并为目录内每个说明文档生成 功能节点到文档节点的 `contains` 边(EXTRACTED);直接含文档的目录之间的父子关系 SHALL 生成 `subfeature_of` 边(EXTRACTED);目录结构 MUST NOT 由 LLM 参与判定;根路径下的散置文档与空目录 MUST 不生成功能节点。

#### Scenario: 多级目录树生成多级功能节点
- **WHEN** 功能文档路径为三级树 `用户指南/消息通信/设备数据上报/`,`.md` 文档位于第三级目录
- **THEN** `设备数据上报` 等每个直接含文档的目录各生成一个 feature 节点,`消息通信` 一级生成其父功能节点,两者之间有 `subfeature_of` EXTRACTED 边

#### Scenario: 单级功能目录生成功能节点
- **WHEN** 功能文档根路径含子目录 `订单管理/` 与 `退款/`,各含 2 个 `.md` 文档
- **THEN** 图谱生成两个 feature 节点,每个节点有 2 条 `contains` EXTRACTED 边指向其目录内文档节点

#### Scenario: 散置文档与空目录
- **WHEN** 根路径下存在未入子目录的 `.md` 与一个空子目录
- **THEN** 散置文档按既有文档语义抽取处理但不挂任何功能节点,空目录被跳过并警告

### Requirement: 确定性候选预筛
在发起任何 LLM 调用前,系统 SHALL 用确定性匹配为每个功能节点生成候选清单:功能名、文档关键词(含文档正文中的英文技术词)、**以及操作级场景节点携带的英文 `capability` gloss**(变更甲产出)对 API 操作节点(路径资源段、HTTP 方法、tag)与实体节点(名称、推断列)做模糊匹配,每功能保留 top-N 候选(N 可配置,默认 20)。`capability` gloss 是跨语言桥信号:它使中文操作页的场景节点凭英文 gloss 与英文 API 路径/资源段在 fuzz `token_set_ratio` 上命中,无需嵌入模型或翻译 pass,无需正文含英文词。模糊匹配 SHALL 大小写不敏感(双侧小写化):HTTP 方法约定大写(`DELETE`/`POST`)、gloss 与路径段为小写,大小写敏感的 `token_set_ratio` 会使 `delete tag`(gloss)对 `DELETE ... tags`(op_text)得 34 分(< 最低阈值)而 0 命中,击垮跨语言桥;双侧小写后同一对标得 75 分,桥生效。无 `capability` 字段的 feature 节点(目录类目层 dir-feature、旧抽取产物)的预筛输入与变更前逐字节一致(零回归;小写化对既有"body-term 恰好大小写一致"的命中是严格改进,不破坏)。无任何候选达到最低阈值的功能 MUST NOT 发起 LLM 调用,且 SHALL 计入 `unmapped` 计数(诚实空:评过但无 API 映射,与"未处理"可区分)。降级路径(name-match ≥90)SHALL 同样双侧小写化。

#### Scenario: 候选有界
- **WHEN** 某功能预筛后有 35 个超过最低阈值的候选
- **THEN** 只保留得分前 20 个进入 LLM 裁决

#### Scenario: 无候选不调用 LLM
- **WHEN** 某功能的所有匹配得分均低于最低阈值
- **THEN** 不为该功能发起 LLM 调用,不生成关联边,`unmapped` 计数 +1

#### Scenario: 跨语言 gloss 桥命中候选(大小写不敏感)
- **WHEN** 一个 `file_type:"feature"` 操作场景节点 label 为中文"删除标签"、`capability:"delete tag"`,语料无中文-英文词典、正文无英文词,API 候选含 `DELETE /v5/iot/{project_id}/.../tags/{tag_id}`(op_text 含 `DELETE` 与 `tags`)
- **THEN** `_feature_text` 纳入 `capability` 经 `_english_terms` 进 prescreen 的 `bridge`,双侧小写后 `token_set_ratio("delete tag", "delete ... tags")` ≥ 最低阈值 → 该 API 进 top-N 候选 → 进入 LLM 裁决

#### Scenario: 无 capability 字段零回归
- **WHEN** 一个目录类目层 dir-feature 节点(无 `capability` 字段)进入预筛
- **THEN** `_feature_text` 不追加 gloss,预筛输入与变更前逐字节一致;小写化对既有命中严格保留(同形串小写后仍等)

### Requirement: LLM 语义裁决生成关联边
系统 SHALL 对候选清单发起 LLM 裁决,生成 功能 → API 操作 的 `implemented_by` 边与 功能 → 实体 的 `uses_entity` 边;所有边 MUST 为 INFERRED 并携带离散 confidence_score(0.95/0.85/0.75/0.65/0.55 档位)与必填的 evidence 属性(文档支撑句原文片段);LLM 返回的目标不在候选清单内、relation 不在白名单内、或置信分不在档位上的结果 MUST 被丢弃或降档;LLM 自评低于最低档位的候选 MUST 标记 AMBIGUOUS 并进入 GRAPH_REPORT.md。

#### Scenario: 强关联边生成
- **WHEN** "退款"功能文档描述退款单创建流程,候选含 `POST /refund-orders` 与实体 `refund_orders`
- **THEN** 生成 `implemented_by` 与 `uses_entity` INFERRED 边,confidence_score 为 0.95,evidence 为文档中的支撑句

#### Scenario: 幻觉目标被丢弃
- **WHEN** LLM 返回的某个 target_id 不在候选清单内
- **THEN** 该结果被丢弃,不生成边

#### Scenario: 无关候选不建边
- **WHEN** LLM 判定某候选与功能无关
- **THEN** 不为该候选生成任何边

#### Scenario: 低置信进人工复核
- **WHEN** LLM 对某候选的自评低于最低档位
- **THEN** 该候选生成 AMBIGUOUS 边并在 GRAPH_REPORT.md 中按功能分组展示

### Requirement: 无 LLM 后端时的降级路径
当无任何 LLM 后端可用时,系统 MUST NOT 报错中断:预筛得分 ≥90 的强匹配仍生成 `evidence: "name-match"`、confidence_score 0.65 的 INFERRED 边,GRAPH_REPORT.md MUST 明示这些边仅来自名称匹配、LLM 未参与;得分 <90 的候选不建边。

#### Scenario: 降级生成名称匹配边
- **WHEN** 未配置任何 LLM 后端,且某功能与 `GET /refunds` 的预筛得分为 95
- **THEN** 生成 `implemented_by` 边,evidence 为 `name-match`,置信 0.65,报告说明降级状态

### Requirement: 关联结果缓存与成本控制
系统 SHALL 按功能文档内容 hash 与候选清单 hash 的组合缓存 LLM 裁决结果;文档或候选清单任一变化时缓存失效重裁;两者均未变时重跑 MUST NOT 发起 LLM 调用;LLM 输入 MUST 限制在候选清单与受 token budget 约束的功能文档摘要内。

#### Scenario: 重跑零调用
- **WHEN** 功能文档与图谱候选清单均未变化,重新构建图谱
- **THEN** 关联边从缓存恢复,不发起任何 LLM 调用

#### Scenario: 新增接口触发重裁
- **WHEN** 语料新增一个 OpenAPI 规范文件,某功能的候选清单发生变化
- **THEN** 该功能的缓存失效并重新裁决

### Requirement: 功能维度的可查询性
功能节点及其关联边 MUST 可被 `graphify query`、`graphify path`、`graphify explain` 直接遍历,使"某功能涉及哪些 API 接口或数据库实体"成为无需额外工具的图谱查询;查询层 MUST NOT 为此变更。

#### Scenario: 查询功能涉及的接口
- **WHEN** 图谱构建完成后执行 `graphify query "退款功能涉及哪些 API 接口"`
- **THEN** 结果子图包含退款 feature 节点及其 `implemented_by` 边连接的操作节点

#### Scenario: explain 功能节点
- **WHEN** 执行 `graphify explain "退款"`
- **THEN** 输出包含该功能的 `implemented_by` 与 `uses_entity` 连接列表及各边 evidence

### Requirement: 从文档语义抽取生成操作级场景节点(带英文 capability gloss)
Part B 语义子代理 SHALL 为每篇描述一个**离散产品操作**(用户在 UI 上执行的单个任务,可映射到具体 API 方法)的 `.md` 页面,在正常 concept 节点之外,额外生成一个场景节点:`file_type: "feature"`、`scenario_kind: "operation"`、`capability: "<英文动词+名词 gloss>"`(如 `delete tag`、`create amqp queue`、`send command`)、`source_file` 指向该 `.md`、`label` 为操作可读名。类目索引页、概述页、纯 UI/计费/权限无 API 页 MUST NOT 生成操作场景节点。`capability` gloss 是跨语言桥信号——它使现有 fuzz prescreen 在英 gloss ↔ 英 op_text 上可命中,无需嵌入模型或翻译 pass。该场景节点与目录类目层(由 `generate_feature_nodes` 生成)`contains`→page 共存,不替换目录来源。子代理不吐 `capability` 时,行为与变更前一致(零回归)。

#### Scenario: 操作页生成带 gloss 的场景节点
- **WHEN** 一篇 `.md` 描述"删除标签"操作步骤,子代理判定其为离散操作
- **THEN** 产出一个 `file_type:"feature"` 节点,`scenario_kind:"operation"`,`capability` 形如 `delete tag`,`source_file` 指向该 `.md`

#### Scenario: 类目页不产场景节点
- **WHEN** 一篇 `.md` 是"实例管理"类目索引页或"消息通信概述"概述页
- **THEN** 不产出操作场景节点(目录层 dir-feature 已覆盖类目,操作层保持纯净)

#### Scenario: 无 API 的 UI 页不产场景节点
- **WHEN** 一篇 `.md` 描述"购买实例"(计费/UI 流)或"访问受限"(权限 UI),无可映射 API
- **THEN** 不产出操作场景节点,后续链接期不为其建边(无 API 不建边)

#### Scenario: 目录层与场景层共存不冲突
- **WHEN** "实例标签管理/"目录下 4 篇操作 `.md` 各产出一个操作场景节点,同时 `generate_feature_nodes` 仍为该目录生成一个 dir-feature 类目节点
- **THEN** 两层共存:dir-feature `contains`→4 个 page 节点;4 个操作场景节点独立 passthrough(因 `file_type:"feature"` 非 `_is_md_file_node`,不被目录逻辑重复归组)

#### Scenario: 子代理不吐 capability 时零回归
- **WHEN** 子代理未输出 `capability` 字段(旧 prompt 或不支持)
- **THEN** 无场景节点产生,目录层与既有链接逻辑行为与变更前逐字节一致

### Requirement: 显式裁决后端注入
`build()` 与 `run_feature_linking()` SHALL 接受一个显式后端名参数(`build()` 为 `feature_llm_backend: str | None`,`run_feature_linking()` 为 `llm_backend: str | None`),使 feature→API 裁决可走任意已注册后端(含 `claude-cli` 订阅鉴权后端),而不被 `detect_backend()` 的自动优先级表锁定为付费 key 后端或名称匹配降级;裁决 LLM callable 的解析优先级 MUST 为:显式 `llm_call` > 显式 `llm_backend`(经 `_call_llm(backend=…)` 包装)> 默认 `_default_llm_call`(`detect_backend`);`detect_backend()` MUST NOT 被本能力改动,`claude-cli` MUST 保持显式 opt-in、不进入自动优先级表。

#### Scenario: 显式指定 claude-cli 后端
- **WHEN** 调用 `build([ext_api, ext_product], feature_llm_backend="claude-cli", ...)` 且本机 `claude` 在 PATH
- **THEN** feature→API 裁决经 `claude -p` 子进程执行,产出的 `implemented_by`/`uses_entity` 边 evidence 为 LLM 裁决支撑句(非 `name-match`)

#### Scenario: 显式后端不可用时降级
- **WHEN** `feature_llm_backend="claude-cli"` 但本机 `claude` 不在 PATH 或 `claude -p` 返回空/异常
- **THEN** 该后端包装 callable 返回 None,系统走既有名称匹配降级路径(≥90 → INFERRED 0.65 evidence="name-match"),构建不中断,GRAPH_REPORT.md 明示降级状态

#### Scenario: 未指定后端保持原行为
- **WHEN** 调用 `build([...])` 未传 `feature_llm_backend`(即 None)
- **THEN** `run_feature_linking` 回落 `_default_llm_call` → `detect_backend()`,行为与变更前逐字节一致(有 key 则裁决,无 key 则名称匹配降级)

#### Scenario: 显式 llm_call 优先级最高
- **WHEN** 库级直接调用 `run_feature_linking(extraction, llm_call=my_callable, llm_backend="claude-cli")`
- **THEN** 使用显式 `llm_call`(`my_callable`),`llm_backend` 被忽略,既有 `llm_call` 注入契约不变

### Requirement: 操作场景节点预筛绕过
对携带 `capability` gloss 的操作场景节点(`file_type:"feature"` + `capability`),预筛 SHALL 退化为"仅排序不硬滤":对其使用 0.0 最低阈值,返回 top-N(按得分排序、不滤分),使候选总进入 LLM 语义裁决。理由:`token_set_ratio` 是 token 级精确匹配,无法桥接 (a) 动词词汇差(gloss `add`/`delete`/`send` vs API 名隐含动词,如 `tagDevice`/`createCommand`),(b) 名词单复数(`tag` vs `tags`),(c) camelCase 复合 API 名不分词(`tagDevice` 不分裂为 `tag`+`device`)。实测 `add tag` 对 `tagDevice` op 得 ~22 分(< 60 阈值),strict 阈值会饿死 LLM(全语料 strict 60 仅 7 条 feature→API 边);bypass 后 LLM 语义裁决产出 92 条边,且对无匹配 API 的场景(`delete tag`/`deploy plugin`/`reset credential` 约 9 个)诚实返 0。无 `capability` 字段的 feature 节点(dir-feature)SHALL 保持 strict 60 阈值(无 gloss,fuzz 是其唯一信号,阈值避免每 feature→全 op 淹没 LLM 调用)。`unmapped` 计数 SHALL 涵盖"评过但 0 边"的所有功能(预筛饿死 或 LLM 拒判),作为诚实空计数。

#### Scenario: 场景节点动词差仍达 LLM
- **WHEN** 一个 `capability:"add tag"` 场景节点,API 含 `POST /v5/iot/{project_id}/tags`(op 名 `tagDevice`,op_text 无 `add` token、`tag`≠`tags`),`token_set_ratio` 得 ~22 分
- **THEN** 该场景节点走 0.0 bypass 阈值,prescreen 仍返回该 op 进 top-N → LLM 裁决 `add tag`↔`tagDevice` 语义等价 → 产出 `implemented_by` 边

#### Scenario: 无匹配 API 诚实空
- **WHEN** 一个 `capability:"delete tag"` 场景节点,语料无"删除标签"API(仅有 `unbind-resource`)
- **THEN** bypass 给 LLM top-N 候选,LLM 裁决无匹配 → 0 边,`unmapped` +1,不伪造

#### Scenario: dir-feature 不走 bypass
- **WHEN** 一个无 `capability` 的 dir-feature 节点,其文本对某 op 得 30 分(< 60)
- **THEN** 该节点保持 strict 60 阈值,该 op 被滤掉;若 top-N 为空则 `unmapped` +1,不调 LLM


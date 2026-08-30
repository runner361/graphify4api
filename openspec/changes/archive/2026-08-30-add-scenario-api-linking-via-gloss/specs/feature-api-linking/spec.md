# feature-api-linking Specification

## MODIFIED Requirements

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

## ADDED Requirements

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

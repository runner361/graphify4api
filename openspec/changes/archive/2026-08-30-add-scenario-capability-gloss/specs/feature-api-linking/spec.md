# feature-api-linking Specification

## ADDED Requirements

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

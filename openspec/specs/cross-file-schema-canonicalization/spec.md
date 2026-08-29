# cross-file-schema-canonicalization Specification

## Purpose
TBD - created by archiving change add-cross-file-schema-canonicalization. Update Purpose after archive.
## Requirements
### Requirement: 跨文件合并同名 schema 副本

系统 SHALL 在构建层(合并后、实体反推前)跨文件按 `schema_name` 合并同名的 schema 节点副本为单一规范节点,使按端点拆分的规范文件不再把同一 schema 切成多个孤立节点。合并后属性 SHALL 取各副本属性的并集。

#### Scenario: 拆分语料的同名 schema 合并
- **WHEN** 同一逻辑 schema(如 `Device`)在多个 spec 文件中各自定义(产生多个同名 `schema_name` 的 schema 节点)
- **THEN** 系统 SHALL 将它们合并为一个规范节点,其 `properties` 为各副本属性的并集,副本节点 SHALL 被删除

#### Scenario: 属性互补合并
- **WHEN** 文件 A 的 `Device` 定义属性 `{id, name}`、文件 B 的 `Device` 定义属性 `{id, status}`,两者 `schema_name` 相同
- **THEN** 规范节点的 `properties` SHALL 为 `{id, name, status}` 的并集

#### Scenario: bundle 语料行为不变
- **WHEN** schema 仅在一个 spec 文件中定义(无同名副本)
- **THEN** 规范化 SHALL 为 no-op(节点与边不变)

### Requirement: 边重定向与去重

指向副本节点的边 SHALL 重定向到规范节点,重定向后产生的重复边 SHALL 按 (source, target, relation) 去重。边的置信标记与 `_origin` 戳记 SHALL 保留。

#### Scenario: references 与 contains 重定向
- **WHEN** 一条 `references` 边(op→schema 副本 或 schema 副本→schema 副本)或一条 `contains` 边(spec 根→schema 副本)的 target 或 source 指向将被删除的副本
- **THEN** 该端点 SHALL 替换为规范节点 id;重定向后若与已有边构成相同 (source, target, relation),则 SHALL 折叠为单条边(保留首条的置信与 context)

#### Scenario: schema→schema $ref 边去重
- **WHEN** 多个文件各自定义了同一条 schema→schema $ref 关系(如 `DeviceList`→`Device`)
- **THEN** 重定向后这些边 SHALL 折叠为 (规范 DeviceList, 规范 Device, references) 单条边

### Requirement: 规范化先于实体反推

schema 规范化 SHALL 在 `run_api_entity_inference` 之前运行,使实体反推的 schema 属性收集与 schema→schema $ref 证据消费合并后的规范节点。

#### Scenario: 实体反推吃到合并属性
- **WHEN** 某资源的操作引用的同名 schema 分布在多文件、各定义部分属性
- **THEN** 实体反推收集的 `inferred_columns` SHALL 包含合并并集后的全部属性(而非仅首个副本的属性)


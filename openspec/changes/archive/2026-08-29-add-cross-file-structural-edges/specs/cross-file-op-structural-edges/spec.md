## ADDED Requirements

### Requirement: 跨文件计算操作间结构边

系统 SHALL 在构建层（合并后、去重前）跨文件计算 OpenAPI 操作间的两类结构关系边，而非在抽取层按单文件计算。计算依据为全部合并后的 `api_operation` 节点，不再受单个 spec 文件内操作数限制。

#### Scenario: 拆分语料补齐 subpath_of 与 shares_schema_with
- **WHEN** 同一 API 的操作分布在多个 spec 文件中（每文件仅 1 个操作），且某嵌套路径操作（如 `/users/{id}/orders` 的 GET）与其父路径操作（`/users/{id}` 的 GET）位于不同文件
- **THEN** 构建层 SHALL 在两者之间产出 `subpath_of` 边（EXTRACTED，confidence_score 不写入），且不同文件中引用同名 schema 的操作之间 SHALL 产出 `shares_schema_with` 边（INFERRED，confidence_score = 0.95）

#### Scenario: bundle 语料行为不变
- **WHEN** 全部操作位于同一 spec 文件
- **THEN** 构建层跨文件计算的结果 SHALL 与原先抽取层 per-file 计算的边集合等价（同边类型、同端点、同置信语义）

### Requirement: subpath_of 置信与语义

`subpath_of` 边表示嵌套路径操作与其父路径操作的关系（`/users/{id}/orders` → `/users/{id}`）。该关系为规范内可直接观测的结构事实，系统 SHALL 将其标记为 EXTRACTED。

#### Scenario: 置信标记
- **WHEN** 构建层产出一条 `subpath_of` 边
- **THEN** 该边 SHALL 标记 `confidence` = `EXTRACTED`，且 SHALL NOT 写入 `confidence_score` 键，SHALL 写入 `_origin` = `ast`

#### Scenario: 父路径选择
- **WHEN** 嵌套路径的父路径存在同 HTTP 方法的操作
- **THEN** 边 target SHALL 指向该同方法父操作
- **WHEN** 父路径无同方法操作但存在其他方法的兄弟操作
- **THEN** 边 target SHALL 回退到该父路径的首个操作

### Requirement: shares_schema_with 置信与防护

`shares_schema_with` 边表示两个操作引用了同名 schema。该关系为相似性推理，系统 SHALL 将其标记为 INFERRED 且 confidence_score = 0.95。

#### Scenario: 置信标记
- **WHEN** 构建层产出一条 `shares_schema_with` 边
- **THEN** 该边 SHALL 标记 `confidence` = `INFERRED`、`confidence_score` = 0.95，SHALL 写入 `_origin` = `ast`，SHALL 在 context 中注明共享的 schema 名

#### Scenario: hub-schema 防护
- **WHEN** 某一 schema 名被超过 `_HUB_SCHEMA_OPS`（30）个操作引用
- **THEN** 系统 SHALL 跳过该 schema 的配对（避免 ErrorResponse 类公共 schema 产生无信号的全连接）

#### Scenario: 边数截断
- **WHEN** 累计产出的 `shares_schema_with` 边达到 `_MAX_SHARE_EDGES`（800）
- **THEN** 系统 SHALL 停止新增该类边，并在结果中标记被截断

### Requirement: 抽取层不再产出操作间结构边

抽取层 `extract_openapi` SHALL 不再产出 `subpath_of` 与 `shares_schema_with` 边；这两类边 SHALL 仅由构建层产出。抽取层 SHALL 继续产出 `references`、`grouped_under`、`contains` 边。

#### Scenario: 抽取层边集合
- **WHEN** 对单个 spec 文件运行 `extract_openapi`
- **THEN** 结果边集合 SHALL NOT 包含 `subpath_of` 或 `shares_schema_with` 边，SHALL 仍包含 `references`、`grouped_under`、`contains`（当规范中存在对应结构时）

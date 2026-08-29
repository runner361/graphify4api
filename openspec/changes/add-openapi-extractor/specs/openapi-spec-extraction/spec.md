## ADDED Requirements

### Requirement: 识别 OpenAPI/Swagger 规范文件
系统 SHALL 通过顶层键探测识别 OpenAPI 3.x 与 Swagger 2.0 规范文件:根对象存在值为字符串的 `openapi` 或 `swagger` 键,且存在 `paths` 对象键时,该 `.json` 文件 MUST 路由到 OpenAPI 抽取器;未命中的 `.json` 文件 MUST 保持既有处理路径(配置清单照常抽取,数据型 JSON 照常跳过)。

#### Scenario: OpenAPI 3.x 规范被识别
- **WHEN** 语料中存在根键为 `"openapi": "3.0.3"` 且含 `paths` 对象的 `.json` 文件
- **THEN** 该文件被 OpenAPI 抽取器处理,产出非空 nodes/edges

#### Scenario: Swagger 2.0 规范被识别
- **WHEN** 语料中存在根键为 `"swagger": "2.0"` 且含 `paths` 对象的 `.json` 文件
- **THEN** 该文件被 OpenAPI 抽取器处理,产出非空 nodes/edges

#### Scenario: 非规范 JSON 不受影响
- **WHEN** 语料中存在既不含 `openapi` 也不含 `swagger` 根键的 `.json` 文件(如 `package.json` 或数据 fixture)
- **THEN** 该文件走原有 `extract_json` 路径,行为与变更前完全一致

### Requirement: 抽取 API 操作节点
系统 SHALL 为规范中每个 `paths` 下的 path×method 组合创建一个节点,标签为 `METHOD /path` 形式(如 `GET /users`),并记录 `source_file` 与 `source_location`。

#### Scenario: 操作节点生成
- **WHEN** 规范含 `paths: {"/users": {"get": {...}, "post": {...}}}`
- **THEN** 图谱中生成标签分别为 `GET /users` 与 `POST /users` 的两个节点

### Requirement: 抽取 Schema 对象节点与 $ref 引用边
系统 SHALL 为 `components.schemas`(OpenAPI 3.x)或 `definitions`(Swagger 2.0)下的每个命名 schema 创建节点;当操作或 schema 通过 `$ref` 引用内部 schema 时,MUST 生成 `relation: references`、`confidence: EXTRACTED` 的边。

#### Scenario: $ref 生成 EXTRACTED 边
- **WHEN** `GET /users` 的响应 schema 为 `{"$ref": "#/components/schemas/User"}`
- **THEN** 生成 `GET /users` 节点到 `User` schema 节点的 `references` 边,confidence 为 EXTRACTED

#### Scenario: 两个规范版本的 schema 位置归一
- **WHEN** Swagger 2.0 规范将 schema 定义在 `definitions` 下
- **THEN** 抽取结果与定义在 `components/schemas` 下的 OpenAPI 3.x 规范结构一致

### Requirement: 抽取 Tag 分组关系
系统 SHALL 为操作声明的每个 tag 创建 tag 节点,并生成操作到 tag 的 `grouped_under` 边,confidence 为 EXTRACTED。

#### Scenario: tag 分组边生成
- **WHEN** `GET /users` 操作声明 `tags: ["admin"]`
- **THEN** 生成 `GET /users` 到 `admin` tag 节点的 `grouped_under` EXTRACTED 边

### Requirement: 抽取路径层级与共享 Schema 关系
系统 SHALL 生成两类结构性关系边:同前缀路径之间的 `subpath_of` 边(EXTRACTED);引用了相同 schema 的两个操作之间的 `shares_schema_with` 边(INFERRED,带 confidence_score)。

#### Scenario: 子路径层级边
- **WHEN** 规范同时含 `/users` 与 `/users/{id}` 路径
- **THEN** `GET /users/{id}` 操作与 `GET /users` 操作之间存在 `subpath_of` EXTRACTED 边

#### Scenario: 共享 schema 推断边
- **WHEN** `POST /users` 与 `GET /users/{id}` 都引用 schema `User`
- **THEN** 两操作节点之间存在 `shares_schema_with` INFERRED 边

### Requirement: 产出符合统一抽取 Schema 并具备大文件防护
抽取器输出 MUST 通过 `validate.py` 的 schema 校验(nodes 含 id/label/source_file/source_location,edges 含 source/target/relation/confidence);超过 20 MiB 的规范文件 MUST 跳过并在结果中携带 `error` 说明,不得产出部分结果。

#### Scenario: 输出可被 build 消费
- **WHEN** 对任一有效规范文件运行抽取
- **THEN** 结果 dict 可直接传入 `build_from_json` 而不触发 schema 校验错误

#### Scenario: 超大规范被跳过
- **WHEN** 规范文件超过 20 MiB
- **THEN** 返回空 nodes/edges 且含 `error` 字段说明原因

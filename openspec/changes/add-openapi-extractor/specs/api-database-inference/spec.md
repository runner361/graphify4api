## ADDED Requirements

### Requirement: 从规范反推数据库实体
系统 SHALL 在图构建阶段,仅依据 OpenAPI/Swagger 抽取产物反推后端可能的数据库实体:从 `paths` 的资源段提取实体候选(丢弃 `{param}` 参数段,`/users` 与 `/users/{id}` 归并为同一实体 `users`),并将该实体各操作引用的 schema 属性并集作为推断列;每个推断实体 MUST 生成带 `inferred` 标记的虚拟实体节点。此推断 MUST NOT 依赖语料中存在任何 SQL 来源。

#### Scenario: 同一资源的全套 CRUD 操作归并为一个实体
- **WHEN** 规范对 `users` 资源定义了 `GET /users`、`POST /users`、`GET /users/{id}`、`PUT /users/{id}`、`DELETE /users/{id}` 五个操作
- **THEN** 图谱中只生成一个 `users` 虚拟实体节点,五个操作节点分别通过 `reads_from`/`writes_to` 边连接到它,而不是每个操作各生成一个实体

#### Scenario: 属性并集构成推断列
- **WHEN** `GET /users` 响应 schema `User` 含 `id/name/email`,`POST /users` 请求 schema 含 `name/email/role`
- **THEN** `users` 实体的推断列为并集 `id/name/email/role`

#### Scenario: 无 schema 引用的资源仍生成实体
- **WHEN** 资源段对应的操作未引用任何 schema(无请求体/响应定义)
- **THEN** 该实体节点仍生成,仅含名称,不携带推断列

#### Scenario: 无 SQL 语料下推断独立成立
- **WHEN** 语料只含 OpenAPI 规范 JSON 文件,不含任何 `.sql` 文件
- **THEN** 图谱中仍产出完整的虚拟实体、实体间关系与操作读写边

### Requirement: 实体间关系推断
系统 SHALL 生成两类实体间关系边:路径嵌套关系(`/users/{id}/orders` → `orders` 对 `users` 的 `belongs_to` 边);schema 属性引用关系(某实体 schema 的属性通过 `$ref` 引用另一实体 schema 时,生成两实体间的引用边);两类证据同时存在时 MUST 合并为一条边并标注双来源;所有实体间关系边 MUST 为 INFERRED 并携带 confidence_score。

#### Scenario: 嵌套路径生成 belongs_to
- **WHEN** 规范含路径 `/users/{id}/orders`
- **THEN** 生成 `orders` 到 `users` 的 `belongs_to` INFERRED 边

#### Scenario: $ref 属性生成实体引用
- **WHEN** `Order` schema 的属性 `user` 为 `{"$ref": "#/components/schemas/User"}`
- **THEN** 生成 `orders` 实体到 `users` 实体的引用边

#### Scenario: 双证据合并
- **WHEN** 同一对实体同时存在嵌套路径与 `$ref` 属性两类证据
- **THEN** 只保留一条关系边,并标注两个来源

### Requirement: 操作到实体的读写边
系统 SHALL 为每个 API 操作生成其资源实体上的语义边:GET 操作生成 `reads_from` 边;POST、PUT、PATCH、DELETE 操作生成 `writes_to` 边;边 MUST 为 INFERRED 并携带 confidence_score。

#### Scenario: 读操作连接实体
- **WHEN** 规范含 `GET /users`
- **THEN** `GET /users` 操作节点与 `users` 虚拟实体之间存在 `reads_from` INFERRED 边

#### Scenario: 写操作连接实体
- **WHEN** 规范含 `POST /users`
- **THEN** `POST /users` 操作节点与 `users` 虚拟实体之间存在 `writes_to` INFERRED 边

### Requirement: 诚实标记与可追溯
虚拟实体节点 MUST 携带可区分真实表节点的标记(`inferred` 属性或等价机制),使 GRAPH_REPORT.md 与图查询能够区分"推导出的"与"读到的"结构;所有推断边 MUST 携带 `source_file` 与 `confidence_score`,并 MUST 可被 `graphify query`/`path`/`explain` 直接遍历。

#### Scenario: 报告可区分推断实体
- **WHEN** 图谱同时含虚拟实体与(若存在的)真实 SQL 表节点
- **THEN** GRAPH_REPORT.md 中两者可明确区分

#### Scenario: query 可遍历推断结构
- **WHEN** 图谱构建完成后执行 `graphify query "what database entities does the API write to"`
- **THEN** 结果子图包含经 `writes_to` 边连接到虚拟实体的操作节点

### Requirement: 与真实数据库结构的对账
当语料同时含 OpenAPI 规范与 SQL DDL 来源(`.sql` 文件或 `--postgres` 内省)时,系统 SHALL 将虚拟实体与 `extract_sql` 产出的真实表节点按名称(含单复数归一)匹配并合并:真实表节点的身份 MUST 保留,虚拟实体独有的推断列以补充信息附加;未匹配到真实表的虚拟实体保持独立存在。

#### Scenario: 真实表存在时合并
- **WHEN** 语料含 `users` 虚拟实体(推断列 id/name)与 `CREATE TABLE users (id, name, created_at)` 的表节点
- **THEN** 两节点合并为一个,保留真实表身份,`created_at` 等真实列完整保留,虚拟独有的列以推断补充信息标注

#### Scenario: 虚拟实体未匹配到真实表
- **WHEN** 某虚拟实体在 SQL 来源中无对应表
- **THEN** 该虚拟实体节点保留,推断标记不变

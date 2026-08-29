## 1. 前置决策与骨架

- [x] 1.1 解决 design 开放问题:确认两个新 file_type(`api_operation` 操作节点、`inferred_entity` 虚拟实体)进入 `validate.py` 合法枚举,并确认 `_minhash`、manifest、HTML 可视化对未知 file_type 的容错;确认推断列以实体节点属性存储(与 sql.py 列表示方式对齐,实现时核实其列表示法)
- [x] 1.2 创建 `graphify/extractors/openapi.py` 模块骨架:`extract_openapi(path: Path) -> dict`,含 20 MiB 有界读、`json.loads` 解析、顶层键探测函数 `_is_openapi_spec(doc)`(`openapi`/`swagger` 为字符串且 `paths` 为 dict),非规范返回 `{"nodes": [], "edges": [], "skipped": "not an openapi spec"}`

## 2. 节点与 EXTRACTED 边抽取

- [x] 2.1 实现 Swagger 2.0 / OpenAPI 3.x 归一化:统一 `definitions` ↔ `components/schemas`、`basePath` 前缀处理,输出内部表示(schemas dict、paths dict)
- [x] 2.2 实现操作节点抽取:遍历 `paths` × HTTP 方法(get/post/put/patch/delete/options/head),生成 `<stem>_op_<method>_<path>` 节点(`file_type: api_operation`),标签 `METHOD /path`,记录 source_file/source_location;忽略 `parameters`/`summary` 等非方法键
- [x] 2.3 实现 schema 节点与内部 `$ref` 边:命名 schema 生成 `<stem>_schema_<name>` 节点;`#/components/schemas/X`、`#/definitions/X` 形态的 `$ref`(含 requestBody/responses/嵌套属性中的递归出现)生成 `references` EXTRACTED 边;外部 URL `$ref` 生成 `ref_` 前缀概念节点
- [x] 2.4 实现 tag 节点与 `grouped_under` EXTRACTED 边;实现路径层级 `subpath_of` 边(`/users/{id}` → `/users`)
- [x] 2.5 实现 `shares_schema_with` INFERRED 边:引用同一 schema 的操作对,confidence_score 取 0.95(直接结构证据)

## 3. 派发表接入

- [x] 3.1 在 `graphify/extract.py` 的 `.json` 分派处、`extract_json` 调用之前插入 openapi 探测:命中走 `extract_openapi`,未命中原样回落;确认 mcp 配置(`mcp.json` 等)与配置清单路径不受影响
- [x] 3.2 在 `graphify/extractors/__init__.py` re-export `extract_openapi`;确认 `detect.py`/`watch.py` 无需改动(`.json` 已在 CODE_EXTENSIONS 与 _WATCHED_EXTENSIONS)

## 4. 虚拟数据库实体反推(核心,build 阶段)

- [x] 4.1 在 `graphify/build.py`(或其调用的合并流程)新增反推步骤入口:仅收集 openapi 来源的操作/schema 产物,不依赖任何 SQL 来源在场
- [x] 4.2 实现资源提取与实体归并:路径按 `/` 分段、丢弃 `{param}` 段;同一资源的全套 CRUD 操作归并为**一个**虚拟实体节点(`<stem>_entity_<resource>`,`file_type: inferred_entity`,标签 `<resource> (inferred)`);含动词段或 RPC 式路径跳过实体推断但保留操作节点
- [x] 4.3 实现属性聚合:按"实体→操作→引用 schema"链路聚合属性并集为推断列(存为实体节点属性),每列记录读侧(响应)/写侧(请求体)来源;含数组 `$ref` 解包;无 schema 引用的实体仅含名称
- [x] 4.4 实体间 ER 关系:嵌套路径生成 `belongs_to`(子→父,INFERRED 0.85);实体 schema 属性 `$ref` 指向另一实体 schema 生成实体引用边(INFERRED 0.85);双证据并存合并为一条边并标注双来源(0.95)
- [x] 4.5 操作→实体读写边:GET → `reads_from`,POST/PUT/PATCH/DELETE → `writes_to`,INFERRED 0.95,携带 source_file 与 confidence_score
- [x] 4.6 诚实标记落地:`inferred_entity` file_type + `inferred: true` 节点属性;确认 GRAPH_REPORT.md 与 graph.json 输出中可区分虚拟实体与真实结构

## 5. 与真实 DDL 的对账(次要)

- [x] 5.1 实现(仅当语料含 `.sql`/`--postgres` 表节点时):资源名与表名匹配(单复数归一精确比对优先,rapidfuzz `token_set_ratio` ≥90 兜底);合并保留真实表节点 ID 与真实列,虚拟独有列附加为 `inferred_columns`;未匹配的虚拟实体原样保留,不产生 AMBIGUOUS 噪声边

## 6. 测试

- [x] 6.1 新增 fixtures:`tests/fixtures/openapi/openapi3-petstore.json`(含 $ref、tags、嵌套路径 `/users/{id}/orders`、全套 CRUD)与 `tests/fixtures/openapi/swagger2-minimal.json`(definitions 形态);真实语料 `tests/opeapi/merged_swagger.json`(≈1.05 MiB,超旧 1 MiB 上限的实例)用于集成验证
- [x] 6.2 `tests/test_languages.py` 新增规范抽取用例:规范识别与回落、操作/schema/tag 节点、$ref EXTRACTED 边、shares_schema_with、subpath_of、两版本归一一致
- [x] 6.3 新增反推用例(核心场景,**语料无任何 SQL 文件**):五个 CRUD 操作归并为单实体、属性并集与读写侧来源、belongs_to 嵌套关系、$ref 实体引用边、inferred 标记、无 schema 引用资源仅含名称、RPC 式路径不产生实体
- [x] 6.4 新增对账用例:同语料加入 `CREATE TABLE` fixture 后虚拟实体与真实表合并、真表身份保留、`inferred_columns` 附加、未匹配实体保留
- [x] 6.5 跑全量回归 `uv run pytest tests/ -q`,确认无既有用例破坏
- [x] 6.6 集成验证:以 `tests/opeapi/merged_swagger.json` 为语料构建图谱,产出写入 `tests/api-graph/`(graph.json、GRAPH_REPORT.md),人工抽查实体反推与边质量

## 7. 文档

- [x] 7.1 更新 `ARCHITECTURE.md` 模块表:登记 `openapi.py` 入口与输入输出(该文档受 `tests/test_architecture_doc.py` 约束,所引符号必须真实存在)
- [x] 7.2 更新 `README.md` 文件类型表:JSON 行注明 OpenAPI/Swagger 规范会被解析并反推数据库实体;`docs/how-it-works.md` 补充反推一节

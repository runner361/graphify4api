## Why

graphify 目前把 OpenAPI/Swagger 规范文件当作"数据型 JSON"跳过(`graphify/extractors/json_config.py` 的 #1224 策略:配置门禁不识别 `openapi`/`swagger` 顶层键,返回空结果)。同时 `.json` 在 `detect.py` 中归类为代码文件,语义通道(LLM pass)也看不到它——结果是 API 规范文件入图后产出为零。

目标语料形态:**只有 OpenAPI/Swagger JSON,没有 `.sql` 文件**。核心需求是纯从 API 规范反推后端可能的数据库实体——多个 CRUD 操作归并为一个数据实体节点,构成可查询的 ER 级数据模型图谱;这类信息全部可从规范确定性导出,不需要 LLM。

## What Changes

- 新增 `graphify/extractors/openapi.py`:`extract_openapi(path) -> dict`,按顶层键探测识别 OpenAPI 3.x / Swagger 2.0 规范
- 抽取节点:API 操作节点(`GET /users`)、schema 对象节点、tag 节点、path 节点
- 生成 `EXTRACTED` 边:`references`($ref 显式引用)、`grouped_under`(tag)、`subpath_of`(路径层级);`INFERRED` 边:`shares_schema_with`(两操作共用 schema)
- **反推虚拟数据库实体(核心)**:路径资源段 → 实体候选(`/users`、`/users/{id}`、其全部 CRUD 操作 → 一个 `users` 实体节点);各操作引用的 schema 属性并集 → 推断列;实体节点携带 `inferred` 诚实标记,不依赖任何 SQL 来源
- **实体间 ER 关系**:路径嵌套 → `belongs_to`(`/users/{id}/orders` → orders belongs_to users);schema 属性 `$ref` → 实体引用边;双证据合并
- **操作→实体读写边**:GET → `reads_from`,POST/PUT/PATCH/DELETE → `writes_to`(INFERRED + confidence_score)
- (次要)语料出现真实 DDL 时,虚拟实体与 `extract_sql` 表节点对账合并(真表优先,虚拟列作补充)
- `extract.py` 的 `.json` 派发表在通用 `extract_json` 之前插入 openapi 探测(仿照 mcp_ingest 模式)
- 新增 `tests/fixtures/` 样例规范与 `tests/test_languages.py` 用例

## Capabilities

### New Capabilities
- `openapi-spec-extraction`: 解析 OpenAPI/Swagger JSON 规范文件,产出 API 操作、schema、tag、path 节点及规范内显式声明的关系($ref、tag 分组、路径层级),全部为 EXTRACTED 置信级
- `api-database-inference`: 纯从规范反推后端数据库实体——CRUD 操作按资源归并为实体节点、schema 属性并集为推断列、嵌套路径与 $ref 为实体间 ER 关系、按 HTTP 方法生成读写边;全部带 inferred 诚实标记与 INFERRED 置信;语料含真实 DDL 时与表节点对账合并

### Modified Capabilities

(无——`openspec/specs/` 当前为空,不存在需要修改的既有能力规范)

## Impact

- 新增:`graphify/extractors/openapi.py`
- 修改:`graphify/extract.py`(`.json` 派发表插入 openapi 探测)、`graphify/extractors/__init__.py`(re-export)
- 修改:`graphify/build.py` 或其调用的合并流程(实体反推步骤:资源归并、属性聚合、ER 关系、读写边;对账逻辑)
- 修改:`graphify/validate.py`(file_type 枚举扩展:`api_operation`、`inferred_entity`)
- 测试:`tests/fixtures/openapi/` 样例、`tests/test_languages.py` 新用例(含无 SQL 纯规范语料的核心场景)
- 依赖:无新增(rapidfuzz 已是核心依赖,仅对账使用;tree-sitter-json 已在核心依赖)
- 不变更:数据型 JSON 跳过策略对非规范 JSON 继续生效;`.json` 的 detect 分类保持 code 不动

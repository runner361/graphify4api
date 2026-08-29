## Context

graphify 的 JSON 处理现状:`.json` 在 `detect.py` 归类为 code,AST 通道派发给 `graphify/extractors/json_config.py::extract_json`;该函数用 `_is_config_json` 门禁(文件名白名单 + 顶层键探测)只认配置清单,其余按"数据型 JSON"跳过(#1224,防止孤儿键节点)。OpenAPI/Swagger 规范的顶层键不命中门禁,产出为零;语义通道只收 docs/papers/images,也看不到它。

**目标语料形态(用户明确的前提):语料中没有 `.sql` 文件,只有 OpenAPI/Swagger JSON。**核心需求是纯从规范反推后端可能的数据库实体(实体、列、实体间关系),SQL 对账仅在语料后续出现 DDL 时作为次要能力参与。

可复用的既有设施:`extractors/base.py` 的 `_make_id`/`_file_stem` ID 约定;`mcp_ingest.py` 的"特定 JSON schema 一等公民抽取"先例;`extractors/sql.py` 的表/列/外键抽取(对账时的真实表来源);`resolution.py` 跨文件解析层;`dedup.py` 去重合并;`validate.py` 产出 schema 校验;rapidfuzz 核心依赖(仅对账使用)。

约束:遵循项目"代码抽取零 API 成本、全部本地"哲学;产出必须符合统一抽取 schema(EXTRACTED|INFERRED|AMBIGUOUS + confidence_score);ARCHITECTURE.md 五步扩展配方;`test_architecture_doc.py` 校验文档与代码一致。

## Goals / Non-Goals

**Goals:**
- OpenAPI 3.x 与 Swagger 2.0 的 `.json` 规范文件产出非空图谱:操作、schema、tag、path 节点
- 规范内显式关系($ref、tag、路径层级)以 EXTRACTED 入图
- **纯从规范反推虚拟数据库实体**:资源段→实体、schema 属性并集→推断列、路径嵌套与 $ref→实体间 ER 关系,无需任何 SQL 来源在场
- 操作→实体的读写边(GET→reads_from,写方法→writes_to,INFERRED)
- 推断产物带诚实标记(inferred),与真实结构可区分、可查询
- (次要)语料出现真实 DDL 时,虚拟实体与真实表对账合并
- 不破坏现有 `.json` 处理:配置清单照旧,数据型 JSON 照旧跳过

**Non-Goals:**
- 列类型/主键/索引/约束推断(列名级别已够图谱使用,类型推断噪声过大)
- YAML 格式规范;跨文件外部 `$ref` 解析
- LLM tiebreaker;从源代码框架装饰器抽路由
- OpenAPI 3.1 JSON Schema 全量保真
- 非 REST 风格路径(`/api/v1/getUserInfo` 这类 RPC 式路径)的实体反推——操作节点照常生成,但跳过实体推断

## Decisions

**D1 识别方式:顶层键探测,而非文件名白名单。**
`openapi`(string 版本号)或 `swagger`(string)在根,且 `paths` 为 object 即判定为规范文件。备选:文件名白名单——被否,真实语料中规范文件名五花八门,顶层键是规范自带的、零误报的判别特征(与 `_is_config_json` 键探测同一思路)。

**D2 解析方式:`json.loads` 字典遍历,而非 tree-sitter pair-walk。**
OpenAPI 语义结构深,按 key 语义取值才是正道;tree-sitter walk 恰会复现 #1224 要防的孤儿键节点爆炸。有界读防护沿用 json_config 的模式,但上限独立设定为 **20 MiB**(不跟随其 1 MiB:真实多服务合并规范可达兆级,`tests/opeapi/merged_swagger.json` ≈1.05 MiB 已超旧限),超限返回 `error`。

**D3 节点 ID 命名空间:全部以文件 stem 前缀,防 J-4 类碰撞。**
`<stem>_op_get_users`、`<stem>_schema_user`、`<stem>_tag_admin`、`<stem>_path_users`;虚拟实体统一 `<stem>_entity_<resource>`。外部 URL `$ref` 一律 `ref_` 前缀概念节点(既有约定)。同一符号多处出现时靠 `dedup.py` 事后合并,抽取器不做全局决策。

**D4 实体反推在 build/merge 阶段执行,仅依赖 openapi 抽取产物。**
反推需要跨操作(同资源出现在多条路径)甚至跨文件(同域多个 spec 文件)的聚合视野,单文件抽取器做不到;且需与 dedup/hyperedge 的 remap 时序衔接。SQL 缺席是常态而非边界:推断的输入只有 openapi extractions,`extract_sql` 产物仅在对账(D7)时参与。备选:抽取器内直接生成实体——被否,视野不足且时序冲突。

**D5 反推算法三步(确定性,零 LLM):**
1. **资源提取**:路径按 `/` 分段,丢弃 `{param}` 段;剩余资源段为实体候选,相邻资源对构成嵌套关系候选(`/users/{id}/orders` → 实体 `users`、`orders`,嵌套对 orders→users)。含动词段或单段 RPC 式路径不参与实体推断(Non-Goal),但操作节点照常生成。
2. **属性聚合**:对每个实体,聚合其全部操作引用的 schema(requestBody、responses,含数组解包 `$ref` 指向同一 schema)的属性并集;每列记录读侧/写侧来源(响应=读侧、请求体=写侧),并集即为推断列。
3. **关系推断**:嵌套路径 → `belongs_to`(子→父,INFERRED 0.85);实体 schema 属性值为指向另一实体 schema 的 `$ref` → 实体引用边(INFERRED 0.85,"外键语义"是推断,不是规范陈述);两类证据并存 → 合并为一条边,标注双来源,confidence 提升至 0.95。

**D6 置信语义:推断的"存在性"落在节点标记上,边的置信描述关系本身。**
虚拟实体节点携带 `inferred: true` 属性与带后缀的标签(`users (inferred)`),file_type 采用新枚举 `inferred_entity`——这是"该实体是否真实存在于后端"这一假设的载体。op→实体边为 INFERRED 0.95:路径显式命名了资源,"操作触及该资源"近乎事实,而"资源是持久化实体"的假设由节点标记承担。这样审计链清晰:边说关系,节点说假设。备选:全部标 AMBIGUOUS——被否,会把这些边逐出主图谱语义,与 reads_from/writes_to 既有语义不符。

**D7 对账策略(次要):真表优先,虚拟列作补充。**
真实表存在时,按资源名与表名匹配(单复数归一直接比对,残余歧义用 rapidfuzz `token_set_ratio` ≥90 兜底);合并保留真实表节点 ID 与全部真实列,虚拟独有列附加为 `inferred_columns` 属性;未匹配的虚拟实体原样保留。对账失败不产生任何 AMBIGUOUS 边(避免噪声),仅在实体节点属性中记录未确认状态。

**D8 派发表插入点:`.json` 分支内、`extract_json` 之前。**
先做 D1 键探测(有界读头部),命中走 `extract_openapi`,未命中原样回落。`detect.py`/`watch.py` 均已含 `.json`,零改动。

## Risks / Trade-offs

- [反推实体是假设而非事实(API 可能是聚合接口、无持久层、一个实体跨多表)] → D6 的 inferred 标记 + GRAPH_REPORT.md 显著区分;列不进 file_type=code 主语义
- [非 REST 路径污染实体提取(`/api/v1/getUserInfo`)] → D5.1 显式跳过非类 REST 路径的实体推断,操作节点不受影响
- [属性并集过度扩张(不同接口复用同名 schema 却属不同域)] → 并集按"实体→操作→schema"链路聚合,不按 schema 全局并;列级别噪声由 inferred 标记兜底
- [大规范超 20 MiB 被跳过] → 上限为独立常量(默认 20 MiB,覆盖 `tests/opeapi` 真实语料);超限返回 `error` 字段;后续可加环境变量调整
- [Swagger 2.0 与 OpenAPI 3.x 结构差异(`definitions` vs `components/schemas`)] → 抽取器内归一化到统一内部表示;fixtures 各放一份
- [规范与代码同时定义路由导致重复] → D3 命名空间隔离 + `dedup.py` 兜底
- [对账误合并(通用名 `users` 匹配到无关库表)] → D7 双重门控:精确归一匹配优先,rapidfuzz 兜底阈值 90,合并仅发生在语料同时含两来源时

## Migration Plan

纯新增能力,无存量行为变更:新增模块 + 派发表插入一行探测 + build 阶段反推步骤。回滚 = 删派发表探测调用与 build 反推调用,`.json` 处理回到现状。`graphify-out/` 缓存按内容 hash 失效,规范文件自动重抽。

## Open Questions

- `inferred_entity` 作为新 file_type 需同步扩展 `validate.py` 合法枚举,并确认 `_minhash`/manifest/HTML 可视化对未知 file_type 的容错——tasks 首项验证。
- 推断列是否需要细粒度到"每列一个节点"(可查询"哪些实体有 email 字段")vs 仅作实体节点属性(轻量)?初版选属性(与 sql.py 列表示方式对齐,实现时确认),后续可演进。

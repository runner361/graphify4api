## 1. 构建层 schema 规范化函数

- [x] 1.1 在 `graphify/api_inference.py` 新增 `run_api_schema_canonicalization(extraction)`:遍历节点,按 `schema_name`(仅 `openapi_kind=="schema"` 且有非空 name)分组,识别 >1 副本的组
- [x] 1.2 每组选规范节点(`properties` 最长者,平手取首个),其余副本 `properties` 并入规范节点属性并集;建立 `copy_id -> canonical_id` 重定向映射;副本标记待删
- [x] 1.3 边重定向:遍历 `extraction["edges"]`,凡 source/target 命中副本 id 则替换为规范 id;重定向后按 (source, target, relation) 去重(保留首条,丢弃重复),保留置信/confidence_score/context/`_origin`
- [x] 1.4 删除副本节点(`extraction["nodes"]` 过滤);返回 summary(合并组数、删除节点数、折叠边数)

## 2. 接入构建流水线

- [x] 2.1 `graphify/build.py` 合并后、`run_api_entity_inference` 之前调用 `run_api_schema_canonicalization(combined)`
- [x] 2.2 确认 `run_api_entity_inference` 的 `schema_props`/`schema_ref_pairs` 收集在规范化后吃到合并属性与去重 $ref 图(无需改 inference 内部,验证即可)

## 3. 测试

- [x] 3.1 `tests/test_api_inference.py` 新增 `test_cross_file_schema_canonicalization`:两文件各定义同名 `Device`(A={id,name}、B={id,status}),extract 两文件合并 → `run_api_schema_canonicalization` → 断言只剩 1 个 `Device` 节点、`properties` 为并集 `{id,name,status}`、副本节点消失
- [x] 3.2 同测试断言边重定向:指向副本的 `references`/`contains` 边重定向到规范节点,重复的 schema→schema $ref 边折叠为单条
- [x] 3.3 新增 `test_canonicalization_bundle_is_noop`:单文件无副本 → 节点/边不变

## 4. 文档与验证

- [x] 4.1 `docs/how-it-works.md` OpenAPI 段补注:构建层跨文件按 `schema_name` 合并同名 schema 副本(属性并集、边重定向),拆分语料不再产生孤立同名节点
- [x] 4.2 跑 `python -m pytest tests/test_api_inference.py tests/test_languages.py -k "openapi or api_inference or schema or canonical" -q` 全绿(13+7 passed)
- [x] 4.3 跑 `python -m pytest tests/test_extract.py tests/test_mcp_ingest.py -q` 确认 dispatch 契约无回归(45 失败全为 tree-sitter bash/json 文法缺失的基线环境失败,0 回归;180 passed)
- [x] 4.4 corpus 对比:IoTDA 173-op 拆分/合并语料 fixtures 已不在本 worktree(仅 3 个小 fixture),无法重跑精确数字;机制由 `test_cross_file_schema_canonicalization`(属性并集+边重定向+$ref 折叠+副本删除)与 `test_canonicalization_bundle_is_noop`(bundle no-op)+ build-tier 冒烟(petstore 合并 fixture:规范化 0/0/0,实体数不变)覆盖验证

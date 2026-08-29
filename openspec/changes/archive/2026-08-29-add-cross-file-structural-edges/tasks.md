## 1. 抽取层移除 per-file 结构边生成

- [x] 1.1 在 `graphify/extractors/openapi.py` 删除 `subpath_of` 生成块（`parent_path` 内嵌函数 + 循环）与 `shares_schema_with` 配对块
- [x] 1.2 删除仅服务上述两块、别处不用的 per-file 索引：`paths`、`first_op_by_pm`、`op_ids_by_path`、`ops_by_schema`（保留 `op_records`，tags 块仍用）
- [x] 1.3 删除常量 `_MAX_SHARE_EDGES`、`_HUB_SCHEMA_OPS`（将迁入 api_inference.py）；更新模块 docstring（10-11 行）注明两类边现由构建层跨文件计算

## 2. 构建层新增跨文件结构边

- [x] 2.1 在 `graphify/api_inference.py` 新增常量 `_MAX_SHARE_EDGES = 800`、`_HUB_SCHEMA_OPS = 30`（保留 ErrorResponse hub 注释）
- [x] 2.2 扩展 `_edge` helper：加 `confidence="INFERRED"` 与 `score=0.95` 参数；当 `confidence == "EXTRACTED"` 时不写 `confidence_score` 键（与抽取层 `add_edge` 契约一致），保留 `_origin: "ast"` 戳记
- [x] 2.3 新增 `_infer_op_structural_edges(op_nodes, _edge)`：从 op 节点构建全局 `paths`/`first_op_by_pm`/`op_ids_by_path`/`ops_by_schema`（按 schema 名聚合 refs_read+refs_write）；搬入 `parent_path` 剥尾段回溯逻辑；产出 `subpath_of`（EXTRACTED，同方法优先、回退兄弟首个）与 `shares_schema_with`（INFERRED 0.95，带 hub 上限 + 截断防护）
- [x] 2.4 在 `run_api_entity_inference` 收集 `op_nodes` 之后调用 `_infer_op_structural_edges`，边数计入 `summary["edges"]`

## 3. 测试调整

- [x] 3.1 `tests/test_languages.py` `test_openapi_grouped_under_and_subpath_of`：`grouped_under` 断言保留；`subpath_of` 改为对 `extract_openapi(OPENAPI3)` 结果跑 `run_api_entity_inference` 后断言，保留 EXTRACTED 置信断言
- [x] 3.2 `tests/test_languages.py` `test_openapi_shares_schema_with_inferred_095`：改为跑 inference 后断言 INFERRED 0.95 + "shared schema" context
- [x] 3.3 `tests/test_languages.py` `test_swagger2_normalization_matches_openapi3_products`：对 r 跑 inference 后再断言 `{references, grouped_under, subpath_of, shares_schema_with, contains} <= _relations`
- [x] 3.4 `tests/test_api_inference.py` 新增 `test_cross_file_subpath_and_shares_schema`：构造两拆分 spec 文件（A 含 `/users` GET/POST，B 含 `/users/{id}/orders` GET 且共享 `User` schema），extract 两文件 → 合并 → `run_api_entity_inference` → 断言跨文件 subpath_of 边与 shares_schema_with 边均出现

## 4. 文档与验证

- [x] 4.1 `docs/how-it-works.md`「OpenAPI reverse inference」段补注：subpath_of / shares_schema_with 在构建层跨文件计算，按端点拆分的 spec 文件也能产出这两类操作间结构边
- [x] 4.2 跑 `python -m pytest tests/test_api_inference.py tests/test_languages.py -k "openapi or api_inference or shares or subpath" -q` 全绿
- [x] 4.3 跑 `python -m pytest tests/test_extract.py tests/test_mcp_ingest.py -q` 确认 dispatch 契约无回归
- [x] 4.4 重跑 corpus 对比脚本：拆分版 `shares_schema_with` 0→~61+、`subpath_of` 0→~110+，bundle 版两类边数不变，两形态实体数仍 34=34；删临时脚本

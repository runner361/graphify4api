## Why

OpenAPI 抽取产生的两类**操作-操作结构边**——`subpath_of`（嵌套路径关系）和 `shares_schema_with`（操作间共享 schema）——当前在抽取层按**单文件**计算。当一个 API 规范按端点拆分成多个文件（华为 IoTDA 的真实导出形态：每文件 1 个路径 × 1 个方法）时，单文件内只有 1 个操作，这两类边天然为 0。实测同一套 173 接口 API：bundle 版拿到 110 + 61 = 171 条结构边，拆分版拿到 0 条，导致拆分版图谱偏散、社区检测信号弱——而拆分版同时具备 bundle 版没有的「功能可追溯性」优势（每操作的 `source_file` 指向功能子目录）。系统需同时支持两种形态并让两者图谱质量等价。

## What Changes

- 把 `subpath_of` 和 `shares_schema_with` 的生成从**抽取层 per-file**（`extract_openapi`）上提到**构建层跨文件**（`run_api_entity_inference`，运行于合并后、去重前）。
- 构建层已在做跨文件全局反推（实体 id 全局、CRUD 跨文件归并），op 节点在合并后已携带 `api_path`/`http_method`/`refs_read`/`refs_write`，足以构建全局路径索引与 schema 索引。
- 语义保持不变：`subpath_of` 为 EXTRACTED 1.0（路径嵌套是规范内结构事实），`shares_schema_with` 为 INFERRED 0.95（同名 schema 配对推理）；保留 hub-schema 上限与截断防护。
- bundle 版行为不变（跨文件 = 单文件内跨操作，结果一致）；拆分版补齐 171 条结构边，与 bundle 版图谱等价，同时保留功能可追溯性。

## Capabilities

### New Capabilities
- `cross-file-op-structural-edges`: 在构建层跨文件计算 OpenAPI 操作间的结构关系边（`subpath_of` 嵌套路径、`shares_schema_with` 共享 schema），使按端点拆分的规范文件也能产出这些边，不再受单文件操作数限制。

### Modified Capabilities
<!-- 无既有规范层面的需求变化（本 worktree 无前置 specs）；行为变化由上述新能力规范承载。 -->

## Impact

- `graphify/extractors/openapi.py`：移除 `subpath_of` / `shares_schema_with` 生成块及仅服务于它们的 per-file 索引（`paths`/`first_op_by_pm`/`op_ids_by_path`/`ops_by_schema`）与常量 `_MAX_SHARE_EDGES`/`_HUB_SCHEMA_OPS`；更新模块 docstring。
- `graphify/api_inference.py`：新增上述两常量；扩展 `_edge` helper 以支持 EXTRACTED 边（无 confidence_score 键，与抽取层 `add_edge` 契约一致）；新增 `_infer_op_structural_edges` 在 `run_api_entity_inference` 内调用，边数计入 summary。
- 测试：`tests/test_languages.py` 三个断言改为「抽取后跑 inference 再断言」；`tests/test_api_inference.py` 新增跨文件回归测试。
- 文档：`docs/how-it-works.md` OpenAPI 段补注构建层跨文件计算。
- 依赖 `add-openapi-extractor`（已落地于基线提交 8cde391）。

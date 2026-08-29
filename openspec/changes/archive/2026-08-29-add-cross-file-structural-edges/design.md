## Context

OpenAPI 抽取器（`extract_openapi`）与构建层反推（`run_api_entity_inference`）已随基线提交 8cde391 落地。两类**操作-操作结构边** `subpath_of`、`shares_schema_with` 当前在抽取层 per-file 计算：用 per-file 的 `paths` 集合、`first_op_by_pm`、`op_ids_by_path`、`ops_by_schema` 索引。这使按端点拆分的语料（每文件 1 操作）丢失全部结构边。

构建层 `run_api_entity_inference` 已运行于合并后、去重前的 `combined`，且本就是跨文件全局的（实体 id 全局 `entity_<resource>`、CRUD 跨文件归并）。op 节点在该阶段携带 `api_path`/`http_method`/`refs_read`/`refs_write`/`id`，足以支撑全局索引。

## Goals / Non-Goals

**Goals:**
- `subpath_of` / `shares_schema_with` 在构建层跨文件计算，拆分版与 bundle 版产出等价的结构边。
- 保留两类边的原语义与置信：`subpath_of` EXTRACTED 1.0、`shares_schema_with` INFERRED 0.95。
- 保留 hub-schema 上限（`_HUB_SCHEMA_OPS=30`）与截断防护（`_MAX_SHARE_EDGES=800`），防止 ErrorResponse 类公共 schema 产生无信号的全连接。
- 保留 `_origin: "ast"` 戳记，防 fuzzy dedup 折叠。

**Non-Goals:**
- 不改变 `references`/`grouped_under`/`contains`（文件内结构事实，仍由抽取层产出）。
- 不改变实体反推逻辑（CRUD 归并、列聚合、belongs_to、DDL 对账）。
- 不新增跨文件 shares_schema_with 的「跨 schema 名等价」匹配（仅同名 schema 配对，与原语义一致）。

## Decisions

### D1：整体上提到构建层，而非抽取层加跨文件逻辑
**选择**：移除抽取层的两类边生成，整体迁入 `run_api_entity_inference`。
**替代方案**：在抽取层维持生成，再在构建层补一份跨文件增量。否决——会产生 per-file 与跨文件两套重叠边，需额外去重，且抽取层 per-file 结构对拆分版恒为 0，是死代码。
**理由**：构建层是唯一能见到合并后全部操作的层级；单一来源更清晰。

### D2：subpath_of 保留 EXTRACTED，shares_schema_with 保留 INFERRED
**选择**：沿用原置信语义，不统一为 INFERRED。
**理由**：路径嵌套是规范内可直接观测的结构事实（EXTRACTED 1.0 诚实）；两操作共享同名 schema 是相似性推理（INFERRED 0.95）。改语义会破坏既有 `GRAPH_REPORT.md` 审计契约与文档。

### D3：扩展 `_edge` helper 以发 EXTRACTED 边
**选择**：给 `_edge` 加 `confidence="INFERRED"` 与 `score=0.95` 参数；当 `confidence == "EXTRACTED"` 时**不写** `confidence_score` 键。
**替代方案**：为结构边另写一个 helper。否决——`_edge` 已含 `seen_new_edges` 去重与 `_origin: "ast"` 戳记，复用即可。
**理由**：与抽取层 `add_edge` 契约一致（EXTRACTED 边无 score 键），build.py 对 EXTRACTED 边的处理已兼容。

### D4：全局索引在 `_infer_op_structural_edges` 内就地构建
**选择**：从 `op_nodes` 构建 `paths`/`first_op_by_pm`/`op_ids_by_path`/`ops_by_schema`，逻辑与原抽取层同构（`parent_path` 剥尾段回溯）。
**理由**：op id 在该阶段稳定；跨文件后父路径操作可在另一文件，正是拆分版补边的关键。`ops_by_schema` 按 schema **名**聚合（非 schema 节点 id），跨文件同名 schema 即关联——比 per-file 更正确。

## Risks / Trade-offs

- [bundle 版边数微变] 跨文件 `shares_schema_with` 按 schema 名配对，若不同文件的**不同 schema 节点**恰巧同名会多连边 → 缓解：同名即语义等价，本就是该边的意图；且 `references` 边仍按节点 id 精确，不受影响。预期 bundle 版（单文件）边数不变。
- [构建层边数膨胀] 大语料可能产生大量配对 → 缓解：保留 `_HUB_SCHEMA_OPS=30` 上限（>30 操作引用同一 schema 时跳过，避免 ErrorResponse 全连接）与 `_MAX_SHARE_EDGES=800` 截断。
- [测试断言位移] 原 3 个测试断言直接对 `extract_openapi` 结果检查结构边，迁移后需改为跑 inference 再断言 → 缓解：测试调整在 tasks 内显式列出。

## Migration Plan

纯内部重构，无对外 API 变更、无数据迁移。上线步骤：移除抽取层生成 → 构建层新增 → 调测试 → 跑 `pytest` → 重跑 corpus 对比验证拆分版补齐、bundle 版不变。回滚：单 commit revert 即可恢复 per-file 生成。

## Open Questions

无。

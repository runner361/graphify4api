## Why

同一套 173 接口 IoTDA API 的实测显示:拆分版(每端点一文件)最终图有 **510 个 schema 节点**(254 个逻辑名,256 个冗余副本)、**365 条 schema→schema $ref 边**(bundle 仅 181)、**683 条 contains→schema 边**(bundle 290),而 op→schema references 两边都是 200 条、完全等价。冗余**全在 schema 层**:每个文件独立定义自己用到的 schema(`DeviceList`→`Device` 这种 $ref 关系图在几十个文件里各画一遍)。根因与已完成的 `subpath_of`/`shares_schema_with` 上提同构——per-file 抽取看不到跨文件,但 schema 的重复还会**留在最终图**(build 的 fuzzy dedup 不合并带 `_origin:"ast"` 戳记的同名 schema 副本)。`Page` 分页 DTO 被切成 23 个互不相连的孤立节点,既浪费体积,又丢失"这些是同一个 schema"的关系信号。

## What Changes

- 在构建层(`api_inference`,合并后、去重前)新增 schema 规范化:跨文件按 `schema_name` 合并同名 schema 副本为单一规范节点,属性取并集(同名 schema 在不同文件的属性定义常有差异,并集即逻辑 schema 的真实形状)。
- 把指向各副本的边(`references` op→schema、`schema→schema` $ref、`contains` spec→schema)重定向到规范节点,折叠重定向后产生的重复边(同 src/tgt/relation)。
- 删除冗余副本节点。实体反推(`schema_props`、`schema_ref_pairs`)在规范化之后运行,自然吃到合并后的属性与 $ref 图。
- bundle 版行为不变(单文件无副本,规范化为 no-op)。拆分版 schema 节点 510→254、references 565→~381、contains 856→~600(残差为功能追溯的 tag/spec 根,该保留)。

## Capabilities

### New Capabilities
- `cross-file-schema-canonicalization`: 在构建层跨文件合并同名 schema 副本(属性并集、边重定向、副本删除),使按端点拆分的规范文件不再把同一 schema 切成多个孤立节点。

### Modified Capabilities
<!-- 本 worktree 无前置 specs;行为由新能力规范承载。 -->

## Impact

- `graphify/api_inference.py`:新增 `run_api_schema_canonicalization(extraction)`(合并 + 边重定向 + 副本删除 + 边去重),在 `run_api_entity_inference` 之前调用。
- `graphify/build.py`:合并后、`run_api_entity_inference` 之前插入规范化调用。
- 测试:`tests/test_api_inference.py` 新增跨文件 schema 合并回归(两文件同名 schema 属性互补 → 并集、边重定向、副本消失)。
- 文档:`docs/how-it-works.md` OpenAPI 段补注 schema 规范化。
- 依赖 `add-openapi-extractor`(基线 8cde391)。与 `add-cross-file-structural-edges` 正交,互不依赖。

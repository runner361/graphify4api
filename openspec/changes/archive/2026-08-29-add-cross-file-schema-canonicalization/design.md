## Context

基线 `add-openapi-extractor`(8cde391)落地了 OpenAPI 抽取与构建层实体反推。抽取层 per-file 产出 schema 节点:每个 spec 文件把 `definitions`/`components/schemas` 里自己用到的 schema 各定义一份(stem 前缀 id,如 `fileA_schema_Device`)。同一逻辑 schema(如 `Device`)在被多个文件引用时,产生多个独立节点 + 多份 `schema→schema` $ref 边 + 多条 `spec→schema` contains 边。

实测(173 接口 IoTDA 拆分版 vs bundle):schema 节点 510 vs 254(256 冗余副本)、schema→schema $ref 边 365 vs 181(+184)、contains→schema 边 683 vs 290(+393)。冗余全在 schema 层;op→schema references 200=200 等价。build 的 fuzzy dedup 不合并这些副本(`_origin:"ast"` 戳记防折叠 + 副本 id 不同),256 个冗余节点全部进最终 `graph.json`。

## Goals / Non-Goals

**Goals:**
- 构建层跨文件按 `schema_name` 合并同名 schema 副本为单一规范节点,属性取并集。
- 重定向指向副本的 `references`/`contains` 边到规范节点,折叠重定向后的重复边,删除副本节点。
- 实体反推在规范化后运行,吃到合并属性与去重 $ref 图。
- bundle 版 no-op(单文件无副本);split 版冗余收敛到与 bundle 等价(残差仅功能追溯结构)。

**Non-Goals:**
- 不改抽取层 schema 产出(per-file 仍各自定义;规范化是构建层职责,单一来源)。
- 不改 op→schema references 边语义(已等价)。
- 不做跨"API 服务"的同名 schema 合并策略(见 Risks)。

## Decisions

### D1:按 `schema_name` 全局合并,属性取并集
**选择**:以 `schema_name`(bare 名,如 `Device`)为合并键,跨全部合并后节点,取属性并集。
**替代方案**:按 stem 前缀分组(不跨文件)——否决,等于不合并。按属性子集关系条件合并——否决,复杂且 iotda 同名 schema 属性常有差异但确是同一 schema,子集判断会漏合。
**理由**:`$ref` 在一个 OpenAPI spec 内本就是按名解析的;一个 corpus 通常是同一 API 服务的多份导出,同名即同 schema。并集是逻辑 schema 的真实形状(各文件定义的属性互补)。

### D2:规范节点选取"属性最全者",副本删除
**选择**:每组同名取 `properties` 最长的节点为规范 id(保留其 id),其余副本的属性并入规范节点的 `properties`(并集)后删除副本节点。
**理由**:保留属性最全者的 id 减少属性迁移;属性并集补全缺失列。

### D3:边重定向 + 去重,而非删除后重建
**选择**:遍历所有边,凡 source/target 是副本 id 则替换为规范 id;重定向后按 (source,target,relation) 去重(保留首条,丢弃后续),保留 EXTRACTED/INFERRED 置信与 `_origin` 戳记。
**替代方案**:删除所有指向副本的边再从规范节点重建——否决,会丢失 context/置信等边属性,且 references 边的 source 是 op(非 schema),不能从规范节点重建。
**理由**:重定向保留边语义;去重折叠重定向产生的同 (src,tgt,relation) 副本。

### D4:规范化先于实体反推
**选择**:`build.py` 合并后先 `run_api_schema_canonicalization` 再 `run_api_entity_inference`。
**理由**:实体反推的 `schema_props`(name→properties)与 `schema_ref_pairs`(schema→schema $ref)直接消费规范节点——合并后属性更全、$ref 图去重,实体列推断与 belongs_to 证据更准。

## Risks / Trade-offs

- [跨服务同名 schema 误并] 混合 corpus 里两个不同 API 各有同名但语义不同的 schema(如两个微服务都叫 `User`)→ 按 name 合并会误并。缓解:OpenAPI 同名 schema 在同一服务内本就是按名 $ref 解析的;跨服务 corpus 较少见且通常不同名。若未来出现,可加 "同 stem 前缀或同 spec 上下文" 的门控——当前不预设该复杂度。诚实记录为已知权衡。
- [属性并集引入噪声列] 某文件同名 schema 定义了独有属性(可能是该端点的视图)→ 并集会让规范 schema 带上所有端点的属性。缓解:这正是"逻辑 schema 的全貌",对实体列推断是增益而非噪声(更多列被收集);列来源仍带 schema 名溯源。
- [边去重丢失 context] 重定向后多条同 (src,tgt,relation) 边折叠为首条,其余 context 丢失。缓解:context 是辅助信息(如 "schema $ref"),首条已足够;不丢置信与 _origin。

## Migration Plan

纯构建层内部重构,无对外 API 变更。上线:新增规范化函数 → build.py 插入调用 → 测试 → pytest → corpus 对比验证 split 收敛到 bundle。回滚:单 commit revert。规范化是幂等的(对已规范化的输入 no-op)。

## Open Questions

无。

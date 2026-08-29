## Context

两个前置事实:(1) 基础图谱层(变更 `add-openapi-extractor`)产出 `file_type: api_operation` 的操作节点与 `file_type: inferred_entity` 的虚拟实体节点,后者携带推断列属性;(2) graphify 的 docs 通道已能对 `.md` 做语义抽取(概念节点),`llm.py` 已抽象 9 类 LLM 后端(自动探测、并发、429 重试、超时),`cache.py` 按内容 hash 缓存语义结果,`build.py` 把 LLM 数值置信折叠为 INFERRED(既有约定)。

用户新输入:产品功能说明文档路径,按功能项分子目录,子目录内存放该功能的说明 Markdown。要做的是 功能 → 接口/实体 的语义关联,并支持功能维度查询。关键鸿沟:功能描述是自然语言(常为中文,如"支持订单部分退款"),目标是技术命名(`/refund-orders/{id}`、实体 `refund_orders`)——词面部分重叠但不可靠,语义对齐必须 LLM。

约束:项目信条"不是向量索引"(无 embedding 基建,不引入);LLM 边一律 INFERRED + 证据可追溯;目录结构是 ground truth 不用 LLM 猜。

## Goals / Non-Goals

**Goals:**
- 功能项子目录 → feature 节点(确定性),文档以 contains 边挂接
- 功能 → API 操作 `implemented_by`、功能 → 实体 `uses_entity` 的 INFERRED 边,带离散置信分与 evidence 证据引文
- 两段式成本控制:确定性预筛把 LLM 输入压到每功能 top-N 候选
- 无 LLM 后端时优雅降级(名称强匹配低档边 + 报告说明)
- 关联结果内容 hash 缓存,重跑零 LLM 成本
- `query`/`path`/`explain` 直接回答功能维度问题,查询层零改动

**Non-Goals:**
- 不引入 embedding/向量检索(项目明确"不是向量索引")
- 不做功能→代码文件/函数的关联(后续可扩展,先接口/实体)
- 不让 LLM 发明功能项(目录即功能;LLM 不参与功能节点生成)
- 不修改社区检测与图谱聚类算法(新边自然参与 Leiden,属免费收益)
- 不做功能间关系(功能A 依赖功能B)——留待后续

## Decisions

**D1 功能节点来自目录结构,不由 LLM 归纳;粒度 = 直接包含 `.md` 的目录(任意层级)。**
每个**直接含说明文档的目录**生成一个 feature 节点(`<path>_feature_<name>`,`file_type: feature`),其 `.md` 以 `contains` EXTRACTED 边挂接;目录间父子关系生成 `subfeature_of` EXTRACTED 边(子功能→父功能,父目录仅作分组无文档时不生成节点、边连到最近的祖先功能)。备选一:LLM 从内容聚类归纳功能——被否,目录是用户给定的组织意图;备选二:根路径直接子目录=功能项——**被真实语料否决**:`tests/md/iotdm_20260815_000331`(华为 IoTDM 用户指南,130 文件)是三级中文树(`用户指南/消息通信/设备数据上报/…`),直接子目录规则会退化成单一"用户指南"功能;"直接含文档的目录"规则在任意深度下都给出正确的功能粒度。

**D2 两段式:rapidfuzz 预筛 + LLM 裁决,而不是全量清单直接问 LLM。**
全量问 LLM 在大语料(数百操作/实体)下上下文爆炸、幻觉率上升、成本线性膨胀;纯 rapidfuzz 跨不过语义鸿沟("订单管理" vs `/orders` + `/fulfillments` 的多对一)。预筛:功能名 + 文档关键词(markdown quick-scan 的标题/高频词)对 操作(path 资源段 + method + tag)、实体(名 + 推断列)做 `token_set_ratio`,取 top-N(默认 20)候选。LLM 只裁决候选,输入有界、输出可校验。备选:embedding 检索——被否(D-约束:无向量基建)。

**D3 LLM 输出契约与防幻觉校验。**
Prompt 给出功能描述(目录内文档拼接摘要,受 token budget 约束,超长走既有 file_slice 切片)+ 候选清单(id、标签、路径/实体名、关键属性),要求输出 JSON 数组:`{target_id, relation: implemented_by|uses_entity, confidence_score, evidence}`;evidence 必填(文档中的支撑句原文片段)。解析时**target_id 白名单校验**:不在候选清单内的目标一律丢弃;relation 白名单校验;置信分必须落在 rubric 档位(0.95/0.85/0.75/0.65/0.55,与语义抽取 rubric 一致),非法值取相邻低档。JSON 解析失败按既有 LLM 基建的重试/二分逻辑处理。

**D4 边语义与置信落点。**
`implemented_by`(feature → api_operation)、`uses_entity`(feature → inferred_entity 或真实表节点)。全部 INFERRED(build.py 既有折叠逻辑天然覆盖),evidence 存为边属性并在 GRAPH_REPORT.md 展示;LLM 自评低置信(<0.55 档)的候选标 AMBIGUOUS 进报告人工复核,不进主边。AMBIGUOUS 边在报告中按功能分组展示,方便产品/研发一次性审。

**D5 触发时机:关联 pass 在 build/merge 阶段执行。**
关联目标(操作/实体节点)来自其他文件的抽取产物,只有 merge 阶段才齐备;与实体反推(change 1 的 D4)同层、先后执行(实体反推先,关联引用其产物)。功能节点生成则在 extract 阶段(与 markdown 抽取同步)。备选:extract 时即时关联——被否,时序上目标不存在。

**D6 LLM 基建全复用,缓存键=双 hash。**
后端探测/并发/超时/重试全部走 `llm.py`;缓存键 = 功能文档内容 hash + 候选清单 hash(候选清单变了——比如新增接口——缓存自动失效重裁),存 `graphify-out/cache/`。无任何后端可用时降级:预筛 ≥90 的强匹配生成 `evidence: "name-match"` 的 INFERRED 0.65 边,GRAPH_REPORT.md 明示"LLM 未参与,仅名称匹配";低于 90 不建边。

**D7 中文功能名的预筛归一。**
中文功能名("退款管理")与英文路径(`/refunds`)词面零重叠,rapidfuzz 直接比会漏。初版策略:功能名中英混合词切分(简单规则:连续拉丁词段直接抽取 + 中文词保留整词比对文档内英文术语),文档正文中的英文技术词(常出现接口名/表名)是主要桥接信号——预筛输入不只用功能名,必须含文档关键词。jieba 分词为可选增强(既有 `[chinese]` extra),不作为硬依赖。

## Risks / Trade-offs

- [LLM 幻觉目标(编造不存在的接口)] → D3 白名单校验,候选外目标一律丢弃
- [预筛漏召回(正确接口不在 top-N)] → N 可配(默认 20);预筛输入强制含文档关键词而非仅功能名;AMBIGUOUS 报告让漏网可见(人工补);后续可加"功能-接口"人工标注覆盖通道
- [多对多误联(通用功能"用户管理"连到大量接口)] → LLM rubric 压置信 + evidence 必填;报告按功能分组复核
- [中文-英文语义鸿沟导致预筛失效] → D7 文档关键词桥接;jieba 可选增强;最坏情况退化为 LLM 输入只有功能名(仍可用,只是候选质量降)
- [成本:功能数 × 每功能一次 LLM 调用] → 候选有界(top-N)、缓存双 hash、并发走既有基建;比逐文档全量抽取便宜一个量级
- [`feature` 新 file_type 的下游容错(HTML 可视化/manifest/_minhash)] → 与 change 1 的枚举扩展同批验证
- [功能文档质量参差(空目录、超长文档)] → 空目录跳过并警告;超长走 file_slice 既有切片

## Migration Plan

纯新增层:功能节点生成 + 关联 pass + 新边类型,不动既有抽取/聚类/查询行为。回滚 = 移除关联 pass 调用点与功能目录识别,其余图谱产物不变。缓存按 hash 失效,无迁移。

## Open Questions

- ~~多级功能目录是否需要二级 feature 节点~~ 已由真实语料回答:D1 修订为"直接含 .md 的目录 = 功能项 + subfeature_of 父子边"。
- 功能文档同时描述多个功能项(交叉文档)时,目录归属即唯一归属是否够用?初版是(目录即功能),交叉场景靠 evidence 语义在 LLM 层体现。

## Why

基础图谱(变更 `add-openapi-extractor`)产出 API 操作节点与反推的数据库实体节点,但它们只承载结构信息,没有业务语义。产品团队的语言是功能项("订单管理"、"退款流程"),且功能说明文档天然按功能项分目录存放。功能描述(自然语言,常为中文)与接口路径/实体名(技术命名)之间没有结构对齐,确定性规则无法可靠桥接——这一层关联需要 LLM 语义推断。目标查询形态:"订单管理功能涉及哪些 API 接口?写哪些数据实体?"

## What Changes

- **功能节点确定性生成**:功能文档根路径下的每个功能项子目录生成一个 feature 节点,目录内文档以 `contains` EXTRACTED 边挂接(目录结构是用户给定的 ground truth,不用 LLM 猜)
- **确定性候选预筛**:功能名 + 文档关键词 与 操作路径段/tag/实体名/实体属性做 rapidfuzz 匹配,每功能取 top-N 候选(默认 20),控制 LLM 上下文与成本
- **LLM 语义裁决**:对候选清单批量裁决,输出 目标/关系/离散置信分/证据引文(evidence 必填);防幻觉校验——LLM 返回的目标必须在候选清单内
- **新边类型**:`implemented_by`(功能 → API 操作)、`uses_entity`(功能 → 数据库实体),全部 INFERRED + confidence_score + evidence 属性;AMBIGUOUS 级结果进 GRAPH_REPORT.md 人工复核
- **降级路径**:无 LLM 后端时,预筛强匹配(≥90)仍生成 `evidence=name-match` 的低档边,并在报告说明 LLM 未参与
- LLM 后端复用 `llm.py` 既有多后端(gemini/kimi/claude/openai/deepseek/ollama/bedrock/azure/claude-cli,自动探测);关联结果按内容 hash 进语义缓存,重跑零成本
- 查询层零改动:`query`/`path`/`explain` 遍历新边即可回答功能维度问题

## Capabilities

### New Capabilities
- `feature-api-linking`: 从按功能项组织的产品文档目录生成功能节点,经确定性预筛 + LLM 语义裁决构建 功能→API 操作(implemented_by)与 功能→数据库实体(uses_entity)的关联边,使"某功能涉及哪些接口/实体"成为图谱可直接回答的查询

### Modified Capabilities

(无——`openspec/specs/` 当前为空)

## Impact

- **实现顺序依赖**:`add-openapi-extractor` 必须先落地(`api_operation`/`inferred_entity` 节点是本变更的关联目标);本变更的功能节点层与预筛层可先行开发,LLM 裁决层的联调依赖前者
- 修改:`graphify/detect.py`/`collect_files`(功能目录结构识别)、`graphify/extract.py` 或新模块(功能节点生成)、`graphify/build.py` 或其合并流程(关联 pass 调用点)、`graphify/cache.py`(关联缓存键)、`graphify/validate.py`(`feature` file_type 枚举)
- LLM 调用:复用 `llm.py`;用户需配置任一既有后端(与 docs 语义抽取同要求);功能-接口关联是除文档抽取外新增的 LLM 消耗点(每功能一次调用,预筛已把候选压到 top-N)
- 依赖:无新增第三方库(rapidfuzz 已有;中文分词 jieba 为可选增强,走既有 `[chinese]` extra)

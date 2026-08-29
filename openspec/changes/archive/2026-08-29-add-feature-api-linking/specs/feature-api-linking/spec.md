## ADDED Requirements

### Requirement: 从功能文档目录结构生成功能节点
系统 SHALL 为功能文档路径下**每个直接包含说明文档的目录**(任意层级)生成一个 feature 节点(`file_type: feature`),并为目录内每个说明文档生成 功能节点到文档节点的 `contains` 边(EXTRACTED);直接含文档的目录之间的父子关系 SHALL 生成 `subfeature_of` 边(EXTRACTED);目录结构 MUST NOT 由 LLM 参与判定;根路径下的散置文档与空目录 MUST 不生成功能节点。

#### Scenario: 多级目录树生成多级功能节点
- **WHEN** 功能文档路径为三级树 `用户指南/消息通信/设备数据上报/`,`.md` 文档位于第三级目录
- **THEN** `设备数据上报` 等每个直接含文档的目录各生成一个 feature 节点,`消息通信` 一级生成其父功能节点,两者之间有 `subfeature_of` EXTRACTED 边

#### Scenario: 单级功能目录生成功能节点
- **WHEN** 功能文档根路径含子目录 `订单管理/` 与 `退款/`,各含 2 个 `.md` 文档
- **THEN** 图谱生成两个 feature 节点,每个节点有 2 条 `contains` EXTRACTED 边指向其目录内文档节点

#### Scenario: 散置文档与空目录
- **WHEN** 根路径下存在未入子目录的 `.md` 与一个空子目录
- **THEN** 散置文档按既有文档语义抽取处理但不挂任何功能节点,空目录被跳过并警告

### Requirement: 确定性候选预筛
在发起任何 LLM 调用前,系统 SHALL 用确定性匹配为每个功能生成候选清单:功能名与文档关键词(含文档正文中的英文技术词)对 API 操作节点(路径资源段、HTTP 方法、tag)与实体节点(名称、推断列)做模糊匹配,每功能保留 top-N 候选(N 可配置,默认 20);无任何候选达到最低阈值的功能 MUST NOT 发起 LLM 调用。

#### Scenario: 候选有界
- **WHEN** 某功能预筛后有 35 个超过最低阈值的候选
- **THEN** 只保留得分前 20 个进入 LLM 裁决

#### Scenario: 无候选不调用 LLM
- **WHEN** 某功能的所有匹配得分均低于最低阈值
- **THEN** 不为该功能发起 LLM 调用,不生成关联边

### Requirement: LLM 语义裁决生成关联边
系统 SHALL 对候选清单发起 LLM 裁决,生成 功能 → API 操作 的 `implemented_by` 边与 功能 → 实体 的 `uses_entity` 边;所有边 MUST 为 INFERRED 并携带离散 confidence_score(0.95/0.85/0.75/0.65/0.55 档位)与必填的 evidence 属性(文档支撑句原文片段);LLM 返回的目标不在候选清单内、relation 不在白名单内、或置信分不在档位上的结果 MUST 被丢弃或降档;LLM 自评低于最低档位的候选 MUST 标记 AMBIGUOUS 并进入 GRAPH_REPORT.md。

#### Scenario: 强关联边生成
- **WHEN** "退款"功能文档描述退款单创建流程,候选含 `POST /refund-orders` 与实体 `refund_orders`
- **THEN** 生成 `implemented_by` 与 `uses_entity` INFERRED 边,confidence_score 为 0.95,evidence 为文档中的支撑句

#### Scenario: 幻觉目标被丢弃
- **WHEN** LLM 返回的某个 target_id 不在候选清单内
- **THEN** 该结果被丢弃,不生成边

#### Scenario: 无关候选不建边
- **WHEN** LLM 判定某候选与功能无关
- **THEN** 不为该候选生成任何边

#### Scenario: 低置信进人工复核
- **WHEN** LLM 对某候选的自评低于最低档位
- **THEN** 该候选生成 AMBIGUOUS 边并在 GRAPH_REPORT.md 中按功能分组展示

### Requirement: 无 LLM 后端时的降级路径
当无任何 LLM 后端可用时,系统 MUST NOT 报错中断:预筛得分 ≥90 的强匹配仍生成 `evidence: "name-match"`、confidence_score 0.65 的 INFERRED 边,GRAPH_REPORT.md MUST 明示这些边仅来自名称匹配、LLM 未参与;得分 <90 的候选不建边。

#### Scenario: 降级生成名称匹配边
- **WHEN** 未配置任何 LLM 后端,且某功能与 `GET /refunds` 的预筛得分为 95
- **THEN** 生成 `implemented_by` 边,evidence 为 `name-match`,置信 0.65,报告说明降级状态

### Requirement: 关联结果缓存与成本控制
系统 SHALL 按功能文档内容 hash 与候选清单 hash 的组合缓存 LLM 裁决结果;文档或候选清单任一变化时缓存失效重裁;两者均未变时重跑 MUST NOT 发起 LLM 调用;LLM 输入 MUST 限制在候选清单与受 token budget 约束的功能文档摘要内。

#### Scenario: 重跑零调用
- **WHEN** 功能文档与图谱候选清单均未变化,重新构建图谱
- **THEN** 关联边从缓存恢复,不发起任何 LLM 调用

#### Scenario: 新增接口触发重裁
- **WHEN** 语料新增一个 OpenAPI 规范文件,某功能的候选清单发生变化
- **THEN** 该功能的缓存失效并重新裁决

### Requirement: 功能维度的可查询性
功能节点及其关联边 MUST 可被 `graphify query`、`graphify path`、`graphify explain` 直接遍历,使"某功能涉及哪些 API 接口或数据库实体"成为无需额外工具的图谱查询;查询层 MUST NOT 为此变更。

#### Scenario: 查询功能涉及的接口
- **WHEN** 图谱构建完成后执行 `graphify query "退款功能涉及哪些 API 接口"`
- **THEN** 结果子图包含退款 feature 节点及其 `implemented_by` 边连接的操作节点

#### Scenario: explain 功能节点
- **WHEN** 执行 `graphify explain "退款"`
- **THEN** 输出包含该功能的 `implemented_by` 与 `uses_entity` 连接列表及各边 evidence

## 1. 功能节点层(可先行,不依赖 change 1)

- [x] 1.1 `feature` 加入 `validate.py` file_type 合法枚举(与 `add-openapi-extractor` 的 `api_operation`/`inferred_entity` 同批);确认 HTML 可视化、manifest、`_minhash` 对新枚举的容错
- [x] 1.2 功能文档目录识别:**直接包含 `.md` 的目录 = 功能项**(任意层级);直接含文档目录间的父子关系生成 `subfeature_of` EXTRACTED 边;真实语料为三级中文树(`tests/md/iotdm_20260815_000331`,华为 IoTDM 用户指南 130 文件);根级散置文档不挂功能节点;空目录跳过并警告
- [x] 1.3 feature 节点生成(`<dir>_feature_<name>`,`file_type: feature`)+ 到目录内文档节点的 `contains` EXTRACTED 边;注意与 markdown 语义抽取的 `<slug>_doc` 节点 ID 对齐(build.py 既有 twin 合并逻辑)
- [x] 1.4 功能摘要与关键词:目录内文档按序拼接、超长走 `file_slice` 既有切片、token budget 约束;提取功能名 + 标题 + 文档正文英文技术词作为预筛输入(D7 中英桥接)

## 2. 确定性预筛器

- [x] 2.1 候选特征构建:API 操作(路径资源段 + HTTP 方法 + tag)、实体(名称 + 推断列);中英混合词切分(连续拉丁词段直接抽取,中文词保留整词)
- [x] 2.2 rapidfuzz `token_set_ratio` 打分、每功能 top-N(默认 20,N 可配)、最低阈值过滤、无候选功能跳过(不发起 LLM)

## 3. LLM 裁决 pass

- [x] 3.1 裁决 prompt 与输出 JSON 契约(target_id、relation: implemented_by|uses_entity、confidence_score 档位、evidence 必填);复用 `llm.py` 后端探测/并发/超时/重试/二分
- [x] 3.2 结果解析与防幻觉:target_id 候选白名单校验(候选外丢弃)、relation 白名单、置信档位校验(非法值降相邻低档)、低于最低档标 AMBIGUOUS
- [x] 3.3 降级路径:无任何后端时,预筛 ≥90 强匹配生成 `evidence: "name-match"`、0.65 的 INFERRED 边;<90 不建边
- [x] 3.4 缓存:双 hash 键(功能文档内容 hash + 候选清单 hash),接入 `cache.py` 语义缓存体系

## 4. 接入 build 与报告

- [x] 4.1 build/merge 阶段调用关联 pass,时序在实体反推(`add-openapi-extractor` 的 build 步骤)之后;`implemented_by`/`uses_entity` 边并入图谱
- [x] 4.2 GRAPH_REPORT.md 新增"功能 → 接口/实体"小节:按功能分组列出关联边与 evidence;AMBIGUOUS 候选分组展示;降级运行时明示"仅名称匹配,LLM 未参与"
- [x] 4.3 确认 `query`/`path`/`explain` 对新边零改动可遍历(集成验证,不改查询代码)

## 5. 测试与文档

- [x] 5.1 fixtures:小型合成功能树(中文功能名+英文技术词)+ 真实语料 `tests/md/iotdm_20260815_000331`(三级中文树)+ `tests/opeapi/merged_swagger.json`
- [x] 5.2 单测:目录→功能节点与散文档/空目录策略、预筛 top-N 截断与最低阈值、中文功能名经文档英文词桥接命中、LLM mock 后端(stub)裁决输出、白名单丢弃幻觉目标、AMBIGUOUS 分流、缓存命中与候选变更失效、降级路径
- [x] 5.3 集成测试(依赖 change 1 已实现):`graphify query "退款功能涉及哪些接口"` 与 `explain "退款"` 返回关联边与 evidence
- [x] 5.4 全量回归 `uv run pytest tests/ -q`
- [x] 5.5 集成验证:`tests/opeapi` + `tests/md/iotdm_20260815_000331` 双语料构建,产出写入 `tests/api-graph/`,抽查 功能→接口/实体 边与 evidence 质量(真实 IoTDM 语料含中文功能名↔英文路径桥接)
- [x] 5.6 文档:`ARCHITECTURE.md` 登记新模块入口、`README.md` 功能层说明、`docs/how-it-works.md` 增补"功能关联层"一节(LLM 消耗点与降级行为)

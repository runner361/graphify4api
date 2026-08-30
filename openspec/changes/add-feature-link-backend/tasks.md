# Implementation Tasks

## Spec

- [x] 1. 撰写 openspec 变更 `add-feature-link-backend`:proposal.md / design.md / tasks.md / specs delta / .openspec.yaml
- [x] 2. `openspec validate add-feature-link-backend` 通过(0 error) — `Change 'add-feature-link-backend' is valid`

## 代码

- [x] 3. `graphify/feature_link.py`:`run_feature_linking()` 签名加 `llm_backend: str | None = None`;实现优先级解析(`llm_call` > `llm_backend` 经 `_call_llm` 包装 > `_default_llm_call`);显式后端异常返 None 触发既有降级
- [x] 4. `graphify/build.py`:`build()` 签名加 `feature_llm_backend: str | None = None`(位在 `dedup_llm_backend` 后、`root` 前);`run_feature_linking(combined)` → `run_feature_linking(combined, llm_backend=feature_llm_backend)`
- [x] 5. 不改 `graphify/llm.py`(`_call_llm` claude-cli 分支已存在、`detect_backend()` 不动)

## 测试

- [x] 6. 新增 `run_feature_linking` 的 `llm_backend` 注入单测:`test_llm_backend_routes_through_call_llm` / `test_llm_backend_unavailable_degrades_to_name_match` / `test_explicit_llm_call_takes_precedence_over_llm_backend`(stub `_call_llm`)
- [x] 7. 新增 `build(feature_llm_backend=…)` 透传单测:`test_build_threads_feature_llm_backend_to_run_feature_linking` / `test_build_feature_llm_backend_defaults_to_none`
- [x] 8. 既有 feature-link 测试全绿(默认 `None` 行为不变)
- [x] 9. `python -m pytest`:本变更 0 回归 — 干净树 128 failed/4680 passed vs 本树 127 failed/4685 passed(多 5 = 新测试;全部 127/128 失败均为既有 Windows GBK 编码/环境问题,与本变更无关)

## 验证(三图谱 + 端到端)

- [x] 10. 环境就绪:`claude.cmd` 在 PATH(`shutil.which` → `C:\Users\icsl\AppData\Roaming\npm\claude.cmd`);`claude -p` 冒烟通过(envelope 正常返回);建 `tests/api-graph/{api,product,combined,synthetic}/`
- [x] 11. API 图谱:detect `tests/opeapi/iotda`(173 .json),extract(openapi,0 LLM,1029 节点/1594 边),`build([ext_api])` → 796 节点/1709 边/193 INFERRED/34 社区/0 feature 边(符合预期:无 .md→无 feature 节点)
- [x] 12. 产品结构图谱:detect `tests/md/iotdm_20260815_000331`(130 .md),extract(`extract_markdown`,0 LLM)得 ext_product_ast(1004 节点/995 边:130 page + 874 heading)
- [x] 13. 产品语义图谱:7 个 general-purpose subagent 并行(~20 .md/chunk)得 250 节点/455 边/21 超边
- [x] 14. 产品图谱:合并 ast+semantic(1254 节点),`build([ext_product])` → 1281 节点/1455 边/90 INFERRED/90 社区/36 feature 节点/0 feature→API 边(符合预期:产品语料无 api_operation→feature_link 早退)
- [x] 15. 合并图谱(真实语料):`build([ext_api, ext_product], feature_llm_backend="claude-cli")` → 2077 节点/3164 边/283 INFERRED/36 feature 节点/**0 feature→API 边** — 见下方发现
- [x] 16. 端到端 claude-cli 验证(合成语料):合成 feature 文档(正文含英文 API 路径段 `amqp-queues`/`POST /v5/iot`)绕过语言桥缺口,`build([ext_api, ext_syn], feature_llm_backend="claude-cli")` → **3 feature→API 边,全部 LLM 裁决(0 name-match 降级)**:2× `implemented_by`(POST+DELETE `/amqp-queues`,conf 0.95,evidence 为裁决支撑句非 name-match)+ 1× `uses_entity`(`amqp-queues` 实体,conf 0.95)。证明 `build(..., feature_llm_backend="claude-cli")` → prescreen → 真实 `claude -p` 子进程 → INFERRED 边的完整路径生效(变更前 `detect_backend` 永不选 claude-cli → 必降级,此路径不可达)

## 发现(真实语料的语言桥缺口,非本变更回归)

- **现象:** 真实 iotda(API,英文路径)+ iotdm(产品,中文文档)合并图谱,`feature_llm_backend="claude-cli"` 下 36 feature 全部 0 候选 → 0 LLM 调用 → 0 feature→API 边。
- **根因:** `feature_link._prescreen` 用 `fuzz.token_set_ratio(feature_text, op_text)` 且最低阈值 `_MIN_PRESCREEN=60`。`feature_text` 的跨语言桥 `_english_terms` 从 `.md` 正文刮取 ≥3 长拉丁词;但 iotdm 产品文档为纯中文,正文几乎不含 iotda 的英文 API 路径段(如 `amqp-queues`/`/v5/iot`),故 `feature_text` 与英文 `op_text`(`POST /v5/iot/{project_id}/amqp-queues`)相似度 < 60,36 feature 全部 0 候选,LLM 从未被调用。
- **定性:** 这是 `feature_link` 既有的跨语言预筛缺口(`feature-api-linking` spec 的"确定性候选预筛"在中文产品↔英文 API 场景下召回为 0),**与本变更无关** — 本变更只负责"有候选时把裁决路由到 claude-cli",合成语料证明该路由端到端可用。缺口本身应作为后续变更(如:prescreen 增加中文功能名↔英文路径的语义/翻译桥,或允许 LLM 在零候选时做一次开放裁决)。

## 收尾(待用户决定)

- [ ] 17. `openspec archive add-feature-link-backend`(promote delta 到 `openspec/specs/feature-api-linking/spec.md`)— 需用户确认
- [ ] 18. 主仓库 v8 分支 6 个未 push commit(55dbef2 等)是否 push — 铁律:不主动 commit/push,待用户确认

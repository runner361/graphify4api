# feature-api-linking Specification

## ADDED Requirements

### Requirement: 显式裁决后端注入
`build()` 与 `run_feature_linking()` SHALL 接受一个显式后端名参数(`build()` 为 `feature_llm_backend: str | None`,`run_feature_linking()` 为 `llm_backend: str | None`),使 feature→API 裁决可走任意已注册后端(含 `claude-cli` 订阅鉴权后端),而不被 `detect_backend()` 的自动优先级表锁定为付费 key 后端或名称匹配降级;裁决 LLM callable 的解析优先级 MUST 为:显式 `llm_call` > 显式 `llm_backend`(经 `_call_llm(backend=…)` 包装)> 默认 `_default_llm_call`(`detect_backend`);`detect_backend()` MUST NOT 被本能力改动,`claude-cli` MUST 保持显式 opt-in、不进入自动优先级表。

#### Scenario: 显式指定 claude-cli 后端
- **WHEN** 调用 `build([ext_api, ext_product], feature_llm_backend="claude-cli", ...)` 且本机 `claude` 在 PATH
- **THEN** feature→API 裁决经 `claude -p` 子进程执行,产出的 `implemented_by`/`uses_entity` 边 evidence 为 LLM 裁决支撑句(非 `name-match`)

#### Scenario: 显式后端不可用时降级
- **WHEN** `feature_llm_backend="claude-cli"` 但本机 `claude` 不在 PATH 或 `claude -p` 返回空/异常
- **THEN** 该后端包装 callable 返回 None,系统走既有名称匹配降级路径(≥90 → INFERRED 0.65 evidence="name-match"),构建不中断,GRAPH_REPORT.md 明示降级状态

#### Scenario: 未指定后端保持原行为
- **WHEN** 调用 `build([...])` 未传 `feature_llm_backend`(即 None)
- **THEN** `run_feature_linking` 回落 `_default_llm_call` → `detect_backend()`,行为与变更前逐字节一致(有 key 则裁决,无 key 则名称匹配降级)

#### Scenario: 显式 llm_call 优先级最高
- **WHEN** 库级直接调用 `run_feature_linking(extraction, llm_call=my_callable, llm_backend="claude-cli")`
- **THEN** 使用显式 `llm_call`(`my_callable`),`llm_backend` 被忽略,既有 `llm_call` 注入契约不变

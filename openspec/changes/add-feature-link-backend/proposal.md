## Why

`feature-api-linking` 能力嫁接进 `build()` 时(`build.py` 调 `run_feature_linking(combined)`),只留了 `_default_llm_call` 这一条 LLM 路径:它内部调 `detect_backend()`,而 `detect_backend()` 的自动优先级表(`llm.py`)**不含 `claude-cli`**——`claude-cli` 后端走本机 `claude -p`(Pro/Max 订阅鉴权、无需 API key),但它只在显式 `--backend claude-cli` 时才被选中,`detect_backend()` 永远不会自动返回它。

结果:在只具备 Claude Code 订阅、未配置任何付费 API key 的环境里(本仓库当前环境即如此:只有 `ANTHROPIC_AUTH_TOKEN` + dashscope 端点,`graphify` 的 claude 后端读的是 `ANTHROPIC_API_KEY`,读不到 token → `detect_backend()` 返回 None),`run_feature_linking` **永远走名称匹配降级路径**,feature→API 的 `implemented_by`/`uses_entity` 边无法经 LLM 裁决。

`build()` 已有先例:`dedup_llm_backend` 参数(`build.py:1349`)把一个显式后端名透传给去重的 LLM tiebreaker。feature-link 这层当年嫁接时**唯独没把后端透传出来**——本变更补这个缺口,与 `dedup_llm_backend` 完全对称。

## What Changes

- `build()` 新增 `feature_llm_backend: str | None = None` 关键字参数,镜像 `dedup_llm_backend` 的形态与语义
- `build()` 内 `run_feature_linking(combined)` 调用改为 `run_feature_linking(combined, llm_backend=feature_llm_backend)`
- `run_feature_linking()` 新增 `llm_backend: str | None = None` 关键字参数;裁决 LLM callable 的解析优先级:**显式 `llm_call` > 显式 `llm_backend`(经 `_call_llm(backend=…)` 包装)> 默认 `_default_llm_call`(`detect_backend`)**
- `_call_llm`(`llm.py`)对 `claude-cli` 后端的支持**已存在**(`llm.py:2885-2930`,走 `claude -p`、解析 envelope、返回纯文本 `result`、不要求 API key),本变更不改动它
- **不改 `detect_backend()`**:claude-cli 保持显式 opt-in,不进入自动优先级表,避免把所有 feature-link(以及受 `detect_backend` 影响的其它调用点)无声切到 `claude -p`、产生预期外的订阅用量
- 验证:用 iotda 的 OpenAPI JSON + 产品功能 `.md` 两份独立抽取,在抽取层合并(`build([ext_api, ext_product], feature_llm_backend="claude-cli", …)`),产出含 claude-cli 裁决 feature→API 边的合并图谱

## Capabilities

### Modified Capabilities

- `feature-api-linking`: 新增"显式裁决后端注入"能力——`build()` 与 `run_feature_linking()` 接受一个显式后端名,使 feature→API 裁决可走任意已注册后端(含 `claude-cli` 订阅鉴权后端),而不被 `detect_backend()` 的自动优先级锁定为付费 key 后端或名称匹配降级

### New Capabilities

(无)

## Impact

- 修改:`graphify/build.py`(`build()` 签名加 `feature_llm_backend` + 透传到 `run_feature_linking` 调用)
- 修改:`graphify/feature_link.py`(`run_feature_linking()` 签名加 `llm_backend`;新增 backend→llm_call 解析;`llm_call` 与 `llm_backend` 同时给出时 `llm_call` 优先的优先级语义)
- 不变:`graphify/llm.py`(`_call_llm` 的 claude-cli 分支已存在,不改;`detect_backend()` 不改)
- 不变:默认行为(不传 `feature_llm_backend` 时 → `llm_backend=None` → 回落 `_default_llm_call` → `detect_backend` → 无 key 时名称匹配降级,与变更前完全一致)
- 测试:新增 `run_feature_linking` 的 `llm_backend` 注入用例(stub `_call_llm`)与 `build(feature_llm_backend=…)` 透传用例;既有 feature-link 测试不受影响
- 不变:`references/shared/update.md`(增量路径仍 `build_from_json`,不跑 feature-link)

## Context

`build()`(`graphify/build.py:1344`)是构建期总入口,串起三趟推断:schema canonicalization、op 结构边 + `inferred_entity`、feature-linking,最后 dedup 并委托 `build_from_json`。其中去重那趟已暴露 `dedup_llm_backend` 关键字参数(`build.py:1349`),把一个显式后端名透传给去重的 LLM tiebreaker——这是仓库里"把 LLM 后端名从顶层 API 注入到某趟推断"的既定范式。

feature-linking 这趟(`build.py:1403` 调 `run_feature_linking(combined)`)当年嫁接时**没把后端名透传出来**:`run_feature_linking` 的 `llm_call` 参数确实存在(`feature_link.py:462`),但 `build()` 调它时没传,于是回落到模块内 `_default_llm_call`(`feature_link.py:448`)。`_default_llm_call` 内部调 `detect_backend()`(`llm.py:3103`),而 `detect_backend()` 的自动优先级表**不含 `claude-cli`**——claude-cli 后端走本机 `claude -p`(订阅鉴权、无 API key),只在显式 `backend="claude-cli"` 时被 `_call_llm` 选中(`llm.py:2885`)。

净效应:在只有 Claude Code 订阅、无任何付费 API key 的环境里(`detect_backend()` 返回 None),feature→API 的 `implemented_by`/`uses_entity` 边**永远走名称匹配降级**(`feature_link.py` 的 name-match ≥90 → INFERRED 0.65 evidence="name-match"),LLM 裁决路径形同虚设。本变更把这个透传缺口补上,与 `dedup_llm_backend` 完全对称。

## Goals

- `build()` 顶层可注入 feature-link 裁决后端名,含 `claude-cli` 订阅鉴权后端
- 默认行为(不传新参数)与变更前逐字节一致:回落 `detect_backend` → 无 key 则名称匹配降级
- `run_feature_linking` 既有的 `llm_call` 注入契约不变(库级直接调用者仍可传 callable);新增 `llm_backend` 名注入作为更易用的等价入口
- 不改 `detect_backend()`、不改 `_call_llm` 的 claude-cli 分支(已存在且可用)
- 验证:用真实语料(iotda OpenAPI + iotdm 产品功能 `.md`)在抽取层合并并 `build(…, feature_llm_backend="claude-cli")`,产出含 claude-cli 裁决 feature→API 边的合并图谱

## Non-Goals

- **不**把 `claude-cli` 加入 `detect_backend()` 自动优先级表(会让所有受 `detect_backend` 影响的调用点无声切到订阅用量,且与本变更"显式 opt-in"的设计相悖)
- **不**改 `graphify/skill*.md` 或 skillgen fragments(skill 的 Step 4/5 用 `build([...], root=..., directed=...)`,feature_llm_backend 留 None 即可;skill 路径不需要 feature-link 裁决,产品语义边由 Part B subagent 产出)
- **不**改增量路径 `references/shared/update.md`(走 `build_from_json`,不跑 feature-link,正确不变)
- **不**改图层级 `merge-graphs` CLI(它本就不跨图跑 feature-link;跨层合并的正确做法是抽取层 `build([ext1, ext2])`,本变更让其能显式指定后端)
- **不**实现 feature-link 的批量化/并发 `claude -p` 调用(每功能一次串行调用,慢但正确;并发优化留作后续)

## Decisions

### D1: 镜像 `dedup_llm_backend` 的参数形态

`build()` 新增 `feature_llm_backend: str | None = None`,与 `dedup_llm_backend` 同位、同类型、同默认值。命名遵循既有约定(`*_llm_backend` 后缀)。放在 `dedup_llm_backend` 之后、`root` 之前,保持关键字参数区与现有签名风格一致。

**理由:** 仓库已有这个范式的唯一实例就是 `dedup_llm_backend`;复刻它使新参数零认知成本、零风格分歧,且让"build 的某趟推断可独立指定后端"成为一个一致的模式而非一次性补丁。

### D2: `run_feature_linking` 加 `llm_backend` 名参数(而非只透传 callable)

`run_feature_linking` 既有的 `llm_call: Callable | None` 保留;新增 `llm_backend: str | None = None`。解析优先级:

1. `llm_call is not None` → 直接用(库级直接调用者的既有契约不变)
2. `llm_backend is not None` → 构造一个包装 callable,内部 `from graphify.llm import _call_llm; return _call_llm(prompt, backend=llm_backend, max_tokens=2048)`,异常时返回 `None`(触发既有降级路径)
3. 两者皆 None → `_default_llm_call`(现状)

**理由:** `build()` 持有的是后端**名**(str),不是 callable;若 `build()` 自己构造 callable 再传 `llm_call`,就把 `_call_llm` 的导入与包装逻辑塞进 `build.py`,而那本属 feature-link 模块的职责。让 `run_feature_linking` 接受名并自行解析,职责内聚,且 `feature_llm_backend="claude-cli"` 这种调用对用户最直观。

### D3: 显式后端失败时复用既有降级,不抛错

当 `llm_backend` 给定但该后端不可用(如 `claude-cli` 但 `claude` 不在 PATH、或 `claude -p` 超时/返回空),包装 callable 返回 `None`,`run_feature_linking` 走与"无后端"相同的名称匹配降级路径。不抛异常中断构建。

**理由:** feature-link 是 enrichment 层,失败不应让整个 `build()` 崩;且既有降级路径已有 GRAPH_REPORT.md 明示机制。用户体验:指定 claude-cli 但本机没装 → 静默降级 + 报告标注,而非硬失败。

### D4: 不动 `detect_backend()` 与 `_call_llm` claude-cli 分支

`_call_llm` 的 claude-cli 分支(`llm.py:2885-2930`:跑 `[claude_cmd, "-p", "--output-format", "json", "--no-session-persistence"]`、解析 envelope、返回 `result`、Windows 用 `shutil.which("claude.cmd")`、不要求 key)已完整可用。`detect_backend()` 不改,claude-cli 保持显式 opt-in。

**理由:** `detect_backend()` 被多处调用(Part B 的 Gemini 回落、去重默认、feature-link 默认)。把 claude-cli 塞进自动表会让所有这些路径在装有 Claude Code 的机器上无声切到 `claude -p`——订阅用量不可预测,且违背"订阅鉴权后端应显式选用"的合理预期。显式注入 = 用户知情。

### D5: spec delta 用 ADDED(而非 MODIFIED 降级需求)

新增一条"显式裁决后端注入"需求,含四个场景(显式后端被用 / 显式后端不可用降级 / 未指定保持原行为 / `llm_call` 优先级最高)。既有"无 LLM 后端时的降级路径"需求**不改**:它的措辞"当无任何 LLM 后端可用时"在新语义下仍成立(显式后端不可用 → callable 返 None → 等价"无后端可用" → 走降级),无需重述。

**理由:** ADDED 不与既有需求冲突、不需重述既有需求正文,review 面积最小。

## Risks / Trade-offs

- **claude-cli 调用慢且串行:** 每个有候选的功能发一次 `claude -p` 子进程(冷启动 + 推理)。N 个功能 ≈ N 次串行调用,可能数分钟。**接受:** 正确性优先;缓存(`feature_link.py` 的 content-hash 缓存)使重跑零调用。后续可加并发,但属非目标。
- **订阅用量:** `claude -p` 走 Pro/Max 订阅配额。显式 opt-in(D4)让用户知情;不进自动表避免无声消耗。
- **`claude -p` 输出不稳:** envelope 解析已在 `_call_llm` 处理;若 `result` 为空/非预期 JSON,包装 callable 返 None → 降级(D3)。不致崩。
- **签名扩展的兼容性:** `feature_llm_backend` 是带默认值的关键字参数,既有所有 `build(...)` 调用者不受影响。`run_feature_linking` 同理(`llm_backend` 带默认值)。

## Migration Plan

1. 纯增量、纯加法,无破坏性变更。既有调用点(skill Step 4/5、CLI、增量路径)全部走默认 `None`,行为不变。
2. 想用订阅鉴权做 feature-link 的调用方:`build([ext_api, ext_product], feature_llm_backend="claude-cli", root=..., directed=...)`。
3. 库级直接调用 `run_feature_linking` 的既有代码传 `llm_call=...` 的,继续工作(优先级 1)。
4. 无数据迁移、无配置迁移。

## Open Questions

- feature-link 的 `claude -p` 并发化:留作后续变更(本变更 Non-Goals 明示)。是否需要一个 `feature_llm_concurrency` 参数?暂不引入,YAGNI。
- 是否把 `feature_llm_backend` 也暴露到 CLI(`graphify build --feature-llm-backend claude-cli`)?当前验证走库级 `build()` 调用,CLI 暴露留待有需求时再加。

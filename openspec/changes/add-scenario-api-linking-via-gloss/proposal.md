## Why

`add-scenario-capability-gloss`(变更甲)让 Part B 子代理为每个操作级 `.md` 页面吐一个 `file_type:"feature"` 场景节点,带英文 `capability` gloss(如"删除标签"→`delete tag`)。但场景节点**此刻是悬空的**:变更为止,`run_feature_linking` 的 `_feature_text` **不读 `capability`**——它只组装 feature label + 文件名 + heading + 从 `.md` 正文刮的英文词(`_english_terms`)。

对中文产品文档(iotdm 130 篇 `.md`),这复现了 `feature-link-prescreen-language-gap` 记忆里的同一道墙:scenario 节点的 `fdir` 退化为 `.md` 文件路径本身,`files_by_dir.get(fdir)` 命中空 → 无 page 节点 → 正文不刮 → `_feature_text` 退化成纯中文 label(如"删除标签")。`_prescreen` 的 `bridge = _english_terms(feature_text)` 对纯中文得空串 → 返回 `[]` → 0 候选 → LLM 从不被调用 → 0 边。**gloss 写进了节点,却没被 prescreen 用上**——跨语言桥断在最后一公里。

本变更补上这一公里:`_feature_text` SHALL 把节点上的 `capability` 英文 gloss 纳入 prescreen 输入。由于 `_prescreen` 已用 `_english_terms` 抽取英文词素打分,英文 gloss(如 `delete tag`)直接进 `bridge`,与英文 op_text(如 `DELETE /v5/iot/.../tags/{tag_id}` → `delete tags`)在 fuzz `token_set_ratio` 上命中 → 候选进 top-N → LLM 裁决(或降级名称匹配)→ `implemented_by` 边生成。无新增 LLM pass、无嵌入模型、无 API key——gloss 由变更甲的子代理顺带产出,本变更只是**读它**。

## What Changes

- `graphify/feature_link.py` 的 `_feature_text`:在组装 prescreen 输入时,SHALL 把 `feature.get("capability")`(变更甲场景节点的英文 gloss)加入 parts。英文 gloss 经 `_english_terms` 进入 `_prescreen` 的 `bridge`,使中文操作页的场景节点能与英文 API 路径/资源段跨语言命中。无 `capability` 字段的 feature 节点(目录类目层 dir-feature、旧抽取产物)行为不变(零回归)。
- `run_feature_linking` 返回摘要 SHALL 增加 `unmapped` 计数:预筛后无任何候选(`not cand_ids`)的 feature 数。这是"诚实空"信号——让调用方/测试/未来报告能量化"多少场景无 API 映射、不建边",而非把"未映射"与"未处理"混为一谈。`build()` 当前丢弃返回值,本次不强行接入报告(避免 skillgen 报告层 scope 膨胀);计数 forward-compatible,供测试断言与后续报告接入。
- 既有 `if not cand_ids: continue`(无候选不建边)语义不变,本变更显式断言它(测试):scenario 节点无匹配 API → `unmapped` +1、0 边、不伪造。
- `_prescreen` 与 `_degrade` 的 fuzz 打分 SHALL 改为大小写不敏感(双侧 `.lower()`):实测 `token_set_ratio("delete tag", "DELETE iot instances tags")` = 34(< 60 阈值,0 命中),双侧小写后 = 75(命中)。HTTP 方法约定大写、gloss 小写,大小写敏感会击垮 gloss 桥——这是 prescreen 的潜在健壮性缺陷(老 body-term 桥仅靠"POST"恰好大小写一致才命中),本变更一并修。既有"同形大小写一致"的命中小写后严格保留(零回归)。
- 携带 `capability` 的场景节点 SHALL 走预筛 bypass:对其用 0.0 最低阈值(退化为"仅排序不硬滤",返回 top-N 不滤分),使候选总进 LLM 语义裁决。理由(全语料端到端实测):`token_set_ratio` 是 token 级精确匹配,即使大小写不敏感 + gloss 入 bridge,仍桥不了 (a) 动词词汇差(gloss `add`/`delete`/`send` vs API 名隐含动词,如 `tagDevice`/`createCommand` 里没有 `add`/`send` token),(b) 名词单复数(`tag` vs `tags`),(c) camelCase 复合名不分词(`tagDevice` 不分裂为 `tag`+`device`)。实测 `add tag` 对 `tagDevice` op 仅 ~22 分(< 60),strict 阈值全语料仅产 7 条 feature→API 边、饿死 54/56 scenario;bypass 后 LLM 语义裁决产 92 条边,且对无匹配 API 的 ~9 个 scenario 诚实返 0。无 `capability` 的 dir-feature SHALL 保持 strict 60(无 gloss,fuzz 是其唯一信号,阈值避免每 feature→全 op 淹没 LLM)。`_prescreen` 加 `min_prescreen` 参数,`run_feature_linking` 按 `feat.get("capability")` 选阈值。
- `unmapped` 计数 SHALL 扩展为"评过但 0 边"的统一诚实空计数(预筛饿死 OR LLM 拒判),而非仅"预筛 0 候选"。early-return(有 feature 无 op)也返 `unmapped=len(features)`。这样 bypass 下 LLM 诚实返 0 的 scenario 也被正确计入,与"未处理"仍可区分。
- 不改 `_english_terms` / `_op_text` / `_entity_text` 的文本构造(只在小写化在打分 call-site 做,保持 prompt/显示用的原始文本不变)/ `generate_feature_nodes` / `_is_md_file_node` / LLM 裁决 prompt / 缓存。
- 不改 Part B prompt(属变更甲)。

## Capabilities

### Modified Capabilities

- `feature-api-linking`:MODIFIED "确定性候选预筛"——预筛输入明确纳入操作级场景节点的英文 `capability` gloss 作为跨语言桥信号;中文操作页场景节点凭 gloss 与英文 API 路径命中 top-N,不再因正文无英文词而 0 候选早退。新增"跨语言 gloss 桥命中"场景;强化"无候选不建边"为可计数的诚实空(`unmapped`)。ADDED "操作场景节点预筛绕过"——对带 `capability` 的场景节点用 0.0 阈值(prescreen 退化为仅排序不硬滤,候选总进 LLM 语义裁决以桥接动词汇差/单复数/camelCase 复合名),dir-feature 保持 strict 60。

### New Capabilities

(无)

## Impact

- 修改:`graphify/feature_link.py`(`_feature_text` 读 `capability`;`run_feature_linking` 返回增 `unmapped` 计数 + early-return 同步)
- 不变:`graphify/build.py`(`build` 调 `run_feature_linking` 仍丢弃返回;签名不变);`_prescreen`/`_english_terms`/裁决/缓存/降级
- 不变:Part B prompt(变更甲已落)、skillgen 产物(本变更不动 prompt)
- 默认零回归:无 `capability` 字段的 feature 节点(目录层、旧产物)行为逐字节不变;有 gloss 的场景节点从"悬空"变为可链接
- 依赖:依赖变更甲 `add-scenario-capability-gloss` 产出 `capability` 字段;依赖 `add-feature-link-backend` 的 `feature_llm_backend`(裁决用 `claude-cli` 订阅后端,无 key)
- 验证:单元测试——(a) 带 gloss 的 scenario 节点 → prescreen 命中英文 op → 边生成;(b) 无匹配 API 的 scenario → `unmapped` +1、0 边;端到端见 task #22(iotda+iotdm 合并图谱出 scenario→API 边)

# How graphify works

## The three passes

graphify processes your files in three passes:

**Pass 1 — Code structure (free, no API calls)**
Tree-sitter parses your code files and extracts classes, functions, imports, call graphs, and inline comments. This runs locally with no LLM involved. 25 languages supported. SQL files get special treatment: tables, views, foreign keys, and JOIN relationships are extracted deterministically.

Code files are not sent to the LLM semantic extractor in the normal pipeline. If a corpus contains only code files, Pass 3 is skipped entirely; semantic extraction is reserved for docs, papers, images, and transcripts.

**Pass 2 — Video and audio (local, no API calls)**
Video and audio files are transcribed with faster-whisper. To focus the transcript on your domain, the transcription prompt is seeded with your top god nodes (the most-connected concepts in your code graph so far). Transcripts are cached — re-runs skip already-processed files.

**Pass 3 — Docs, papers, images (Claude subagents, costs tokens)**
Claude runs in parallel over markdown, PDFs, images, and transcripts. Each subagent reads a batch of files and outputs a JSON fragment: nodes, edges, and any group relationships. The fragments are merged into a single graph.

Before Pass 3, optional converters turn supported pointer/binary formats into
Markdown sidecars under `graphify-out/converted/`. Office files (`.docx`,
`.xlsx`) use the `[office]` extra. Google Workspace shortcuts (`.gdoc`,
`.gsheet`, `.gslides`) are opt-in with `--google-workspace` or
`GRAPHIFY_GOOGLE_WORKSPACE=1` and require an authenticated `gws` CLI.

---

## How community detection works

Communities are found using the [Leiden algorithm](https://www.nature.com/articles/s41598-019-41695-z) — a graph-clustering method that groups nodes by edge density. Nodes with many connections between them end up in the same community.

**No embeddings needed.** The semantic similarity edges that Claude extracts (`semantically_similar_to`) are already in the graph, so they influence community shape directly. The graph structure is the similarity signal — there's no separate embedding step or vector database.

---

## Confidence tagging

Every relationship is tagged with one of three labels:

| Tag | Meaning |
|-----|---------|
| `EXTRACTED` | Found directly in the source (e.g. a function call, an import) |
| `INFERRED` | A reasonable inference Claude made, with a `confidence_score` (0.0–1.0) |
| `AMBIGUOUS` | Uncertain — flagged in the report for manual review |

EXTRACTED edges always have confidence 1.0. INFERRED edges use a discrete rubric:
- **0.95** — near-certain (explicit cross-file reference, one plausible target)
- **0.85** — strong evidence (naming + context align)
- **0.75** — reasonable (contextual but not explicit)
- **0.65** — weak (naming similarity only)
- **0.55** — speculative

---

## OpenAPI reverse inference (database entities from API specs)

When the corpus contains OpenAPI/Swagger JSON (any `.json` with an `openapi`/`swagger` version string and a `paths` object), graphify extracts it deterministically — no LLM, no tree-sitter, just `json.loads`:

- **operation nodes** — one per path × HTTP method (`GET /users`, `POST /orders`), carrying the referenced schema names split into `refs_read` (response side) and `refs_write` (request body side)
- **schema / tag nodes** — named schemas (with their property lists, merging `allOf`/`anyOf`/`oneOf` composites) and tags
- **EXTRACTED edges** — `references` (every `$ref`, including nested array/property/composite occurrences), `grouped_under` (operation → tag), `contains` (spec file → node)

The build phase then reverse-infers the **backend database entities** the API implies — the core premise being that a REST backend usually backs one table per resource. This runs after the per-file extractions merge and before dedup, in `api_inference.run_api_entity_inference`:

- **op → op structural edges (cross-file)** — `subpath_of` (EXTRACTED, nested path operation → parent-path operation, same HTTP method preferred) and `shares_schema_with` (INFERRED 0.95, operations referencing the same schema NAME). These are computed at the build tier over the merged op set, NOT per-file in the extractor, so a spec split into one file per endpoint still derives them — the parent-path operation and the shared-schema operation may live in different spec files. Hub schemas referenced by >30 ops are skipped (an ubiquitous ErrorResponse would otherwise form an all-connected blob) and total `shares_schema_with` edges are capped at 800.

- **resource extraction** — paths are split on `/`, `{param}` segments dropped, generic/version segments (`api`, `v1`) removed; the last non-param segment names the resource (`/users/{id}/orders` → `orders`)
- **CRUD merge** — the full CRUD set over one resource collapses into ONE `inferred_entity` node (`devices (inferred)`), carrying `inferred: true` + `file_type: inferred_entity` as honest markers so virtual entities stay distinguishable from real structure in `graph.json` and `GRAPH_REPORT.md`
- **column aggregation** — the union of properties across every schema the resource's operations `$ref`, with `read_columns` / `write_columns` provenance (response vs request side)
- **op → entity edges** — `reads_from` (GET/HEAD/OPTIONS) and `writes_to` (POST/PUT/PATCH/DELETE), INFERRED 0.95
- **entity relations** — `belongs_to` from nested paths (`orders belongs_to users`), upgraded to 0.95 when a schema `$ref` between the two entities' schemas corroborates the nesting (0.85 otherwise); entity `references` from schema `$ref` links not covered by nesting (0.85)
- **RPC exclusion** — verb-segment paths (`/user/delete`, `/devices/batchDeleteUsers`, `.../freeze`) name actions, not resources; they keep their operation nodes but opt out of entity inference

When the corpus also contains real DDL (`.sql` `CREATE TABLE` nodes), reconciliation prefers the real table: operations link to the **real** table node, the inferred columns attach as supplementary `inferred_columns`, and no virtual entity is minted. Unmatched virtual entities survive as-is — no `AMBIGUOUS` noise edges.

Entity node ids are global (`entity_<resource>`), not per-file, so the same resource split across several spec files merges into one entity.

A **schema canonicalization** step (`api_inference.run_api_schema_canonicalization`) runs just before entity inference, merging same-`schema_name` schema nodes that a per-endpoint split corpus produces (each file redefines the schemas it references). For each name, the richest copy becomes the canonical node, the others' properties are folded into a union, edges off the copies are redirected onto the canonical, duplicate `(source, target, relation)` edges are folded, and the copies are deleted. This makes a split corpus (one API, many files) stop fragmenting one logical schema into dozens of isolated nodes — a bundle corpus (single file, no duplicates) is a no-op.

## Feature → interface/entity linking (product-doc directories)

When the corpus also contains **product documentation organized as one subdirectory per feature** (each subdirectory directly holds the `.md` files describing that feature), graphify builds a feature tier on top of the API/entity nodes above (`feature_link.generate_feature_nodes` + `feature_link.run_feature_linking`, run after entity inference, before dedup).

- **Feature nodes are deterministic.** A directory that directly contains `.md` files *is* a feature (any depth); nested feature directories link to their nearest ancestor via `subfeature_of` (EXTRACTED), and each feature links to its docs via `contains` (EXTRACTED). Root-level scattered docs and empty directories get no feature node — directory structure is ground truth, the LLM never participates in feature-node creation.
- **Linking is two-stage and LLM-adjudicated.** For each feature, a deterministic rapidfuzz `token_set_ratio` prescreen shortlists the top-N `api_operation` and `inferred_entity` nodes whose path/segments/columns overlap the feature's doc keywords. The shortlist then goes to the LLM (same multi-backend dispatch as extraction) with a strict JSON contract — `{target_id, relation, confidence_score, evidence}` — and an anti-hallucination whitelist that drops any `target_id` the prescreen did not surface. Links are `implemented_by` (feature → operation) and `uses_entity` (feature → entity), always INFERRED with a discrete `confidence_score` and a mandatory `evidence` quote from the docs; LLM self-ratings below the rubric floor become AMBIGUOUS and surface in `GRAPH_REPORT.md` for review.
- **Cross-lingual bridge.** Feature names are often Chinese while paths/table names are English — there is no shared lexeme. The prescreen therefore scores on the English technical terms the doc *bodies* mention (API paths, protocol and table names), which bridge the Chinese feature name to the English path tokens.
- **Degradation without an LLM.** When no backend is configured, a name-match path takes over: a candidate whose English overlap with the feature text scores ≥ 90 becomes an INFERRED 0.65 edge with `evidence: "name-match"`; below 90 no edge is built. This is honest — a Chinese feature doc with no English path tokens in its body produces zero edges rather than invented ones. `GRAPH_REPORT.md` flags these runs as lexical-only.
- **Dual-hash cache.** Each adjudication result is cached under a key hashing both the feature's doc text and the candidate shortlist, so reruns are free and a changed candidate set correctly invalidates.

`query`, `path`, and `explain` traverse the new edges with no code change — "which interfaces does this feature touch" is now a graph walk from the feature node.

---

## Token benchmark

The first run extracts and builds the graph — this costs tokens. Every subsequent query reads the compact graph instead of raw files. That's where the savings compound.

On a mixed corpus (Karpathy repos + 5 papers + 4 images, 52 files): **71.5x fewer tokens per query** vs reading the raw files directly.

| Corpus | Files | Reduction |
|--------|-------|-----------|
| Karpathy repos + papers + images | 52 | **71.5x** |
| graphify source + Transformer paper | 4 | **5.4x** |
| httpx (synthetic Python library) | 6 | ~1x |

Token reduction scales with corpus size. Six files already fits in a context window — the graph value there is structural clarity, not compression. At 52 files the savings compound quickly.

Each `worked/` folder in the repo has the raw input files and actual output (`GRAPH_REPORT.md`, `graph.json`) so you can run it yourself and verify.

---

## Parallel extraction

Code files are extracted in parallel using `ProcessPoolExecutor` — bypasses Python's GIL for genuine multiprocessing. Doc/paper/image batches are dispatched as parallel Claude subagents. On a corpus of 84 code files, parallel AST extraction runs in about 1.66x less time than sequential.

---

## SHA256 cache

Every extracted file is fingerprinted by content hash. Re-runs skip unchanged files entirely — only new or modified files go through extraction again. The cache lives in `graphify-out/cache/`.

---

## The graph format

The output `graph.json` uses NetworkX's node-link format. Each node has:
- `id` — stable identifier
- `label` — human-readable name
- `file_type` — `code`, `document`, `paper`, `image`, `rationale`
- `source_file` — where it came from

See [RFC: file-level node summaries](node-summaries-rfc.md) for two proposed
ways to add compact optional summaries for AI navigation.

Each edge has:
- `source`, `target` — node IDs
- `relation` — verb phrase (e.g. `calls`, `imports`, `implements`, `semantically_similar_to`)
- `confidence` — `EXTRACTED`, `INFERRED`, or `AMBIGUOUS`
- `confidence_score` — float (INFERRED only)
- `source_file` — where the relationship was found

Hyperedges (group relationships connecting 3+ nodes) live in `G.graph["hyperedges"]`.

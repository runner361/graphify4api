"""Feature -> API operation / database entity linking (#add-feature-api-linking).

A build-tier pass over the merged extraction, run AFTER entity inference
(#add-openapi-extractor) and BEFORE dedup, so feature nodes and their
``implemented_by`` / ``uses_entity`` edges flow through dedup and clustering
like any other product.

Two stages:

1. :func:`generate_feature_nodes`
   Markdown file nodes are grouped by the directory that DIRECTLY contains
   them (design D1: any depth). Each such directory becomes one feature node
   (``file_type "feature"``); its ``.md`` file nodes attach via ``contains``
   (EXTRACTED). Parent<->child pairs of directly-doc-bearing directories yield
   ``subfeature_of`` (EXTRACTED, child -> nearest ancestor feature dir). Root-
   level scattered docs and empty dirs get no feature node. Directory structure
   is ground truth — the LLM never participates in feature-node creation.

2. :func:`run_feature_linking`
   For each feature: a deterministic rapidfuzz prescreen
   (``token_set_ratio`` of feature name + doc heading keywords against
   ``api_operation`` nodes — path resource segments + HTTP method — and
   entity nodes — name + ``inferred_columns``); keep top-N. Then either
   LLM-adjudicate the candidates (contract: ``{target_id, relation,
   confidence_score, evidence}``; anti-hallucination whitelist drops any
   ``target_id`` not in the candidate set; confidence snapped to the discrete
   rubric), or, with no LLM backend, degrade: name-match score >= 90 ->
   INFERRED 0.65 edge with ``evidence "name-match"``.

Honesty contract (project tenet "not a vector index", honest audit trail):
feature nodes + structural edges are EXTRACTED (directory ground truth);
linking edges are INFERRED with a discrete ``confidence_score`` and a
mandatory ``evidence`` attribute; LLM self-rated < 0.55 candidates become
AMBIGUOUS and surface in GRAPH_REPORT.md for manual review.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePath

# --- prescreen / rubric constants ---------------------------------------

# Discrete confidence rubric shared with the semantic extractor
# (references/extraction-spec.md). LLM self-ratings are snapped to the nearest
# legal value; anything below the floor becomes AMBIGUOUS.
_CONFIDENCE_RUBRIC = (0.95, 0.85, 0.75, 0.65, 0.55)
_AMBIGUOUS_FLOOR = 0.55

_TOP_N = 20              # max candidates per feature sent to the LLM (D2)
_MIN_PRESCREEN = 60.0    # below this a candidate is not worth the LLM's time
_NAME_MATCH_THRESHOLD = 90.0  # degradation: >= this -> 0.65 name-match edge (D6)
# Scenario nodes (file_type "feature" with a `capability` gloss) carry a
# structured English verb+noun bridge that token-level fuzz cannot exploit:
# API op names are camelCase compounds (tagDevice, createCommand) that don't
# split into the gloss's words, nouns differ in number (tag vs tags), and the
# gloss verb (add/delete/send) rarely appears as a standalone token in the op
# text. A >=60 hard gate therefore starves the LLM of correct candidates
# (empirically 19-22 for `delete tag` vs the tag ops). For scenario nodes
# prescreen only RANKS (returns top-N by score) and never gates -- the LLM
# adjudicator, which reads semantics, decides. Validated end-to-end on the full
# iotdm+iotda corpus: strict 60 -> 7 feature->API/entity edges; scenario bypass
# -> 92, nearly all correct, with the LLM honestly returning 0 for the ~9
# scenarios that have no matching API (delete tag/deploy plugin/reset credential)
# (#add-scenario-api-linking-via-gloss). dir-features keep the 60 gate -- they
# have no gloss, so fuzz is their only signal and the gate avoids flooding the
# LLM with Chinese-label -> all-ops calls.
_SCENARIO_MIN_PRESCREEN = 0.0

_MD_EXTS = (".md", ".mdx", ".qmd", ".skill")
_RELATIONS = ("implemented_by", "uses_entity")


# --- id / text helpers ---------------------------------------------------


def _slug(text: str) -> str:
    """Path/label -> a stable node-id slug (mirrors the project's make_id:
    lowercase, runs of non-word chars -> ``_``, unicode word chars kept so
    Chinese feature names survive)."""
    return re.sub(r"\W+", "_", str(text).strip().lower()).strip("_") or "_"


def _is_md_file_node(n: dict) -> bool:
    """True for a markdown *page* (file) node — the node representing the .md
    file itself, not a heading/concept node extracted from its body.

    The markdown extractor stamps every node with ``file_type "document"`` and
    the page node's ``label`` is the source filename; heading nodes carry the
    heading text as label. ``label == PurePath(source_file).name`` + a markdown
    extension picks exactly the page nodes."""
    if n.get("file_type") != "document":
        return False
    sf = n.get("source_file") or ""
    if not sf.lower().endswith(_MD_EXTS):
        return False
    return n.get("label") == PurePath(sf).name


def _feature_dir(source_file: str) -> str:
    """The directory that directly contains a doc, as a posix-relative
    string (normalises Windows backslashes)."""
    return PurePath(source_file).parent.as_posix()


def _dir_name(dir_posix: str) -> str:
    """Final path segment of a directory — the feature's human label."""
    return PurePath(dir_posix).name or dir_posix


def _feature_id(dir_posix: str) -> str:
    return _slug(dir_posix) + "_feature"


# --- stage 1: feature node generation (deterministic) --------------------


def generate_feature_nodes(extraction: dict) -> dict:
    """Mutate ``extraction`` in place: emit feature nodes + ``contains`` +
    ``subfeature_of`` edges from the directory structure of markdown page
    nodes. No-op when the corpus has no markdown docs in subdirectories
    (root-level scattered docs get no feature node, per D1).

    Returns a summary ``{features, contains, subfeature_of}``.
    """
    nodes: list[dict] = extraction.get("nodes", [])  # type: ignore[assignment]
    edges: list[dict] = extraction.get("edges", [])  # type: ignore[assignment]

    # group markdown page nodes by their immediate directory
    files_by_dir: dict[str, list[dict]] = {}
    for n in nodes:
        if _is_md_file_node(n):
            d = _feature_dir(n["source_file"])
            # D1: a doc sitting directly at the corpus root (parent is "." or
            # empty) is a scattered doc, not a feature directory — skip it so
            # root-level notes don't spawn a feature node.
            if d in ("", "."):
                continue
            files_by_dir.setdefault(d, []).append(n)

    if not files_by_dir:
        return {"features": 0, "contains": 0, "subfeature_of": 0}

    feature_dirs = set(files_by_dir)
    made_contains = 0
    made_sub = 0
    seen_edges: set[tuple] = set()

    def _add_edge(src: str, tgt: str, relation: str) -> None:
        key = (src, tgt, relation)
        if key in seen_edges:
            return
        seen_edges.add(key)
        edges.append({
            "source": src, "target": tgt, "relation": relation,
            "confidence": "EXTRACTED", "source_file": src,
            "source_location": None, "_origin": "ast", "weight": 1.0,
        })

    for d, file_nodes in files_by_dir.items():
        fid = _feature_id(d)
        nodes.append({
            "id": fid, "label": _dir_name(d), "file_type": "feature",
            "source_file": d + "/", "source_location": None,
            "_origin": "ast", "feature_dir": d,
            "doc_count": len(file_nodes),
        })
        for fn in file_nodes:
            _add_edge(fid, fn["id"], "contains")
            made_contains += 1

    # subfeature_of: each feature -> its nearest ancestor feature dir.
    for d in feature_dirs:
        child = _feature_id(d)
        ancestor = _nearest_ancestor_feature(d, feature_dirs)
        if ancestor is not None:
            _add_edge(child, _feature_id(ancestor), "subfeature_of")
            made_sub += 1

    return {"features": len(feature_dirs), "contains": made_contains,
            "subfeature_of": made_sub}


def _nearest_ancestor_feature(dir_posix: str, feature_dirs: set[str]) -> str | None:
    """Walk parents of ``dir_posix`` until one is itself a feature dir
    (directly bears .md). Returns that dir's posix path, or None."""
    parent = PurePath(dir_posix).parent.as_posix()
    while parent and parent != dir_posix:
        if parent in feature_dirs:
            return parent
        up = PurePath(parent).parent.as_posix()
        if up == parent:
            break
        parent = up
    return None


# --- stage 2 prescreen: deterministic candidate shortlist ----------------


def _op_text(n: dict) -> str:
    """Candidate text for an api_operation: method + path resource segments."""
    parts = []
    method = n.get("http_method")
    if method:
        parts.append(method)
    path = n.get("api_path") or ""
    if path:
        parts.append(path)
        # resource segments (drop {params}, drop version/stopwords) so
        # `/users/{id}/orders` contributes `users orders`. Version filter is
        # a regex (v\\d+) so v5/v6 etc. — the real IoTDM paths use v5 — are
        # dropped, not just the v1/v2/v3 the early spec hardcoded.
        for seg in path.split("/"):
            if not seg or seg.startswith("{"):
                continue
            low = seg.lower()
            if low == "api" or re.match(r"v\d+$", low):
                continue
            parts.append(seg)
    if not parts:
        parts.append(n.get("label", ""))
    return " ".join(parts)


def _entity_text(n: dict) -> str:
    """Candidate text for an inferred_entity / reconciled real table."""
    parts = [n.get("label", "")]
    cols = n.get("inferred_columns") or n.get("read_columns") or n.get("write_columns")
    if cols:
        parts.append(" ".join(str(c) for c in cols))
    return " ".join(parts)


def _english_terms(text: str) -> str:
    """Latin-word runs of length >= 3 from ``text`` — the cross-lingual
    bridge signal (D7). Chinese feature names share no lexeme with English
    path/table tokens, but the doc *body* mentions API paths, protocol names
    and table names in English; those tokens are what prescreen matches on."""
    return " ".join(re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text or ""))


def _feature_text(feature: dict, file_nodes: list[dict],
                  doc_nodes: list[dict]) -> str:
    """Prescreen input: feature name + doc filenames + heading/section labels
    under the feature's files + English technical terms scraped from the doc
    bodies (D7: the body terms bridge Chinese feature names to English
    path/table tokens — without them prescreen can't surface cross-lingual
    candidates and the LLM never gets a shortlist).

    For operation-scenario feature nodes (file_type "feature" emitted by Part B
    per add-scenario-capability-gloss), the node carries an English
    ``capability`` gloss (e.g. "delete tag") distilled from the page. That gloss
    IS the cross-lingual bridge for these nodes — their ``fdir`` degrades to
    the ``.md`` path itself (no dir-keyed page nodes), so body scraping yields
    nothing for them; the gloss replaces it. Appended here so ``_prescreen``'s
    ``_english_terms`` bridge picks it up and matches English op_text. Nodes
    without ``capability`` (dir-category features, legacy extractions) append
    nothing — zero regression."""
    parts = [feature.get("label", "")]
    cap = feature.get("capability")
    if cap:
        parts.append(cap)
    for fn in file_nodes:
        parts.append(PurePath(fn.get("source_file", "")).stem)
    # heading/concept nodes whose source_file lives under this feature
    fids = {fn["id"] for fn in file_nodes}
    body_terms: list[str] = []
    for dn in doc_nodes:
        sf = dn.get("source_file") or ""
        if _feature_dir(sf) == feature.get("feature_dir"):
            if dn.get("id") not in fids and dn.get("label"):
                parts.append(dn["label"])
    # scrape English terms straight from the .md bodies
    for fn in file_nodes:
        sf = fn.get("source_file") or ""
        try:
            text = Path(sf).read_text(encoding="utf-8", errors="ignore")
        except (OSError, ValueError):
            text = ""
        t = _english_terms(text)
        if t:
            body_terms.append(t)
    parts.extend(body_terms)
    return " ".join(p for p in parts if p)


def _prescreen(feature_text: str, candidates: list[tuple[dict, str]],
               top_n: int = _TOP_N,
               min_prescreen: float = _MIN_PRESCREEN) -> list[dict]:
    """rapidfuzz token_set_ratio shortlist. ``candidates`` is a list of
    ``(node, candidate_text)``. Returns up to ``top_n`` nodes scoring >=
    ``min_prescreen``, highest first. ``min_prescreen`` defaults to the strict
    ``_MIN_PRESCREEN`` gate; callers pass ``_SCENARIO_MIN_PRESCREEN`` (0.0) for
    scenario nodes so prescreen only ranks top-N and never gates -- letting the
    LLM adjudicate verb/number/compound-name gaps fuzz can't bridge.

    Scoring uses only the English-termlink subset of ``feature_text``: the
    feature name is usually Chinese and shares no lexeme with English path /
    table tokens, so scoring the full (Chinese-dominated) text would bury the
    cross-lingual bridge signal (D7). The English body terms — API paths,
    protocol and table names the docs mention — are what actually matches."""
    bridge = _english_terms(feature_text)
    if not bridge:
        return []
    try:
        from rapidfuzz import fuzz
    except ImportError:  # pragma: no cover - rapidfuzz is a core dep
        return [c[0] for c in candidates[:top_n]]
    scored = []
    # Case-insensitive: HTTP methods are conventionally uppercase (DELETE/POST),
    # capability glosses and doc-body terms are lowercase, and path segments
    # are lowercase. A case-sensitive token_set_ratio would miss the obvious
    # `delete tag` (gloss) <-> `DELETE ... tags` (op_text) overlap that the
    # cross-lingual gloss bridge exists to surface (#add-scenario-api-linking).
    bridge_l = bridge.lower()
    for node, ctxt in candidates:
        score = fuzz.token_set_ratio(bridge_l, ctxt.lower())
        if score >= min_prescreen:
            scored.append((score, node))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [n for _, n in scored[:top_n]]


# --- stage 2 LLM adjudication --------------------------------------------


_PROMPT_HEADER = (
    "You are a linkage adjudicator. Given a product feature and a shortlist "
    "of API operations / database entities (candidates), decide which the "
    "feature is implemented by or uses. Output ONLY a JSON array. Each "
    "element: {\"target_id\", \"relation\": implemented_by|uses_entity, "
    "\"confidence_score\": 0.95|0.85|0.75|0.65|0.55, \"evidence\": <verbatim "
    "phrase from the feature docs justifying the link>}. Omit unrelated "
    "candidates. Never invent target_ids outside the candidate list."
)


def _build_prompt(feature: dict, op_cands: list[dict],
                  ent_cands: list[dict], feature_text: str = "") -> str:
    # feature_text is the assembled prescreen input (feature name + doc
    # headings + body English terms); hand it to the LLM verbatim so the
    # adjudicator sees the same bridge signal prescreen scored on, not a
    # bare directory label.
    lines = [_PROMPT_HEADER, "", "FEATURE:", feature.get("label", ""),
             "DOCS:", feature_text[:4000], "", "CANDIDATES:"]
    for n in op_cands:
        lines.append(f"- id={n['id']} kind=operation label={n.get('label','')} "
                     f"method={n.get('http_method','')} path={n.get('api_path','')}")
    for n in ent_cands:
        lines.append(f"- id={n['id']} kind=entity label={n.get('label','')} "
                     f"columns={n.get('inferred_columns') or []}")
    lines.append("JSON:")
    return "\n".join(lines)


def _snap_confidence(value) -> float | None:
    """Snap an arbitrary LLM confidence to the nearest legal rubric value.
    Below the floor -> None (caller routes to AMBIGUOUS)."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v < _AMBIGUOUS_FLOOR:
        return None
    return min(_CONFIDENCE_RUBRIC, key=lambda r: abs(r - v))


def _extract_json_array(raw: str) -> list:
    """Best-effort pull of a JSON array out of an LLM text reply (handles
    fenced code blocks and surrounding prose)."""
    if not raw:
        return []
    # strip ``` fences
    fenced = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", raw, re.S)
    if fenced:
        raw = fenced.group(1)
    # fall back to the first balanced [...] span
    if "[" not in raw:
        return []
    start = raw.index("[")
    depth = 0
    for i in range(start, len(raw)):
        if raw[i] == "[":
            depth += 1
        elif raw[i] == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(raw[start:i + 1])
                except json.JSONDecodeError:
                    return []
    return []


def _parse_adjudication(raw: str, candidate_ids: set[str]) -> list[dict]:
    """Parse + anti-hallucination validate the LLM reply. Drops any item whose
    ``target_id`` is not in the candidate whitelist, whose relation is illegal,
    or whose evidence is missing. Snaps confidence to the rubric; sub-floor
    items become AMBIGUOUS. Returns a list of edge-dict payloads:
    ``{target_id, relation, confidence_score, confidence, evidence}``."""
    out = []
    for item in _extract_json_array(raw):
        if not isinstance(item, dict):
            continue
        tid = item.get("target_id")
        rel = item.get("relation")
        if tid not in candidate_ids or rel not in _RELATIONS:
            continue  # hallucinated target or illegal relation -> drop
        evidence = item.get("evidence")
        if not evidence:
            continue  # evidence is mandatory
        snapped = _snap_confidence(item.get("confidence_score"))
        if snapped is None:
            out.append({"target_id": tid, "relation": rel,
                        "confidence_score": 0.3, "confidence": "AMBIGUOUS",
                        "evidence": str(evidence), "_origin": "semantic"})
        else:
            out.append({"target_id": tid, "relation": rel,
                        "confidence_score": snapped, "confidence": "INFERRED",
                        "evidence": str(evidence), "_origin": "semantic"})
    return out


def _degrade(op_cands: list[dict], ent_cands: list[dict], feature_text: str
             ) -> list[dict]:
    """No-LLM degradation path (D6): name-match >= 90 -> INFERRED 0.65 edge
    with ``evidence "name-match"``. Below 90 -> no edge. Scores on the English
    bridge subset (same cross-lingual rationale as :func:`_prescreen`)."""
    bridge = _english_terms(feature_text)
    if not bridge:
        return []
    try:
        from rapidfuzz import fuzz
    except ImportError:  # pragma: no cover
        return []
    out = []
    bridge_l = bridge.lower()
    for n in op_cands + ent_cands:
        ctxt = _op_text(n) if n.get("file_type") == "api_operation" else _entity_text(n)
        if fuzz.token_set_ratio(bridge_l, ctxt.lower()) >= _NAME_MATCH_THRESHOLD:
            rel = "implemented_by" if n.get("file_type") == "api_operation" else "uses_entity"
            out.append({"target_id": n["id"], "relation": rel,
                        "confidence_score": 0.65, "confidence": "INFERRED",
                        "evidence": "name-match", "_origin": "ast"})
    return out


# --- cache (dual hash: feature doc text + candidate set) -----------------


def _cache_key(feature_text: str, candidate_ids: list[str]) -> str:
    fh = hashlib.sha256(feature_text.encode("utf-8")).hexdigest()[:16]
    ch = hashlib.sha256("\n".join(sorted(candidate_ids)).encode("utf-8")).hexdigest()[:16]
    return f"{fh}_{ch}"


def _cache_path(cache_root, key: str):
    from pathlib import Path
    return Path(cache_root) / "feature-linking" / f"{key}.json"


def _load_cache(cache_root, key: str) -> list[dict] | None:
    p = _cache_path(cache_root, key)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            return data.get("edges")
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _save_cache(cache_root, key: str, edges: list[dict]) -> None:
    p = _cache_path(cache_root, key)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"edges": edges}, ensure_ascii=False),
                     encoding="utf-8")
    except OSError:
        pass  # cache is best-effort; never fail the build over it


# --- orchestration -------------------------------------------------------


def _default_llm_call(prompt: str) -> str | None:
    """Use llm.py's raw-prompt entry + detected backend. Returns None when no
    backend is configured (caller degrades). Local import keeps the module's
    import graph acyclic (llm.py lives at the heavy LLM tier)."""
    from graphify.llm import _call_llm, detect_backend  # type: ignore
    backend = detect_backend()
    if backend is None:
        return None
    try:
        return _call_llm(prompt, backend=backend, max_tokens=2048)
    except Exception:
        return None


def run_feature_linking(
    extraction: dict,
    *,
    llm_call=None,
    llm_backend: str | None = None,
    top_n: int = _TOP_N,
    cache_root=None,
) -> dict:
    """Mutate ``extraction`` in place: for each feature node, prescreen + LLM
    adjudicate (or degrade) against the corpus's api_operation / entity nodes,
    appending ``implemented_by`` / ``uses_entity`` INFERRED edges. No-op when
    there are no feature nodes (run :func:`generate_feature_nodes` first) or no
    API/entity targets to link.

    ``llm_call``: optional ``(prompt: str) -> str | None`` for tests to inject
    a stub backend. Defaults to the real llm.py dispatch; when no backend is
    configured the degradation path runs.

    ``llm_backend``: optional explicit backend name (e.g. "claude-cli",
    "gemini", "kimi") routed through llm.py's ``_call_llm``. Resolution
    precedence: explicit ``llm_call`` > explicit ``llm_backend`` > the
    ``detect_backend`` default (``_default_llm_call``). ``claude-cli`` lets a
    caller route adjudication through the local ``claude -p`` subscription
    backend (no API key) instead of relying on ``detect_backend``, which never
    auto-selects it. When an explicit backend is unavailable the wrapper
    returns None and the degradation path runs (no hard failure).
    """
    nodes: list[dict] = extraction.get("nodes", [])  # type: ignore[assignment]
    edges: list[dict] = extraction.get("edges", [])  # type: ignore[assignment]

    features = [n for n in nodes if n.get("file_type") == "feature"]
    ops = [n for n in nodes if n.get("file_type") == "api_operation"]
    entities = [n for n in nodes
                if n.get("file_type") == "inferred_entity"
                or n.get("inferred_columns") is not None]
    if not features or (not ops and not entities):
        # features exist but nothing to map them to -> all unmapped (honest empty)
        return {"features": len(features), "edges": 0, "llm": False,
                "unmapped": len(features)}

    if cache_root is None:
        cache_root = "graphify-out/cache"
    if llm_call is None:
        if llm_backend is not None:
            # Explicit backend name (e.g. "claude-cli") → wrap _call_llm so the
            # caller need only pass a str, not a callable. Exceptions (backend
            # missing, claude -p empty/timeout) → None → degradation path.
            from graphify.llm import _call_llm  # type: ignore
            _backend = llm_backend

            def llm_call(prompt: str, _b=_backend) -> str | None:
                try:
                    return _call_llm(prompt, backend=_b, max_tokens=2048)
                except Exception:
                    return None
        else:
            llm_call = _default_llm_call

    op_cand_pairs = [(n, _op_text(n)) for n in ops]
    ent_cand_pairs = [(n, _entity_text(n)) for n in entities]
    all_doc_nodes = [n for n in nodes if n.get("file_type") == "document"]

    # index file nodes by id for feature-text assembly
    file_nodes_by_id = {n["id"]: n for n in nodes if _is_md_file_node(n)}
    # file nodes grouped by feature dir (mirrors generate_feature_nodes)
    files_by_dir: dict[str, list[dict]] = {}
    for n in nodes:
        if _is_md_file_node(n):
            files_by_dir.setdefault(_feature_dir(n["source_file"]), []).append(n)

    made = 0
    used_llm = False
    unmapped = 0  # features that produced 0 edges -- prescreen-starved OR
                  # LLM-adjudicated-and-rejected. Honest-empty count: a feature
                  # here reached no API/entity mapping (#add-scenario-api-linking).
    seen_edges: set[tuple] = set()

    def _emit(feature_id: str, payload: dict) -> None:
        key = (feature_id, payload["target_id"], payload["relation"])
        if key in seen_edges:
            return
        seen_edges.add(key)
        edges.append({
            "source": feature_id, "target": payload["target_id"],
            "relation": payload["relation"], "confidence": payload["confidence"],
            "confidence_score": payload["confidence_score"],
            "source_file": feature_id, "source_location": None,
            "evidence": payload["evidence"], "_origin": payload.get("_origin", "ast"),
            "weight": 1.0,
        })

    for feat in features:
        fdir = feat.get("feature_dir") or (feat.get("source_file", "").rstrip("/"))
        ftext = _feature_text(feat, files_by_dir.get(fdir, []), all_doc_nodes)
        # Scenario nodes carry an English `capability` gloss; token-level fuzz
        # can't bridge verb/number/compound-name gaps to the API (add<->tagDevice,
        # tag<->tags), so don't hard-gate them. Let prescreen rank top-N and the
        # LLM adjudicate. dir-features keep the strict 60 gate (no gloss -> fuzz
        # is their only signal).
        pthresh = _SCENARIO_MIN_PRESCREEN if feat.get("capability") else _MIN_PRESCREEN
        op_cands = _prescreen(ftext, op_cand_pairs, top_n, min_prescreen=pthresh)
        ent_cands = _prescreen(ftext, ent_cand_pairs, top_n, min_prescreen=pthresh)
        cand_ids = {n["id"] for n in op_cands + ent_cands}
        if not cand_ids:
            unmapped += 1
            continue

        ckey = _cache_key(ftext, sorted(cand_ids))
        cached = _load_cache(cache_root, ckey)
        if cached is not None:
            for payload in cached:
                _emit(feat["id"], payload)
                made += 1
            if not cached:
                unmapped += 1   # cached honest-empty adjudication
            continue

        prompt = _build_prompt(feat, op_cands, ent_cands, ftext)
        raw = llm_call(prompt)
        if raw is not None:
            used_llm = True
            payloads = _parse_adjudication(raw, cand_ids)
        else:
            payloads = _degrade(op_cands, ent_cands, ftext)
        for payload in payloads:
            _emit(feat["id"], payload)
            made += 1
        if not payloads:
            unmapped += 1   # adjudicated but no mapping found (honest empty)
        _save_cache(cache_root, ckey, payloads)

    return {"features": len(features), "edges": made, "llm": used_llm,
            "unmapped": unmapped}

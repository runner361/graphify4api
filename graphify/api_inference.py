"""Build-tier reverse inference of backend database entities from OpenAPI
extraction products (#add-openapi-extractor).

Deterministic, LLM-free fold executed by ``build()`` after the per-file
extractions merge and before dedup. The premise: a REST backend usually
backs ONE table per resource, so the full CRUD set over a path resource
(GET/POST /users, GET/PUT/DELETE /users/{id}, ...) collapses into ONE
``inferred_entity`` node per resource, carrying:

* ``inferred: True`` + ``file_type: "inferred_entity"`` — honest markers so
  virtual entities stay distinguishable from real structure in graph.json
  and GRAPH_REPORT.md
* ``inferred_columns`` — union of the properties of every schema the
  resource's operations $ref, with ``read_columns`` / ``write_columns``
  provenance (response side vs request side)
* ``reads_from`` / ``writes_to`` edges from each operation (INFERRED 0.95 —
  the spec is evidence, the table is the inference)
* ``belongs_to`` entity relations from nested paths (/users/{id}/orders ->
  orders belongs_to users), upgraded to 0.95 when a schema $ref between the
  two entities' schemas corroborates the nesting (0.85 otherwise)
* entity ``references`` from schema $ref links not already covered by a
  belongs_to (INFERRED 0.85)

Entity node ids are GLOBAL (``entity_<resource>``), not stem-prefixed:
the whole point of running at build tier is that the same resource split
across several spec files merges into one entity.

When the corpus also contains real DDL (.sql table nodes), reconciliation
prefers the real table (#add-openapi-extractor D7): operations link to the
REAL table node, the inferred columns attach to it as ``inferred_columns``
supplementary evidence, and no virtual entity is minted. Unmatched virtual
entities survive as-is — no AMBIGUOUS noise edges.
"""
from __future__ import annotations

import re

from graphify.extractors.base import _make_id

try:  # hard dependency (pyproject), guard keeps unit tests importable anywhere
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover
    fuzz = None

# Path segments that never name a resource.
_GENERIC_SEGMENTS = frozenset({"api", "apis", "rest", "service", "services",
                               "gateway", "openapi", "swagger"})
_VERSION_SEG = re.compile(r"^v\d", re.IGNORECASE)
_STOP_SEGMENTS = frozenset({
    "health", "ping", "metrics", "status", "version", "versions", "info",
    "heartbeat", "favicon.ico", "index", "home", "root", "me", "self",
    "swagger", "doc", "docs", "schema", "schemas",
})
# RPC-style verb segments: /user/delete, /batchDeleteUsers, /devices/bind.
# Such paths name ACTIONS, not resources — they keep their operation nodes
# but opt out of entity inference entirely.
_RPC_VERBS = frozenset({
    "get", "list", "find", "search", "fetch", "query", "count", "batch",
    "bulk", "create", "add", "new", "update", "edit", "modify", "set",
    "delete", "remove", "destroy", "drop", "cancel", "confirm", "approve",
    "reject", "check", "verify", "validate", "calc", "calculate", "compute",
    "generate", "parse", "convert", "transform", "import", "export",
    "upload", "download", "send", "receive", "push", "pull", "notify",
    "publish", "subscribe", "bind", "unbind", "register", "unregister",
    "login", "logout", "auth", "authenticate", "authorize", "refresh",
    "reset", "retry", "sync", "migrate", "clone", "copy", "move",
    "duplicate", "archive", "restore", "activate", "deactivate", "start",
    "stop", "run", "exec", "execute", "call", "invoke", "trigger", "close",
    "open", "enable", "disable", "test",
    # action-style verbs observed in real specs (IoTDM) — a path segment that
    # names an operation, not a resource, must not mint a phantom entity.
    "action", "actions", "freeze", "unfreeze", "reboot", "restart",
    "shutdown", "lock", "unlock", "suspend", "resume", "renew", "resend",
    "pay", "refund", "charge", "submit", "apply", "assign", "revoke",
    "grant", "switch", "toggle", "rebuild", "deploy", "undeploy",
})
_CAMEL_VERB_RE = re.compile(
    r"^(?:" + "|".join(sorted(_RPC_VERBS)) + r")[A-Z0-9]")

_FUZZ_TABLE_THRESHOLD = 90

# --- op-op structural edge caps (moved here from the extraction tier so the
# --- pairing spans spec files; a per-endpoint split corpus still derives
# --- these edges) ---
_MAX_SHARE_EDGES = 800
# A schema referenced by more ops than this is a hub (e.g. the ubiquitous
# ErrorResponse): pairwise shares_schema_with over it carries no signal.
_HUB_SCHEMA_OPS = 30


def _is_rpc_segment(seg: str) -> bool:
    low = seg.lower()
    if low in _RPC_VERBS:
        return True
    # token forms: user-delete, delete_user
    if len(re.split(r"[-_.]", low)) > 1 and any(
            t in _RPC_VERBS for t in re.split(r"[-_.]", low)):
        return True
    # camelCase verb prefix: batchDeleteUsers, queryDeviceStatus
    return bool(_CAMEL_VERB_RE.match(seg))


def _path_resource(api_path: str) -> tuple[str | None, str | None]:
    """(resource, parent_resource) from an operation path, (None, None) when
    the path is RPC-style / param-only / generic.

    /api/v1/users      -> ("users", None)
    /users/{id}/orders -> ("orders", "users")
    /users/{id}        -> ("users", None)
    /user/delete       -> (None, None)   # RPC verb segment
    """
    segs = [s for s in api_path.split("/")
            if s and not (s.startswith("{") and s.endswith("}"))]
    segs = [s for s in segs
            if s.lower() not in _GENERIC_SEGMENTS and not _VERSION_SEG.match(s)]
    if not segs:
        return None, None
    if any(_is_rpc_segment(s) for s in segs):
        return None, None
    resource = segs[-1]
    if resource.lower() in _STOP_SEGMENTS:
        return None, None
    parent = segs[-2] if len(segs) >= 2 else None
    return resource, parent


def _norm_name(name: str) -> str:
    """Comparison form of a table/resource name: lowercase, drop schema
    qualifiers (public.users -> users), squeeze separators."""
    n = str(name).lower().strip().strip('`"[]')
    n = n.rsplit(".", 1)[-1]
    return re.sub(r"[^a-z0-9一-鿿]+", "_", n).strip("_")


def _singularize(n: str) -> str:
    """users->user, categories->category, statuses->status; leaves
    ss/us/is endings (status, analysis) alone."""
    if len(n) < 4 or n.endswith(("ss", "us", "is")):
        return n
    for suffix in ("ies", "ses", "xes", "zes", "es"):
        if n.endswith(suffix) and len(n) - len(suffix) >= 2:
            return n[:-len(suffix)] + ("y" if suffix == "ies" else "")
    if n.endswith("s") and len(n) - 1 >= 3:
        return n[:-1]
    return n


def _table_key(node: dict) -> str:
    return _singularize(_norm_name(node.get("label", "")))


def _match_table(resource_key: str, table_index: dict[str, list[dict]]) -> dict | None:
    """Real .sql table node for a resource key: singular/plural-normalized
    exact match first (index keys are singularized, so probe both forms),
    rapidfuzz token_set_ratio >= 90 fallback."""
    for key in (resource_key, _singularize(resource_key)):
        candidates = table_index.get(key)
        if candidates:
            return candidates[0]
    if fuzz is None or not table_index:
        return None
    best_node, best_score = None, 0.0
    for key, nodes in table_index.items():
        score = fuzz.token_set_ratio(resource_key, key)
        if score > best_score:
            best_node, best_score = nodes[0], score
    return best_node if best_score >= _FUZZ_TABLE_THRESHOLD else None


def _parent_path(api_path: str, paths: set[str]) -> str | None:
    """Ancestor path of ``api_path`` that is itself a known operation path,
    found by stripping the last segment repeatedly. None when no ancestor is
    a known path. Cross-file: the parent operation may live in another spec."""
    segs = api_path.split("/")
    while len(segs) > 1:
        segs = segs[:-1]
        cand = "/".join(segs)
        if cand and cand != api_path and cand in paths:
            return cand
    return None


def _infer_op_structural_edges(op_nodes: list[dict], edge_fn) -> int:
    """Emit the two operation-to-operation structural edges across the whole
    merged op set (run at build tier so a per-endpoint split corpus — where
    each file holds one operation — still derives them):

    * ``subpath_of`` (EXTRACTED) — a nested-path operation links to its
      parent-path operation; same HTTP method preferred, else the parent's
      first sibling.
    * ``shares_schema_with`` (INFERRED 0.95) — operations referencing the
      same schema NAME pair up, with ``_HUB_SCHEMA_OPS`` / ``_MAX_SHARE_EDGES``
      caps so a ubiquitous ErrorResponse does not produce an all-connected blob.

    ``edge_fn(src, tgt, relation, score, source_file, context=, confidence=)``
    handles dedup and the ``_origin: "ast"`` tier stamp. Returns the number of
    shares_schema_with edges emitted (for truncation reporting).
    """
    if not op_nodes:
        return 0

    def _op_path(op: dict) -> str:
        p = op.get("api_path")
        if isinstance(p, str) and p:
            return p
        label = op.get("label")
        if isinstance(label, str) and " " in label:
            return label.split(" ", 1)[1]
        return ""

    # Global indices across all files.
    paths: set[str] = set()
    first_op_by_pm: dict[tuple[str, str], str] = {}  # (path, method) -> nid
    op_ids_by_path: dict[str, list[str]] = {}
    op_src: dict[str, str] = {}  # op id -> source_file
    ops_by_schema: dict[str, list[str]] = {}  # schema NAME -> [op id]
    for op in op_nodes:
        nid = op.get("id", "")
        if not nid:
            continue
        if isinstance(op.get("source_file"), str):
            op_src[nid] = op["source_file"]
        ap = _op_path(op)
        if ap:
            paths.add(ap)
            op_ids_by_path.setdefault(ap, []).append(nid)
        method = str(op.get("http_method") or "").upper()
        if ap and method:
            first_op_by_pm.setdefault((ap, method), nid)
        seen: set[str] = set()
        for name in (op.get("refs_read") or []) + (op.get("refs_write") or []):
            if isinstance(name, str) and name and name not in seen:
                seen.add(name)
                ops_by_schema.setdefault(name, []).append(nid)

    # --- subpath_of (EXTRACTED): nested path -> parent-path op ---
    for op in op_nodes:
        nid = op.get("id", "")
        ap = _op_path(op)
        if not nid or not ap:
            continue
        parent = _parent_path(ap, paths)
        if not parent:
            continue
        method = str(op.get("http_method") or "").upper()
        target = first_op_by_pm.get((parent, method))
        if target is None:
            siblings = op_ids_by_path.get(parent) or []
            if not siblings:
                continue
            target = siblings[0]
        edge_fn(nid, target, "subpath_of", 1.0,
                op.get("source_file") or "",
                context=f"{ap} nested under {parent}",
                confidence="EXTRACTED")

    # --- shares_schema_with (INFERRED 0.95): ops referencing same schema ---
    share_count = 0
    truncated = False
    for name in sorted(ops_by_schema):
        if share_count >= _MAX_SHARE_EDGES:
            truncated = True
            break
        op_list = ops_by_schema[name]
        if len(op_list) < 2 or len(op_list) > _HUB_SCHEMA_OPS:
            continue
        for i in range(len(op_list)):
            for j in range(i + 1, len(op_list)):
                if share_count >= _MAX_SHARE_EDGES:
                    truncated = True
                    break
                src_file = op_src.get(op_list[i], "")
                edge_fn(op_list[i], op_list[j], "shares_schema_with", 0.95,
                        src_file,
                        context=f"shared schema: {name}")
                share_count += 1
    # truncated exposed via the returned count for summary reporting
    return share_count + (1 if truncated else 0)


def run_api_entity_inference(extraction: dict) -> dict:
    """Mutate the merged build input in place: append inferred entity nodes
    and INFERRED edges, enrich reconciled real table nodes. No-op (returns
    empty summary) when the merge carries no ``api_operation`` nodes."""
    nodes: list[dict] = extraction.get("nodes")
    if nodes is None:
        nodes = []
        extraction["nodes"] = nodes
    edges: list[dict] = extraction.get("edges")
    if edges is None:
        edges = []
        extraction["edges"] = edges
    op_nodes = [n for n in nodes
                if isinstance(n, dict) and n.get("file_type") == "api_operation"]
    summary = {"entities": 0, "reconciled": 0, "nodes": 0, "edges": 0}
    if not op_nodes:
        return summary

    # schema name -> properties, and id -> name for schema->schema ref edges
    schema_props: dict[str, list[str]] = {}
    schema_name_by_id: dict[str, str] = {}
    for n in nodes:
        if isinstance(n, dict) and n.get("openapi_kind") == "schema":
            name = n.get("schema_name")
            if isinstance(name, str) and name:
                schema_name_by_id[n.get("id", "")] = name
                props = n.get("properties")
                if isinstance(props, list) and props:
                    schema_props[name] = [str(p) for p in props]
    schema_ref_pairs: set[tuple[str, str]] = set()
    for e in edges:
        if not isinstance(e, dict) or e.get("relation") != "references":
            continue
        src = schema_name_by_id.get(e.get("source"))
        tgt = schema_name_by_id.get(e.get("target"))
        if src and tgt and src != tgt:
            schema_ref_pairs.add((src, tgt))

    # real .sql table nodes, indexed by normalized name (file nodes carry a
    # "*.sql" label; sourceless cross-file stubs have an empty source_file)
    table_index: dict[str, list[dict]] = {}
    for n in nodes:
        if not isinstance(n, dict):
            continue
        src = n.get("source_file")
        label = n.get("label")
        if (isinstance(src, str) and src.lower().endswith(".sql")
                and isinstance(label, str) and not label.lower().endswith(".sql")):
            table_index.setdefault(_table_key(n), []).append(n)

    def _label_path(label: object) -> str | None:
        if not isinstance(label, str) or " " not in label:
            return None
        return label.split(" ", 1)[1]

    # --- accumulate entities: resource key -> ops, columns, parents ---
    entities: dict[str, dict] = {}
    for op in op_nodes:
        api_path = op.get("api_path")
        if not isinstance(api_path, str):
            api_path = _label_path(op.get("label")) or ""
        resource, parent = _path_resource(api_path)
        if resource is None:
            continue
        key = _norm_name(resource)
        if not key:
            continue
        ent = entities.get(key)
        if ent is None:
            ent = entities[key] = {
                "label": resource, "ops": [], "methods": set(),
                "read_cols": {}, "write_cols": {},  # col -> first source schema
                "schemas": set(), "parents": set(), "source_files": set(),
            }
        method = str(op.get("http_method") or "").upper()
        ent["ops"].append(op)
        if method:
            ent["methods"].add(method)
        if isinstance(op.get("source_file"), str) and op["source_file"]:
            ent["source_files"].add(op["source_file"])
        for name in (op.get("refs_read") or []):
            if isinstance(name, str):
                ent["schemas"].add(name)
                for col in schema_props.get(name, []):
                    ent["read_cols"].setdefault(col, name)
        for name in (op.get("refs_write") or []):
            if isinstance(name, str):
                ent["schemas"].add(name)
                for col in schema_props.get(name, []):
                    ent["write_cols"].setdefault(col, name)
        if parent:
            pkey = _norm_name(parent)
            if pkey and pkey != key:
                ent["parents"].add(pkey)

    # --- mint nodes (virtual or reconciled real table) + op read/write edges ---
    existing_ids = {n.get("id") for n in nodes if isinstance(n, dict)}
    new_nodes: list[dict] = []
    new_edges: list[dict] = []
    seen_new_edges: set[tuple[str, str, str]] = set()
    ent_node_id: dict[str, str] = {}
    first_source = lambda ent: sorted(ent["source_files"])[0] if ent["source_files"] else ""

    def _edge(src: str, tgt: str, relation: str, score: float,
              source_file: str, context: str | None = None,
              confidence: str = "INFERRED") -> None:
        if not src or not tgt or src == tgt:
            return
        key = (src, tgt, relation)
        if key in seen_new_edges:
            return
        seen_new_edges.add(key)
        edge = {"source": src, "target": tgt, "relation": relation,
                "confidence": confidence, "source_file": source_file,
                "weight": 1.0,
                # Deterministic derivation: stamp the tier so fuzzy dedup
                # treats these as structural products and never folds an
                # entity into a same-name schema node (#2334 tier rules).
                "_origin": "ast"}
        # EXTRACTED edges carry no confidence_score (matches the extraction
        # tier's add_edge contract); INFERRED/AMBIGUOUS always do.
        if confidence != "EXTRACTED":
            edge["confidence_score"] = score
        if context:
            edge["context"] = context
        new_edges.append(edge)

    # --- operation-to-operation structural edges, computed cross-file so a
    # --- per-endpoint split corpus still derives subpath_of /
    # --- shares_schema_with (these used to be per-file in the extractor;
    # --- moved here so they span spec files). ---
    _infer_op_structural_edges(op_nodes, _edge)

    for key, ent in entities.items():
        real = _match_table(key, table_index)
        cols = sorted(set(ent["read_cols"]) | set(ent["write_cols"]))
        if real is not None:
            target_id = real["id"]
            prior = real.get("inferred_columns")
            merged = sorted(set(prior) | set(cols)) if isinstance(prior, list) else cols
            real["inferred_columns"] = merged
            real["read_columns"] = sorted(ent["read_cols"])
            real["write_columns"] = sorted(ent["write_cols"])
            real["entity_inferred_from"] = "openapi"
            summary["reconciled"] += 1
        else:
            target_id = _make_id("entity", key)
            base = target_id
            n = 2
            while target_id in existing_ids:  # never hijack an unrelated node
                target_id = f"{base}_{n}"
                n += 1
            existing_ids.add(target_id)
            new_nodes.append({
                "id": target_id,
                "label": f"{ent['label']} (inferred)",
                "file_type": "inferred_entity",
                "source_file": first_source(ent),
                "source_location": None,
                # Deterministic derivation (no LLM): tier stamp keeps fuzzy
                # dedup from collapsing the virtual entity into a same-name
                # schema node — the entity must survive as its own node or
                # the honest inferred/real distinction is lost (#2334).
                "_origin": "ast",
                "inferred": True,
                "inferred_columns": cols,
                "read_columns": sorted(ent["read_cols"]),
                "write_columns": sorted(ent["write_cols"]),
                "http_methods": sorted(m for m in ent["methods"] if m),
                "operation_count": len(ent["ops"]),
                "schema_names": sorted(s for s in ent["schemas"] if s),
                "source_files": sorted(ent["source_files"]),
            })
        ent_node_id[key] = target_id

        for op in ent["ops"]:
            method = str(op.get("http_method") or "").upper()
            relation = ("reads_from" if method in ("GET", "HEAD", "OPTIONS")
                        else "writes_to")
            _edge(op.get("id", ""), target_id, relation, 0.95,
                  op.get("source_file") or "",
                  context=f"{method} {op.get('api_path', '')}".strip())

    # --- belongs_to (nested path) +/- schema $ref corroboration ---
    covered: set[tuple[str, str]] = set()
    for key, ent in entities.items():
        child_id = ent_node_id.get(key, "")
        for parent_key in ent["parents"]:
            parent_ent = entities.get(parent_key)
            parent_id = ent_node_id.get(parent_key, "")
            if not parent_ent or not parent_id or parent_id == child_id:
                continue
            ref_evidence = any(
                a in ent["schemas"] and b in parent_ent["schemas"]
                for (a, b) in schema_ref_pairs)
            _edge(child_id, parent_id, "belongs_to",
                  0.95 if ref_evidence else 0.85,
                  first_source(ent),
                  context=("nested path + schema $ref" if ref_evidence
                           else "nested path"))
            covered.add((child_id, parent_id))

    # --- entity references from schema $ref links (skip pairs already
    # --- connected by belongs_to in the same direction) ---
    for (a, b) in sorted(schema_ref_pairs):
        for ka, ent_a in entities.items():
            if a not in ent_a["schemas"]:
                continue
            for kb, ent_b in entities.items():
                if kb == ka or b not in ent_b["schemas"]:
                    continue
                sid, tid = ent_node_id.get(ka, ""), ent_node_id.get(kb, "")
                if not sid or not tid or sid == tid or (sid, tid) in covered:
                    continue
                covered.add((sid, tid))
                _edge(sid, tid, "references", 0.85, first_source(ent_a),
                      context="schema $ref")

    nodes.extend(new_nodes)
    edges.extend(new_edges)
    summary["entities"] = len(entities)
    summary["nodes"] = len(new_nodes)
    summary["edges"] = len(new_edges)
    return summary

"""OpenAPI / Swagger spec extractor (#add-openapi-extractor).

Deterministic, LLM-free parse of OpenAPI 3.x and Swagger 2.0 JSON specs:

* one ``api_operation`` node per path x HTTP method (``METHOD /path`` label)
* one node per named schema (``openapi_kind: "schema"``, property names in
  ``properties``) and per tag (``openapi_kind: "tag"``)
* EXTRACTED edges: ``contains`` (spec file -> node), ``references`` ($ref,
  including nested array/allOf/property occurrences), ``grouped_under``
  (operation -> tag)
* ``subpath_of`` (nested path operation -> parent op) and
  ``shares_schema_with`` (operations referencing the same schema) are NOT
  emitted here — they are computed at the build tier by
  :mod:`graphify.api_inference` so they span spec files (a per-endpoint
  split corpus still gets them).

Swagger 2 and OpenAPI 3 are normalized onto one internal shape
(``definitions`` <-> ``components/schemas``, body parameter <-> requestBody)
before the single walk, so both produce identical node/edge kinds.

The build phase (``graphify.api_inference``) later folds CRUD operation
clusters over the same resource into inferred database entities; for that,
operation nodes carry ``refs_read`` / ``refs_write`` schema-NAME lists.

Data-shaped .json never reaches :func:`extract_openapi` by accident — the
``.json`` dispatch routes through :func:`extract_json_spec_aware`, which
probes the file head and falls back to the config/manifest extractor for
anything that is not a spec.
"""
from __future__ import annotations

import json
from pathlib import Path

from graphify.extractors.base import _file_stem, _make_id

# Specs are read fully (no tree-sitter streaming), so bound the read at
# 20 MiB — one byte over marks the file too large, mirroring json_config's
# TOCTOU-safe bounded read (#add-openapi-extractor raised this from 1 MiB).
_SPEC_MAX_BYTES = 20 * 1024 * 1024
# Cheap head probe so ordinary data/config JSON routed through
# extract_json_spec_aware never pays a full 20 MiB read + json.loads.
_PROBE_BYTES = 256 * 1024

_HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch")
_WRITE_METHODS = frozenset({"post", "put", "patch", "delete"})  # noqa: F841 — consumed by api_inference consumers/reporting

# Soft caps for pathological specs: a 20 MiB dump of paths could otherwise
# emit tens of thousands of nodes into the merge.
_MAX_OPS = 3000
_MAX_SCHEMAS = 3000
# shares_schema_with / subpath_of caps (_MAX_SHARE_EDGES, _HUB_SCHEMA_OPS)
# now live in graphify.api_inference — those edges are computed at build
# tier, cross-file.


def _path_item_has_method(item: object) -> bool:
    """True when a path-item object carries at least one HTTP method key —
    the structural signature of an API spec that no ordinary data JSON
    (datasets, routing configs, response dumps) reproduces."""
    if not isinstance(item, dict):
        return False
    return any(m in item for m in _HTTP_METHODS)


def _is_openapi_spec(doc: object) -> bool:
    """True when the parsed document is an OpenAPI/Swagger-shaped spec.

    Two acceptance paths:
    * standard — a version string (``openapi`` or ``swagger``) + a ``paths``
      object;
    * per-endpoint export — some API documentation systems (e.g. Huawei
      IoTDA) emit one JSON per operation: no ``openapi``/``swagger`` key, but
      a ``paths`` object whose single item carries an HTTP method, plus a
      ``definitions``/``components.schemas`` schema container. The
      HTTP-method-in-path-item check is the strong discriminator that keeps
      data JSON out.
    """
    if not isinstance(doc, dict):
        return False
    paths = doc.get("paths")
    if not isinstance(paths, dict) or not paths:
        return False
    version = doc.get("openapi")
    if not isinstance(version, str):
        version = doc.get("swagger")
    if isinstance(version, str):
        return True
    # Non-standard per-endpoint export: accept on paths + HTTP method keys.
    return any(_path_item_has_method(item) for item in paths.values())


def _probe_spec_candidate(path: Path) -> bool:
    """Cheap head-of-file candidacy check for the .json router.

    Reads at most 256 KiB and looks for ``"paths"`` plus either a version
    key (``"openapi"``/``"swagger"``) or a schema container
    (``"definitions"``/``"components"``/``"schemas"``). The schema-container
    marker catches non-standard per-endpoint exports (Huawei IoTDA, which
    has no ``swagger`` key) without probing every data JSON on disk. False
    positives are fine — the full parse in :func:`extract_openapi` makes the
    final call; a false negative would silently skip a spec.
    """
    try:
        with path.open("rb") as f:
            head = f.read(_PROBE_BYTES)
    except OSError:
        return False
    if b'"paths"' not in head:
        return False
    return (b'"openapi"' in head or b'"swagger"' in head
            or b'"definitions"' in head or b'"components"' in head
            or b'"schemas"' in head)


def extract_json_spec_aware(path: Path) -> dict:
    """Router registered for ``.json`` in the dispatch table: real specs get
    structured extraction, everything else falls through to the config /
    manifest extractor with its pre-existing behaviour untouched."""
    if _probe_spec_candidate(path):
        result = extract_openapi(path)
        if result.get("nodes") or result.get("edges"):
            return result
    from graphify.extractors.json_config import extract_json
    return extract_json(path)


def _ref_name(ref: object) -> str | None:
    """Map an internal $ref to a schema name: ``#/components/schemas/X``
    (OpenAPI 3) and ``#/definitions/X`` (Swagger 2) -> X; anything else
    (parameters, responses, external URLs) -> None."""
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return None
    parts = ref[2:].split("/")
    if len(parts) == 3 and parts[0] == "components" and parts[1] == "schemas":
        return parts[2]
    if len(parts) == 2 and parts[0] == "definitions":
        return parts[1]
    return None


def _collect_schema_refs(node: object, names: set[str], external: set[str],
                         depth: int = 0, seen: set[int] | None = None) -> None:
    """Recursively collect $ref'd schema names from a schema subtree.

    Handles the nesting a flat key-walk would miss: ``properties`` values,
    ``items`` (arrays), ``allOf``/``oneOf``/``anyOf`` composites and
    ``additionalProperties`` schemas. Depth- and cycle-guarded — recursive
    $ref chains (tree-shaped schemas) are common in real specs. Non-internal
    refs (external URLs / files) land in ``external`` untouched.
    """
    if depth > 10:
        return
    if isinstance(node, dict):
        if seen is None:
            seen = set()
        if id(node) in seen:
            return
        seen.add(id(node))
        ref = node.get("$ref")
        if isinstance(ref, str):
            name = _ref_name(ref)
            if name is not None:
                names.add(name)
            elif ref:
                external.add(ref)
            return  # a $ref pointer has no other structure worth walking
        for value in node.values():
            _collect_schema_refs(value, names, external, depth + 1, seen)
    elif isinstance(node, list):
        for item in node:
            _collect_schema_refs(item, names, external, depth + 1, seen)


def _op_schema_refs(op: dict) -> tuple[set[str], set[str], set[str]]:
    """(refs_read, refs_write, external_refs) for one operation object.

    Response schemas are the read side, request bodies the write side.
    Swagger 2 (``parameters[in=body]``, ``responses[code].schema``) and
    OpenAPI 3 (``requestBody.content``, ``responses[code].content``) shapes
    are both accepted — normalization happens here rather than by rewriting
    the document, so the original stays available for node attributes.
    """
    refs_read: set[str] = set()
    refs_write: set[str] = set()
    external: set[str] = set()

    params = op.get("parameters")
    if isinstance(params, list):
        for prm in params:
            if isinstance(prm, dict) and prm.get("in") == "body":
                _collect_schema_refs(prm.get("schema"), refs_write, external)

    body = op.get("requestBody")
    if isinstance(body, dict):
        content = body.get("content")
        if isinstance(content, dict):
            for media in content.values():
                if isinstance(media, dict):
                    _collect_schema_refs(media.get("schema"), refs_write, external)

    responses = op.get("responses")
    if isinstance(responses, dict):
        for resp in responses.values():
            if not isinstance(resp, dict):
                continue
            content = resp.get("content")
            if isinstance(content, dict):
                for media in content.values():
                    if isinstance(media, dict):
                        _collect_schema_refs(media.get("schema"), refs_read, external)
            else:
                _collect_schema_refs(resp.get("schema"), refs_read, external)
    return refs_read, refs_write, external


def _schema_properties(schema: object) -> list[str]:
    """Property names of a named schema, merging ``allOf``/``anyOf``/``oneOf``
    composites — a ``NewUser: {allOf: [{$ref: User}, {properties: {password}}]}``
    shape must contribute ``password`` alongside whatever User contributes
    downstream, or composed write-side columns silently vanish."""
    props: list[str] = []
    if not isinstance(schema, dict):
        return props
    own = schema.get("properties")
    if isinstance(own, dict):
        props += [str(k) for k in own]
    for combiner in ("allOf", "anyOf", "oneOf"):
        subs = schema.get(combiner)
        if isinstance(subs, list):
            for sub in subs:
                if isinstance(sub, dict) and isinstance(sub.get("properties"), dict):
                    props += [str(k) for k in sub["properties"]]
    return props


def extract_openapi(path: Path) -> dict:
    """Extract an OpenAPI 3.x / Swagger 2.0 JSON spec (see module docstring)."""
    try:
        with path.open("rb") as f:
            source = f.read(_SPEC_MAX_BYTES + 1)
        if len(source) > _SPEC_MAX_BYTES:
            return {"nodes": [], "edges": [],
                    "error": "openapi spec too large to index (> 20 MiB)"}
        if source.startswith(b"\xef\xbb\xbf"):  # Windows tools love BOMs
            source = source[3:]
        doc = json.loads(source)
    except json.JSONDecodeError:
        return {"nodes": [], "edges": [],
                "skipped": "not an openapi spec (unparseable json)"}
    except OSError as e:
        return {"nodes": [], "edges": [], "error": str(e)}
    if not _is_openapi_spec(doc):
        return {"nodes": [], "edges": [], "skipped": "not an openapi spec"}

    # --- Swagger 2 / OpenAPI 3 normalization (task 2.1) ---
    components = doc.get("components")
    schemas = components.get("schemas") if isinstance(components, dict) else None
    if not isinstance(schemas, dict):
        schemas = doc.get("definitions")
    if not isinstance(schemas, dict):
        schemas = {}
    paths = doc.get("paths") or {}
    base_path = doc.get("basePath")
    if not isinstance(base_path, str):
        base_path = ""

    stem = _file_stem(path)
    str_path = str(path)
    nodes: list[dict] = []
    edges: list[dict] = []
    seen_ids: set[str] = set()
    seen_edges: set[tuple[str, str, str]] = set()
    truncated = False
    external_refs: set[str] = set()

    def add_node(nid: str, label: str, file_type: str = "code", **attrs) -> None:
        if nid and nid not in seen_ids:
            seen_ids.add(nid)
            node = {"id": nid, "label": label, "file_type": file_type,
                    "source_file": str_path, "source_location": None,
                    # Deterministic extraction: stamp the tier explicitly
                    # rather than faking an "L1" line number (#2334).
                    "_origin": "ast"}
            node.update(attrs)
            nodes.append(node)

    def add_edge(src: str, tgt: str, relation: str, *,
                 confidence: str = "EXTRACTED", score: float | None = None,
                 context: str | None = None) -> bool:
        if not src or not tgt or src == tgt:
            return False
        key = (src, tgt, relation)
        if key in seen_edges:
            return False
        seen_edges.add(key)
        edge = {"source": src, "target": tgt, "relation": relation,
                "confidence": confidence, "source_file": str_path,
                "source_location": None, "_origin": "ast", "weight": 1.0}
        if score is not None:
            edge["confidence_score"] = score
        if context:
            edge["context"] = context
        edges.append(edge)
        return True

    file_nid = _make_id(str(path))
    # spec_version: standard openapi/swagger key, else the non-standard
    # ``version`` key some per-endpoint exports carry (Huawei IoTDA: "2.0").
    version = doc.get("openapi") or doc.get("swagger")
    if not isinstance(version, str) and isinstance(doc.get("version"), str):
        version = doc["version"]
    version = version or ""
    add_node(file_nid, path.name, openapi_kind="spec", spec_version=version,
             base_path=base_path)

    # --- schema nodes (pass 1: create all named schemas first so $ref edges
    # --- never race a later definition into a property-less placeholder) ---
    schema_nids: dict[str, str] = {}  # schema name -> node id
    for name, schema in schemas.items():
        if len(schema_nids) >= _MAX_SCHEMAS:
            truncated = True
            break
        if not isinstance(name, str) or not name:
            continue
        props = _schema_properties(schema)
        nid = _make_id(stem, "schema", name)
        schema_nids[name] = nid
        add_node(nid, name, openapi_kind="schema", schema_name=name,
                 properties=props)
        add_edge(file_nid, nid, "contains")

    def ensure_schema_node(name: str) -> str:
        """Node id for a schema name, minting a property-less node when the
        $ref target is not among the named definitions (unresolvable refs
        still need a real endpoint — validate checks edge endpoints exist)."""
        nid = schema_nids.get(name)
        if nid is None:
            nid = _make_id(stem, "schema", name)
            schema_nids[name] = nid
            add_node(nid, name, openapi_kind="schema", schema_name=name,
                     properties=[])
        return nid

    # --- schema -> schema $ref edges (entity relation evidence for the
    # --- build phase's ER inference) ---
    for name, schema in schemas.items():
        if not isinstance(name, str) or not isinstance(schema, dict):
            continue
        refs: set[str] = set()
        ext: set[str] = set()
        _collect_schema_refs(schema, refs, ext)
        external_refs |= ext
        for ref in sorted(refs):
            if ref != name:  # self-recursive schemas carry no relation signal
                add_edge(schema_nids[name], ensure_schema_node(ref),
                         "references", context="schema $ref")

    # --- operation nodes ---
    op_records: list[dict] = []       # {nid, method, raw_path, op}

    for raw_path, item in paths.items():
        if truncated:
            break
        if not isinstance(raw_path, str) or raw_path.startswith("x-"):
            continue
        if not isinstance(item, dict):
            continue
        display = f"{base_path}{raw_path}"
        for method in _HTTP_METHODS:
            op = item.get(method)
            if not isinstance(op, dict):
                continue
            if len(op_records) >= _MAX_OPS:
                truncated = True
                break
            refs_read, refs_write, ext = _op_schema_refs(op)
            external_refs |= ext
            nid = _make_id(stem, "op", method, *raw_path.split("/"))
            attrs: dict = {"http_method": method.upper(), "api_path": display,
                           "refs_read": sorted(refs_read),
                           "refs_write": sorted(refs_write)}
            if isinstance(op.get("operationId"), str):
                attrs["operation_id"] = op["operationId"]
            add_node(nid, f"{method.upper()} {display}",
                     file_type="api_operation", **attrs)
            add_edge(file_nid, nid, "contains")
            op_records.append({"nid": nid, "method": method,
                               "raw_path": raw_path, "op": op})
            for name in sorted(refs_read | refs_write):
                add_edge(nid, ensure_schema_node(name), "references",
                         context=("response schema" if name in refs_read
                                  else "request schema"))

    # --- tags ---
    for rec in op_records:
        tags = rec["op"].get("tags")
        if not isinstance(tags, list):
            continue
        for tag in tags:
            if not isinstance(tag, str) or not tag:
                continue
            tag_nid = _make_id(stem, "tag", tag)
            add_node(tag_nid, tag, openapi_kind="tag")
            add_edge(file_nid, tag_nid, "contains")
            add_edge(rec["nid"], tag_nid, "grouped_under")

    # --- subpath_of and shares_schema_with are computed at build tier in
    # --- graphify.api_inference, so a per-endpoint split corpus still
    # --- derives them across files. See _infer_op_structural_edges.

    # --- external $ref targets: concept nodes, mirroring json_config's J-4
    # --- namespacing so external pointers never collide with code nodes ---
    for ref in sorted(external_refs):
        ref_nid = _make_id("ref", ref)
        add_node(ref_nid, ref, file_type="concept")
        add_edge(file_nid, ref_nid, "references", context="external $ref")

    result = {"nodes": nodes, "edges": edges}
    if truncated:
        result["truncated"] = True
    return result

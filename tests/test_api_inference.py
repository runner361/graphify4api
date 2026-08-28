"""Build-tier reverse inference of database entities from OpenAPI products
(#add-openapi-extractor).

The core premise under test: the corpus has NO .sql files — entities are
reverse-inferred purely from the API spec (CRUD clusters over one resource
collapse into ONE inferred entity, with column unions and read/write
provenance from the referenced schemas). Reconciliation with real DDL is
the secondary behaviour (#D7: real table wins).
"""
from __future__ import annotations

from pathlib import Path

from graphify.api_inference import _path_resource, run_api_entity_inference
from graphify.extract import extract_openapi

FIXTURES = Path(__file__).parent / "fixtures"
PETSTORE = FIXTURES / "openapi" / "openapi3-petstore.json"


def _merged_spec() -> dict:
    r = extract_openapi(PETSTORE)
    return {"nodes": r["nodes"], "edges": r["edges"]}


def _entities(ext: dict) -> dict[str, dict]:
    return {n["label"]: n for n in ext["nodes"]
            if n.get("file_type") == "inferred_entity"}


def _op(nid: str, method: str, path: str, refs_read=(), refs_write=(),
        source_file: str = "api.json") -> dict:
    return {"id": nid, "label": f"{method} {path}", "file_type": "api_operation",
            "source_file": source_file, "source_location": None,
            "http_method": method, "api_path": path,
            "refs_read": list(refs_read), "refs_write": list(refs_write)}


def _schema(nid: str, name: str, props, source_file: str = "api.json") -> dict:
    return {"id": nid, "label": name, "file_type": "code",
            "source_file": source_file, "source_location": None,
            "openapi_kind": "schema", "schema_name": name,
            "properties": list(props)}


# --- resource extraction rules -------------------------------------------


def test_path_resource_rules():
    assert _path_resource("/api/v1/users") == ("users", None)
    assert _path_resource("/users/{id}/orders") == ("orders", "users")
    assert _path_resource("/users/{id}") == ("users", None)
    assert _path_resource("/user/delete") == (None, None)          # RPC verb
    assert _path_resource("/devices/batchDeleteUsers") == (None, None)  # camel verb
    assert _path_resource("/devices/{id}/bind") == (None, None)
    assert _path_resource("/health") == (None, None)                # stopword
    assert _path_resource("/{tenant}/gadgets") == ("gadgets", None)  # param-only parent


# --- the core scenario: five CRUD ops -> ONE entity ------------------------


def test_five_crud_ops_merge_into_one_entity():
    ext = _merged_spec()
    run_api_entity_inference(ext)
    ents = _entities(ext)
    assert "users (inferred)" in ents
    users = ents["users (inferred)"]
    # 5 REST ops: list/create on /users + read/update/delete on /users/{id}.
    # POST /users/batchDelete is RPC-style and opts out of entity inference.
    assert users["operation_count"] == 5
    assert users["http_methods"] == ["DELETE", "GET", "POST", "PUT"]
    assert users["inferred"] is True
    assert users["_origin"] == "ast"  # deterministic derivation, dedup-protected


def test_column_union_with_read_write_provenance():
    ext = _merged_spec()
    run_api_entity_inference(ext)
    users = _entities(ext)["users (inferred)"]
    # read side: User (id/name/profile/pets — response $refs, nested included)
    assert {"id", "name", "profile", "pets"} <= set(users["read_columns"])
    # write side: NewUser's allOf composite contributes `password`
    assert "password" in users["write_columns"]
    assert users["inferred_columns"] == sorted(
        set(users["read_columns"]) | set(users["write_columns"]))


def test_nested_path_belongs_to_with_schema_ref_upgrade():
    ext = _merged_spec()
    run_api_entity_inference(ext)
    labels = {n["id"]: n["label"] for n in ext["nodes"]}
    edges = [e for e in ext["edges"] if e["relation"] == "belongs_to"]
    pair = [e for e in edges
            if labels.get(e["source"]) == "orders (inferred)"
            and labels.get(e["target"]) == "users (inferred)"]
    assert len(pair) == 1
    # Order.buyer -> User $ref corroborates the /users/{id}/orders nesting:
    # dual evidence collapses to ONE edge at 0.95 (not two at 0.85)
    assert pair[0]["confidence"] == "INFERRED"
    assert pair[0]["confidence_score"] == 0.95


def test_op_entity_read_write_edges():
    ext = _merged_spec()
    run_api_entity_inference(ext)
    labels = {n["id"]: n["label"] for n in ext["nodes"]}
    reads = {(labels.get(e["source"]), labels.get(e["target"]))
             for e in ext["edges"] if e["relation"] == "reads_from"}
    writes = {(labels.get(e["source"]), labels.get(e["target"]))
              for e in ext["edges"] if e["relation"] == "writes_to"}
    assert ("GET /users", "users (inferred)") in reads
    assert ("POST /users", "users (inferred)") in writes
    assert ("DELETE /users/{id}", "users (inferred)") in writes
    for e in ext["edges"]:
        if e["relation"] in ("reads_from", "writes_to"):
            assert e["confidence"] == "INFERRED"
            assert e["confidence_score"] == 0.95


def test_rpc_and_health_paths_stay_entity_free():
    ext = _merged_spec()
    run_api_entity_inference(ext)
    rpc = next(n["id"] for n in ext["nodes"]
               if n["label"] == "POST /users/batchDelete")
    assert not any(e["source"] == rpc and e["relation"] in ("reads_from", "writes_to")
                   for e in ext["edges"])
    assert "health (inferred)" not in _entities(ext)


def test_resource_without_schemas_is_name_only():
    ext = {"nodes": [_op("op1", "GET", "/reports")], "edges": []}
    run_api_entity_inference(ext)
    ent = _entities(ext)["reports (inferred)"]
    assert ent["inferred_columns"] == []
    assert ent["operation_count"] == 1


def test_cross_spec_files_merge_into_one_entity():
    ext = {"nodes": [
        _op("a_op", "GET", "/devices", source_file="spec_a.json"),
        _op("b_op", "POST", "/devices", source_file="spec_b.json"),
    ], "edges": []}
    run_api_entity_inference(ext)
    ent = _entities(ext)["devices (inferred)"]
    assert ent["operation_count"] == 2
    assert ent["source_files"] == ["spec_a.json", "spec_b.json"]


def test_entity_schema_ref_relation_between_entities():
    # /gadgets + /widgets, no nesting, but Gadget has a $ref -> Widget:
    # entity references edge (INFERRED 0.85), not belongs_to
    nodes = [
        _op("op_g", "GET", "/gadgets", refs_read=("Gadget",)),
        _op("op_w", "GET", "/widgets", refs_read=("Widget",)),
        _schema("s_g", "Gadget", ["gid", "widget"]),
        _schema("s_w", "Widget", ["wid"]),
    ]
    edges = [{"source": "s_g", "target": "s_w", "relation": "references",
              "confidence": "EXTRACTED", "source_file": "api.json",
              "source_location": None, "weight": 1.0}]
    ext = {"nodes": nodes, "edges": edges}
    run_api_entity_inference(ext)
    labels = {n["id"]: n["label"] for n in ext["nodes"]}
    refs = [e for e in ext["edges"]
            if e["relation"] == "references"
            and labels.get(e["source"], "").endswith("(inferred)")
            and labels.get(e["target"], "").endswith("(inferred)")]
    assert len(refs) == 1
    assert labels[refs[0]["source"]] == "gadgets (inferred)"
    assert labels[refs[0]["target"]] == "widgets (inferred)"
    assert refs[0]["confidence_score"] == 0.85


# --- reconciliation with real DDL (secondary, #D7 real-table-wins) ---------


def _table(nid: str, name: str) -> dict:
    return {"id": nid, "label": name, "file_type": "code",
            "source_file": "schema.sql", "source_location": "L3"}


def test_sql_reconciliation_real_table_wins():
    table = _table("schema_users", "user")  # singular table vs plural resource
    op = _op("op1", "GET", "/users", refs_read=("User",))
    nodes = [table, op, _schema("s_user", "User", ["id", "name"])]
    ext = {"nodes": nodes, "edges": []}
    run_api_entity_inference(ext)
    # no virtual entity minted: the real table absorbed the resource
    assert not _entities(ext)
    assert table["inferred_columns"] == ["id", "name"]
    assert table["entity_inferred_from"] == "openapi"
    reads = [e for e in ext["edges"] if e["relation"] == "reads_from"]
    assert reads and reads[0]["target"] == "schema_users"
    assert reads[0]["confidence_score"] == 0.95


def test_unmatched_entity_survives_reconciliation():
    nodes = [
        _table("schema_billing", "invoices"),
        _op("op1", "GET", "/users", refs_read=("User",)),
        _schema("s_user", "User", ["id"]),
    ]
    ext = {"nodes": nodes, "edges": []}
    run_api_entity_inference(ext)
    assert "users (inferred)" in _entities(ext)  # untouched, no AMBIGUOUS noise

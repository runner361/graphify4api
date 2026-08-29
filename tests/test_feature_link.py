"""Tests for the feature -> API/entity linking tier (#add-feature-api-linking).

Covers: directory->feature-node strategy (scattered docs / empty dirs get no
feature node), prescreen top-N truncation + floor, Chinese feature name bridged
to English path tokens via doc-body terms, LLM-mock adjudication with
anti-hallucination whitelist + AMBIGUOUS routing, dual-hash cache hit +
candidate-change invalidation, and the no-LLM degradation path.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from graphify.feature_link import (
    generate_feature_nodes,
    run_feature_linking,
    _is_md_file_node,
    _feature_dir,
    _op_text,
    _entity_text,
    _english_terms,
    _prescreen,
    _parse_adjudication,
    _cache_key,
)
from graphify.extractors.markdown import extract_markdown


# --- helpers --------------------------------------------------------------

def _md_node(path_str: str, body: str = "", tmp: Path | None = None) -> dict:
    """A real markdown page node + its file on disk (so _feature_text can read
    the body for the English bridge)."""
    p = (tmp or Path("/tmp/fltest")) / path_str
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    md = extract_markdown(p)
    # extract_markdown emits source_file verbatim (posix here); normalize
    for n in md["nodes"]:
        n["source_file"] = str(p).replace("\\", "/")
    return md["nodes"][0]


def _op(id_: str, method: str, path: str, label: str | None = None) -> dict:
    return {"id": id_, "label": label or f"{method} {path}",
            "file_type": "api_operation", "source_file": "api.json",
            "http_method": method, "api_path": path,
            "refs_read": [], "refs_write": []}


def _ent(id_: str, label: str, cols: list[str]) -> dict:
    return {"id": id_, "label": label, "file_type": "inferred_entity",
            "source_file": "api.json", "inferred_columns": cols}


# --- stage 1: feature node generation -------------------------------------

def test_feature_node_from_directly_doc_bearing_dir(tmp_path):
    n = _md_node("退款/退款流程.md", "# 退款\n调用 POST /refund-orders", tmp_path)
    ext = {"nodes": [n], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    s = generate_feature_nodes(ext)
    assert s["features"] == 1
    assert s["contains"] == 1
    feat = [x for x in ext["nodes"] if x["file_type"] == "feature"]
    assert len(feat) == 1
    assert feat[0]["label"] == "退款"          # dir basename is the feature label
    assert feat[0]["_origin"] == "ast"
    assert any(e["relation"] == "contains" for e in ext["edges"])


def test_scattered_root_docs_get_no_feature_node(tmp_path):
    # a .md directly at the corpus root (parent == ".") — no feature dir
    n = _md_node("notes.md", "# notes", tmp_path)
    n["source_file"] = "notes.md"           # simulate corpus-root relative path
    ext = {"nodes": [n], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    s = generate_feature_nodes(ext)
    assert s["features"] == 0            # root-level scattered doc -> no feature node


def test_subfeature_of_between_nested_feature_dirs(tmp_path):
    child = _md_node("支付/退款/退款流程.md", "# 退款", tmp_path)
    parent = _md_node("支付/支付流程.md", "# 支付", tmp_path)
    ext = {"nodes": [child, parent], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    s = generate_feature_nodes(ext)
    assert s["features"] == 2
    assert s["subfeature_of"] == 1
    sub = [e for e in ext["edges"] if e["relation"] == "subfeature_of"]
    assert len(sub) == 1
    assert sub[0]["confidence"] == "EXTRACTED"
    # child feature -> parent feature
    assert sub[0]["source"].endswith("_feature") and sub[0]["target"].endswith("_feature")


def test_empty_corpus_is_noop():
    ext = {"nodes": [], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    assert generate_feature_nodes(ext) == {"features": 0, "contains": 0, "subfeature_of": 0}


# --- stage 2 prescreen -----------------------------------------------------

def test_op_text_drops_params_and_version():
    t = _op_text(_op("o", "GET", "/api/v5/users/{id}/orders"))
    # resource segments users + orders survive in the text; the {id} and
    # version tokens do NOT appear as standalone resource segments.
    assert "users" in t and "orders" in t
    segs = t.split()
    assert "{id}" not in segs and "v5" not in segs and "api" not in segs


def test_english_terms_extracts_latin_runs():
    terms = _english_terms("退款 调用 POST /refund-orders 接口")
    assert "refund" in terms          # latin runs survive (rapidfuzz later
    assert "orders" in terms          # splits on punctuation for matching)
    assert "POST" in terms


def test_prescreen_top_n_truncation_and_floor():
    # 30 candidates all sharing the `refund` resource token -> truncated to 5
    cands = [(_op(f"o{i}", "POST", f"/refund/{i}"), _op_text(_op(f"o{i}", "POST", f"/refund/{i}")))
             for i in range(30)]
    bridge = "refund"
    got = _prescreen(bridge, cands, top_n=5)
    assert len(got) == 5
    # a candidate sharing no token with the bridge is excluded (below floor)
    cands_low = [(_op("x", "POST", "/totally-unrelated-zzz"), "totally unrelated zzz")]
    assert _prescreen("refund", cands_low, top_n=5) == []


def test_chinese_feature_name_bridged_via_doc_body_english(tmp_path):
    # feature name is Chinese; only the doc BODY mentions the English path token
    n = _md_node("退款/退款流程.md", "# 退款流程\n创建退款单,调用 POST /refund-orders 接口", tmp_path)
    op = _op("op_refund", "POST", "/refund-orders")
    ext = {"nodes": [n, op], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    generate_feature_nodes(ext)
    from graphify.feature_link import _feature_text
    feat = [x for x in ext["nodes"] if x["file_type"] == "feature"][0]
    files = [x for x in ext["nodes"] if _is_md_file_node(x)]
    ftext = _feature_text(feat, files, ext["nodes"])
    got = _prescreen(ftext, [(op, _op_text(op))], top_n=5)
    assert got and got[0]["id"] == "op_refund"


# --- stage 3 LLM adjudication ---------------------------------------------

def _mock_llm_returning(ops_ents_ids):
    """Stub LLM that returns one good op link, one good entity link, and one
    HALLUCINATED id (must be dropped by the whitelist)."""
    good_op, good_ent, fake = ops_ents_ids
    return json.dumps([
        {"target_id": good_op, "relation": "implemented_by",
         "confidence_score": 0.95, "evidence": "POST /refund-orders 接口"},
        {"target_id": good_ent, "relation": "uses_entity",
         "confidence_score": 0.85, "evidence": "退款单"},
        {"target_id": fake, "relation": "implemented_by",
         "confidence_score": 0.9, "evidence": "hallucinated"},      # dropped
    ])


def test_llm_adjudication_whitelist_drops_hallucination(tmp_path):
    n = _md_node("退款/退款流程.md", "# 退款\n调用 POST /refund-orders 接口", tmp_path)
    op = _op("op_refund", "POST", "/refund-orders")
    ent = _ent("ent_refund", "refund_orders", ["id", "amount"])
    ext = {"nodes": [n, op, ent], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    generate_feature_nodes(ext)
    mock = _mock_llm_returning(("op_refund", "ent_refund", "FAKE_NOT_A_CANDIDATE"))
    s = run_feature_linking(ext, llm_call=lambda p: mock, cache_root=str(tmp_path / "c"))
    assert s["llm"] is True
    impl = [e for e in ext["edges"] if e["relation"] == "implemented_by"]
    uses = [e for e in ext["edges"] if e["relation"] == "uses_entity"]
    assert [e["target"] for e in impl] == ["op_refund"]
    assert [e["target"] for e in uses] == ["ent_refund"]
    # FAKE was dropped — no edge targets it
    assert not any(e["target"] == "FAKE_NOT_A_CANDIDATE" for e in ext["edges"])
    # confidence snapped to the rubric + INFERRED
    assert impl[0]["confidence_score"] == 0.95 and impl[0]["confidence"] == "INFERRED"
    assert impl[0]["evidence"]


def test_llm_subfloor_confidence_routes_to_ambiguous(tmp_path):
    n = _md_node("退款/退款流程.md", "# 退款\n调用 POST /refund-orders 接口", tmp_path)
    op = _op("op_refund", "POST", "/refund-orders")
    ext = {"nodes": [n, op], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    generate_feature_nodes(ext)
    mock = json.dumps([{"target_id": "op_refund", "relation": "implemented_by",
                        "confidence_score": 0.2, "evidence": "weak guess"}])
    run_feature_linking(ext, llm_call=lambda p: mock, cache_root=str(tmp_path / "c"))
    e = [x for x in ext["edges"] if x["relation"] == "implemented_by"][0]
    assert e["confidence"] == "AMBIGUOUS" and e["confidence_score"] == 0.3


def test_missing_evidence_dropped(tmp_path):
    n = _md_node("退款/退款流程.md", "# 退款\nPOST /refund-orders", tmp_path)
    op = _op("op_refund", "POST", "/refund-orders")
    ext = {"nodes": [n, op], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    generate_feature_nodes(ext)
    mock = json.dumps([{"target_id": "op_refund", "relation": "implemented_by",
                        "confidence_score": 0.95}])   # no evidence -> dropped
    run_feature_linking(ext, llm_call=lambda p: mock, cache_root=str(tmp_path / "c"))
    assert not [e for e in ext["edges"] if e["relation"] == "implemented_by"]


# --- stage 3.4 cache ------------------------------------------------------

def test_cache_hit_skips_llm(tmp_path):
    n = _md_node("退款/退款流程.md", "# 退款\nPOST /refund-orders 接口", tmp_path)
    op = _op("op_refund", "POST", "/refund-orders")
    ext = {"nodes": [n, op], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    generate_feature_nodes(ext)
    calls = {"n": 0}

    def llm(p):
        calls["n"] += 1
        return json.dumps([{"target_id": "op_refund", "relation": "implemented_by",
                            "confidence_score": 0.95, "evidence": "POST /refund-orders"}])
    croot = str(tmp_path / "c")
    run_feature_linking(ext, llm_call=llm, cache_root=croot)
    assert calls["n"] == 1
    # second run with identical feature text + candidate set -> cache hit, no LLM
    ext2 = {"nodes": [n, op], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    generate_feature_nodes(ext2)
    s = run_feature_linking(ext2, llm_call=llm, cache_root=croot)
    assert calls["n"] == 1                       # not called again
    assert s["llm"] is False                     # cache served it
    assert [e["target"] for e in ext2["edges"] if e["relation"] == "implemented_by"]


def test_cache_key_changes_with_candidates():
    k1 = _cache_key("feature text A", ["a", "b"])
    k2 = _cache_key("feature text A", ["a", "b"])
    k3 = _cache_key("feature text A", ["a", "c"])     # candidate set changed
    k4 = _cache_key("feature text B", ["a", "b"])     # feature text changed
    assert k1 == k2
    assert k1 != k3 and k1 != k4


# --- stage 3.3 degradation (no LLM) ---------------------------------------

def test_degradation_name_match_edge(tmp_path):
    # doc body mentions the exact English path token -> name-match >= 90
    n = _md_node("退款/退款流程.md", "# 退款\nPOST /refund-orders 接口", tmp_path)
    op = _op("op_refund", "POST", "/refund-orders")
    ext = {"nodes": [n, op], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    generate_feature_nodes(ext)
    s = run_feature_linking(ext, llm_call=lambda p: None, cache_root=str(tmp_path / "c"))
    assert s["llm"] is False
    e = [x for x in ext["edges"] if x["relation"] == "implemented_by"]
    assert e and e[0]["confidence"] == "INFERRED" and e[0]["confidence_score"] == 0.65
    assert e[0]["evidence"] == "name-match"


def test_degradation_below_threshold_no_edge(tmp_path):
    # no English bridge overlap -> no degradation edge (honest zero)
    n = _md_node("退款/退款流程.md", "# 退款\n创建退款单", tmp_path)
    op = _op("op_refund", "POST", "/refund-orders")
    ext = {"nodes": [n, op], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    generate_feature_nodes(ext)
    s = run_feature_linking(ext, llm_call=lambda p: None, cache_root=str(tmp_path / "c"))
    assert s["edges"] == 0
    assert not [e for e in ext["edges"] if e["relation"] in ("implemented_by", "uses_entity")]


def test_no_api_targets_is_noop(tmp_path):
    n = _md_node("退款/退款流程.md", "# 退款\nPOST /refund-orders", tmp_path)
    ext = {"nodes": [n], "edges": [], "hyperedges": [], "input_tokens": 0, "output_tokens": 0}
    generate_feature_nodes(ext)
    s = run_feature_linking(ext, llm_call=lambda p: "{}", cache_root=str(tmp_path / "c"))
    assert s["edges"] == 0

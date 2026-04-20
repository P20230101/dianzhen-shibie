from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from retrieval_kg_common import GraphEdge, GraphNode, RetrievalChunk, read_json, tokenize, write_json  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "external_retrieval_kg"


def test_retrieval_chunk_round_trip(tmp_path: Path) -> None:
    chunk = RetrievalChunk(
        paper_id="10_1016_j_compositesb_2019_107565",
        chunk_id="10_1016_j_compositesb_2019_107565:text:001",
        source_type="text",
        text="Crushing behavior and optimization of sheet-based 3D periodic cellular structures",
        page_no=1,
        figure_id=None,
        table_id=None,
        source_path="data/01_raw/pdfs/library/lattice/10_1016_j_compositesb_2019_107565/original.pdf",
    )

    path = tmp_path / "chunk.json"
    write_json(path, chunk.to_dict())

    payload = read_json(path)
    reconstructed = RetrievalChunk(**payload)

    assert reconstructed == chunk
    assert tokenize(payload["text"])[:3] == ["crushing", "behavior", "and"]


def test_graph_node_and_edge_round_trip(tmp_path: Path) -> None:
    node = GraphNode(node_id="sample:row-104", node_type="sample", label="row-104")
    edge = GraphEdge(
        source_id="sample:row-104",
        target_id="evidence:row-104:sea_j_g",
        relation="supports_field",
    )

    node_path = tmp_path / "node.json"
    edge_path = tmp_path / "edge.json"
    write_json(node_path, node.to_dict())
    write_json(edge_path, edge.to_dict())

    assert GraphNode(**read_json(node_path)) == node
    assert GraphEdge(**read_json(edge_path)) == edge


def test_fixtures_match_expected_contract() -> None:
    corpus_rows = [
        RetrievalChunk(**json.loads(line))
        for line in (FIXTURES_DIR / "mini_corpus.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    query = read_json(FIXTURES_DIR / "mini_query.json")
    sample = read_json(FIXTURES_DIR / "mini_samples.json")
    evidence = read_json(FIXTURES_DIR / "mini_evidence.json")

    assert len(corpus_rows) == 1
    assert corpus_rows[0].paper_id == "10_1016_j_compositesb_2019_107565"
    assert query["paper_id"] == "10_1016_j_compositesb_2019_107565"
    assert sample["paper_id"] == "10_1016_j_compositesb_2019_107565"
    assert evidence["sample_id"] == sample["sample_id"]

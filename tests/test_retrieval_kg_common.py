from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from retrieval_kg_common import GraphEdge, GraphNode, RetrievalChunk, read_json, tokenize, write_json  # type: ignore  # noqa: E402


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

    payload = chunk.to_dict()
    output_path = tmp_path / "chunk.json"

    write_json(output_path, payload)
    round_trip = read_json(output_path)

    assert payload["paper_id"] == "10_1016_j_compositesb_2019_107565"
    assert payload["source_type"] == "text"
    assert tokenize(payload["text"])[:3] == ["crushing", "behavior", "and"]
    assert round_trip["chunk_id"] == "10_1016_j_compositesb_2019_107565:text:001"


def test_graph_node_and_edge_round_trip() -> None:
    node = GraphNode(node_id="sample:sample-1", node_type="sample", label="sample-1")
    edge = GraphEdge(source_id="paper:paper-1", target_id="sample:sample-1", relation="contains_sample")

    assert node.to_dict() == {
        "node_id": "sample:sample-1",
        "node_type": "sample",
        "label": "sample-1",
    }
    assert edge.to_dict() == {
        "source_id": "paper:paper-1",
        "target_id": "sample:sample-1",
        "relation": "contains_sample",
    }

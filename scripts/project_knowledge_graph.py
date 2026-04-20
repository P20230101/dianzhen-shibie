from __future__ import annotations

import argparse
from pathlib import Path

from retrieval_kg_common import GraphEdge, GraphNode, read_json, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES_PATH = ROOT / "outputs" / "p1" / "extracted" / "samples_v1.json"
DEFAULT_EVIDENCE_PATH = ROOT / "outputs" / "p1" / "extracted" / "evidence_v1.json"
DEFAULT_OUTPUT_PATH = ROOT / "outputs" / "kg" / "knowledge_graph.json"


def _load_rows(path: Path) -> list[dict[str, object]]:
    payload = read_json(path)
    if not isinstance(payload, list):
        raise ValueError(f"expected a JSON array in {path}")
    rows: list[dict[str, object]] = []
    for row in payload:
        if not isinstance(row, dict):
            raise ValueError(f"expected row objects in {path}")
        rows.append(row)
    return rows


def dedupe_nodes(nodes: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[str] = set()
    ordered: list[dict[str, object]] = []
    for node in nodes:
        node_id = str(node["node_id"])
        if node_id in seen:
            continue
        seen.add(node_id)
        ordered.append(node)
    return ordered


def dedupe_edges(edges: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[tuple[str, str, str]] = set()
    ordered: list[dict[str, object]] = []
    for edge in edges:
        key = (str(edge["source_id"]), str(edge["target_id"]), str(edge["relation"]))
        if key in seen:
            continue
        seen.add(key)
        ordered.append(edge)
    return ordered


def project_graph(samples: list[dict[str, object]], evidence: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    nodes: list[dict[str, object]] = []
    edges: list[dict[str, object]] = []

    accepted_samples = {
        row["sample_id"]: row
        for row in samples
        if row.get("review_status") == "accepted" and row.get("needs_manual_review") is False
    }

    for sample_id, sample_row in accepted_samples.items():
        sample_node_id = f"sample:{sample_id}"
        paper_node_id = f"paper:{sample_row['paper_id']}"
        nodes.append(GraphNode(node_id=sample_node_id, node_type="sample", label=str(sample_id)).to_dict())
        nodes.append(GraphNode(node_id=paper_node_id, node_type="paper", label=str(sample_row["paper_id"])).to_dict())
        edges.append(GraphEdge(source_id=paper_node_id, target_id=sample_node_id, relation="contains_sample").to_dict())

    for row in evidence:
        if not row.get("verified_by_human"):
            continue
        sample_id = row["sample_id"]
        if sample_id not in accepted_samples:
            continue
        evidence_node_id = f"evidence:{row['evidence_id']}"
        nodes.append(GraphNode(node_id=evidence_node_id, node_type="evidence", label=str(row["field_name"])).to_dict())
        edges.append(GraphEdge(source_id=f"sample:{sample_id}", target_id=evidence_node_id, relation="supports_field").to_dict())

    return {"nodes": dedupe_nodes(nodes), "edges": dedupe_edges(edges)}


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project validated samples and evidence into a lightweight KG")
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES_PATH)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    samples = _load_rows(args.samples)
    evidence = _load_rows(args.evidence)
    graph = project_graph(samples, evidence)
    write_json(args.out, graph)
    print(f"knowledge graph written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

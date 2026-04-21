from __future__ import annotations

import argparse
from pathlib import Path

from retrieval_kg_common import GraphEdge, GraphNode, read_json, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES_PATH = ROOT / "outputs" / "p1" / "extracted" / "samples_v1.json"
DEFAULT_EVIDENCE_PATH = ROOT / "outputs" / "p1" / "extracted" / "evidence_v1.json"
DEFAULT_OUTPUT_PATH = ROOT / "outputs" / "kg" / "knowledge_graph.json"


def _accepted_samples(samples: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    accepted: dict[str, dict[str, object]] = {}
    for row in samples:
        if row.get("review_status") != "accepted":
            continue
        if row.get("needs_manual_review") is not False:
            continue
        sample_id = str(row["sample_id"])
        accepted[sample_id] = row
    return accepted


def _dedupe_nodes(nodes: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[str] = set()
    ordered: list[dict[str, object]] = []
    for node in nodes:
        node_id = str(node["node_id"])
        if node_id in seen:
            continue
        seen.add(node_id)
        ordered.append(node)
    return ordered


def _dedupe_edges(edges: list[dict[str, object]]) -> list[dict[str, object]]:
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
    accepted = _accepted_samples(samples)

    for sample_id, sample_row in accepted.items():
        paper_id = str(sample_row["paper_id"])
        nodes.append(GraphNode(node_id=f"sample:{sample_id}", node_type="sample", label=sample_id).to_dict())
        nodes.append(GraphNode(node_id=f"paper:{paper_id}", node_type="paper", label=paper_id).to_dict())
        edges.append(
            GraphEdge(
                source_id=f"paper:{paper_id}",
                target_id=f"sample:{sample_id}",
                relation="contains_sample",
            ).to_dict()
        )

    for row in evidence:
        if row.get("verified_by_human") is not True:
            continue
        sample_id = str(row["sample_id"])
        if sample_id not in accepted:
            continue
        evidence_id = str(row["evidence_id"])
        nodes.append(
            GraphNode(
                node_id=f"evidence:{evidence_id}",
                node_type="evidence",
                label=str(row["field_name"]),
            ).to_dict()
        )
        edges.append(
            GraphEdge(
                source_id=f"sample:{sample_id}",
                target_id=f"evidence:{evidence_id}",
                relation="supports_field",
            ).to_dict()
        )

    return {"nodes": _dedupe_nodes(nodes), "edges": _dedupe_edges(edges)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Project validated samples and evidence into a lightweight KG")
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES_PATH)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    samples = read_json(args.samples)
    evidence = read_json(args.evidence)
    if not isinstance(samples, list):
        raise SystemExit(f"expected a JSON array in {args.samples}")
    if not isinstance(evidence, list):
        raise SystemExit(f"expected a JSON array in {args.evidence}")

    graph = project_graph(samples, evidence)
    write_json(args.out, graph)
    print(f"knowledge graph written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

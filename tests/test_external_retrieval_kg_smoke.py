from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "external_retrieval_kg"


def _run(args: list[str]) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def test_external_retrieval_to_kg_smoke(tmp_path: Path) -> None:
    corpus_path = tmp_path / "corpus.jsonl"
    corpus_manifest_path = tmp_path / "corpus_manifest.json"
    candidates_path = tmp_path / "candidates.json"
    graph_path = tmp_path / "knowledge_graph.json"
    samples_path = tmp_path / "accepted_samples.json"
    evidence_path = tmp_path / "verified_evidence.json"

    samples = json.loads((ROOT / "outputs/p1/extracted/samples_v1.json").read_text(encoding="utf-8"))
    samples[0]["review_status"] = "accepted"
    samples[0]["needs_manual_review"] = False
    samples_path.write_text(json.dumps(samples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    evidence = json.loads((ROOT / "outputs/p1/extracted/evidence_v1.json").read_text(encoding="utf-8"))
    evidence[0]["verified_by_human"] = True
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    _run(
        [
            "scripts/build_retrieval_corpus.py",
            "--register",
            "data/01_raw/pdfs/paper_register.csv",
            "--library",
            "data/01_raw/pdfs/library",
            "--out",
            str(corpus_path),
            "--manifest",
            str(corpus_manifest_path),
        ]
    )
    _run(
        [
            "scripts/query_retrieval.py",
            "--corpus",
            str(corpus_path),
            "--query",
            str(FIXTURES_DIR / "mini_query.json"),
            "--out",
            str(candidates_path),
        ]
    )
    _run(
        [
            "scripts/project_knowledge_graph.py",
            "--samples",
            str(samples_path),
            "--evidence",
            str(evidence_path),
            "--out",
            str(graph_path),
        ]
    )

    assert corpus_path.exists()
    assert candidates_path.exists()
    assert graph_path.exists()

    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0

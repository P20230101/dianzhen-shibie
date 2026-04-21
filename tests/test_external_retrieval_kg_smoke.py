from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "external_retrieval_kg"


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def test_external_retrieval_to_kg_smoke(tmp_path: Path) -> None:
    corpus_path = tmp_path / "corpus.jsonl"
    manifest_path = tmp_path / "corpus_manifest.json"
    candidates_path = tmp_path / "candidates.json"
    graph_path = tmp_path / "knowledge_graph.json"

    _run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_retrieval_corpus.py"),
            "--register",
            str(FIXTURES_DIR / "paper_register_sample.csv"),
            "--library",
            str(ROOT / "data" / "01_raw" / "pdfs" / "library"),
            "--out",
            str(corpus_path),
            "--manifest",
            str(manifest_path),
        ]
    )
    _run(
        [
            sys.executable,
            str(ROOT / "scripts" / "query_retrieval.py"),
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
            sys.executable,
            str(ROOT / "scripts" / "project_knowledge_graph.py"),
            "--samples",
            str(FIXTURES_DIR / "mini_samples.json"),
            "--evidence",
            str(FIXTURES_DIR / "mini_evidence.json"),
            "--out",
            str(graph_path),
        ]
    )

    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
    graph = json.loads(graph_path.read_text(encoding="utf-8"))

    assert corpus_path.exists()
    assert manifest_path.exists()
    assert candidates["query_id"] == "q-001"
    assert len(candidates["candidates"]) > 0
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0

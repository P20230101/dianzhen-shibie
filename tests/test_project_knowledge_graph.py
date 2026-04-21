from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from project_knowledge_graph import main, project_graph  # type: ignore  # noqa: E402
from retrieval_kg_common import read_json  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "external_retrieval_kg"


def test_project_graph_only_accepts_verified_rows() -> None:
    samples = read_json(FIXTURES_DIR / "mini_samples.json")
    evidence = read_json(FIXTURES_DIR / "mini_evidence.json")

    graph = project_graph(samples, evidence)
    expected = read_json(FIXTURES_DIR / "mini_graph_expected.json")

    assert graph == expected


def test_main_exports_projected_graph(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples.json"
    evidence_path = tmp_path / "evidence.json"
    out_path = tmp_path / "knowledge_graph.json"

    samples_path.write_text((FIXTURES_DIR / "mini_samples.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "mini_evidence.json").read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = main([
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
        "--out",
        str(out_path),
    ])

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    expected = read_json(FIXTURES_DIR / "mini_graph_expected.json")

    assert exit_code == 0
    assert payload == expected

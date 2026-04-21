from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from promote_p1_review import main as promote_main  # type: ignore  # noqa: E402
from project_knowledge_graph import main as project_main  # type: ignore  # noqa: E402
from retrieval_kg_common import read_json  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "outputs" / "p1" / "extracted"


def test_main_promotes_pending_rows_in_place(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    samples_path.write_text((FIXTURES_DIR / "samples_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "evidence_v1.json").read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = promote_main([
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    promoted_samples = read_json(samples_path)
    promoted_evidence = read_json(evidence_path)

    assert exit_code == 0
    assert all(row["review_status"] == "accepted" for row in promoted_samples)
    assert all(row["needs_manual_review"] is False for row in promoted_samples)
    assert all(row["verified_by_human"] is True for row in promoted_evidence)
    assert "Promoted after P1 validation" in promoted_samples[0]["review_notes"]


def test_promoted_rows_project_to_non_empty_graph(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"
    out_path = tmp_path / "knowledge_graph.json"

    samples_path.write_text((FIXTURES_DIR / "samples_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "evidence_v1.json").read_text(encoding="utf-8"), encoding="utf-8")

    promote_exit = promote_main([
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])
    project_exit = project_main([
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
        "--out",
        str(out_path),
    ])

    payload = json.loads(out_path.read_text(encoding="utf-8"))

    assert promote_exit == 0
    assert project_exit == 0
    assert len(payload["nodes"]) >= 2
    assert len(payload["edges"]) >= 1
    assert any(node["node_type"] == "sample" for node in payload["nodes"])
    assert any(node["node_type"] == "evidence" for node in payload["nodes"])

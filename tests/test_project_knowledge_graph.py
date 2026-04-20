from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from project_knowledge_graph import project_graph  # type: ignore  # noqa: E402
from retrieval_kg_common import read_json  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "external_retrieval_kg"


def test_project_graph_only_accepts_verified_rows() -> None:
    samples = [
        {
            "sample_id": "sample-1",
            "paper_id": "10_1016_j_compositesb_2019_107565",
            "review_status": "accepted",
            "needs_manual_review": False,
        }
    ]
    evidence = [
        {
            "evidence_id": "e-1",
            "sample_id": "sample-1",
            "field_name": "structure_main_class",
            "field_value": "tpms",
            "source_priority": "T1",
            "source_type": "text",
            "verified_by_human": True,
        },
        {
            "evidence_id": "e-2",
            "sample_id": "sample-1",
            "field_name": "sea_j_g",
            "field_value": "12.776",
            "source_priority": "T1",
            "source_type": "text",
            "verified_by_human": False,
        },
    ]

    graph = project_graph(samples, evidence)
    expected = read_json(FIXTURES_DIR / "mini_graph_expected.json")

    assert graph == expected

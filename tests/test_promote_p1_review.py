from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from promote_p1_review import main as promote_main  # type: ignore  # noqa: E402
from project_knowledge_graph import main as project_main  # type: ignore  # noqa: E402
from build_pdf_sample_bundle import main as build_bundle_main  # type: ignore  # noqa: E402
from retrieval_kg_common import read_json  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "outputs" / "p1" / "extracted"


def test_main_promotes_pending_rows_in_place(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    samples_path.write_text(
        json.dumps(
            [
                {
                    "paper_id": "10_1016_j_demo_0000_000000",
                    "sample_id": "10_1016_j_demo_0000_000000-sample-1",
                    "review_status": "pending",
                    "needs_manual_review": True,
                    "review_notes": "Seeded from the review queue.",
                }
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    evidence_path.write_text(
        json.dumps(
            [
                {
                    "evidence_id": "10_1016_j_demo_0000_000000-sample-1-ev-001",
                    "sample_id": "10_1016_j_demo_0000_000000-sample-1",
                    "field_name": "raw_structure",
                    "verified_by_human": False,
                }
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = promote_main([
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    promoted_samples = read_json(samples_path)
    promoted_evidence = read_json(evidence_path)

    assert exit_code == 0
    assert promoted_samples[0]["review_status"] == "accepted"
    assert promoted_samples[0]["needs_manual_review"] is False
    assert promoted_samples[0]["review_notes"] == "Seeded from the review queue. Promoted after P1 validation to enable KG projection."
    assert promoted_evidence[0]["verified_by_human"] is True


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


def test_promoted_psh_bundle_grows_the_kg(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"
    out_path = tmp_path / "knowledge_graph.json"

    samples_path.write_text((FIXTURES_DIR / "samples_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "evidence_v1.json").read_text(encoding="utf-8"), encoding="utf-8")

    build_exit = build_bundle_main([
        "--paper-id",
        "10_1016_j_compstruct_2019_111219",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])
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

    assert build_exit == 0
    assert promote_exit == 0
    assert project_exit == 0
    assert len(payload["nodes"]) > 18
    assert len(payload["edges"]) > 15
    assert any(node["label"] == "10_1016_j_compstruct_2019_111219-psh-a5-b1p568-t0p3" for node in payload["nodes"])


def test_promoted_tws_2020_bundle_grows_the_kg(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"
    out_path = tmp_path / "knowledge_graph.json"

    samples_path.write_text((FIXTURES_DIR / "samples_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "evidence_v1.json").read_text(encoding="utf-8"), encoding="utf-8")

    build_exit = build_bundle_main([
        "--paper-id",
        "10_1016_j_tws_2020_106623",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])
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

    assert build_exit == 0
    assert promote_exit == 0
    assert project_exit == 0
    assert len(payload["nodes"]) > 24
    assert len(payload["edges"]) > 20
    assert any(node["label"] == "10_1016_j_tws_2020_106623-sth-r015-v1" for node in payload["nodes"])


def test_promoted_tws_2019_bundle_grows_the_kg(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"
    out_path = tmp_path / "knowledge_graph.json"

    samples_path.write_text((FIXTURES_DIR / "samples_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "evidence_v1.json").read_text(encoding="utf-8"), encoding="utf-8")

    build_exit = build_bundle_main([
        "--paper-id",
        "10_1016_j_tws_2019_106436",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])
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

    assert build_exit == 0
    assert promote_exit == 0
    assert project_exit == 0
    assert len(payload["nodes"]) > 30
    assert len(payload["edges"]) > 25
    assert any(node["label"] == "10_1016_j_tws_2019_106436-g06-hierarchical-honeycomb" for node in payload["nodes"])


def test_promoted_matdes_2017_bundle_grows_the_kg(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"
    out_path = tmp_path / "knowledge_graph.json"

    samples_path.write_text((FIXTURES_DIR / "samples_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "evidence_v1.json").read_text(encoding="utf-8"), encoding="utf-8")

    build_exit = build_bundle_main([
        "--paper-id",
        "10_1016_j_matdes_2017_10_028",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])
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

    assert build_exit == 0
    assert promote_exit == 0
    assert project_exit == 0
    assert len(payload["nodes"]) > 36
    assert len(payload["edges"]) > 30
    assert any(node["label"] == "10_1016_j_matdes_2017_10_028-rd016-hierarchical-honeycomb" for node in payload["nodes"])


def test_promoted_ijimpeng_2023_bundle_grows_the_kg(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"
    out_path = tmp_path / "knowledge_graph.json"

    samples_path.write_text((FIXTURES_DIR / "samples_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "evidence_v1.json").read_text(encoding="utf-8"), encoding="utf-8")

    build_exit = build_bundle_main([
        "--paper-id",
        "10_1016_j_ijimpeng_2023_104713",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])
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

    assert build_exit == 0
    assert promote_exit == 0
    assert project_exit == 0
    assert len(payload["nodes"]) > 50
    assert len(payload["edges"]) > 42
    assert any(node["label"] == "10_1016_j_ijimpeng_2023_104713-design1-reinforced-hexagonal-lattice" for node in payload["nodes"])


def test_promoted_engstruct_2023_bundle_grows_the_kg(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"
    out_path = tmp_path / "knowledge_graph.json"

    samples_path.write_text((FIXTURES_DIR / "samples_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "evidence_v1.json").read_text(encoding="utf-8"), encoding="utf-8")

    build_exit = build_bundle_main([
        "--paper-id",
        "10_1016_j_engstruct_2023_116510",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])
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

    assert build_exit == 0
    assert promote_exit == 0
    assert project_exit == 0
    assert len(payload["nodes"]) > 58
    assert len(payload["edges"]) > 49
    assert any(node["label"] == "10_1016_j_engstruct_2023_116510-knee-b7p71-d2p00" for node in payload["nodes"])


def test_promoted_compstruct_2018_bundle_grows_the_kg(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"
    out_path = tmp_path / "knowledge_graph.json"

    samples_path.write_text((FIXTURES_DIR / "samples_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "evidence_v1.json").read_text(encoding="utf-8"), encoding="utf-8")

    build_exit = build_bundle_main([
        "--paper-id",
        "10_1016_j_compstruct_2018_03_050",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])
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

    assert build_exit == 0
    assert promote_exit == 0
    assert project_exit == 0
    assert len(payload["nodes"]) > 43
    assert len(payload["edges"]) > 36
    assert any(node["label"] == "10_1016_j_compstruct_2018_03_050-n2-r0125-triangular-hierarchical" for node in payload["nodes"])

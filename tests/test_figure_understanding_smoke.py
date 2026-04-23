from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_figure_understanding import build_figure_understanding_corpus  # type: ignore  # noqa: E402
from build_figure_understanding import main as build_figure_understanding_main  # type: ignore  # noqa: E402
from figure_understanding_vlm import FixtureFigureInterpreter  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "figure_understanding"
LIBRARY_ROOT = ROOT / "data" / "01_raw" / "pdfs" / "library"


def _write_fixture_response(tmp_path: Path) -> Path:
    response_path = tmp_path / "unit_vlm_response.json"
    response = {
        "units": [
            {
                "panel_label": "",
                "kind": "figure",
                "crop_bbox": {"l": 0, "t": 0, "r": 1, "b": 1},
                "figure_type": "curve_plot",
                "recaption": "Compression curves compare gyroid and diamond lattices.",
                "figure_summary": "The plot shows stress-strain response under compression.",
                "confidence": 0.92,
                "source_refs": [
                    "paper:10_1016_j_addma_2022_102887",
                    "page:3",
                    "figure:fig_001",
                ],
            }
        ]
    }
    response_path.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return response_path


def test_end_to_end_smoke_writes_unit_outputs(tmp_path: Path) -> None:
    output_path = tmp_path / "figure_units_v1.jsonl"
    manifest_path = tmp_path / "manifest.json"
    review_path = tmp_path / "figure_units_review.csv"
    backend = FixtureFigureInterpreter(_write_fixture_response(tmp_path))

    payload = json.loads((FIXTURES_DIR / "mini_docling_payload.json").read_text(encoding="utf-8"))

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    records = build_figure_understanding_corpus(
        register_path=FIXTURES_DIR / "mini_register.csv",
        library_root=LIBRARY_ROOT,
        output_path=output_path,
        manifest_path=manifest_path,
        review_path=review_path,
        interpreter=backend,
        document_provider=lambda _pdf_path: FakeDocument(),
    )

    assert output_path.exists()
    assert manifest_path.exists()
    assert review_path.exists()
    assert len(records) == 1

    jsonl_rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert jsonl_rows == records
    assert jsonl_rows[0]["unit_id"] == "fig_001_u01"
    assert jsonl_rows[0]["source_figure_id"] == "fig_001"
    assert jsonl_rows[0]["panel_label"] is None
    assert jsonl_rows[0]["needs_manual_review"] is False

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["unit_count"] == 1
    assert manifest["source_figure_count"] == 1
    assert manifest["paper_count"] == 1

    with review_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == [
        {
            "paper_id": "10_1016_j_addma_2022_102887",
            "source_figure_id": "fig_001",
            "unit_id": "fig_001_u01",
            "unit_index": "1",
            "kind": "figure",
            "panel_label": "",
            "source_page_no": "3",
            "source_image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_001.png",
            "image_path": str(Path(output_path.parent / "images" / "10_1016_j_addma_2022_102887" / "fig_001_u01.png")),
            "crop_bbox": "{\"l\": 0, \"t\": 0, \"r\": 1, \"b\": 1}",
            "caption_text": "Figure 2. Stress-strain curves under quasi-static compression.",
            "context_text": "The figure compares gyroid and diamond lattice responses under compression.",
            "figure_type": "curve_plot",
            "recaption": "Compression curves compare gyroid and diamond lattices.",
            "figure_summary": "The plot shows stress-strain response under compression.",
            "confidence": "0.92",
            "needs_manual_review": "false",
            "source_refs": "paper:10_1016_j_addma_2022_102887;page:3;figure:fig_001",
        }
    ]


def test_main_writes_expected_outputs_with_fixture_backend(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "figure_units_v1.jsonl"
    manifest_path = tmp_path / "manifest.json"
    review_path = tmp_path / "figure_units_review.csv"
    fixture_response = _write_fixture_response(tmp_path)
    payload = json.loads((FIXTURES_DIR / "mini_docling_payload.json").read_text(encoding="utf-8"))

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    import build_figure_understanding as figure_module  # type: ignore  # noqa: E402

    monkeypatch.setattr(figure_module, "_load_document", lambda _provider, _pdf_path: FakeDocument())

    exit_code = build_figure_understanding_main([
        "--register",
        str(FIXTURES_DIR / "mini_register.csv"),
        "--library-root",
        str(LIBRARY_ROOT),
        "--output",
        str(output_path),
        "--manifest",
        str(manifest_path),
        "--review",
        str(review_path),
        "--fixture-response",
        str(fixture_response),
    ])

    assert exit_code == 0
    assert output_path.exists()
    assert manifest_path.exists()
    assert review_path.exists()

    jsonl_rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(jsonl_rows) == 1
    assert jsonl_rows[0]["unit_id"] == "fig_001_u01"
    assert jsonl_rows[0]["source_figure_id"] == "fig_001"
    assert manifest["unit_count"] == 1
    assert manifest["source_figure_count"] == 1


def test_seeded_figure_artifacts_are_checked_in() -> None:
    figure_dir = ROOT / "data" / "03_figures"
    jsonl_path = figure_dir / "figure_units_v1.jsonl"
    manifest_path = figure_dir / "manifest.json"
    review_path = figure_dir / "figure_units_review.csv"

    assert jsonl_path.exists()
    assert manifest_path.exists()
    assert review_path.exists()

    jsonl_rows = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["unit_count"] == len(jsonl_rows) == 4
    assert manifest["source_figure_count"] == 2
    assert manifest["paper_count"] == 1
    assert {row["unit_id"] for row in jsonl_rows} == {"fig_003_a", "fig_003_b", "fig_003_c", "fig_004_u01"}
    assert all(Path(row["image_path"]).exists() for row in jsonl_rows)

    with review_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 4
    assert {row["unit_id"] for row in rows} == {"fig_003_a", "fig_003_b", "fig_003_c", "fig_004_u01"}

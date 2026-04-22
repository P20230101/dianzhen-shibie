from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_figure_understanding import build_figure_understanding_corpus  # type: ignore  # noqa: E402
from figure_understanding_vlm import FixtureFigureInterpreter  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "figure_understanding"
LIBRARY_ROOT = ROOT / "data" / "01_raw" / "pdfs" / "library"


def test_end_to_end_smoke_writes_figure_outputs(tmp_path: Path) -> None:
    output_path = tmp_path / "figures_v1.jsonl"
    manifest_path = tmp_path / "manifest.json"
    review_path = tmp_path / "figures_review.csv"
    backend = FixtureFigureInterpreter(FIXTURES_DIR / "mini_vlm_response.json")

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
    assert jsonl_rows[0]["figure_type"] == "curve_plot"
    assert jsonl_rows[0]["needs_manual_review"] is False
    assert jsonl_rows[0]["panel_labels"] == ["a", "b"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["figure_count"] == 1
    assert manifest["paper_count"] == 1

    with review_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == [
        {
            "paper_id": "10_1016_j_addma_2022_102887",
            "figure_id": "fig_001",
            "page_no": "3",
            "image_path": "tests/fixtures/figure_understanding/mini_figure_image.png",
            "caption_text": "Figure 2. Stress-strain curves under quasi-static compression.",
            "context_text": "The figure compares gyroid and diamond lattice responses under compression.",
            "panel_labels": "a;b",
            "figure_type": "curve_plot",
            "recaption": "Compression curves compare gyroid and diamond lattices.",
            "figure_summary": "The gyroid lattice shows a higher plateau stress than the diamond lattice under compression.",
            "confidence": "0.92",
            "needs_manual_review": "false",
            "source_refs": "paper:10_1016_j_addma_2022_102887;page:3;figure:fig_001",
        }
    ]

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_figure_understanding import extract_figures  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "figure_understanding"


class FakeFigureInterpreter:
    def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
        assert image_path.endswith("mini_figure_image.png")
        assert caption_text == "Figure 2. Stress-strain curves under quasi-static compression."
        assert context_text == "The figure compares gyroid and diamond lattice responses under compression."
        return {
            "panel_labels": ["b", "a"],
            "figure_type": "curve_plot",
            "recaption": "Compression curves compare gyroid and diamond lattices.",
            "figure_summary": "The plot shows stress-strain response under compression.",
            "confidence": 0.91,
            "source_refs": [
                "paper:10_1016_j_addma_2022_102887",
                "page:3",
                "figure:fig_001",
            ],
        }


def test_extract_figures_emits_image_level_records() -> None:
    payload = json.loads((FIXTURES_DIR / "mini_docling_payload.json").read_text(encoding="utf-8"))

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    records = extract_figures(
        FakeDocument(),
        paper_id="10_1016_j_addma_2022_102887",
        source_path="data/01_raw/pdfs/library/lattice/10_1016_j_addma_2022_102887/original.pdf",
        interpreter=FakeFigureInterpreter(),
        review_threshold=0.85,
    )

    assert len(records) == 1
    assert records[0]["paper_id"] == "10_1016_j_addma_2022_102887"
    assert records[0]["figure_id"] == "fig_001"
    assert records[0]["figure_type"] == "curve_plot"
    assert records[0]["panel_labels"] == ["a", "b"]
    assert records[0]["needs_manual_review"] is False

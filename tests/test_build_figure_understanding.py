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
        assert image_path.endswith("fig_001.png")
        assert caption_text == "Figure 2. Stress-strain curves under quasi-static compression."
        assert context_text == "The figure compares gyroid and diamond lattice responses under compression."
        return {
            "panel_labels": ["b", "a"],
            "subfigure_map": {
                "a": "gyroid lattice",
                "b": "diamond lattice",
            },
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
    assert records[0]["subfigure_map"] == {
        "a": "gyroid lattice",
        "b": "diamond lattice",
    }
    assert records[0]["needs_manual_review"] is False


def test_extract_figures_handles_composite_and_microstructure_images() -> None:
    payload = json.loads((FIXTURES_DIR / "multi_docling_payload.json").read_text(encoding="utf-8"))
    expected = json.loads((FIXTURES_DIR / "multi_figure_expected.json").read_text(encoding="utf-8"))

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    class MultiFigureInterpreter:
        def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
            if image_path.endswith("fig_003.png"):
                assert caption_text == "Figure 3. Composite figure summarizing structure, curve, and failure snapshots."
                assert context_text == "Panel a, b, and c are a composite figure with curves, snapshots, and fracture path annotations."
                return {
                    "panel_labels": ["c", "a", "b"],
                    "subfigure_map": {
                        "c": "fracture path",
                        "a": "stress-strain response",
                        "b": "deformed specimen",
                    },
                    "figure_type": "composite_figure",
                    "recaption": "Panels a-c summarize response, deformation, and fracture path.",
                    "figure_summary": "The composite figure ties together response curves, deformed state, and failure localization.",
                    "confidence": 0.89,
                    "source_refs": [
                        "paper:10_1016_j_addma_2022_102887",
                        "page:5",
                        "figure:fig_003",
                    ],
                }
            if image_path.endswith("fig_004.png"):
                assert caption_text == "Figure 4. Microstructure image of the fractured surface after compression."
                assert context_text == "SEM microstructure image of the fractured surface after compression."
                return {
                    "panel_labels": [],
                    "subfigure_map": {},
                    "figure_type": "microstructure_image",
                    "recaption": "SEM micrograph of the fractured surface shows pore collapse and ligament tearing.",
                    "figure_summary": "The microstructure image highlights fractured ligaments and collapsed pores after compression.",
                    "confidence": 0.93,
                    "source_refs": [
                        "paper:10_1016_j_addma_2022_102887",
                        "page:7",
                        "figure:fig_004",
                    ],
                }
            raise AssertionError(f"unexpected image path: {image_path}")

    records = extract_figures(
        FakeDocument(),
        paper_id="10_1016_j_addma_2022_102887",
        source_path="data/01_raw/pdfs/library/lattice/10_1016_j_addma_2022_102887/original.pdf",
        interpreter=MultiFigureInterpreter(),
        review_threshold=0.85,
    )

    assert records == expected

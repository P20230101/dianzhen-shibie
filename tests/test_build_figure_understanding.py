from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_figure_understanding import extract_figures  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "figure_understanding"
LIBRARY_ROOT = ROOT / "data" / "01_raw" / "pdfs" / "library"


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


def test_extract_figures_recovers_page_caption_and_skips_page_one_noise() -> None:
    payload = {
        "texts": [
            {
                "text": "Fig. 2. Stress-strain curves under quasi-static compression.",
                "prov": [
                    {
                        "page_no": 2,
                        "bbox": {"l": 40.0, "t": 430.0, "r": 420.0, "b": 410.0, "coord_origin": "BOTTOMLEFT"},
                    }
                ],
            }
        ],
        "pictures": [
            {
                "figure_id": "fig_noise",
                "prov": [
                    {
                        "page_no": 1,
                        "bbox": {"l": 20.0, "t": 720.0, "r": 180.0, "b": 640.0, "coord_origin": "BOTTOMLEFT"},
                    }
                ],
                "captions": [],
                "children": [],
                "image": {"size": {"width": 29.0, "height": 29.0}},
                "image_path": "data/03_figures/images/noise.png",
            },
            {
                "figure_id": "fig_real",
                "prov": [
                    {
                        "page_no": 2,
                        "bbox": {"l": 50.0, "t": 700.0, "r": 420.0, "b": 500.0, "coord_origin": "BOTTOMLEFT"},
                    }
                ],
                "captions": [],
                "children": [{"$ref": "#/texts/0"}],
                "image_path": "data/03_figures/images/real.png",
            },
        ],
    }

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    class CaptionAwareInterpreter:
        def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
            assert image_path.endswith("real.png")
            assert caption_text == "Fig. 2. Stress-strain curves under quasi-static compression."
            assert context_text == "Fig. 2. Stress-strain curves under quasi-static compression."
            return {
                "panel_labels": ["a", "b"],
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
                    "page:2",
                    "figure:fig_real",
                ],
            }

    records = extract_figures(
        FakeDocument(),
        paper_id="10_1016_j_addma_2022_102887",
        source_path="data/01_raw/pdfs/library/lattice/10_1016_j_addma_2022_102887/original.pdf",
        interpreter=CaptionAwareInterpreter(),
        review_threshold=0.85,
    )

    assert len(records) == 1
    assert records[0]["figure_id"] == "fig_real"
    assert records[0]["caption_text"] == "Fig. 2. Stress-strain curves under quasi-static compression."
    assert records[0]["context_text"] == "Fig. 2. Stress-strain curves under quasi-static compression."
    assert records[0]["needs_manual_review"] is False


def test_extract_figures_skips_tiny_page_one_noise_even_with_children() -> None:
    payload = {
        "texts": [
            {
                "text": "Fig. 2. Stress-strain curves under quasi-static compression.",
                "prov": [
                    {
                        "page_no": 2,
                        "bbox": {"l": 40.0, "t": 430.0, "r": 420.0, "b": 410.0, "coord_origin": "BOTTOMLEFT"},
                    }
                ],
            }
        ],
        "pictures": [
            {
                "figure_id": "fig_noise",
                "prov": [
                    {
                        "page_no": 1,
                        "bbox": {"l": 20.0, "t": 720.0, "r": 180.0, "b": 640.0, "coord_origin": "BOTTOMLEFT"},
                    }
                ],
                "captions": [],
                "children": [{"$ref": "#/texts/0"}],
                "image": {"size": {"width": 29.0, "height": 29.0}},
                "image_path": "data/03_figures/images/noise.png",
            },
            {
                "figure_id": "fig_real",
                "prov": [
                    {
                        "page_no": 2,
                        "bbox": {"l": 50.0, "t": 700.0, "r": 420.0, "b": 500.0, "coord_origin": "BOTTOMLEFT"},
                    }
                ],
                "captions": [],
                "children": [{"$ref": "#/texts/0"}],
                "image": {"size": {"width": 400.0, "height": 320.0}},
                "image_path": "data/03_figures/images/real.png",
            },
        ],
    }

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    class TinyNoiseInterpreter:
        def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
            assert image_path.endswith("real.png")
            assert caption_text == "Fig. 2. Stress-strain curves under quasi-static compression."
            assert context_text == "Fig. 2. Stress-strain curves under quasi-static compression."
            return {
                "panel_labels": ["a", "b"],
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
                    "page:2",
                    "figure:fig_real",
                ],
            }

    records = extract_figures(
        FakeDocument(),
        paper_id="10_1016_j_addma_2022_102887",
        source_path="data/01_raw/pdfs/library/lattice/10_1016_j_addma_2022_102887/original.pdf",
        interpreter=TinyNoiseInterpreter(),
        review_threshold=0.85,
    )

    assert len(records) == 1
    assert records[0]["figure_id"] == "fig_real"


def test_extract_figures_keeps_large_page_one_graphics() -> None:
    payload = {
        "pictures": [
            {
                "figure_id": "fig_graphical_abstract",
                "prov": [
                    {
                        "page_no": 1,
                        "bbox": {"l": 25.0, "t": 710.0, "r": 420.0, "b": 520.0, "coord_origin": "BOTTOMLEFT"},
                    }
                ],
                "captions": [],
                "children": [],
                "image": {"size": {"width": 240.0, "height": 180.0}},
                "image_path": "data/03_figures/images/graphical_abstract.png",
            }
        ]
    }

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    class GraphicsInterpreter:
        def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
            assert image_path.endswith("graphical_abstract.png")
            assert caption_text is None
            assert context_text is None
            return {
                "panel_labels": [],
                "subfigure_map": {},
                "figure_type": "graphical_abstract",
                "recaption": "Graphical abstract of the paper.",
                "figure_summary": "A graphical abstract summarizing the work.",
                "confidence": 0.92,
                "source_refs": ["paper:10_1016_j_matdes_2018_05_059"],
            }

    records = extract_figures(
        FakeDocument(),
        paper_id="10_1016_j_matdes_2018_05_059",
        source_path="data/01_raw/pdfs/library/lattice/10_1016_j_matdes_2018_05_059/original.pdf",
        interpreter=GraphicsInterpreter(),
        review_threshold=0.85,
    )

    assert len(records) == 1
    assert records[0]["figure_id"] == "fig_graphical_abstract"
    assert records[0]["needs_manual_review"] is True


def test_build_corpus_resolves_source_path_register_column(tmp_path: Path) -> None:
    from build_figure_understanding import build_figure_understanding_corpus  # type: ignore  # noqa: E402
    from figure_understanding_vlm import FixtureFigureInterpreter  # type: ignore  # noqa: E402

    payload = json.loads((FIXTURES_DIR / "mini_docling_payload.json").read_text(encoding="utf-8"))
    expected_pdf_path = ROOT / "data" / "01_raw" / "pdfs" / "library" / "lattice" / "10_1016_j_addma_2022_102887" / "original.pdf"

    register_path = tmp_path / "paper_register.csv"
    register_path.write_text(
        "paper_id,source_path,library_path\n"
        f"10_1016_j_addma_2022_102887,{expected_pdf_path},{expected_pdf_path}\n",
        encoding="utf-8",
    )

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    seen_paths: list[Path] = []

    def document_provider(pdf_path: Path) -> object:
        seen_paths.append(pdf_path)
        return FakeDocument()

    output_path = tmp_path / "figures_v1.jsonl"
    manifest_path = tmp_path / "manifest.json"
    review_path = tmp_path / "figures_review.csv"

    records = build_figure_understanding_corpus(
        register_path=register_path,
        library_root=LIBRARY_ROOT,
        output_path=output_path,
        manifest_path=manifest_path,
        review_path=review_path,
        interpreter=FixtureFigureInterpreter(FIXTURES_DIR / "mini_vlm_response.json"),
        document_provider=document_provider,
    )

    assert seen_paths == [expected_pdf_path]
    assert len(records) == 1
    assert output_path.exists()
    assert manifest_path.exists()
    assert review_path.exists()

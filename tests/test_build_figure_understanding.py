from __future__ import annotations

import base64
import csv
import json
from io import BytesIO
from pathlib import Path
import sys

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_figure_understanding import build_figure_understanding_corpus  # type: ignore  # noqa: E402
from build_figure_understanding import extract_figures  # type: ignore  # noqa: E402
from build_figure_understanding import _materialize_picture_image  # type: ignore  # noqa: E402


LIBRARY_ROOT = ROOT / "data" / "01_raw" / "pdfs" / "library"


def _write_source_image(path: Path, size: tuple[int, int], left_color: tuple[int, int, int], right_color: tuple[int, int, int]) -> None:
    image = Image.new("RGB", size)
    mid_x = size[0] // 2
    for x in range(size[0]):
        for y in range(size[1]):
            image.putpixel((x, y), left_color if x < mid_x else right_color)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def test_materialize_picture_image_overwrites_existing_placeholder(tmp_path: Path) -> None:
    target_root = tmp_path / "artifact" / "images"
    stale_path = target_root / "10_1016_j_addma_2022_102887" / "fig_001.png"
    _write_source_image(stale_path, (1, 1), (255, 255, 255), (255, 255, 255))

    buffer = BytesIO()
    Image.new("RGB", (2, 2), (255, 0, 0)).save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")

    picture = {
        "image": {
            "uri": f"data:image/png;base64,{encoded}",
            "mimetype": "image/png",
        }
    }

    result_path = _materialize_picture_image(
        picture=picture,
        paper_id="10_1016_j_addma_2022_102887",
        figure_id="fig_001",
        image_output_root=target_root,
    )

    assert result_path == str(stale_path)
    with Image.open(stale_path) as image:
        assert image.size == (2, 2)
        assert image.getpixel((0, 0))[:3] == (255, 0, 0)


def test_extract_figures_emits_unit_records_and_writes_distinct_crops(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    source_image = artifact_dir / "images" / "10_1016_j_addma_2022_102887" / "fig_003.png"
    _write_source_image(source_image, (8, 4), (255, 0, 0), (0, 0, 255))

    payload = {
        "pictures": [
            {
                "figure_id": "fig_003",
                "prov": [{"page_no": 5}],
                "captions": [
                    "Figure 3. Composite figure summarizing structure, curve, and failure snapshots."
                ],
                "description": "Panel a, b, and c are a composite figure with curves, snapshots, and fracture path annotations.",
                "image_path": str(source_image),
            }
        ]
    }

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    class FakeFigureInterpreter:
        def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
            assert image_path == str(source_image)
            assert caption_text == "Figure 3. Composite figure summarizing structure, curve, and failure snapshots."
            assert context_text == "Panel a, b, and c are a composite figure with curves, snapshots, and fracture path annotations."
            return {
                "units": [
                    {
                        "panel_label": "a",
                        "kind": "panel",
                        "crop_bbox": {"l": 0, "t": 0, "r": 4, "b": 4},
                        "figure_type": "curve_plot",
                        "recaption": "Panel a shows the stress-strain response.",
                        "figure_summary": "The left half shows the response curve.",
                        "confidence": 0.92,
                        "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:5", "figure:fig_003"],
                    },
                    {
                        "panel_label": "b",
                        "kind": "panel",
                        "crop_bbox": {"l": 4, "t": 0, "r": 8, "b": 4},
                        "figure_type": "curve_plot",
                        "recaption": "Panel b shows the deformed specimen.",
                        "figure_summary": "The right half shows the post-compression state.",
                        "confidence": 0.90,
                        "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:5", "figure:fig_003"],
                    },
                ]
            }

    records = extract_figures(
        FakeDocument(),
        paper_id="10_1016_j_addma_2022_102887",
        source_path="data/01_raw/pdfs/library/lattice/10_1016_j_addma_2022_102887/original.pdf",
        interpreter=FakeFigureInterpreter(),
        review_threshold=0.85,
        image_output_root=artifact_dir / "images",
    )

    assert len(records) == 2
    assert [record["unit_id"] for record in records] == ["fig_003_a", "fig_003_b"]
    assert [record["source_figure_id"] for record in records] == ["fig_003", "fig_003"]
    assert [record["panel_label"] for record in records] == ["a", "b"]
    assert [record["needs_manual_review"] for record in records] == [False, False]

    first_crop = Image.open(artifact_dir / "images" / "10_1016_j_addma_2022_102887" / "fig_003_a.png")
    second_crop = Image.open(artifact_dir / "images" / "10_1016_j_addma_2022_102887" / "fig_003_b.png")
    try:
        assert first_crop.size == (4, 4)
        assert second_crop.size == (4, 4)
        assert first_crop.getpixel((0, 0)) == (255, 0, 0)
        assert second_crop.getpixel((0, 0)) == (0, 0, 255)
    finally:
        first_crop.close()
        second_crop.close()


def test_extract_figures_recovers_page_caption_and_skips_page_one_noise(tmp_path: Path) -> None:
    noise_image = tmp_path / "noise.png"
    real_image = tmp_path / "real.png"
    _write_source_image(noise_image, (29, 29), (32, 32, 32), (64, 64, 64))
    _write_source_image(real_image, (8, 4), (255, 255, 0), (0, 128, 0))

    payload = {
        "texts": [
            {
                "text": "Fig. 2. Stress-strain curves under quasi-static compression.",
                "prov": [{"page_no": 2, "bbox": {"l": 40.0, "t": 430.0, "r": 420.0, "b": 410.0}}],
            }
        ],
        "pictures": [
            {
                "figure_id": "fig_noise",
                "prov": [{"page_no": 1, "bbox": {"l": 20.0, "t": 720.0, "r": 180.0, "b": 640.0}}],
                "captions": [],
                "children": [],
                "image": {"size": {"width": 29.0, "height": 29.0}},
                "image_path": str(noise_image),
            },
            {
                "figure_id": "fig_real",
                "prov": [{"page_no": 2, "bbox": {"l": 50.0, "t": 700.0, "r": 420.0, "b": 500.0}}],
                "captions": [{"$ref": "#/texts/0"}],
                "children": [{"$ref": "#/texts/0"}],
                "image_path": str(real_image),
            },
        ],
    }

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    class CaptionAwareInterpreter:
        def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
            assert image_path == str(real_image)
            assert caption_text == "Fig. 2. Stress-strain curves under quasi-static compression."
            assert context_text == "Fig. 2. Stress-strain curves under quasi-static compression."
            return {
                "units": [
                    {
                        "panel_label": "",
                        "kind": "figure",
                        "crop_bbox": {"l": 0, "t": 0, "r": 8, "b": 4},
                        "figure_type": "curve_plot",
                        "recaption": "Compression curves compare gyroid and diamond lattices.",
                        "figure_summary": "The plot shows stress-strain response under compression.",
                        "confidence": 0.91,
                        "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:2", "figure:fig_real"],
                    }
                ]
            }

    records = extract_figures(
        FakeDocument(),
        paper_id="10_1016_j_addma_2022_102887",
        source_path="data/01_raw/pdfs/library/lattice/10_1016_j_addma_2022_102887/original.pdf",
        interpreter=CaptionAwareInterpreter(),
        review_threshold=0.85,
        image_output_root=tmp_path / "artifact" / "images",
    )

    assert len(records) == 1
    assert records[0]["unit_id"] == "fig_real_u01"
    assert records[0]["source_figure_id"] == "fig_real"
    assert records[0]["caption_text"] == "Fig. 2. Stress-strain curves under quasi-static compression."
    assert records[0]["context_text"] == "Fig. 2. Stress-strain curves under quasi-static compression."
    assert records[0]["needs_manual_review"] is False


def test_build_corpus_resolves_source_path_register_column_and_writes_unit_outputs(tmp_path: Path) -> None:
    payload = {
        "pictures": [
            {
                "figure_id": "fig_001",
                "prov": [{"page_no": 3}],
                "captions": ["Figure 2. Stress-strain curves under quasi-static compression."],
                "description": "The figure compares gyroid and diamond lattice responses under compression.",
                "image_path": str(tmp_path / "source.png"),
            }
        ]
    }
    source_image = Path(payload["pictures"][0]["image_path"])
    _write_source_image(source_image, (8, 4), (255, 0, 0), (0, 0, 255))

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    class FakeFigureInterpreter:
        def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
            return {
                "units": [
                    {
                        "panel_label": "a",
                        "kind": "panel",
                        "crop_bbox": {"l": 0, "t": 0, "r": 4, "b": 4},
                        "figure_type": "curve_plot",
                        "recaption": "Panel a shows the stress-strain response.",
                        "figure_summary": "The panel shows the response curve for the gyroid lattice.",
                        "confidence": 0.92,
                        "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:3", "figure:fig_001"],
                    }
                ]
            }

    register_path = tmp_path / "paper_register.csv"
    register_path.write_text(
        "paper_id,source_path,library_path\n"
        "10_1016_j_addma_2022_102887," + str(source_image) + "," + str(source_image) + "\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "figure_units_v1.jsonl"
    manifest_path = tmp_path / "manifest.json"
    review_path = tmp_path / "figure_units_review.csv"

    records = build_figure_understanding_corpus(
        register_path=register_path,
        library_root=LIBRARY_ROOT,
        output_path=output_path,
        manifest_path=manifest_path,
        review_path=review_path,
        interpreter=FakeFigureInterpreter(),
        document_provider=lambda _pdf_path: FakeDocument(),
    )

    assert len(records) == 1
    assert output_path.exists()
    assert manifest_path.exists()
    assert review_path.exists()

    jsonl_rows = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert jsonl_rows[0]["unit_id"] == "fig_001_a"
    assert jsonl_rows[0]["source_figure_id"] == "fig_001"
    assert jsonl_rows[0]["image_path"].endswith("fig_001_a.png")

    with review_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == [
        {
            "paper_id": "10_1016_j_addma_2022_102887",
            "source_figure_id": "fig_001",
            "unit_id": "fig_001_a",
            "unit_index": "1",
            "kind": "panel",
            "panel_label": "a",
            "source_page_no": "3",
            "source_image_path": str(source_image),
            "image_path": str(output_path.parent / "images" / "10_1016_j_addma_2022_102887" / "fig_001_a.png"),
            "crop_bbox": "{\"l\": 0, \"t\": 0, \"r\": 4, \"b\": 4}",
            "caption_text": "Figure 2. Stress-strain curves under quasi-static compression.",
            "context_text": "The figure compares gyroid and diamond lattice responses under compression.",
            "figure_type": "curve_plot",
            "recaption": "Panel a shows the stress-strain response.",
            "figure_summary": "The panel shows the response curve for the gyroid lattice.",
            "confidence": "0.92",
            "needs_manual_review": "false",
            "source_refs": "paper:10_1016_j_addma_2022_102887;page:3;figure:fig_001",
        }
    ]

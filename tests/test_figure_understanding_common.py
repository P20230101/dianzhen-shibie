from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from figure_understanding_common import build_unit_record, normalize_panel_labels, write_jsonl, write_review_csv  # type: ignore  # noqa: E402


def test_normalize_panel_labels_sorts_and_deduplicates() -> None:
    assert normalize_panel_labels(["b", " a ", "A", None, ""]) == ["a", "b"]


def test_build_unit_record_matches_contract() -> None:
    raw = {
        "paper_id": "10_1016_j_addma_2022_102887",
        "source_figure_id": "fig_003",
        "unit_id": "fig_003_a",
        "unit_index": 1,
        "kind": "panel",
        "panel_label": "a",
        "source_page_no": 5,
        "source_image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_003.png",
        "image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_003_a.png",
        "crop_bbox": {"l": 12, "t": 34, "r": 56, "b": 78},
        "caption_text": "Figure 3. Composite figure summarizing structure, curve, and failure snapshots.",
        "context_text": "Panel a, b, and c are a composite figure with curves, snapshots, and fracture path annotations.",
    }

    interpretation = {
        "figure_type": "curve_plot",
        "recaption": "Panel a shows the stress-strain response.",
        "figure_summary": "The panel shows the response curve for the gyroid lattice.",
        "confidence": 0.92,
        "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:5", "figure:fig_003"],
    }

    record = build_unit_record(raw, interpretation, review_threshold=0.8)

    assert record == {
        "paper_id": "10_1016_j_addma_2022_102887",
        "source_figure_id": "fig_003",
        "unit_id": "fig_003_a",
        "unit_index": 1,
        "kind": "panel",
        "panel_label": "a",
        "source_page_no": 5,
        "source_image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_003.png",
        "image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_003_a.png",
        "crop_bbox": {"l": 12, "t": 34, "r": 56, "b": 78},
        "caption_text": "Figure 3. Composite figure summarizing structure, curve, and failure snapshots.",
        "context_text": "Panel a, b, and c are a composite figure with curves, snapshots, and fracture path annotations.",
        "figure_type": "curve_plot",
        "recaption": "Panel a shows the stress-strain response.",
        "figure_summary": "The panel shows the response curve for the gyroid lattice.",
        "confidence": 0.92,
        "needs_manual_review": False,
        "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:5", "figure:fig_003"],
    }


def test_write_jsonl_and_review_csv_round_trip(tmp_path: Path) -> None:
    raw = {
        "paper_id": "10_1016_j_addma_2022_102887",
        "source_figure_id": "fig_003",
        "unit_id": "fig_003_a",
        "unit_index": 1,
        "kind": "panel",
        "panel_label": "a",
        "source_page_no": 5,
        "source_image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_003.png",
        "image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_003_a.png",
        "crop_bbox": {"l": 12, "t": 34, "r": 56, "b": 78},
        "caption_text": "Figure 3. Composite figure summarizing structure, curve, and failure snapshots.",
        "context_text": "Panel a, b, and c are a composite figure with curves, snapshots, and fracture path annotations.",
    }
    interpretation = {
        "figure_type": "curve_plot",
        "recaption": "Panel a shows the stress-strain response.",
        "figure_summary": "The panel shows the response curve for the gyroid lattice.",
        "confidence": 0.92,
        "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:5", "figure:fig_003"],
    }
    record = build_unit_record(raw, interpretation, review_threshold=0.8)

    jsonl_path = tmp_path / "figure_units_v1.jsonl"
    csv_path = tmp_path / "figure_units_review.csv"
    write_jsonl([record], jsonl_path)
    write_review_csv([record], csv_path)

    jsonl_rows = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert jsonl_rows == [record]

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == [
        {
            "paper_id": "10_1016_j_addma_2022_102887",
            "source_figure_id": "fig_003",
            "unit_id": "fig_003_a",
            "unit_index": "1",
            "kind": "panel",
            "panel_label": "a",
            "source_page_no": "5",
            "source_image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_003.png",
            "image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_003_a.png",
            "crop_bbox": "{\"l\": 12, \"t\": 34, \"r\": 56, \"b\": 78}",
            "caption_text": "Figure 3. Composite figure summarizing structure, curve, and failure snapshots.",
            "context_text": "Panel a, b, and c are a composite figure with curves, snapshots, and fracture path annotations.",
            "figure_type": "curve_plot",
            "recaption": "Panel a shows the stress-strain response.",
            "figure_summary": "The panel shows the response curve for the gyroid lattice.",
            "confidence": "0.92",
            "needs_manual_review": "false",
            "source_refs": "paper:10_1016_j_addma_2022_102887;page:5;figure:fig_003",
        }
    ]

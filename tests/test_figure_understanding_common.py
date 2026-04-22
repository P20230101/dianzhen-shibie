from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from figure_understanding_common import build_figure_record, normalize_panel_labels, write_jsonl, write_review_csv  # type: ignore  # noqa: E402
from retrieval_kg_common import read_json  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "figure_understanding"


def test_normalize_panel_labels_sorts_and_deduplicates() -> None:
    assert normalize_panel_labels(["b", " a ", "A", None, ""]) == ["a", "b"]


def test_build_figure_record_matches_fixture_contract() -> None:
    payload = read_json(FIXTURES_DIR / "mini_figure_payload.json")
    expected = read_json(FIXTURES_DIR / "mini_figure_expected.json")
    assert isinstance(payload, dict)

    record = build_figure_record(
        raw=payload["raw"],
        interpretation=payload["interpretation"],
        review_threshold=float(payload["review_threshold"]),
    )

    assert record == expected


def test_write_jsonl_and_review_csv_round_trip(tmp_path: Path) -> None:
    payload = read_json(FIXTURES_DIR / "mini_figure_payload.json")
    expected = read_json(FIXTURES_DIR / "mini_figure_expected.json")
    record = build_figure_record(
        raw=payload["raw"],
        interpretation=payload["interpretation"],
        review_threshold=float(payload["review_threshold"]),
    )

    jsonl_path = tmp_path / "figures_v1.jsonl"
    csv_path = tmp_path / "figures_review.csv"
    write_jsonl([record], jsonl_path)
    write_review_csv([record], csv_path)

    jsonl_rows = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert jsonl_rows == [expected]

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == [
        {
            "paper_id": "10_1016_j_addma_2022_102887",
            "figure_id": "fig_001",
            "page_no": "3",
            "image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_001.png",
            "caption_text": "Stress-strain curves of gyroid and diamond lattices.",
            "context_text": "Figure 2 shows quasi-static compression results.",
            "panel_labels": "a;b",
            "figure_type": "curve_plot",
            "recaption": "Stress-strain curves compare gyroid and diamond lattices.",
            "figure_summary": "The curves show distinct plateau behavior under compression.",
            "confidence": "0.78",
            "needs_manual_review": "true",
            "source_refs": "paper:10_1016_j_addma_2022_102887;page:3;figure:fig_001",
        }
    ]

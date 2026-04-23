from __future__ import annotations

import csv
import json
import re
from pathlib import Path
import sys

from PIL import Image
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_figure_understanding_report import (  # type: ignore  # noqa: E402
    load_manifest,
    load_records,
    main,
    render_report_html,
    write_report_html,
)


def _write_review_csv(path: Path, records: list[dict[str, object]]) -> None:
    fieldnames = [
        "paper_id",
        "source_figure_id",
        "unit_id",
        "unit_index",
        "kind",
        "panel_label",
        "source_page_no",
        "source_image_path",
        "image_path",
        "crop_bbox",
        "caption_text",
        "context_text",
        "figure_type",
        "recaption",
        "figure_summary",
        "confidence",
        "needs_manual_review",
        "source_refs",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "paper_id": record["paper_id"],
                    "source_figure_id": record["source_figure_id"],
                    "unit_id": record["unit_id"],
                    "unit_index": record["unit_index"],
                    "kind": record["kind"],
                    "panel_label": record["panel_label"],
                    "source_page_no": record["source_page_no"],
                    "source_image_path": record["source_image_path"],
                    "image_path": record["image_path"],
                    "crop_bbox": json.dumps(record["crop_bbox"], ensure_ascii=False),
                    "caption_text": record["caption_text"],
                    "context_text": record["context_text"],
                    "figure_type": record["figure_type"],
                    "recaption": record["recaption"],
                    "figure_summary": record["figure_summary"],
                    "confidence": record["confidence"],
                    "needs_manual_review": str(bool(record["needs_manual_review"])).lower(),
                    "source_refs": ";".join(str(item) for item in record["source_refs"]),
                }
            )


def _write_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1, 1), color)
    image.save(path)


def test_load_records_and_render_report_html(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    image_dir = artifact_dir / "images" / "paper_1"
    image_dir.mkdir(parents=True)
    _write_image(image_dir / "fig_003_a.png", (255, 0, 0))
    _write_image(image_dir / "fig_003_b.png", (0, 0, 255))

    record_b = {
        "paper_id": "paper_1",
        "source_figure_id": "fig_003",
        "unit_id": "fig_003_b",
        "unit_index": 2,
        "kind": "panel",
        "panel_label": "b",
        "source_page_no": 5,
        "source_image_path": str(image_dir / "fig_003.png"),
        "image_path": str(image_dir / "fig_003_b.png"),
        "crop_bbox": {"l": 4, "t": 0, "r": 8, "b": 4},
        "caption_text": "Caption <two> & \"quoted\"",
        "context_text": "Context > two",
        "figure_type": "curve_plot",
        "recaption": "Recaption B & details",
        "figure_summary": "Summary with <tag> B",
        "confidence": 0.55,
        "needs_manual_review": True,
        "source_refs": ["ref:2"],
    }
    record_a = {
        "paper_id": "paper_1",
        "source_figure_id": "fig_003",
        "unit_id": "fig_003_a",
        "unit_index": 1,
        "kind": "panel",
        "panel_label": "a",
        "source_page_no": 5,
        "source_image_path": str(image_dir / "fig_003.png"),
        "image_path": str(image_dir / "fig_003_a.png"),
        "crop_bbox": {"l": 0, "t": 0, "r": 4, "b": 4},
        "caption_text": "Caption <one> & \"quoted\"",
        "context_text": "Context > one",
        "figure_type": "curve_plot",
        "recaption": "Recaption A & details",
        "figure_summary": "Summary with <tag> A",
        "confidence": 0.91,
        "needs_manual_review": False,
        "source_refs": ["ref:1"],
    }

    (artifact_dir / "figure_units_v1.jsonl").write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in [record_b, record_a]) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figure_units_review.csv", [record_a, record_b])

    manifest = {
        "register_path": "register.csv",
        "library_root": "library",
        "output_path": "figure_units_v1.jsonl",
        "review_path": "figure_units_review.csv",
        "paper_count": 1,
        "source_figure_count": 1,
        "unit_count": 2,
        "paper_ids": ["paper_1"],
    }
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    loaded_records = load_records(artifact_dir)
    loaded_manifest = load_manifest(artifact_dir)

    assert [record["unit_id"] for record in loaded_records] == ["fig_003_a", "fig_003_b"]
    assert [record["image_path"] for record in loaded_records] == [
        "images/paper_1/fig_003_a.png",
        "images/paper_1/fig_003_b.png",
    ]
    assert loaded_manifest == manifest

    html = render_report_html("paper_1", loaded_manifest, loaded_records, "2026-04-23 10:11:12")

    assert "paper_1" in html
    assert "Source figure count" in html
    assert "Unit count" in html
    assert "Auto-pass count" in html
    assert "Manual-review count" in html
    assert "2026-04-23 10:11:12" in html
    assert html.count('class="figure-card"') == 2
    assert 'data-status="auto-pass"' in html
    assert 'data-status="manual-review"' in html
    assert 'src="images/paper_1/fig_003_a.png"' in html
    assert 'src="images/paper_1/fig_003_b.png"' in html
    assert "unit_id" in html
    assert "source_figure_id" in html
    assert "crop_bbox" in html
    assert "figure_type" in html
    assert "confidence" in html
    assert "needs_manual_review" in html
    assert "caption_text" in html
    assert "recaption" in html
    assert "figure_summary" in html
    assert "source_refs" in html
    assert "subfigure_map" not in html
    assert "Caption &lt;one&gt; &amp; &quot;quoted&quot;" in html
    assert "Summary with &lt;tag&gt; A" in html
    assert "ref:1" in html

    output_path = artifact_dir / "report.html"
    write_report_html(output_path, html)
    assert output_path.read_text(encoding="utf-8") == html


def test_main_builds_self_contained_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    artifact_dir = tmp_path / "artifact"
    image_dir = artifact_dir / "images" / "paper_1"
    image_dir.mkdir(parents=True)
    _write_image(image_dir / "fig_020_a.png", (0, 255, 0))

    record = {
        "paper_id": "paper_1",
        "source_figure_id": "fig_020",
        "unit_id": "fig_020_a",
        "unit_index": 1,
        "kind": "panel",
        "panel_label": "a",
        "source_page_no": 8,
        "source_image_path": str(image_dir / "fig_020.png"),
        "image_path": str(image_dir / "fig_020_a.png"),
        "crop_bbox": {"l": 0, "t": 0, "r": 1, "b": 1},
        "caption_text": "Caption",
        "context_text": "Context",
        "figure_type": "comparison",
        "recaption": "Recaption",
        "figure_summary": "Summary",
        "confidence": 0.8,
        "needs_manual_review": False,
        "source_refs": [],
    }

    (artifact_dir / "figure_units_v1.jsonl").write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figure_units_review.csv", [record])
    (artifact_dir / "manifest.json").write_text(
        json.dumps(
            {
                "paper_count": 1,
                "source_figure_count": 1,
                "unit_count": 1,
                "paper_ids": ["paper_1"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "report"
    exit_code = main([
        "--artifact-dir",
        str(artifact_dir),
        "--output-dir",
        str(output_dir),
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert (output_dir / "index.html").exists()
    assert (output_dir / "images" / "paper_1" / "fig_020_a.png").exists()
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert 'img src="images/paper_1/fig_020_a.png"' in html
    assert str(output_dir / "index.html") in captured.out


def test_load_records_rejects_multiple_papers_in_one_artifact_dir(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    artifact_dir.mkdir(parents=True)

    records = [
        {
            "paper_id": "paper_a",
            "source_figure_id": "fig_001",
            "unit_id": "fig_001_a",
            "unit_index": 1,
            "kind": "panel",
            "panel_label": "a",
            "source_page_no": 1,
            "source_image_path": "images/fig_001.png",
            "image_path": "images/fig_001_a.png",
            "crop_bbox": {"l": 0, "t": 0, "r": 1, "b": 1},
            "caption_text": "Caption A",
            "context_text": "Context A",
            "figure_type": "table",
            "recaption": "Recaption A",
            "figure_summary": "Summary A",
            "confidence": 0.9,
            "needs_manual_review": False,
            "source_refs": [],
        },
        {
            "paper_id": "paper_b",
            "source_figure_id": "fig_001",
            "unit_id": "fig_001_b",
            "unit_index": 1,
            "kind": "panel",
            "panel_label": "b",
            "source_page_no": 2,
            "source_image_path": "images/fig_001.png",
            "image_path": "images/fig_001_b.png",
            "crop_bbox": {"l": 0, "t": 0, "r": 1, "b": 1},
            "caption_text": "Caption B",
            "context_text": "Context B",
            "figure_type": "table",
            "recaption": "Recaption B",
            "figure_summary": "Summary B",
            "confidence": 0.9,
            "needs_manual_review": False,
            "source_refs": [],
        },
    ]

    (artifact_dir / "figure_units_v1.jsonl").write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figure_units_review.csv", records)
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 2, "source_figure_count": 2, "unit_count": 2}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="multiple paper_id values"):
        load_records(artifact_dir)


def test_load_records_rejects_duplicate_unit_keys(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    artifact_dir.mkdir(parents=True)

    records = [
        {
            "paper_id": "paper_a",
            "source_figure_id": "fig_001",
            "unit_id": "fig_001_a",
            "unit_index": 1,
            "kind": "panel",
            "panel_label": "a",
            "source_page_no": 1,
            "source_image_path": "images/fig_001_a.png",
            "image_path": "images/fig_001_a.png",
            "crop_bbox": {"l": 0, "t": 0, "r": 1, "b": 1},
            "caption_text": "Caption A",
            "context_text": "Context A",
            "figure_type": "table",
            "recaption": "Recaption A",
            "figure_summary": "Summary A",
            "confidence": 0.9,
            "needs_manual_review": False,
            "source_refs": [],
        },
        {
            "paper_id": "paper_a",
            "source_figure_id": "fig_001",
            "unit_id": "fig_001_a",
            "unit_index": 2,
            "kind": "panel",
            "panel_label": "a",
            "source_page_no": 2,
            "source_image_path": "images/fig_001_b.png",
            "image_path": "images/fig_001_b.png",
            "crop_bbox": {"l": 0, "t": 0, "r": 1, "b": 1},
            "caption_text": "Caption B",
            "context_text": "Context B",
            "figure_type": "table",
            "recaption": "Recaption B",
            "figure_summary": "Summary B",
            "confidence": 0.9,
            "needs_manual_review": False,
            "source_refs": [],
        },
    ]

    (artifact_dir / "figure_units_v1.jsonl").write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figure_units_review.csv", records)
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 1, "source_figure_count": 1, "unit_count": 2}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate paper_id/unit_id pair"):
        load_records(artifact_dir)


def test_load_records_rejects_image_paths_outside_artifact_image_root(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    artifact_dir.mkdir(parents=True)

    record = {
        "paper_id": "paper_a",
        "source_figure_id": "fig_002",
        "unit_id": "fig_002_a",
        "unit_index": 1,
        "kind": "panel",
        "panel_label": "a",
        "source_page_no": 1,
        "source_image_path": "images/fig_002.png",
        "image_path": "fig_002.png",
        "crop_bbox": {"l": 0, "t": 0, "r": 1, "b": 1},
        "caption_text": "Caption",
        "context_text": "Context",
        "figure_type": "table",
        "recaption": "Recaption",
        "figure_summary": "Summary",
        "confidence": 0.9,
        "needs_manual_review": False,
        "source_refs": [],
    }

    (artifact_dir / "figure_units_v1.jsonl").write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figure_units_review.csv", [record])
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 1, "source_figure_count": 1, "unit_count": 1}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="expected artifact image root"):
        load_records(artifact_dir)


def test_load_records_rejects_review_status_mismatch(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    artifact_dir.mkdir(parents=True)

    record = {
        "paper_id": "paper_a",
        "source_figure_id": "fig_003",
        "unit_id": "fig_003_a",
        "unit_index": 1,
        "kind": "panel",
        "panel_label": "a",
        "source_page_no": 1,
        "source_image_path": "images/fig_003.png",
        "image_path": "images/fig_003.png",
        "crop_bbox": {"l": 0, "t": 0, "r": 1, "b": 1},
        "caption_text": "Caption",
        "context_text": "Context",
        "figure_type": "table",
        "recaption": "Recaption",
        "figure_summary": "Summary",
        "confidence": 0.9,
        "needs_manual_review": False,
        "source_refs": [],
    }

    review_row = dict(record)
    review_row["needs_manual_review"] = True

    (artifact_dir / "figure_units_v1.jsonl").write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figure_units_review.csv", [review_row])
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 1, "source_figure_count": 1, "unit_count": 1}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="needs_manual_review mismatch"):
        load_records(artifact_dir)


def test_load_records_rejects_malformed_review_status(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    artifact_dir.mkdir(parents=True)

    record = {
        "paper_id": "paper_a",
        "source_figure_id": "fig_004",
        "unit_id": "fig_004_a",
        "unit_index": 1,
        "kind": "panel",
        "panel_label": "a",
        "source_page_no": 1,
        "source_image_path": "images/fig_004.png",
        "image_path": "images/fig_004.png",
        "crop_bbox": {"l": 0, "t": 0, "r": 1, "b": 1},
        "caption_text": "Caption",
        "context_text": "Context",
        "figure_type": "table",
        "recaption": "Recaption",
        "figure_summary": "Summary",
        "confidence": 0.9,
        "needs_manual_review": False,
        "source_refs": [],
    }

    (artifact_dir / "figure_units_v1.jsonl").write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (artifact_dir / "figure_units_review.csv").write_text(
        "paper_id,source_figure_id,unit_id,unit_index,kind,panel_label,source_page_no,source_image_path,image_path,crop_bbox,caption_text,context_text,figure_type,recaption,figure_summary,confidence,needs_manual_review,source_refs\n"
        "paper_a,fig_004,fig_004_a,1,panel,a,1,images/fig_004.png,images/fig_004.png,\"{\"\"l\"\": 0, \"\"t\"\": 0, \"\"r\"\": 1, \"\"b\"\": 1}\",Caption,Context,table,Recaption,Summary,0.9,maybe,\n",
        encoding="utf-8",
    )
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 1, "source_figure_count": 1, "unit_count": 1}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid needs_manual_review value"):
        load_records(artifact_dir)

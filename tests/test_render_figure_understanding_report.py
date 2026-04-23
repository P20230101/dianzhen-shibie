from __future__ import annotations

import csv
import json
import re
from pathlib import Path
import sys

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
        "figure_id",
        "page_no",
        "image_path",
        "caption_text",
        "context_text",
        "panel_labels",
        "subfigure_map",
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
                    "figure_id": record["figure_id"],
                    "page_no": record["page_no"],
                    "image_path": record["image_path"],
                    "caption_text": record["caption_text"],
                    "context_text": record["context_text"],
                    "panel_labels": ";".join(str(item) for item in record["panel_labels"]),
                    "subfigure_map": json.dumps(record["subfigure_map"], ensure_ascii=False),
                    "figure_type": record["figure_type"],
                    "recaption": record["recaption"],
                    "figure_summary": record["figure_summary"],
                    "confidence": record["confidence"],
                    "needs_manual_review": str(bool(record["needs_manual_review"])).lower(),
                    "source_refs": ";".join(str(item) for item in record["source_refs"]),
                }
            )


def test_load_records_and_render_report_html(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    image_dir = artifact_dir / "images"
    image_dir.mkdir(parents=True)
    (image_dir / "fig_a.png").write_bytes(b"a")
    (image_dir / "fig_b.png").write_bytes(b"b")

    record_b = {
        "paper_id": "paper<1>",
        "figure_id": "fig_b",
        "page_no": 8,
        "image_path": str(image_dir / "fig_b.png"),
        "caption_text": "Caption <two> & \"quoted\"",
        "context_text": "Context > two",
        "panel_labels": ["b"],
        "subfigure_map": {"b": "right & panel"},
        "figure_type": "microstructure_image",
        "recaption": "Recaption B & details",
        "figure_summary": "Summary with <tag> B",
        "confidence": 0.55,
        "needs_manual_review": True,
        "source_refs": ["ref:2"],
    }
    record_a = {
        "paper_id": "paper<1>",
        "figure_id": "fig_a",
        "page_no": 3,
        "image_path": str(image_dir / "fig_a.png"),
        "caption_text": "Caption <one> & \"quoted\"",
        "context_text": "Context > one",
        "panel_labels": ["a", "b"],
        "subfigure_map": {"a": "left <panel>", "b": "right & panel"},
        "figure_type": "curve_plot",
        "recaption": "Recaption A & details",
        "figure_summary": "Summary with <tag> A",
        "confidence": 0.91,
        "needs_manual_review": False,
        "source_refs": ["ref:1"],
    }

    (artifact_dir / "figures_v1.jsonl").write_text(
        "\n".join(
            json.dumps(record, ensure_ascii=False)
            for record in [record_b, record_a]
        )
        + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figures_review.csv", [record_a, record_b])

    manifest = {
        "register_path": "register.csv",
        "library_root": "library",
        "output_path": "figures_v1.jsonl",
        "review_path": "figures_review.csv",
        "paper_count": 1,
        "figure_count": 2,
        "paper_ids": ["paper<1>"],
    }
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    loaded_records = load_records(artifact_dir)
    loaded_manifest = load_manifest(artifact_dir)

    assert [record["figure_id"] for record in loaded_records] == ["fig_a", "fig_b"]
    assert [record["image_path"] for record in loaded_records] == [
        "images/fig_a.png",
        "images/fig_b.png",
    ]
    assert loaded_manifest == manifest

    html = render_report_html("paper<1>", loaded_manifest, loaded_records, "2026-04-23 10:11:12")

    assert "paper&lt;1&gt;" in html
    assert "Figure count" in html
    assert "Auto-pass count" in html
    assert "Manual-review count" in html
    assert "2026-04-23 10:11:12" in html
    assert html.count('class="figure-card"') == 2
    assert 'data-status="auto-pass"' in html
    assert 'data-status="manual-review"' in html
    assert 'src="images/fig_a.png"' in html
    assert 'src="images/fig_b.png"' in html
    assert "figure_id" in html
    assert "page_no" in html
    assert "figure_type" in html
    assert "confidence" in html
    assert "needs_manual_review" in html
    assert "caption_text" in html
    assert "recaption" in html
    assert "figure_summary" in html
    assert "panel_labels" in html
    assert "subfigure_map" in html
    assert re.search(r'<span class="summary-label">Figure count</span>\s*<div class="summary-value">2</div>', html)
    assert re.search(r'<span class="summary-label">Auto-pass count</span>\s*<div class="summary-value">1</div>', html)
    assert re.search(r'<span class="summary-label">Manual-review count</span>\s*<div class="summary-value">1</div>', html)
    assert "Caption &lt;one&gt; &amp; &quot;quoted&quot;" in html
    assert "Summary with &lt;tag&gt; A" in html
    assert "left &lt;panel&gt;" in html

    output_path = artifact_dir / "report.html"
    write_report_html(output_path, html)
    assert output_path.read_text(encoding="utf-8") == html


def test_main_builds_self_contained_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    artifact_dir = tmp_path / "artifact"
    image_dir = artifact_dir / "images" / "10_1016_j_matdes_2018_05_059"
    image_dir.mkdir(parents=True)
    (image_dir / "fig_020.png").write_bytes(b"figure-020")

    record = {
        "paper_id": "10_1016_j_matdes_2018_05_059",
        "figure_id": "fig_020",
        "page_no": 8,
        "image_path": str(image_dir / "fig_020.png"),
        "caption_text": "Fig. 9. Comparison of FEA efficiency parameter at the plateau end between the MJF HP PA12 (a) Octagonal and (b) Kelvin lattices.",
        "context_text": "Fig. 9. Comparison of FEA efficiency parameter at the plateau end between the MJF HP PA12 (a) Octagonal and (b) Kelvin lattices.",
        "panel_labels": ["(a) octagonal", "(b) kelvin lattices"],
        "subfigure_map": {"octagonal": "Fig. 9(a)", "kelvin": "Fig. 9(b)"},
        "figure_type": "Comparison",
        "recaption": "Fig. 9. Comparison of FEA efficiency parameter at the plateau end between the MJF HP PA12 (a) Octagonal and (b) Kelvin lattices.",
        "figure_summary": "The figure compares the FEA efficiency parameters for two different lattice structures.",
        "confidence": 0.8,
        "needs_manual_review": False,
        "source_refs": [],
    }

    (artifact_dir / "figures_v1.jsonl").write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figures_review.csv", [record])
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 1, "figure_count": 1, "manual_review_count": 0}, ensure_ascii=False),
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
    assert (output_dir / "images" / "10_1016_j_matdes_2018_05_059" / "fig_020.png").exists()
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert 'img src="images/10_1016_j_matdes_2018_05_059/fig_020.png"' in html
    assert str(output_dir / "index.html") in captured.out


def test_load_records_rejects_multiple_papers_in_one_artifact_dir(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    artifact_dir.mkdir(parents=True)

    records = [
        {
            "paper_id": "paper_a",
            "figure_id": "fig_001",
            "page_no": 1,
            "image_path": "images/fig_001.png",
            "caption_text": "Caption A",
            "context_text": "Context A",
            "panel_labels": [],
            "subfigure_map": {},
            "figure_type": "table",
            "recaption": "Recaption A",
            "figure_summary": "Summary A",
            "confidence": 0.9,
            "needs_manual_review": False,
            "source_refs": [],
        },
        {
            "paper_id": "paper_b",
            "figure_id": "fig_001",
            "page_no": 2,
            "image_path": "images/fig_001.png",
            "caption_text": "Caption B",
            "context_text": "Context B",
            "panel_labels": [],
            "subfigure_map": {},
            "figure_type": "table",
            "recaption": "Recaption B",
            "figure_summary": "Summary B",
            "confidence": 0.9,
            "needs_manual_review": False,
            "source_refs": [],
        },
    ]

    (artifact_dir / "figures_v1.jsonl").write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figures_review.csv", records)
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 2, "figure_count": 2}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="multiple paper_id values"):
        load_records(artifact_dir)


def test_load_records_rejects_duplicate_figure_keys(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    artifact_dir.mkdir(parents=True)

    records = [
        {
            "paper_id": "paper_a",
            "figure_id": "fig_001",
            "page_no": 1,
            "image_path": "images/fig_001_a.png",
            "caption_text": "Caption A",
            "context_text": "Context A",
            "panel_labels": [],
            "subfigure_map": {},
            "figure_type": "table",
            "recaption": "Recaption A",
            "figure_summary": "Summary A",
            "confidence": 0.9,
            "needs_manual_review": False,
            "source_refs": [],
        },
        {
            "paper_id": "paper_a",
            "figure_id": "fig_001",
            "page_no": 2,
            "image_path": "images/fig_001_b.png",
            "caption_text": "Caption B",
            "context_text": "Context B",
            "panel_labels": [],
            "subfigure_map": {},
            "figure_type": "table",
            "recaption": "Recaption B",
            "figure_summary": "Summary B",
            "confidence": 0.9,
            "needs_manual_review": False,
            "source_refs": [],
        },
    ]

    (artifact_dir / "figures_v1.jsonl").write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figures_review.csv", records)
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 1, "figure_count": 2}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate paper_id/figure_id pair"):
        load_records(artifact_dir)


def test_load_records_rejects_image_paths_outside_artifact_image_root(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    artifact_dir.mkdir(parents=True)

    record = {
        "paper_id": "paper_a",
        "figure_id": "fig_002",
        "page_no": 1,
        "image_path": "fig_002.png",
        "caption_text": "Caption",
        "context_text": "Context",
        "panel_labels": [],
        "subfigure_map": {},
        "figure_type": "table",
        "recaption": "Recaption",
        "figure_summary": "Summary",
        "confidence": 0.9,
        "needs_manual_review": False,
        "source_refs": [],
    }

    (artifact_dir / "figures_v1.jsonl").write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figures_review.csv", [record])
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 1, "figure_count": 1}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="expected artifact image root"):
        load_records(artifact_dir)


def test_load_records_rejects_review_status_mismatch(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    artifact_dir.mkdir(parents=True)

    record = {
        "paper_id": "paper_a",
        "figure_id": "fig_003",
        "page_no": 1,
        "image_path": "images/fig_003.png",
        "caption_text": "Caption",
        "context_text": "Context",
        "panel_labels": [],
        "subfigure_map": {},
        "figure_type": "table",
        "recaption": "Recaption",
        "figure_summary": "Summary",
        "confidence": 0.9,
        "needs_manual_review": False,
        "source_refs": [],
    }

    review_row = dict(record)
    review_row["needs_manual_review"] = True

    (artifact_dir / "figures_v1.jsonl").write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_review_csv(artifact_dir / "figures_review.csv", [review_row])
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 1, "figure_count": 1}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="needs_manual_review mismatch"):
        load_records(artifact_dir)


def test_load_records_rejects_malformed_review_status(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "data" / "03_figures"
    artifact_dir.mkdir(parents=True)

    record = {
        "paper_id": "paper_a",
        "figure_id": "fig_004",
        "page_no": 1,
        "image_path": "images/fig_004.png",
        "caption_text": "Caption",
        "context_text": "Context",
        "panel_labels": [],
        "subfigure_map": {},
        "figure_type": "table",
        "recaption": "Recaption",
        "figure_summary": "Summary",
        "confidence": 0.9,
        "needs_manual_review": False,
        "source_refs": [],
    }

    review_row = dict(record)
    review_row["needs_manual_review"] = "maybe"

    (artifact_dir / "figures_v1.jsonl").write_text(
        json.dumps(record, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (artifact_dir / "figures_review.csv").write_text(
        "paper_id,figure_id,page_no,image_path,caption_text,context_text,panel_labels,subfigure_map,figure_type,recaption,figure_summary,confidence,needs_manual_review,source_refs\n"
        "paper_a,fig_004,1,images/fig_004.png,Caption,Context,,{},table,Recaption,Summary,0.9,maybe,\n",
        encoding="utf-8",
    )
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"paper_count": 1, "figure_count": 1}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid needs_manual_review value"):
        load_records(artifact_dir)

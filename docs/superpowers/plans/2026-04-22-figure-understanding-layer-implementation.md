# Figure Understanding Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn PDF figures into image-level structured records with type, panel labels, recaption, summary, and confidence, stored under `data/03_figures/` and ready for downstream sample extraction.

**Architecture:** Reuse the current PDF intake/register flow to locate papers, run a figure-aware Docling parse with OCR and picture images enabled, then pass each figure through a pluggable vision interpreter. Keep the output boundary narrow: this branch writes only figure artifacts and tests, not sample/evidence or KG.

**Tech Stack:** Python, Docling, VLM backend, PaddleOCR/Uni-Parser support, JSONL/CSV, pytest fixtures

---

### Task 1: Define the figure record contract and fixture inputs

**Files:**
- Create: `scripts/figure_understanding_common.py`
- Create: `data/03_figures/README.md`
- Create: `tests/fixtures/figure_understanding/mini_figure_payload.json`
- Create: `tests/fixtures/figure_understanding/mini_figure_expected.json`
- Create: `tests/test_figure_understanding_common.py`

- [ ] **Step 1: Write the failing test**

```python
from figure_understanding_common import build_figure_record


def test_build_figure_record_normalizes_and_flags_review():
    raw = {
        "paper_id": "10_1016_j_addma_2022_102887",
        "figure_id": "fig_001",
        "page_no": 3,
        "image_path": "data/03_figures/images/10_1016_j_addma_2022_102887/fig_001.png",
        "caption_text": "Stress-strain curves of gyroid and diamond lattices.",
        "context_text": "Figure 2 shows quasi-static compression results.",
    }
    interpretation = {
        "panel_labels": ["b", "a"],
        "figure_type": "curve_plot",
        "recaption": "Stress-strain curves compare gyroid and diamond lattices.",
        "figure_summary": "The curves show distinct plateau behavior under compression.",
        "confidence": 0.78,
        "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:3", "figure:fig_001"],
    }

    record = build_figure_record(raw, interpretation, review_threshold=0.85)

    assert record["paper_id"] == "10_1016_j_addma_2022_102887"
    assert record["panel_labels"] == ["a", "b"]
    assert record["figure_type"] == "curve_plot"
    assert record["needs_manual_review"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
pytest tests/test_figure_understanding_common.py -v
```

Expected: FAIL because `scripts/figure_understanding_common.py` and `build_figure_record` do not exist yet.

- [ ] **Step 3: Write the minimal implementation**

```python
from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass(frozen=True)
class FigureRecord:
    paper_id: str
    figure_id: str
    page_no: int | None
    image_path: str
    caption_text: str | None
    context_text: str | None
    panel_labels: list[str]
    figure_type: str
    recaption: str | None
    figure_summary: str | None
    confidence: float
    needs_manual_review: bool
    source_refs: list[str]


def normalize_panel_labels(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    labels = sorted({str(item).strip() for item in value if str(item).strip()})
    return labels


def build_figure_record(raw: dict[str, object], interpretation: dict[str, object], review_threshold: float) -> dict[str, object]:
    confidence = float(interpretation.get("confidence") or 0.0)
    record = FigureRecord(
        paper_id=str(raw["paper_id"]),
        figure_id=str(raw["figure_id"]),
        page_no=raw.get("page_no") if isinstance(raw.get("page_no"), int) else None,
        image_path=str(raw["image_path"]),
        caption_text=str(raw["caption_text"]) if raw.get("caption_text") is not None else None,
        context_text=str(raw["context_text"]) if raw.get("context_text") is not None else None,
        panel_labels=normalize_panel_labels(interpretation.get("panel_labels")),
        figure_type=str(interpretation.get("figure_type") or "unknown"),
        recaption=str(interpretation.get("recaption")) if interpretation.get("recaption") is not None else None,
        figure_summary=str(interpretation.get("figure_summary")) if interpretation.get("figure_summary") is not None else None,
        confidence=confidence,
        needs_manual_review=confidence < review_threshold,
        source_refs=[str(item) for item in interpretation.get("source_refs", []) if str(item).strip()],
    )
    return asdict(record)


def write_jsonl(records: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False))
            handle.write("\n")


def write_review_csv(records: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "paper_id",
        "figure_id",
        "page_no",
        "image_path",
        "caption_text",
        "context_text",
        "panel_labels",
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
            row = dict(record)
            row["panel_labels"] = ";".join(record.get("panel_labels", []))
            row["source_refs"] = ";".join(record.get("source_refs", []))
            writer.writerow(row)
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
pytest tests/test_figure_understanding_common.py -v
```

Expected: PASS, and `data/03_figures/README.md` should describe the JSONL/CSV fields without conflicting with sample/evidence.

- [ ] **Step 5: Commit**

```powershell
git add scripts/figure_understanding_common.py data/03_figures/README.md tests/fixtures/figure_understanding/mini_figure_payload.json tests/fixtures/figure_understanding/mini_figure_expected.json tests/test_figure_understanding_common.py
git commit -m "docs: define figure understanding record contract"
```

---

### Task 2: Build the figure registry and binding extractor

**Files:**
- Create: `scripts/build_figure_understanding.py`
- Create: `tests/test_build_figure_understanding.py`
- Create: `tests/fixtures/figure_understanding/mini_docling_payload.json`
- Create: `tests/fixtures/figure_understanding/mini_figure_image.png`

- [ ] **Step 1: Write the failing test**

```python
from build_figure_understanding import extract_figures


class FakeFigureInterpreter:
    def interpret(self, image_path, caption_text, context_text):
        return {
            "panel_labels": ["a"],
            "figure_type": "curve_plot",
            "recaption": "Compression curve of a gyroid lattice.",
            "figure_summary": "The plot shows stress-strain response under compression.",
            "confidence": 0.91,
            "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:3", "figure:fig_001"],
        }


def test_extract_figures_emits_image_level_records(tmp_path: Path):
    payload = {
        "texts": [
            {
                "label": "text",
                "text": "Figure 2. Stress-strain curves under quasi-static compression.",
                "prov": [{"page_no": 3}],
            }
        ],
        "pictures": [
            {
                "figure_id": "fig_001",
                "prov": [{"page_no": 3}],
                "captions": [{"$ref": "#/texts/0"}],
                "image_path": "tests/fixtures/figure_understanding/mini_figure_image.png",
                "bbox": [10, 20, 30, 40],
            }
        ],
    }

    class FakeDocument:
        def export_to_dict(self):
            return payload

    records = extract_figures(
        FakeDocument(),
        paper_id="10_1016_j_addma_2022_102887",
        source_path="data/01_raw/pdfs/library/lattice/10_1016_j_addma_2022_102887/original.pdf",
        interpreter=FakeFigureInterpreter(),
        review_threshold=0.85,
    )

    assert len(records) == 1
    assert records[0]["figure_id"] == "fig_001"
    assert records[0]["figure_type"] == "curve_plot"
    assert records[0]["needs_manual_review"] is False
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
pytest tests/test_build_figure_understanding.py -v
```

Expected: FAIL because `extract_figures` and the figure pipeline script do not exist yet.

- [ ] **Step 3: Write the minimal implementation**

```python
from __future__ import annotations

import argparse
import csv
import json
from functools import lru_cache
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from figure_understanding_common import build_figure_record, write_jsonl, write_review_csv


@lru_cache(maxsize=1)
def _converter() -> DocumentConverter:
    pipeline_options = PdfPipelineOptions(
        do_ocr=True,
        force_backend_text=True,
        generate_page_images=True,
        generate_picture_images=True,
        do_picture_classification=True,
        do_picture_description=True,
        do_chart_extraction=True,
        do_code_enrichment=False,
        do_formula_enrichment=False,
    )
    return DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)},
    )


def extract_figures(document, paper_id: str, source_path: str, interpreter, review_threshold: float) -> list[dict[str, object]]:
    payload = document.export_to_dict()
    texts = payload.get("texts", [])
    pictures = payload.get("pictures", [])
    records: list[dict[str, object]] = []
    for index, item in enumerate(pictures, start=1):
        figure_id = str(item.get("figure_id") or f"fig_{index:03d}")
        page_no = item.get("prov", [{}])[0].get("page_no") if isinstance(item.get("prov"), list) else None
        caption_text = " ".join(
            str(texts[int(ref["$ref"].split("/")[-1])]["text"]).strip()
            for ref in item.get("captions", [])
            if isinstance(ref, dict) and isinstance(ref.get("$ref"), str)
        ) or None
        image_path = str(item.get("image_path") or item.get("image_uri") or item.get("image_file"))
        raw = {
            "paper_id": paper_id,
            "figure_id": figure_id,
            "page_no": page_no,
            "image_path": image_path,
            "caption_text": caption_text,
            "context_text": caption_text,
        }
        interpretation = interpreter.interpret(image_path=image_path, caption_text=caption_text, context_text=caption_text)
        records.append(build_figure_record(raw, interpretation, review_threshold))
    return records
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
pytest tests/test_build_figure_understanding.py -v
```

Expected: PASS, and the CLI path should write `data/03_figures/figures_v1.jsonl`, `data/03_figures/figures_review.csv`, and `data/03_figures/manifest.json`.

- [ ] **Step 5: Commit**

```powershell
git add scripts/build_figure_understanding.py tests/test_build_figure_understanding.py tests/fixtures/figure_understanding/mini_docling_payload.json tests/fixtures/figure_understanding/mini_figure_image.png
git commit -m "feat: add figure registry and binding extractor"
```

---

### Task 3: Add the vision interpreter and end-to-end smoke

**Files:**
- Create: `scripts/figure_understanding_vlm.py`
- Create: `tests/test_figure_understanding_vlm.py`
- Create: `tests/fixtures/figure_understanding/mini_vlm_response.json`
- Create: `tests/fixtures/figure_understanding/mini_register.csv`
- Create: `tests/test_figure_understanding_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from figure_understanding_vlm import FixtureFigureInterpreter


def test_fixture_backend_returns_stable_figure_semantics():
    backend = FixtureFigureInterpreter(Path("tests/fixtures/figure_understanding/mini_vlm_response.json"))
    result = backend.interpret(
        image_path="tests/fixtures/figure_understanding/mini_figure_image.png",
        caption_text="Figure 2. Stress-strain curves under quasi-static compression.",
        context_text="Figure 2 shows the comparison between gyroid and diamond lattices.",
    )

    assert result["figure_type"] == "curve_plot"
    assert result["confidence"] > 0.8
    assert "gyroid" in result["figure_summary"].lower()
```

```python
from pathlib import Path

from build_figure_understanding import build_figure_understanding_corpus
from figure_understanding_vlm import FixtureFigureInterpreter


def test_end_to_end_smoke_writes_figure_outputs(tmp_path: Path):
    output_path = tmp_path / "figures_v1.jsonl"
    manifest_path = tmp_path / "manifest.json"
    review_path = tmp_path / "figures_review.csv"
    backend = FixtureFigureInterpreter(Path("tests/fixtures/figure_understanding/mini_vlm_response.json"))

    class FakeDocument:
        def export_to_dict(self):
            return {
                "texts": [
                    {
                        "label": "text",
                        "text": "Figure 2. Stress-strain curves under quasi-static compression.",
                        "prov": [{"page_no": 3}],
                    }
                ],
                "pictures": [
                    {
                        "figure_id": "fig_001",
                        "prov": [{"page_no": 3}],
                        "captions": [{"$ref": "#/texts/0"}],
                        "image_path": "tests/fixtures/figure_understanding/mini_figure_image.png",
                        "bbox": [10, 20, 30, 40],
                    }
                ],
            }

    build_figure_understanding_corpus(
        register_path=Path("tests/fixtures/figure_understanding/mini_register.csv"),
        library_root=Path("data/01_raw/pdfs/library"),
        output_path=output_path,
        manifest_path=manifest_path,
        review_path=review_path,
        interpreter=backend,
        document_provider=lambda _pdf_path: FakeDocument(),
    )

    assert output_path.exists()
    assert manifest_path.exists()
    assert review_path.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
pytest tests/test_figure_understanding_vlm.py tests/test_figure_understanding_smoke.py -v
```

Expected: FAIL because `FixtureFigureInterpreter` and `build_figure_understanding_corpus` for the new layer do not exist yet.

- [ ] **Step 3: Write the minimal implementation**

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FixtureFigureInterpreter:
    response_path: Path

    def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
        payload = json.loads(self.response_path.read_text(encoding="utf-8"))
        return payload


@dataclass(frozen=True)
class VlmFigureInterpreter:
    model: str

    def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
        raise NotImplementedError("wire this to the configured vision backend")
```

```python
def build_figure_understanding_corpus(
    register_path: Path,
    library_root: Path,
    output_path: Path,
    manifest_path: Path,
    review_path: Path,
    interpreter,
    review_threshold: float = 0.85,
    document_provider=None,
) -> dict[str, object]:
    rows = list(csv.DictReader(register_path.open("r", encoding="utf-8-sig", newline="")))
    records: list[dict[str, object]] = []
    paper_count = 0

    for row in rows:
        paper_id = str(row["paper_id"]).strip()
        family = str(row.get("family") or "").strip()
        source_path = str(row.get("library_path") or (library_root / family / paper_id / "original.pdf"))
        pdf_path = Path(source_path)
        if document_provider is None:
            document = _converter().convert(str(pdf_path), raises_on_error=False).document
        else:
            document = document_provider(pdf_path)
        records.extend(extract_figures(document, paper_id, source_path, interpreter, review_threshold))
        paper_count += 1

    write_jsonl(records, output_path)
    review_rows = [record for record in records if record["needs_manual_review"]]
    write_review_csv(review_rows, review_path)
    manifest = {
        "paper_count": paper_count,
        "figure_count": len(records),
        "output_path": str(output_path),
        "review_path": str(review_path),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
pytest tests/test_figure_understanding_common.py tests/test_build_figure_understanding.py tests/test_figure_understanding_vlm.py tests/test_figure_understanding_smoke.py -v
```

Expected: PASS, with the smoke confirming the chain writes figure-level outputs without touching sample/evidence or KG.

- [ ] **Step 5: Commit**

```powershell
git add scripts/figure_understanding_vlm.py tests/test_figure_understanding_vlm.py tests/test_figure_understanding_smoke.py tests/fixtures/figure_understanding/mini_vlm_response.json tests/fixtures/figure_understanding/mini_register.csv
git commit -m "feat: add figure vision backend and smoke coverage"
```

---

## Coverage Check

- Figure-level schema, normalization, and file contract are covered by Task 1.
- Figure registry extraction from PDF parsing is covered by Task 2.
- Actual image recognition through a pluggable VLM backend and end-to-end smoke verification are covered by Task 3.
- The plan stays out of sample/evidence and KG so the execution boundary remains isolated.

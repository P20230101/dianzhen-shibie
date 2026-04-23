# Figure Understanding Unit Record Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn each independently crop-able figure panel into its own output record, with its own image crop, card, review state, and traceability back to the source figure.

**Architecture:** This branch starts without the figure-understanding baseline, so the first task is to bring in the existing figure pipeline files from the current figure-understanding branch. After that, the data model changes from figure-level records to unit-level records, the crop writer emits one image per unit, and the report renderer consumes only unit-level outputs. The report remains static HTML, but the card count now matches the number of unit records rather than the number of source figures.

**Tech Stack:** Python 3.11+, Docling, PIL, JSONL/CSV, pytest, local Chrome for visual smoke

---

### Task 1: Bring the existing figure-understanding baseline into this branch

**Files:**
- Modify: `scripts/figure_understanding_common.py`
- Modify: `scripts/figure_understanding_vlm.py`
- Modify: `scripts/build_figure_understanding.py`
- Modify: `scripts/render_figure_understanding_report.py`
- Modify: `tests/test_figure_understanding_common.py`
- Modify: `tests/test_figure_understanding_vlm.py`
- Modify: `tests/test_build_figure_understanding.py`
- Modify: `tests/test_render_figure_understanding_report.py`
- Modify: `data/03_figures/README.md`
- Modify: `tests/fixtures/figure_understanding/*`

- [ ] **Step 1: Import the figure-understanding baseline from the existing implementation branch**

Run:

```bash
git merge --no-ff feat/task-023-figure-understanding
```

Expected: the branch gains the figure-understanding pipeline files and fixtures without changing the unit-record behavior yet.

- [ ] **Step 2: Verify the baseline tests now exist and still pass**

Run:

```bash
pytest tests/test_figure_understanding_common.py tests/test_figure_understanding_vlm.py tests/test_build_figure_understanding.py tests/test_render_figure_understanding_report.py -v
```

Expected: PASS on the imported baseline.

- [ ] **Step 3: Commit the baseline sync**

```bash
git add scripts/figure_understanding_common.py scripts/figure_understanding_vlm.py scripts/build_figure_understanding.py scripts/render_figure_understanding_report.py tests/test_figure_understanding_common.py tests/test_figure_understanding_vlm.py tests/test_build_figure_understanding.py tests/test_render_figure_understanding_report.py data/03_figures/README.md tests/fixtures/figure_understanding
git commit -m "feat: import figure understanding baseline"
```

### Task 2: Convert the output model to unit-level records

**Files:**
- Modify: `scripts/figure_understanding_common.py`
- Modify: `scripts/build_figure_understanding.py`
- Modify: `scripts/figure_understanding_vlm.py`
- Modify: `tests/test_figure_understanding_common.py`
- Modify: `tests/test_build_figure_understanding.py`
- Modify: `tests/test_figure_understanding_vlm.py`
- Create: `tests/fixtures/figure_understanding_unit_records/mini_unit_payload.json`
- Create: `tests/fixtures/figure_understanding_unit_records/mini_unit_expected.json`

- [ ] **Step 1: Write a failing unit-level schema test**

```python
def test_build_figure_record_emits_unit_fields() -> None:
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
        "figure_type": "composite_figure",
        "recaption": "Panel a shows the stress-strain response.",
        "figure_summary": "The panel shows the response curve for the gyroid lattice.",
        "confidence": 0.92,
        "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:5", "figure:fig_003"],
    }

    record = build_unit_record(raw, interpretation, review_threshold=0.8)

    assert record["unit_id"] == "fig_003_a"
    assert record["source_figure_id"] == "fig_003"
    assert record["image_path"].endswith("fig_003_a.png")
    assert record["needs_manual_review"] is False
```

- [ ] **Step 2: Run the test to confirm it fails**

Run:

```bash
pytest tests/test_figure_understanding_common.py -k unit_record -v
```

Expected: FAIL because the current baseline still emits figure-level records.

- [ ] **Step 3: Implement the unit record builder and crop metadata normalization**

Add the new record shape in `scripts/figure_understanding_common.py`:

```python
@dataclass(frozen=True)
class FigureUnitRecord:
    paper_id: str
    unit_id: str
    source_figure_id: str
    unit_index: int
    kind: str
    panel_label: str | None
    source_page_no: int | None
    source_image_path: str
    image_path: str
    crop_bbox: dict[str, object]
    caption_text: str | None
    context_text: str | None
    figure_type: str
    recaption: str | None
    figure_summary: str | None
    confidence: float
    needs_manual_review: bool
    source_refs: list[str]
```

Keep the review CSV aligned with the JSONL by writing one row per unit record, and drop `subfigure_map` from the persisted outputs.

- [ ] **Step 4: Run the unit tests again**

Run:

```bash
pytest tests/test_figure_understanding_common.py tests/test_build_figure_understanding.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit the unit-schema change**

```bash
git add scripts/figure_understanding_common.py scripts/build_figure_understanding.py scripts/figure_understanding_vlm.py tests/test_figure_understanding_common.py tests/test_build_figure_understanding.py tests/test_figure_understanding_vlm.py tests/fixtures/figure_understanding_unit_records
git commit -m "feat: emit unit-level figure records"
```

### Task 3: Split crops and report rendering by unit

**Files:**
- Modify: `scripts/build_figure_understanding.py`
- Modify: `scripts/render_figure_understanding_report.py`
- Modify: `tests/test_build_figure_understanding.py`
- Modify: `tests/test_render_figure_understanding_report.py`
- Create: `tests/fixtures/figure_understanding_unit_records/mini_unit_image.png`

- [ ] **Step 1: Write a failing crop-and-render test**

```python
def test_extract_units_writes_distinct_crops_and_report_cards(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    image_dir = artifact_dir / "images" / "10_1016_j_addma_2022_102887"
    image_dir.mkdir(parents=True)
    (image_dir / "fig_003_a.png").write_bytes(b"a")
    (image_dir / "fig_003_b.png").write_bytes(b"b")

    records = [
        {
            "paper_id": "10_1016_j_addma_2022_102887",
            "unit_id": "fig_003_a",
            "source_figure_id": "fig_003",
            "unit_index": 1,
            "kind": "panel",
            "panel_label": "a",
            "source_page_no": 5,
            "source_image_path": str(image_dir / "fig_003.png"),
            "image_path": str(image_dir / "fig_003_a.png"),
            "crop_bbox": {"l": 12, "t": 34, "r": 56, "b": 78},
            "caption_text": "Figure 3. Composite figure summarizing structure, curve, and failure snapshots.",
            "context_text": "Panel a, b, and c are a composite figure with curves, snapshots, and fracture path annotations.",
            "figure_type": "composite_figure",
            "recaption": "Panel a shows the stress-strain response.",
            "figure_summary": "The panel shows the response curve for the gyroid lattice.",
            "confidence": 0.92,
            "needs_manual_review": False,
            "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:5", "figure:fig_003"],
        },
        {
            "paper_id": "10_1016_j_addma_2022_102887",
            "unit_id": "fig_003_b",
            "source_figure_id": "fig_003",
            "unit_index": 2,
            "kind": "panel",
            "panel_label": "b",
            "source_page_no": 5,
            "source_image_path": str(image_dir / "fig_003.png"),
            "image_path": str(image_dir / "fig_003_b.png"),
            "crop_bbox": {"l": 60, "t": 34, "r": 104, "b": 78},
            "caption_text": "Figure 3. Composite figure summarizing structure, curve, and failure snapshots.",
            "context_text": "Panel a, b, and c are a composite figure with curves, snapshots, and fracture path annotations.",
            "figure_type": "composite_figure",
            "recaption": "Panel b shows the deformed specimen.",
            "figure_summary": "The panel shows the post-compression specimen state.",
            "confidence": 0.90,
            "needs_manual_review": False,
            "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:5", "figure:fig_003"],
        },
    ]

    review_path = artifact_dir / "figure_units_review.csv"
    jsonl_path = artifact_dir / "figure_units_v1.jsonl"
    manifest_path = artifact_dir / "manifest.json"
    write_jsonl(records, jsonl_path)
    write_review_csv(records, review_path)
    write_json(
        manifest_path,
        {
            "figure_count": 2,
            "paper_count": 1,
            "manual_review_count": 0,
            "paper_ids": ["10_1016_j_addma_2022_102887"],
        },
    )

    loaded = load_records(artifact_dir)
    html = render_report_html(
        "10_1016_j_addma_2022_102887",
        load_manifest(artifact_dir),
        loaded,
        "2026-04-23 10:00",
    )

    assert len(loaded) == 2
    assert html.count('class="figure-card"') == 2
    assert 'subfigure_map' not in html
    assert 'src="images/10_1016_j_addma_2022_102887/fig_003_a.png"' in html
    assert 'src="images/10_1016_j_addma_2022_102887/fig_003_b.png"' in html
```

The test should assert:

1. two unit images exist
2. unit IDs are unique
3. the report contains two cards
4. the report no longer renders a `subfigure_map` block as the primary output

- [ ] **Step 2: Run the test to confirm the current renderer fails**

Run:

```bash
pytest tests/test_build_figure_understanding.py tests/test_render_figure_understanding_report.py -k unit -v
```

Expected: FAIL because the current baseline still renders figure-level cards.

- [ ] **Step 3: Implement unit crop generation and unit card rendering**

Update `scripts/build_figure_understanding.py` so the splitter emits one record per unit and the crop writer saves each crop under `data/03_figures/images/<paper_id>/<unit_id>.png`.

Update `scripts/render_figure_understanding_report.py` so it:

```python
def load_records(artifact_dir: Path) -> list[dict[str, object]]:
    jsonl_path = artifact_dir / "figure_units_v1.jsonl"
    review_path = artifact_dir / "figure_units_review.csv"
    records = _read_jsonl_records(jsonl_path)
    review_rows = _read_review_rows(review_path)
    return _ordered_unit_records(records, review_rows)

def _render_unit_card(record: dict[str, object]) -> str:
    status = _status_for_record(record)
    image_src = html_escape(str(record.get("image_path") or ""), quote=True)
    unit_id = _escape_text(record.get("unit_id"))
    return (
        f'<article class="figure-card" data-status="{status}">'
        '<div class="figure-media">'
        f'<img src="{image_src}" alt="Crop for unit {unit_id}">'
        "</div>"
        '<div class="figure-content">'
        '<div class="figure-heading">'
        f"<h2>{unit_id}</h2>"
        f'<span class="status-badge">{html_escape(status, quote=True)}</span>'
        "</div>"
        '<div class="field-grid">'
        f"{_render_field('unit_id', unit_id)}"
        f"{_render_field('source_figure_id', _escape_text(record.get('source_figure_id')))}"
        f"{_render_field('panel_label', _escape_text(record.get('panel_label')))}"
        f"{_render_field('kind', _escape_text(record.get('kind')))}"
        f"{_render_field('source_page_no', _escape_text(record.get('source_page_no')))}"
        f"{_render_field('figure_type', _escape_text(record.get('figure_type')))}"
        f"{_render_field('recaption', _escape_text(record.get('recaption')))}"
        f"{_render_field('figure_summary', _escape_text(record.get('figure_summary')))}"
        "</div>"
        "</div>"
        "</article>"
    )
```

The report should keep the same static HTML shape, but the card body must be unit-level.

- [ ] **Step 4: Run the renderer tests**

Run:

```bash
pytest tests/test_render_figure_understanding_report.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit the render split**

```bash
git add scripts/build_figure_understanding.py scripts/render_figure_understanding_report.py tests/test_build_figure_understanding.py tests/test_render_figure_understanding_report.py tests/fixtures/figure_understanding_unit_records/mini_unit_image.png
git commit -m "feat: render unit-level figure cards"
```

### Task 4: Verify end-to-end output in Chrome

**Files:**
- Modify: `scripts/render_figure_understanding_report.py`
- Modify: `tests/test_render_figure_understanding_report.py`

- [ ] **Step 1: Generate the unit-level report artifact**

Run:

```bash
python scripts/render_figure_understanding_report.py --artifact-dir data/03_figures --output-dir reports/figure-understanding-unit-records/10_1016_j_addma_2022_102887
```

- [ ] **Step 2: Open the generated HTML in Chrome**

Open:

```text
reports/figure-understanding-unit-records/10_1016_j_addma_2022_102887/index.html
```

Verify in Chrome that:

1. every panel-level unit has its own card
2. each card shows its own crop
3. the source figure traceability is visible
4. the card count matches the unit count

- [ ] **Step 3: Run the final test pass**

Run:

```bash
pytest tests/test_build_figure_understanding.py tests/test_render_figure_understanding_report.py tests/test_figure_understanding_common.py tests/test_figure_understanding_vlm.py -v
```

Expected: PASS.

- [ ] **Step 4: Commit the final branch state**

```bash
git add scripts/ tests/ docs/superpowers/plans/2026-04-23-figure-understanding-unit-record-implementation.md
git commit -m "feat: make figure understanding unit-level"
```

### Self-Review

**1. Spec coverage:**  
- Unit-level records are the new primary output.
- Crops are written per unit.
- Review state is unit-specific.
- The report renders one card per unit.
- Chrome verification is included at the end.

**2. Placeholder scan:**  
- No vague implementation notes remain in the tasks.
- Every task has concrete files and commands.

**3. Type consistency:**  
- `unit_id`, `source_figure_id`, `unit_index`, `crop_bbox`, and `source_image_path` are used consistently across the tasks.
- The output filenames remain `figure_units_v1.jsonl`, `figure_units_review.csv`, and `manifest.json`.

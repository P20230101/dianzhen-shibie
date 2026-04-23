# Figure Understanding Report Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a self-contained static HTML report that makes the figure-understanding output readable without JSON.

**Architecture:** A single Python renderer reads one paper's `figures_v1.jsonl`, `manifest.json`, and `figures_review.csv`, copies the referenced crop images into a report-local `images/` tree, and emits one `index.html` with inline CSS and no runtime dependencies. The page shows the paper summary first, then one card per figure with the original crop and the structured interpretation side by side. Tests cover the renderer directly plus a CLI smoke that builds a report from fixture artifacts.

**Tech Stack:** Python 3.11+, standard library (`argparse`, `csv`, `html`, `json`, `pathlib`, `shutil`, `datetime`), pytest.

---

### Task 1: Build the report renderer core

**Files:**
- Create: `C:\Users\Administrator\Desktop\dianzhen shujuku\.worktrees\task-023-figure-understanding-finish\scripts\render_figure_understanding_report.py`
- Create: `C:\Users\Administrator\Desktop\dianzhen shujuku\.worktrees\task-023-figure-understanding-finish\tests\test_render_figure_understanding_report.py`

- [ ] **Step 1: Write the failing test**

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_figure_understanding_report import render_report_html


def test_render_report_html_shows_summary_and_status_cards() -> None:
    records = [
        {
            "paper_id": "10_1016_j_matdes_2018_05_059",
            "figure_id": "fig_020",
            "page_no": 8,
            "image_path": "images/10_1016_j_matdes_2018_05_059/fig_020.png",
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
        },
        {
            "paper_id": "10_1016_j_matdes_2018_05_059",
            "figure_id": "fig_002",
            "page_no": 1,
            "image_path": "images/10_1016_j_matdes_2018_05_059/fig_002.png",
            "caption_text": None,
            "context_text": None,
            "panel_labels": ["1", "2", "3"],
            "subfigure_map": {"1": "Simple cubic lattice"},
            "figure_type": "SEM images",
            "recaption": "A series of SEM images showing different lattice structures.",
            "figure_summary": "The image shows a progression from a simple cubic structure to more complex lattices.",
            "confidence": 95.0,
            "needs_manual_review": True,
            "source_refs": [],
        },
    ]

    html = render_report_html(
        paper_id="10_1016_j_matdes_2018_05_059",
        manifest={"figure_count": 2, "paper_count": 1, "manual_review_count": 1},
        records=records,
        generated_at="2026-04-23 10:00",
    )

    assert "Figure Understanding Report" in html
    assert "10_1016_j_matdes_2018_05_059" in html
    assert "fig_020" in html
    assert "fig_002" in html
    assert "Comparison" in html
    assert "Manual review" in html
    assert 'data-status="auto-pass"' in html
    assert 'data-status="manual-review"' in html
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
pytest tests/test_render_figure_understanding_report.py -v
```

Expected: fail with `ModuleNotFoundError` or missing `render_report_html`.

- [ ] **Step 3: Write the minimal implementation**

Implement the renderer with these exact responsibilities:

```python
def load_records(artifact_dir: Path) -> list[dict[str, object]]: ...
def load_manifest(artifact_dir: Path) -> dict[str, object]: ...
def render_report_html(
    paper_id: str,
    manifest: dict[str, object],
    records: list[dict[str, object]],
    generated_at: str,
) -> str: ...
def write_report_html(output_path: Path, html: str) -> None: ...
```

The HTML should:

- render a top summary block with paper ID, figure count, auto-pass count, manual-review count, and generation time
- render one card per figure
- show the crop image on the left and the structured fields on the right
- use `data-status="auto-pass"` and `data-status="manual-review"` on the cards
- escape all user-facing text with `html.escape`

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
pytest tests/test_render_figure_understanding_report.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/render_figure_understanding_report.py tests/test_render_figure_understanding_report.py
git commit -m "feat: add figure understanding report renderer"
```

### Task 2: Add the CLI and self-contained asset materialization

**Files:**
- Modify: `C:\Users\Administrator\Desktop\dianzhen shujuku\.worktrees\task-023-figure-understanding-finish\scripts\render_figure_understanding_report.py`
- Modify: `C:\Users\Administrator\Desktop\dianzhen shujuku\.worktrees\task-023-figure-understanding-finish\tests\test_render_figure_understanding_report.py`

- [ ] **Step 1: Write the failing CLI smoke test**

```python
import sys
from pathlib import Path
import csv
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_figure_understanding_report import main


def test_main_materializes_self_contained_report(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    image_dir = artifact_dir / "images" / "10_1016_j_matdes_2018_05_059"
    image_dir.mkdir(parents=True)

    shutil.copy2(
        Path(r"C:\Users\Administrator\Desktop\dianzhen shujuku\.worktrees\task-023-figure-understanding-finish\tests\fixtures\figure_understanding\mini_figure_image.png"),
        image_dir / "fig_020.png",
    )

    records = [
        {
            "paper_id": "10_1016_j_matdes_2018_05_059",
            "figure_id": "fig_020",
            "page_no": 8,
            "image_path": "images/10_1016_j_matdes_2018_05_059/fig_020.png",
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
    ]

    (artifact_dir / "figures_v1.jsonl").write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )
    (artifact_dir / "manifest.json").write_text(
        json.dumps({"figure_count": 1, "paper_count": 1, "manual_review_count": 0}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (artifact_dir / "figures_review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["paper_id", "figure_id", "image_path"])
        writer.writeheader()
        writer.writerow({"paper_id": "10_1016_j_matdes_2018_05_059", "figure_id": "fig_020", "image_path": "images/10_1016_j_matdes_2018_05_059/fig_020.png"})

    output_dir = tmp_path / "report"
    exit_code = main(["--artifact-dir", str(artifact_dir), "--output-dir", str(output_dir)])

    assert exit_code == 0
    assert (output_dir / "index.html").exists()
    assert (output_dir / "images" / "10_1016_j_matdes_2018_05_059" / "fig_020.png").exists()
    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert 'img src="images/10_1016_j_matdes_2018_05_059/fig_020.png"' in html
```

- [ ] **Step 2: Run the smoke test to verify it fails**

Run:

```bash
pytest tests/test_render_figure_understanding_report.py -v
```

Expected: fail because `main()` does not yet parse the CLI or copy images.

- [ ] **Step 3: Implement the CLI and asset copy**

Add a `main(argv: list[str] | None = None) -> int` entry point that:

1. accepts `--artifact-dir` and `--output-dir`
2. loads `figures_v1.jsonl`, `manifest.json`, and `figures_review.csv`
3. infers the single `paper_id` from the records
4. copies every referenced crop image from `<artifact_dir>/images/<paper_id>/...` into `<output_dir>/images/<paper_id>/...`
5. writes `<output_dir>/index.html`
6. prints the final report path and returns `0`

The CLI should keep the report self-contained by writing relative image links into the HTML, not absolute filesystem paths.

- [ ] **Step 4: Run the smoke test to verify it passes**

Run:

```bash
pytest tests/test_render_figure_understanding_report.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/render_figure_understanding_report.py tests/test_render_figure_understanding_report.py
git commit -m "feat: add figure understanding report cli"
```

### Task 3: Generate and verify the real-paper report locally

**Files:**
- No tracked source files required if the renderer is correct.
- Local output target: `C:\Users\Administrator\Desktop\dianzhen shujuku\reports\figure-understanding\10_1016_j_matdes_2018_05_059\index.html`

- [ ] **Step 1: Run the real-paper report build**

Run:

```bash
python scripts/render_figure_understanding_report.py --artifact-dir _tmp_matdes_figures2 --output-dir reports/figure-understanding/10_1016_j_matdes_2018_05_059
```

Expected:

- `reports/figure-understanding/10_1016_j_matdes_2018_05_059/index.html` exists
- `reports/figure-understanding/10_1016_j_matdes_2018_05_059/images/10_1016_j_matdes_2018_05_059/` contains the copied crops
- the terminal prints the final report path

- [ ] **Step 2: Open the generated `index.html` and inspect the first sample block**

Check that the page visibly shows:

- `fig_005`
- `fig_006`
- `fig_020`
- `fig_021`
- `fig_002`

and that the status color for `fig_002` differs from the auto-pass cards.

- [ ] **Step 3: Commit only if source files changed**

If any source fix is needed after the real-paper run, commit only the source files that were corrected. Do not commit generated `reports/` artifacts.

---

## Self-Review

### Spec coverage

- Top summary block -> Task 1 renderer and Task 2 CLI summary use `manifest.json` and record counts.
- Image + structured text side-by-side -> Task 1 HTML card template.
- Manual-review boundary remains visible -> Task 1 test includes both auto-pass and manual-review cards.
- Self-contained local page -> Task 2 copies images into the report directory and writes relative links.
- No search/filter/multi-page/server -> explicitly excluded from Task 3 and the architecture.

### Placeholder scan

- No `TBD`, `TODO`, or vague "add appropriate handling" steps remain.
- All file paths are explicit.
- All commands are explicit.

### Type consistency

- `render_report_html`, `load_records`, `load_manifest`, `write_report_html`, and `main` are named consistently across both tasks.
- The report directory convention stays fixed at `reports/figure-understanding/<paper_id>/index.html`.
- The asset convention stays fixed at `reports/figure-understanding/<paper_id>/images/<paper_id>/...`.

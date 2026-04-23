# Task Parallelization Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor paper-expansion work so future paper tasks write only paper-local bundle artifacts, while canonical extracted outputs and KG regeneration stay under a separate serial promotion path.

**Architecture:** Replace direct canonical writes in `build_pdf_sample_bundle.py` with a spec-driven bundle writer. Add a separate batch-promotion script that merges completed bundles into canonical outputs before the existing review-promotion and KG steps. Update tests and governance docs so future extract tasks can be parallelized safely.

**Tech Stack:** Python, JSON, pytest, Markdown, Git

---

## File Structure

**Create:**
- `data/03_bundle_specs/10_1016_j_jmrt_2023_05_167.json`
- `data/03_bundle_specs/10_1016_j_addma_2022_102887.json`
- `data/03_bundle_specs/10_1016_j_compstruct_2018_03_050.json`
- `data/03_bundle_specs/10_1016_j_compstruct_2019_111219.json`
- `data/03_bundle_specs/10_1016_j_tws_2019_106436.json`
- `data/03_bundle_specs/10_1016_j_tws_2020_106623.json`
- `data/03_bundle_specs/10_1016_j_matdes_2017_10_028.json`
- `data/03_bundle_specs/10_1016_j_ijimpeng_2023_104713.json`
- `data/03_bundle_specs/10_1016_j_engstruct_2023_116510.json`
- `data/03_bundle_specs/10_3390_ma18040732.json`
- `data/03_bundle_specs/10_1016_j_cirpj_2024_06_009.json`
- `scripts/pdf_bundle_specs.py`
- `scripts/promote_bundle_batch.py`
- `tests/test_promote_bundle_batch.py`
- `outputs/p1/bundles/.gitkeep`

**Modify:**
- `scripts/build_pdf_sample_bundle.py`
- `tests/test_build_pdf_sample_bundle.py`
- `tests/test_promote_p1_review.py`
- `tasks/branch-strategy.md`
- `tasks/project-overview.md`
- `tasks/workspace-map.md`

---

### Task 1: Introduce the bundle-spec contract and bundle-local writer

**Files:**
- Create: `scripts/pdf_bundle_specs.py`
- Modify: `scripts/build_pdf_sample_bundle.py`
- Modify: `tests/test_build_pdf_sample_bundle.py`
- Create: `outputs/p1/bundles/.gitkeep`

- [ ] **Step 1: Write the failing bundle-output test**

Add this test near the top of `tests/test_build_pdf_sample_bundle.py`:

```python
def test_build_pdf_sample_bundle_writes_bundle_outputs(tmp_path: Path) -> None:
    out_dir = tmp_path / "bundles" / "10_1016_j_jmrt_2023_05_167"

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_jmrt_2023_05_167",
        "--out-dir",
        str(out_dir),
    ])

    sample = read_json(out_dir / "sample.json")
    evidence = read_json(out_dir / "evidence.json")
    expected_sample = read_json(FIXTURES_DIR / "expected_sample.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence.json")

    assert exit_code == 0
    assert sample == expected_sample
    assert evidence == expected_evidence
```

- [ ] **Step 2: Run the new test and confirm it fails**

Run:

```powershell
python -m pytest -q tests/test_build_pdf_sample_bundle.py::test_build_pdf_sample_bundle_writes_bundle_outputs
```

Expected: FAIL because the current CLI still expects `--samples` and `--evidence` and does not create bundle-local outputs.

- [ ] **Step 3: Add the spec loader and validator**

Create `scripts/pdf_bundle_specs.py` with this content:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

from p1_pipeline_common import read_json


ROOT = Path(__file__).resolve().parents[1]
SPECS_ROOT = ROOT / "data" / "03_bundle_specs"


def spec_path_for(paper_id: str, specs_root: Path = SPECS_ROOT) -> Path:
    return specs_root / f"{paper_id}.json"


def load_bundle_spec(paper_id: str, specs_root: Path = SPECS_ROOT) -> dict[str, Any]:
    path = spec_path_for(paper_id, specs_root)
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise SystemExit(f"expected object bundle spec in {path}")
    if payload.get("paper_id") != paper_id:
        raise SystemExit(f"paper_id mismatch in {path}")
    if not isinstance(payload.get("sample"), dict):
        raise SystemExit(f"expected object sample in {path}")
    if not isinstance(payload.get("evidence"), list):
        raise SystemExit(f"expected array evidence in {path}")
    if not isinstance(payload.get("required_fragments"), list):
        raise SystemExit(f"expected array required_fragments in {path}")
    return payload


def find_required_chunk(
    paper_chunks: list[dict[str, Any]],
    *,
    table_id: str | None = None,
    chunk_id_suffix: str | None = None,
) -> dict[str, Any]:
    for row in paper_chunks:
        if table_id is not None and row.get("table_id") != table_id:
            continue
        chunk_id = str(row.get("chunk_id") or "")
        if chunk_id_suffix is not None and not chunk_id.endswith(chunk_id_suffix):
            continue
        return row
    raise SystemExit(f"required chunk not found: table_id={table_id!r}, chunk_id_suffix={chunk_id_suffix!r}")


def clean_text(value: str) -> str:
    return " ".join(value.replace("\x00", "").split())


def validate_required_fragments(
    paper_chunks: list[dict[str, Any]],
    required_fragments: list[dict[str, Any]],
) -> None:
    for item in required_fragments:
        if not isinstance(item, dict):
            raise SystemExit("required_fragments rows must be objects")
        chunk = find_required_chunk(
            paper_chunks,
            table_id=item.get("table_id"),
            chunk_id_suffix=item.get("chunk_id_suffix"),
        )
        expected_fragment = str(item.get("fragment") or "")
        context = str(item.get("context") or "bundle validation")
        cleaned = clean_text(str(chunk.get("text") or ""))
        if expected_fragment not in cleaned:
            raise SystemExit(f"{context} text drifted: expected fragment {expected_fragment!r}")
```

- [ ] **Step 4: Rewrite `build_pdf_sample_bundle.py` to load a spec and write one local bundle**

Replace the CLI/output path of `scripts/build_pdf_sample_bundle.py` so the file centers on these functions:

```python
DEFAULT_BUNDLES_ROOT = ROOT / "outputs" / "p1" / "bundles"


def _bundle_out_dir(paper_id: str, bundles_root: Path = DEFAULT_BUNDLES_ROOT) -> Path:
    return bundles_root / paper_id


def build_bundle(
    paper_id: str,
    *,
    register_path: Path = DEFAULT_REGISTER_PATH,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
    specs_root: Path = SPECS_ROOT,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    _load_register_row(paper_id, register_path)
    corpus = _load_jsonl(corpus_path)
    paper_chunks = [row for row in corpus if row.get("paper_id") == paper_id]
    if not paper_chunks:
        raise SystemExit(f"paper_id not found in corpus: {paper_id}")

    spec = load_bundle_spec(paper_id, specs_root)
    validate_required_fragments(paper_chunks, spec["required_fragments"])
    sample = dict(spec["sample"])
    evidence = [dict(row) for row in spec["evidence"]]
    return sample, evidence


def write_bundle(sample: dict[str, Any], evidence: list[dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "sample.json", sample)
    write_json(out_dir / "evidence.json", evidence)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write one paper-derived bundle to a paper-local bundle directory")
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER_PATH)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    args = parser.parse_args(argv)

    sample, evidence = build_bundle(
        args.paper_id,
        register_path=args.register,
        corpus_path=args.corpus,
    )
    out_dir = args.out_dir or _bundle_out_dir(args.paper_id)
    write_bundle(sample, evidence, out_dir)
    return 0
```

Keep `_load_jsonl`, `_load_register_row`, and the chunk-search helpers only if they are still used by the new generic flow. Remove the paper-specific `_build_*_bundle` branches after the spec files exist.

- [ ] **Step 5: Create the bundle root placeholder**

Create `outputs/p1/bundles/.gitkeep`.

- [ ] **Step 6: Re-run the bundle-output test**

Run:

```powershell
python -m pytest -q tests/test_build_pdf_sample_bundle.py::test_build_pdf_sample_bundle_writes_bundle_outputs
```

Expected: PASS and `sample.json` / `evidence.json` are created under the requested `--out-dir`.

- [ ] **Step 7: Commit the contract and local-writer change**

Run:

```powershell
git add scripts/pdf_bundle_specs.py scripts/build_pdf_sample_bundle.py tests/test_build_pdf_sample_bundle.py outputs/p1/bundles/.gitkeep
git commit -m "feat: write paper bundles to local bundle directories"
```

Expected: one commit containing only the bundle contract, local writer, and the first failing-then-passing test rewrite.

### Task 2: Move current supported papers into data specs and parameterized bundle tests

**Files:**
- Create: `data/03_bundle_specs/*.json`
- Modify: `tests/test_build_pdf_sample_bundle.py`

- [ ] **Step 1: Create the spec files for the current supported paper set**

Create one JSON file per supported paper at these exact paths:

```text
data/03_bundle_specs/10_1016_j_jmrt_2023_05_167.json
data/03_bundle_specs/10_1016_j_addma_2022_102887.json
data/03_bundle_specs/10_1016_j_compstruct_2018_03_050.json
data/03_bundle_specs/10_1016_j_compstruct_2019_111219.json
data/03_bundle_specs/10_1016_j_tws_2019_106436.json
data/03_bundle_specs/10_1016_j_tws_2020_106623.json
data/03_bundle_specs/10_1016_j_matdes_2017_10_028.json
data/03_bundle_specs/10_1016_j_ijimpeng_2023_104713.json
data/03_bundle_specs/10_1016_j_engstruct_2023_116510.json
data/03_bundle_specs/10_3390_ma18040732.json
data/03_bundle_specs/10_1016_j_cirpj_2024_06_009.json
```

Each file must follow this exact shape:

```json
{
  "paper_id": "10_1016_j_jmrt_2023_05_167",
  "sample": {
    "paper_id": "10_1016_j_jmrt_2023_05_167",
    "sample_id": "10_1016_j_jmrt_2023_05_167-p1l-tpms-primitive",
    "raw_structure": "TPMS"
  },
  "evidence": [
    {
      "evidence_id": "10_1016_j_jmrt_2023_05_167-p1l-tpms-primitive-ev-001",
      "sample_id": "10_1016_j_jmrt_2023_05_167-p1l-tpms-primitive",
      "field_name": "raw_design"
    }
  ],
  "required_fragments": [
    {
      "context": "JMRT abstract",
      "chunk_id_suffix": ":text:027",
      "fragment": "manufacturing short glass fiber-reinforced polyamide composites using the FDM process"
    },
    {
      "context": "JMRT table 3",
      "table_id": "table_003",
      "fragment": "Schwarz Primitive"
    }
  ]
}
```

Populate each file by moving the existing sample dict, evidence rows, and `_require_chunk_text` fragments out of the current `_build_*_bundle` functions and into JSON. Do not leave any supported paper hard-coded in Python after this task.

- [ ] **Step 2: Replace the per-paper test functions with one parameterized test**

Rewrite `tests/test_build_pdf_sample_bundle.py` around this mapping:

```python
SUPPORTED_PAPERS = [
    ("10_1016_j_jmrt_2023_05_167", "expected_sample.json", "expected_evidence.json"),
    ("10_1016_j_addma_2022_102887", "expected_sample_addma.json", "expected_evidence_addma.json"),
    ("10_1016_j_compstruct_2018_03_050", "expected_sample_compstruct_2018.json", "expected_evidence_compstruct_2018.json"),
    ("10_1016_j_compstruct_2019_111219", "expected_sample_compstruct_2019.json", "expected_evidence_compstruct_2019.json"),
    ("10_1016_j_tws_2019_106436", "expected_sample_tws_2019.json", "expected_evidence_tws_2019.json"),
    ("10_1016_j_tws_2020_106623", "expected_sample_tws_2020.json", "expected_evidence_tws_2020.json"),
    ("10_1016_j_matdes_2017_10_028", "expected_sample_tws_2017.json", "expected_evidence_tws_2017.json"),
    ("10_1016_j_ijimpeng_2023_104713", "expected_sample_ijimpeng_2023.json", "expected_evidence_ijimpeng_2023.json"),
    ("10_1016_j_engstruct_2023_116510", "expected_sample_engstruct_2023.json", "expected_evidence_engstruct_2023.json"),
    ("10_3390_ma18040732", "expected_sample_ma18040732.json", "expected_evidence_ma18040732.json"),
    ("10_1016_j_cirpj_2024_06_009", "expected_sample_cirpj_2024.json", "expected_evidence_cirpj_2024.json"),
]


@pytest.mark.parametrize(("paper_id", "sample_fixture", "evidence_fixture"), SUPPORTED_PAPERS)
def test_build_pdf_sample_bundle_writes_expected_bundle(
    tmp_path: Path,
    paper_id: str,
    sample_fixture: str,
    evidence_fixture: str,
) -> None:
    out_dir = tmp_path / "bundles" / paper_id

    exit_code = build_bundle_main([
        "--paper-id",
        paper_id,
        "--out-dir",
        str(out_dir),
    ])

    sample = read_json(out_dir / "sample.json")
    evidence = read_json(out_dir / "evidence.json")
    expected_sample = read_json(FIXTURES_DIR / sample_fixture)
    expected_evidence = read_json(FIXTURES_DIR / evidence_fixture)

    assert exit_code == 0
    assert sample == expected_sample
    assert evidence == expected_evidence
```

Keep the corpus-drift regression test, but point it at the new `--out-dir` flow rather than canonical arrays.

- [ ] **Step 3: Run the bundle test module**

Run:

```powershell
python -m pytest -q tests/test_build_pdf_sample_bundle.py
```

Expected: PASS for all supported papers plus the drift regression.

- [ ] **Step 4: Check for leftover hard-coded paper branches**

Run:

```powershell
rg -n "_build_.*_bundle|if paper_id ==" scripts/build_pdf_sample_bundle.py
```

Expected: no output. The builder should be generic, with all paper-specific content moved into `data/03_bundle_specs/`.

- [ ] **Step 5: Commit the spec migration**

Run:

```powershell
git add data/03_bundle_specs scripts/build_pdf_sample_bundle.py tests/test_build_pdf_sample_bundle.py
git commit -m "feat: move paper bundle definitions into data specs"
```

Expected: one commit containing the spec migration and the parameterized bundle tests.

### Task 3: Add serial bundle promotion into canonical outputs

**Files:**
- Create: `scripts/promote_bundle_batch.py`
- Create: `tests/test_promote_bundle_batch.py`

- [ ] **Step 1: Write the failing promotion test**

Create `tests/test_promote_bundle_batch.py` with this test first:

```python
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_pdf_sample_bundle import main as build_bundle_main  # type: ignore  # noqa: E402
from promote_bundle_batch import main as promote_batch_main  # type: ignore  # noqa: E402
from retrieval_kg_common import read_json  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "pdf_sample_bundle"


def test_promote_bundle_batch_appends_selected_papers(tmp_path: Path) -> None:
    bundles_root = tmp_path / "bundles"
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    samples_path.write_text((FIXTURES_DIR / "base_samples.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "base_evidence.json").read_text(encoding="utf-8"), encoding="utf-8")

    build_bundle_main(["--paper-id", "10_1016_j_jmrt_2023_05_167", "--out-dir", str(bundles_root / "10_1016_j_jmrt_2023_05_167")])
    build_bundle_main(["--paper-id", "10_1016_j_addma_2022_102887", "--out-dir", str(bundles_root / "10_1016_j_addma_2022_102887")])

    exit_code = promote_batch_main([
        "--bundles-root",
        str(bundles_root),
        "--paper-id",
        "10_1016_j_jmrt_2023_05_167",
        "--paper-id",
        "10_1016_j_addma_2022_102887",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)

    assert exit_code == 0
    assert any(row["sample_id"] == "10_1016_j_jmrt_2023_05_167-p1l-tpms-primitive" for row in samples)
    assert any(row["sample_id"] == "10_1016_j_addma_2022_102887-i2o-2-mgo" for row in samples)
    assert any(row["sample_id"] == "10_1016_j_jmrt_2023_05_167-p1l-tpms-primitive" for row in evidence)
    assert any(row["sample_id"] == "10_1016_j_addma_2022_102887-i2o-2-mgo" for row in evidence)
```

- [ ] **Step 2: Run the test and confirm the missing script failure**

Run:

```powershell
python -m pytest -q tests/test_promote_bundle_batch.py::test_promote_bundle_batch_appends_selected_papers
```

Expected: FAIL because `scripts/promote_bundle_batch.py` does not exist yet.

- [ ] **Step 3: Create `scripts/promote_bundle_batch.py`**

Create the file with this content:

```python
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from p1_pipeline_common import EVIDENCE_PATH, SAMPLES_PATH, read_json, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLES_ROOT = ROOT / "outputs" / "p1" / "bundles"


def _ensure_rows(payload: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise SystemExit(f"expected array for {label}")
    rows: list[dict[str, Any]] = []
    for row in payload:
        if not isinstance(row, dict):
            raise SystemExit(f"expected object rows for {label}")
        rows.append(row)
    return rows


def _append_unique(rows: list[dict[str, Any]], item: dict[str, Any], key: str) -> None:
    if any(str(row.get(key)) == str(item.get(key)) for row in rows):
        return
    rows.append(item)


def load_bundle(bundle_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    sample = read_json(bundle_dir / "sample.json")
    evidence = read_json(bundle_dir / "evidence.json")
    if not isinstance(sample, dict):
        raise SystemExit(f"expected object sample bundle in {bundle_dir}")
    return sample, _ensure_rows(evidence, str(bundle_dir / "evidence.json"))


def promote_bundle_batch(
    paper_ids: list[str],
    *,
    bundles_root: Path,
    samples_path: Path,
    evidence_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    samples = _ensure_rows(read_json(samples_path), str(samples_path))
    evidence = _ensure_rows(read_json(evidence_path), str(evidence_path))

    for paper_id in paper_ids:
        sample, evidence_rows = load_bundle(bundles_root / paper_id)
        _append_unique(samples, sample, "sample_id")
        for row in evidence_rows:
            _append_unique(evidence, row, "evidence_id")

    return samples, evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Promote selected paper-local bundles into canonical extracted outputs")
    parser.add_argument("--paper-id", action="append", required=True)
    parser.add_argument("--bundles-root", type=Path, default=DEFAULT_BUNDLES_ROOT)
    parser.add_argument("--samples", type=Path, default=SAMPLES_PATH)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE_PATH)
    args = parser.parse_args(argv)

    samples, evidence = promote_bundle_batch(
        args.paper_id,
        bundles_root=args.bundles_root,
        samples_path=args.samples,
        evidence_path=args.evidence,
    )
    write_json(args.samples, samples)
    write_json(args.evidence, evidence)
    return 0
```

- [ ] **Step 4: Add an idempotency test**

Append this test to `tests/test_promote_bundle_batch.py`:

```python
def test_promote_bundle_batch_is_idempotent(tmp_path: Path) -> None:
    bundles_root = tmp_path / "bundles"
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    samples_path.write_text((FIXTURES_DIR / "base_samples.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "base_evidence.json").read_text(encoding="utf-8"), encoding="utf-8")

    build_bundle_main(["--paper-id", "10_1016_j_jmrt_2023_05_167", "--out-dir", str(bundles_root / "10_1016_j_jmrt_2023_05_167")])

    args = [
        "--bundles-root",
        str(bundles_root),
        "--paper-id",
        "10_1016_j_jmrt_2023_05_167",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ]

    assert promote_batch_main(args) == 0
    assert promote_batch_main(args) == 0

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)

    assert [row["sample_id"] for row in samples].count("10_1016_j_jmrt_2023_05_167-p1l-tpms-primitive") == 1
    assert [row["evidence_id"] for row in evidence].count("10_1016_j_jmrt_2023_05_167-p1l-tpms-primitive-ev-001") == 1
```

- [ ] **Step 5: Run the promotion test module**

Run:

```powershell
python -m pytest -q tests/test_promote_bundle_batch.py
```

Expected: PASS.

- [ ] **Step 6: Commit the promotion step**

Run:

```powershell
git add scripts/promote_bundle_batch.py tests/test_promote_bundle_batch.py
git commit -m "feat: add serial bundle batch promotion"
```

Expected: one commit containing only the new promotion script and its tests.

### Task 4: Rewire review/KG integration tests to use local bundles and serial promotion

**Files:**
- Modify: `tests/test_promote_p1_review.py`

- [ ] **Step 1: Replace direct canonical bundle appends with local-bundle + promotion flow**

At the top of `tests/test_promote_p1_review.py`, add:

```python
from promote_bundle_batch import main as promote_batch_main  # type: ignore  # noqa: E402
```

Then replace one of the growth tests with this pattern and apply it to the rest:

```python
def test_promoted_psh_bundle_grows_the_kg(tmp_path: Path) -> None:
    bundles_root = tmp_path / "bundles"
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"
    out_path = tmp_path / "knowledge_graph.json"

    samples_path.write_text((FIXTURES_DIR / "samples_v1.json").read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text((FIXTURES_DIR / "evidence_v1.json").read_text(encoding="utf-8"), encoding="utf-8")

    build_exit = build_bundle_main([
        "--paper-id",
        "10_1016_j_compstruct_2019_111219",
        "--out-dir",
        str(bundles_root / "10_1016_j_compstruct_2019_111219"),
    ])
    promote_batch_exit = promote_batch_main([
        "--bundles-root",
        str(bundles_root),
        "--paper-id",
        "10_1016_j_compstruct_2019_111219",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])
    promote_exit = promote_main([
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])
    project_exit = project_main([
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
        "--out",
        str(out_path),
    ])

    payload = json.loads(out_path.read_text(encoding="utf-8"))

    assert build_exit == 0
    assert promote_batch_exit == 0
    assert promote_exit == 0
    assert project_exit == 0
    assert len(payload["nodes"]) > 18
    assert len(payload["edges"]) > 15
    assert any(node["label"] == "10_1016_j_compstruct_2019_111219-psh-a5-b1p568-t0p3" for node in payload["nodes"])
```

Every current KG-growth test in this module must follow the same four-step path:

1. build bundle locally
2. promote bundle batch into canonical outputs
3. promote review status
4. regenerate KG

- [ ] **Step 2: Run the review/KG integration tests**

Run:

```powershell
python -m pytest -q tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py
```

Expected: PASS.

- [ ] **Step 3: Run the full targeted regression set**

Run:

```powershell
python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_bundle_batch.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py
```

Expected: PASS.

- [ ] **Step 4: Commit the integration rewrite**

Run:

```powershell
git add tests/test_promote_p1_review.py
git commit -m "test: route bundle growth through serial promotion"
```

Expected: one commit containing only the integration test rewrite.

### Task 5: Sync governance docs with the new parallel/serial split

**Files:**
- Modify: `tasks/branch-strategy.md`
- Modify: `tasks/project-overview.md`
- Modify: `tasks/workspace-map.md`

- [ ] **Step 1: Update `tasks/branch-strategy.md`**

Add or replace the rule text so it explicitly says:

```md
## Parallel Rule For Future Paper Tasks

- `extract-paper-bundle` tasks may open in parallel only when they write to `data/03_bundle_specs/<paper-id>.json`, `outputs/p1/bundles/<paper-id>/sample.json`, `outputs/p1/bundles/<paper-id>/evidence.json`, and paper-local expected fixtures.
- `promote-bundle-batch` tasks must stay serial because they write canonical extracted outputs and the project KG.
- `parser-capability` tasks must stay serial because they change shared builder logic and shared regression tests.
```

- [ ] **Step 2: Update `tasks/project-overview.md`**

Replace the `Next Actions` block with:

```md
## Next Actions

1. Land the bundle-output decoupling task.
2. Release future paper tasks as parallel `extract-paper-bundle` tasks.
3. Keep canonical sample/evidence and KG regeneration on serial `promote-bundle-batch` tasks.
```

- [ ] **Step 3: Update `tasks/workspace-map.md`**

Update the snapshot and split notes so they say:

- the current branch still reflects the latest local paper task,
- future paper tasks should move to paper-local bundles,
- canonical outputs are no longer the direct write target for future extract tasks,
- bundle promotion is the new serial integration boundary.

- [ ] **Step 4: Run markdown and whitespace checks**

Run:

```powershell
git diff --check -- tasks/branch-strategy.md tasks/project-overview.md tasks/workspace-map.md docs/superpowers/plans/2026-04-22-task-parallelization-governance-implementation.md
```

Expected: no whitespace or patch-format errors.

- [ ] **Step 5: Commit the governance sync**

Run:

```powershell
git add tasks/branch-strategy.md tasks/project-overview.md tasks/workspace-map.md
git commit -m "docs: sync governance for parallel paper tasks"
```

Expected: one docs-only commit.

### Task 6: Final acceptance check for the migration task

**Files:**
- Test: `scripts/build_pdf_sample_bundle.py`
- Test: `scripts/promote_bundle_batch.py`
- Test: `tests/test_build_pdf_sample_bundle.py`
- Test: `tests/test_promote_bundle_batch.py`
- Test: `tests/test_promote_p1_review.py`
- Test: `tasks/branch-strategy.md`
- Test: `tasks/project-overview.md`
- Test: `tasks/workspace-map.md`

- [ ] **Step 1: Verify the new file set exists**

Run:

```powershell
$paths = @(
  'scripts/pdf_bundle_specs.py',
  'scripts/promote_bundle_batch.py',
  'outputs/p1/bundles/.gitkeep',
  'data/03_bundle_specs/10_1016_j_jmrt_2023_05_167.json',
  'data/03_bundle_specs/10_1016_j_addma_2022_102887.json',
  'data/03_bundle_specs/10_1016_j_compstruct_2018_03_050.json',
  'data/03_bundle_specs/10_1016_j_compstruct_2019_111219.json',
  'data/03_bundle_specs/10_1016_j_tws_2019_106436.json',
  'data/03_bundle_specs/10_1016_j_tws_2020_106623.json',
  'data/03_bundle_specs/10_1016_j_matdes_2017_10_028.json',
  'data/03_bundle_specs/10_1016_j_ijimpeng_2023_104713.json',
  'data/03_bundle_specs/10_1016_j_engstruct_2023_116510.json',
  'data/03_bundle_specs/10_3390_ma18040732.json',
  'data/03_bundle_specs/10_1016_j_cirpj_2024_06_009.json'
)
foreach ($path in $paths) {
  if (-not (Test-Path $path)) { throw "Missing path: $path" }
}
Write-Output 'OK: parallelization migration files exist'
```

Expected: `OK: parallelization migration files exist`

- [ ] **Step 2: Run the full targeted test suite**

Run:

```powershell
python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_bundle_batch.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py
```

Expected: PASS.

- [ ] **Step 3: Verify the builder no longer writes canonical outputs directly**

Run:

```powershell
rg -n "write_json\\(args\\.samples|write_json\\(args\\.evidence|DEFAULT_SAMPLES_PATH|DEFAULT_EVIDENCE_PATH" scripts/build_pdf_sample_bundle.py
```

Expected: no output.

- [ ] **Step 4: Verify the promotion path owns canonical writes**

Run:

```powershell
rg -n "write_json\\(args\\.samples|write_json\\(args\\.evidence" scripts/promote_bundle_batch.py scripts/promote_p1_review.py
```

Expected: both canonical write calls appear only in the promotion path.

- [ ] **Step 5: Final Git hygiene**

Run:

```powershell
git diff --check
git status --short --branch
```

Expected: `git diff --check` has no output. `git status --short --branch` shows only the planned implementation changes for this migration task.

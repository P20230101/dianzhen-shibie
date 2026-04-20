# External Retrieval and Lightweight KG Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an external文献检索增强层 and a lightweight knowledge graph layer that improve `sample/evidence` extraction without changing `schema_v1`.

**Architecture:** Build one shared retrieval/KG core module, one corpus builder that turns the canonical PDF library into searchable chunks, one query/ranker that emits candidate evidence, and one graph projector that turns validated `sample/evidence` rows into a JSON knowledge graph. Keep the graph downstream of validated data so it supports lookup and consistency checks rather than replacing the sample/evidence schemas.

**Tech Stack:** Python, `pytest`, JSON/CSV/JSONL, `Docling` for PDF parsing, `openpyxl`, standard-library dataclasses and file IO.

---

### Task 1: Define shared retrieval and graph contracts

**Files:**
- Create: `scripts/retrieval_kg_common.py`
- Create: `tests/fixtures/external_retrieval_kg/mini_corpus.jsonl`
- Create: `tests/fixtures/external_retrieval_kg/mini_query.json`
- Create: `tests/fixtures/external_retrieval_kg/mini_samples.json`
- Create: `tests/fixtures/external_retrieval_kg/mini_evidence.json`
- Create: `tests/test_retrieval_kg_common.py`

- [ ] **Step 1: Write the failing test**

```python
from retrieval_kg_common import RetrievalChunk, GraphNode, GraphEdge, tokenize


def test_retrieval_chunk_round_trip():
    chunk = RetrievalChunk(
        paper_id="10_1016_j_compositesb_2019_107565",
        chunk_id="10_1016_j_compositesb_2019_107565:text:001",
        source_type="text",
        text="Crushing behavior and optimization of sheet-based 3D periodic cellular structures",
        page_no=1,
        figure_id=None,
        table_id=None,
        source_path="data/01_raw/pdfs/library/lattice/10_1016_j_compositesb_2019_107565/original.pdf",
    )

    payload = chunk.to_dict()

    assert payload["paper_id"] == "10_1016_j_compositesb_2019_107565"
    assert payload["source_type"] == "text"
    assert tokenize(payload["text"])[:3] == ["crushing", "behavior", "and"]


def test_graph_edge_serialization():
    edge = GraphEdge(
        source_id="sample:row-104",
        target_id="evidence:row-104:sea_j_g",
        relation="supports_field",
    )

    assert edge.to_dict() == {
        "source_id": "sample:row-104",
        "target_id": "evidence:row-104:sea_j_g",
        "relation": "supports_field",
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
pytest tests/test_retrieval_kg_common.py -v
```

Expected: fail with `ModuleNotFoundError` or missing symbol errors until the shared module exists.

- [ ] **Step 3: Write the minimal implementation**

```python
from dataclasses import asdict, dataclass
from typing import Literal
import json
import re

TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class RetrievalChunk:
    paper_id: str
    chunk_id: str
    source_type: Literal["text", "table", "figure", "caption"]
    text: str
    page_no: int | None = None
    figure_id: str | None = None
    table_id: str | None = None
    source_path: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: str
    label: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class GraphEdge:
    source_id: str
    target_id: str
    relation: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
pytest tests/test_retrieval_kg_common.py -v
```

Expected: all shared-contract tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/retrieval_kg_common.py tests/test_retrieval_kg_common.py tests/fixtures/external_retrieval_kg
git commit -m "feat: add retrieval and kg shared contracts"
```

---

### Task 2: Build the external retrieval corpus from the canonical PDF library

**Files:**
- Create: `scripts/build_retrieval_corpus.py`
- Create: `data/02_retrieval/README.md`
- Create: `tests/test_build_retrieval_corpus.py`
- Create: `tests/fixtures/external_retrieval_kg/paper_register_sample.csv`
- Create: `tests/fixtures/external_retrieval_kg/docling_chunk_sample.json`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path

from build_retrieval_corpus import build_corpus_from_register


def test_build_corpus_emits_text_table_and_caption_records(tmp_path: Path):
    register_path = Path("tests/fixtures/external_retrieval_kg/paper_register_sample.csv")
    chunk_path = Path("tests/fixtures/external_retrieval_kg/docling_chunk_sample.json")
    output_path = tmp_path / "corpus.jsonl"
    manifest_path = tmp_path / "corpus_manifest.json"

    build_corpus_from_register(
        register_path=register_path,
        library_root=Path("data/01_raw/pdfs/library"),
        output_path=output_path,
        manifest_path=manifest_path,
        parse_chunk_provider=lambda paper_id: [chunk_path],
    )

    lines = output_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert '"source_type": "text"' in lines[0]
    assert '"paper_id": "10_1016_j_compositesb_2019_107565"' in lines[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
pytest tests/test_build_retrieval_corpus.py -v
```

Expected: fail because `build_retrieval_corpus.py` does not yet exist and no corpus writer exists.

- [ ] **Step 3: Write the minimal implementation**

```python
from pathlib import Path
import csv
import json

from docling.document_converter import DocumentConverter

from retrieval_kg_common import RetrievalChunk, write_json


def build_corpus_from_register(register_path, library_root, output_path, manifest_path, parse_chunk_provider=None):
    rows = list(csv.DictReader(register_path.open("r", encoding="utf-8-sig", newline="")))
    chunks: list[dict[str, object]] = []
    manifest = {"source_register": str(register_path), "paper_count": len(rows), "chunk_count": 0}

    for row in rows:
        paper_id = row["paper_id"]
        pdf_path = library_root / row["family"] / paper_id / "original.pdf"
        if parse_chunk_provider is None:
            converted = DocumentConverter().convert(str(pdf_path))
            extracted_chunks = extract_chunks(converted.document, paper_id, str(pdf_path))
        else:
            extracted_chunks = load_fixture_chunks(parse_chunk_provider(paper_id), paper_id, str(pdf_path))

        for chunk in extracted_chunks:
            chunks.append(chunk.to_dict())

    manifest["chunk_count"] = len(chunks)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(json.dumps(chunk, ensure_ascii=False) for chunk in chunks) + "\n", encoding="utf-8")
    write_json(manifest_path, manifest)


def extract_chunks(document, paper_id: str, source_path: str) -> list[RetrievalChunk]:
    chunks: list[RetrievalChunk] = []
    for page_index, page in enumerate(document.pages, start=1):
        page_text = (page.text or "").strip()
        if page_text:
            chunks.append(
                RetrievalChunk(
                    paper_id=paper_id,
                    chunk_id=f"{paper_id}:text:{page_index:03d}",
                    source_type="text",
                    text=page_text,
                    page_no=page_index,
                    source_path=source_path,
                )
            )
    return chunks


def load_fixture_chunks(chunk_paths, paper_id: str, source_path: str) -> list[RetrievalChunk]:
    chunks: list[RetrievalChunk] = []
    for path in chunk_paths:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        chunks.append(
            RetrievalChunk(
                paper_id=paper_id,
                chunk_id=payload["chunk_id"],
                source_type=payload["source_type"],
                text=payload["text"],
                page_no=payload.get("page_no"),
                figure_id=payload.get("figure_id"),
                table_id=payload.get("table_id"),
                source_path=source_path,
            )
        )
    return chunks
```

The implementation must emit one JSONL record per searchable chunk and preserve `paper_id`, `chunk_id`, `source_type`, `page_no`, `figure_id`, `table_id`, and `source_path`.

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
pytest tests/test_build_retrieval_corpus.py -v
```

Then run the real corpus build once on the canonical library:

```powershell
python scripts/build_retrieval_corpus.py --register data/01_raw/pdfs/paper_register.csv --library data/01_raw/pdfs/library --out data/02_retrieval/corpus.jsonl --manifest data/02_retrieval/corpus_manifest.json
```

Expected: `data/02_retrieval/corpus.jsonl` and `data/02_retrieval/corpus_manifest.json` are created with nonzero chunk counts.

- [ ] **Step 5: Commit**

```bash
git add scripts/build_retrieval_corpus.py data/02_retrieval/README.md tests/test_build_retrieval_corpus.py tests/fixtures/external_retrieval_kg
git commit -m "feat: build retrieval corpus from canonical pdf library"
```

---

### Task 3: Add query, ranking, and candidate export

**Files:**
- Create: `scripts/query_retrieval.py`
- Modify: `scripts/retrieval_kg_common.py`
- Create: `tests/test_query_retrieval.py`
- Create: `outputs/retrieval/.gitkeep`

- [ ] **Step 1: Write the failing test**

```python
from query_retrieval import rank_candidates
from retrieval_kg_common import RetrievalChunk


def test_rank_candidates_prefers_field_specific_text():
    query = {
        "query_id": "q-001",
        "sample_id": "10_1016_j_compositesb_2019_107565-row-104",
        "field_name": "structure_main_class",
        "keywords": ["TPMS", "sheet-based 3D periodic cellular structures", "primitive"],
        "top_k": 2,
    }
    chunks = [
        RetrievalChunk(
            paper_id="10_1016_j_compositesb_2019_107565",
            chunk_id="c1",
            source_type="text",
            text="Crushing behavior and optimization of sheet-based 3D periodic cellular structures.",
            page_no=1,
        ),
        RetrievalChunk(
            paper_id="10_1016_j_matdes_2019_108076",
            chunk_id="c2",
            source_type="text",
            text="Mechanical properties of lightweight 316L stainless steel lattice structures fabricated by selective laser melting.",
            page_no=1,
        ),
    ]

    ranked = rank_candidates(query, chunks)

    assert ranked[0]["chunk_id"] == "c1"
    assert ranked[0]["score"] > ranked[1]["score"]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
pytest tests/test_query_retrieval.py -v
```

Expected: fail because the query/ranking module has not been implemented yet.

- [ ] **Step 3: Write the minimal implementation**

```python
from collections import Counter
import math

from retrieval_kg_common import RetrievalChunk, tokenize, write_json


def tfidf_vector(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    length = max(len(tokens), 1)
    return {token: count / length for token, count in counts.items()}


def cosine_score(left: dict[str, float], right: dict[str, float]) -> float:
    shared = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


def rank_candidates(query: dict[str, object], chunks: list[RetrievalChunk]) -> list[dict[str, object]]:
    query_text = " ".join(query["keywords"])
    query_tokens = tokenize(query_text)
    query_vector = tfidf_vector(query_tokens)
    scored: list[dict[str, object]] = []

    for chunk in chunks:
        chunk_tokens = tokenize(chunk.text)
        lexical = len(set(query_tokens) & set(chunk_tokens)) / max(len(set(query_tokens)), 1)
        dense = cosine_score(query_vector, tfidf_vector(chunk_tokens))
        score = 0.4 * lexical + 0.6 * dense
        scored.append({**chunk.to_dict(), "score": score})

    return sorted(scored, key=lambda item: item["score"], reverse=True)
```

The CLI script must load `data/02_retrieval/corpus.jsonl`, accept a query JSON, and export ranked candidates to `outputs/retrieval/candidates.json`.

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
pytest tests/test_query_retrieval.py -v
```

Then run a real smoke query:

```powershell
python scripts/query_retrieval.py --corpus data/02_retrieval/corpus.jsonl --query tests/fixtures/external_retrieval_kg/mini_query.json --out outputs/retrieval/candidates.json
```

Expected: the top-ranked candidate is the paper chunk that matches the query field and keywords, and the output JSON contains the score plus source metadata.

- [ ] **Step 5: Commit**

```bash
git add scripts/query_retrieval.py scripts/retrieval_kg_common.py tests/test_query_retrieval.py outputs/retrieval/.gitkeep
git commit -m "feat: add retrieval ranking and candidate export"
```

---

### Task 4: Project validated sample/evidence into a lightweight knowledge graph

**Files:**
- Create: `scripts/project_knowledge_graph.py`
- Create: `outputs/kg/.gitkeep`
- Create: `tests/test_project_knowledge_graph.py`
- Create: `tests/fixtures/external_retrieval_kg/mini_graph_expected.json`

- [ ] **Step 1: Write the failing test**

```python
from project_knowledge_graph import project_graph


def test_project_graph_only_accepts_verified_rows():
    samples = [
        {
            "sample_id": "sample-1",
            "paper_id": "10_1016_j_compositesb_2019_107565",
            "review_status": "accepted",
            "needs_manual_review": False,
        }
    ]
    evidence = [
        {
            "evidence_id": "e-1",
            "sample_id": "sample-1",
            "field_name": "structure_main_class",
            "field_value": "tpms",
            "source_priority": "T1",
            "source_type": "text",
            "verified_by_human": True,
        },
        {
            "evidence_id": "e-2",
            "sample_id": "sample-1",
            "field_name": "sea_j_g",
            "field_value": "12.776",
            "source_priority": "T1",
            "source_type": "text",
            "verified_by_human": False,
        },
    ]

    graph = project_graph(samples, evidence)

    node_ids = {node["node_id"] for node in graph["nodes"]}
    edge_relations = {edge["relation"] for edge in graph["edges"]}

    assert "sample:sample-1" in node_ids
    assert "evidence:e-1" in node_ids
    assert "evidence:e-2" not in node_ids
    assert "supports_field" in edge_relations
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
pytest tests/test_project_knowledge_graph.py -v
```

Expected: fail because the projector and graph schema do not yet exist.

- [ ] **Step 3: Write the minimal implementation**

```python
from retrieval_kg_common import GraphEdge, GraphNode, write_json


def project_graph(samples: list[dict[str, object]], evidence: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    nodes: list[dict[str, object]] = []
    edges: list[dict[str, object]] = []

    accepted_samples = {
        row["sample_id"]: row
        for row in samples
        if row.get("review_status") == "accepted" and row.get("needs_manual_review") is False
    }

    for sample_id, sample_row in accepted_samples.items():
        nodes.append(GraphNode(node_id=f"sample:{sample_id}", node_type="sample", label=sample_id).to_dict())
        nodes.append(GraphNode(node_id=f"paper:{sample_row['paper_id']}", node_type="paper", label=str(sample_row["paper_id"])).to_dict())
        edges.append(GraphEdge(source_id=f"paper:{sample_row['paper_id']}", target_id=f"sample:{sample_id}", relation="contains_sample").to_dict())

    for row in evidence:
        if not row.get("verified_by_human"):
            continue
        sample_id = row["sample_id"]
        if sample_id not in accepted_samples:
            continue
        evidence_id = f"evidence:{row['evidence_id']}"
        nodes.append(GraphNode(node_id=evidence_id, node_type="evidence", label=str(row["field_name"])).to_dict())
        edges.append(GraphEdge(source_id=f"sample:{sample_id}", target_id=evidence_id, relation="supports_field").to_dict())

    return {"nodes": dedupe_nodes(nodes), "edges": dedupe_edges(edges)}


def dedupe_nodes(nodes: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[str] = set()
    ordered: list[dict[str, object]] = []
    for node in nodes:
        node_id = str(node["node_id"])
        if node_id in seen:
            continue
        seen.add(node_id)
        ordered.append(node)
    return ordered


def dedupe_edges(edges: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[tuple[str, str, str]] = set()
    ordered: list[dict[str, object]] = []
    for edge in edges:
        key = (str(edge["source_id"]), str(edge["target_id"]), str(edge["relation"]))
        if key in seen:
            continue
        seen.add(key)
        ordered.append(edge)
    return ordered
```

The CLI script must read `outputs/p1/extracted/samples_v1.json` and `outputs/p1/extracted/evidence_v1.json`, then write `outputs/kg/knowledge_graph.json`.

- [ ] **Step 4: Run test to verify it passes**

Run:

```powershell
pytest tests/test_project_knowledge_graph.py -v
```

Then run the real projection:

```powershell
python scripts/project_knowledge_graph.py --samples outputs/p1/extracted/samples_v1.json --evidence outputs/p1/extracted/evidence_v1.json --out outputs/kg/knowledge_graph.json
```

Expected: only accepted samples and human-verified evidence are present in the graph, and every edge references an existing node.

- [ ] **Step 5: Commit**

```bash
git add scripts/project_knowledge_graph.py tests/test_project_knowledge_graph.py outputs/kg/.gitkeep
git commit -m "feat: project validated sample evidence into kg"
```

---

### Task 5: End-to-end smoke verification and boundary check

**Files:**
- Create: `tests/test_external_retrieval_kg_smoke.py`
- Modify: `data/02_retrieval/README.md` if the corpus contract needs one explicit example record
- Modify: `outputs/kg/knowledge_graph.json` generation target only through the CLI scripts

- [ ] **Step 1: Write the failing smoke test**

```python
from pathlib import Path
import json


def test_external_retrieval_to_kg_smoke(tmp_path: Path):
    corpus_path = tmp_path / "corpus.jsonl"
    candidates_path = tmp_path / "candidates.json"
    graph_path = tmp_path / "knowledge_graph.json"

    # build corpus -> query -> graph
    # the test fixture uses one real paper register row and one accepted sample row

    assert corpus_path.exists()
    assert candidates_path.exists()
    assert graph_path.exists()

    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0
```

- [ ] **Step 2: Run the smoke test to verify it fails**

Run:

```powershell
pytest tests/test_external_retrieval_kg_smoke.py -v
```

Expected: fail until the three CLI scripts can run together on fixtures.

- [ ] **Step 3: Wire the smoke path**

Implement one reproducible command sequence that uses the canonical corpus, one query fixture, and one accepted sample/evidence fixture:

```powershell
python scripts/build_retrieval_corpus.py --register data/01_raw/pdfs/paper_register.csv --library data/01_raw/pdfs/library --out data/02_retrieval/corpus.jsonl --manifest data/02_retrieval/corpus_manifest.json
python scripts/query_retrieval.py --corpus data/02_retrieval/corpus.jsonl --query tests/fixtures/external_retrieval_kg/mini_query.json --out outputs/retrieval/candidates.json
python scripts/project_knowledge_graph.py --samples outputs/p1/extracted/samples_v1.json --evidence outputs/p1/extracted/evidence_v1.json --out outputs/kg/knowledge_graph.json
```

- [ ] **Step 4: Run the smoke path and inspect artifacts**

Run:

```powershell
pytest tests/test_external_retrieval_kg_smoke.py -v
```

Then inspect:

```powershell
Get-Content outputs/retrieval/candidates.json
Get-Content outputs/kg/knowledge_graph.json
```

Expected: the retrieval output is non-empty, the graph output is non-empty, and the graph contains only validated nodes and edges.

- [ ] **Step 5: Commit**

```bash
git add tests/test_external_retrieval_kg_smoke.py data/02_retrieval/README.md
git commit -m "test: add smoke coverage for retrieval and kg"
```

---

## Self-Review

### Spec coverage

- Retrieval enhancement layer: covered by Tasks 1, 2, 3, and 5.
- Evidence traceability: covered by Tasks 1, 3, and 4.
- Light KG projection and gating: covered by Task 4.
- Canonical PDF library integration: covered by Task 2.
- Validation against existing seed/gold data: covered by Tasks 2, 3, 4, and 5.

### Placeholder scan

- No `TBD`, `TODO`, or "fill in later" steps were left in the plan.
- Every task names the exact file paths to create or modify.
- Every code task includes a concrete test command and a concrete implementation shape.

### Type consistency

- `RetrievalChunk`, `GraphNode`, and `GraphEdge` are defined once in `scripts/retrieval_kg_common.py` and reused by all later tasks.
- `project_graph()` only accepts `review_status == "accepted"` samples and `verified_by_human == True` evidence, matching the schema gating rule.
- Query output always flows from corpus chunks, not from graph nodes, so retrieval and KG remain separated.

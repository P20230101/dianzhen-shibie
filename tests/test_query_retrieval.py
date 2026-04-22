from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from query_retrieval import main, rank_candidates  # type: ignore  # noqa: E402
from retrieval_kg_common import RetrievalChunk, read_json  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "external_retrieval_kg"


def test_rank_candidates_prefers_matching_chunk() -> None:
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
            text="Crushing behavior and optimization of sheet-based 3D periodic cellular structures with primitive TPMS configuration.",
            page_no=1,
            source_path="data/01_raw/pdfs/library/lattice/10_1016_j_compositesb_2019_107565/original.pdf",
        ),
        RetrievalChunk(
            paper_id="10_1016_j_matdes_2019_108076",
            chunk_id="c2",
            source_type="text",
            text="Mechanical properties of lightweight 316L stainless steel lattice structures fabricated by selective laser melting.",
            page_no=1,
            source_path="data/01_raw/pdfs/library/lattice/10_1016_j_matdes_2019_108076/original.pdf",
        ),
    ]

    ranked = rank_candidates(query, chunks)

    assert ranked[0]["chunk_id"] == "c1"
    assert ranked[0]["score"] > ranked[1]["score"]
    assert "score" in ranked[0]
    assert ranked[0]["source_path"].endswith("original.pdf")


def test_main_exports_ranked_candidates(tmp_path: Path) -> None:
    query_path = tmp_path / "query.json"
    corpus_path = tmp_path / "corpus.jsonl"
    out_path = tmp_path / "candidates.json"

    query = read_json(FIXTURES_DIR / "mini_query.json")
    query["top_k"] = 2
    query_path.write_text(json.dumps(query, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    corpus_rows = [json.loads(line) for line in (FIXTURES_DIR / "mini_corpus.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    corpus_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in corpus_rows) + "\n",
        encoding="utf-8",
    )

    exit_code = main([
        "--corpus",
        str(corpus_path),
        "--query",
        str(query_path),
        "--out",
        str(out_path),
    ])

    payload = json.loads(out_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert payload["query_id"] == "q-001"
    assert payload["field_name"] == "structure_main_class"
    assert len(payload["candidates"]) == 2
    assert payload["candidates"][0]["chunk_id"] == "c1"
    assert payload["candidates"][0]["score"] >= payload["candidates"][1]["score"]
    assert "source_type" in payload["candidates"][0]
    assert "source_path" in payload["candidates"][0]

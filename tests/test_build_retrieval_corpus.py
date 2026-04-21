from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_retrieval_corpus import build_corpus_from_register, extract_chunks  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "external_retrieval_kg"


def test_extract_chunks_uses_text_table_and_caption_records() -> None:
    payload = {
        "texts": [
            {
                "label": "text",
                "text": "Crushing behavior and optimization of sheet-based 3D periodic cellular structures.",
                "prov": [{"page_no": 1}],
            },
            {
                "label": "page_header",
                "text": "Table 1. Material summary",
                "prov": [{"page_no": 1}],
            },
        ],
        "tables": [
            {
                "prov": [{"page_no": 1}],
                "captions": [{"$ref": "#/texts/1"}],
                "data": {"table_cells": [{"text": "A"}, {"text": "B"}]},
            }
        ],
        "pictures": [],
    }

    class FakeDocument:
        def export_to_dict(self) -> dict[str, object]:
            return payload

    chunks = extract_chunks(FakeDocument(), "10_1016_j_compositesb_2019_107565", "source.pdf")

    assert len(chunks) == 3
    assert [chunk.source_type for chunk in chunks] == ["text", "table", "caption"]
    assert chunks[0].chunk_id == "10_1016_j_compositesb_2019_107565:text:001"
    assert chunks[1].table_id == "table_001"
    assert chunks[2].text == "Table 1. Material summary"


def test_build_corpus_emits_text_table_and_caption_records(tmp_path: Path) -> None:
    register_path = FIXTURES_DIR / "paper_register_sample.csv"
    chunk_path = FIXTURES_DIR / "docling_chunk_sample.json"
    output_path = tmp_path / "corpus.jsonl"
    manifest_path = tmp_path / "corpus_manifest.json"

    build_corpus_from_register(
        register_path=register_path,
        library_root=ROOT / "data" / "01_raw" / "pdfs" / "library",
        output_path=output_path,
        manifest_path=manifest_path,
        parse_chunk_provider=lambda paper_id: [chunk_path],
    )

    lines = [line for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    records = [json.loads(line) for line in lines]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert len(records) == 3
    assert {record["source_type"] for record in records} == {"text", "table", "caption"}
    assert records[0]["paper_id"] == "10_1016_j_compositesb_2019_107565"
    assert manifest["paper_count"] == 1
    assert manifest["chunk_count"] == 3

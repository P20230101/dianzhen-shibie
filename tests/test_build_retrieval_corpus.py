from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_retrieval_corpus import build_corpus_from_register  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "external_retrieval_kg"


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

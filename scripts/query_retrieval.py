from __future__ import annotations

import argparse
import json
from pathlib import Path

from retrieval_kg_common import RetrievalChunk, read_json, tokenize, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS_PATH = ROOT / "data" / "02_retrieval" / "corpus.jsonl"
DEFAULT_QUERY_PATH = ROOT / "tests" / "fixtures" / "external_retrieval_kg" / "mini_query.json"
DEFAULT_OUTPUT_PATH = ROOT / "outputs" / "retrieval" / "candidates.json"


def _load_corpus_rows(corpus_path: Path) -> list[RetrievalChunk]:
    chunks: list[RetrievalChunk] = []
    for line in corpus_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        row = json.loads(text)
        if not isinstance(row, dict):
            raise ValueError(f"corpus rows must be objects: {corpus_path}")
        chunks.append(
            RetrievalChunk(
                paper_id=str(row["paper_id"]),
                chunk_id=str(row["chunk_id"]),
                source_type=str(row["source_type"]),
                text=str(row["text"]),
                page_no=row.get("page_no") if isinstance(row.get("page_no"), int) else None,
                figure_id=str(row["figure_id"]) if row.get("figure_id") is not None else None,
                table_id=str(row["table_id"]) if row.get("table_id") is not None else None,
                source_path=str(row["source_path"]) if row.get("source_path") is not None else None,
            )
        )
    return chunks


def _query_text(query: dict[str, object]) -> str:
    parts: list[str] = []
    field_name = query.get("field_name")
    if isinstance(field_name, str) and field_name.strip():
        parts.append(field_name.strip())
    keywords = query.get("keywords")
    if isinstance(keywords, list):
        parts.extend(str(item) for item in keywords if str(item).strip())
    elif isinstance(keywords, str) and keywords.strip():
        parts.append(keywords.strip())
    return " ".join(parts)


def rank_candidates(query: dict[str, object], chunks: list[RetrievalChunk]) -> list[dict[str, object]]:
    query_tokens = set(tokenize(_query_text(query)))
    field_name = query.get("field_name")
    field_name_token = str(field_name).lower().replace(" ", "_") if field_name is not None else ""

    ranked: list[dict[str, object]] = []
    for chunk in chunks:
        chunk_tokens = set(tokenize(chunk.text))
        score = float(len(query_tokens & chunk_tokens))
        if field_name_token and field_name_token in chunk.text.lower():
            score += 1.0
        ranked.append({**chunk.to_dict(), "score": score})

    ranked.sort(key=lambda item: (-float(item["score"]), str(item["paper_id"]), str(item["chunk_id"])))
    return ranked


def build_candidates_payload(query: dict[str, object], chunks: list[RetrievalChunk]) -> dict[str, object]:
    ranked = rank_candidates(query, chunks)
    top_k = query.get("top_k")
    limit = int(top_k) if isinstance(top_k, int) and top_k > 0 else len(ranked)
    return {
        "query_id": query.get("query_id"),
        "sample_id": query.get("sample_id"),
        "field_name": query.get("field_name"),
        "top_k": limit,
        "candidates": ranked[:limit],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rank retrieval corpus chunks for a query")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    parser.add_argument("--query", type=Path, default=DEFAULT_QUERY_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    query = read_json(args.query)
    if not isinstance(query, dict):
        raise SystemExit(f"expected a JSON object in {args.query}")
    chunks = _load_corpus_rows(args.corpus)
    payload = build_candidates_payload(query, chunks)
    write_json(args.out, payload)

    print(f"candidates written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

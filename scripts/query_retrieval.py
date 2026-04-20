from __future__ import annotations

import argparse
from collections import Counter
import math
from pathlib import Path

from retrieval_kg_common import RetrievalChunk, load_jsonl, read_json, tokenize, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS_PATH = ROOT / "data" / "02_retrieval" / "corpus.jsonl"
DEFAULT_OUTPUT_PATH = ROOT / "outputs" / "retrieval" / "candidates.json"


def _query_text(query: dict[str, object]) -> str:
    parts: list[str] = []

    field_name = query.get("field_name")
    if isinstance(field_name, str) and field_name.strip():
        parts.append(field_name.replace("_", " "))

    keywords = query.get("keywords")
    if isinstance(keywords, list):
        for keyword in keywords:
            if keyword is None:
                continue
            text = str(keyword).strip()
            if text:
                parts.append(text)

    return " ".join(parts)


def _token_frequencies(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    total = sum(counts.values()) or 1
    return {token: count / total for token, count in counts.items()}


def _cosine_score(left: dict[str, float], right: dict[str, float]) -> float:
    shared = set(left) & set(right)
    if not shared:
        return 0.0
    numerator = sum(left[token] * right[token] for token in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


def rank_candidates(query: dict[str, object], chunks: list[RetrievalChunk]) -> list[dict[str, object]]:
    query_tokens = tokenize(_query_text(query))
    query_term_set = set(query_tokens)
    query_vector = _token_frequencies(query_tokens)

    ranked: list[dict[str, object]] = []
    for chunk in chunks:
        chunk_tokens = tokenize(chunk.text)
        chunk_term_set = set(chunk_tokens)
        lexical_overlap = len(query_term_set & chunk_term_set) / max(len(query_term_set), 1)
        cosine = _cosine_score(query_vector, _token_frequencies(chunk_tokens))
        ranked.append({**chunk.to_dict(), "score": lexical_overlap + cosine})

    return sorted(ranked, key=lambda item: (-float(item["score"]), str(item["chunk_id"])))


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank retrieval candidates for a query")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    chunks = [RetrievalChunk(**row) for row in load_jsonl(args.corpus)]
    query = read_json(args.query)
    if not isinstance(query, dict):
        raise ValueError(f"expected JSON object in {args.query}")

    ranked = rank_candidates(query, chunks)

    top_k_value = query.get("top_k")
    top_k = len(ranked) if top_k_value is None else int(top_k_value)
    if top_k < 0:
        top_k = 0

    payload = {**query, "candidates": ranked[:top_k]}
    write_json(args.out, payload)
    print(f"candidates written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

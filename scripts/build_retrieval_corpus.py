from __future__ import annotations

import argparse
import csv
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from retrieval_kg_common import RetrievalChunk, read_json, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER_PATH = ROOT / "data" / "01_raw" / "pdfs" / "paper_register.csv"
DEFAULT_LIBRARY_ROOT = ROOT / "data" / "01_raw" / "pdfs" / "library"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "02_retrieval" / "corpus.jsonl"
DEFAULT_MANIFEST_PATH = ROOT / "data" / "02_retrieval" / "corpus_manifest.json"

TEXT_LABELS_TO_SKIP = {"page_header", "page_footer"}
REF_RE = re.compile(r"^#/texts/(\d+)$")


@lru_cache(maxsize=1)
def _converter() -> DocumentConverter:
    pipeline_options = PdfPipelineOptions(
        do_ocr=False,
        force_backend_text=True,
        generate_page_images=False,
        generate_picture_images=False,
        do_picture_classification=False,
        do_picture_description=False,
        do_chart_extraction=False,
        do_code_enrichment=False,
        do_formula_enrichment=False,
    )
    return DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)},
    )


def _normalize_text(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _first_page_no(item: dict[str, object]) -> int | None:
    prov = item.get("prov")
    if not isinstance(prov, list) or not prov:
        return None
    first = prov[0]
    if not isinstance(first, dict):
        return None
    page_no = first.get("page_no")
    return int(page_no) if isinstance(page_no, int) else None


def _ref_index(ref: object) -> int | None:
    if not isinstance(ref, dict):
        return None
    value = ref.get("$ref")
    if not isinstance(value, str):
        return None
    match = REF_RE.match(value)
    if not match:
        return None
    return int(match.group(1))


def _resolve_text_refs(refs: object, texts: list[dict[str, object]]) -> str | None:
    if not isinstance(refs, list) or not refs:
        return None
    parts: list[str] = []
    for ref in refs:
        index = _ref_index(ref)
        if index is None or index >= len(texts):
            continue
        text = _normalize_text(texts[index].get("text"))
        if text:
            parts.append(text)
    if not parts:
        return None
    return " ".join(parts)


def _flatten_table_cells(table_data: object) -> str | None:
    if not isinstance(table_data, dict):
        return None
    cells = table_data.get("table_cells")
    if not isinstance(cells, list):
        return None
    parts: list[str] = []
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        text = _normalize_text(cell.get("text"))
        if text:
            parts.append(text)
    if not parts:
        return None
    return " ".join(parts)


def _chunk_from_record(record: dict[str, object], default_paper_id: str, default_source_path: str) -> RetrievalChunk:
    return RetrievalChunk(
        paper_id=str(record.get("paper_id") or default_paper_id),
        chunk_id=str(record["chunk_id"]),
        source_type=str(record["source_type"]),
        text=str(record["text"]),
        page_no=record.get("page_no") if isinstance(record.get("page_no"), int) else None,
        figure_id=_normalize_text(record.get("figure_id")),
        table_id=_normalize_text(record.get("table_id")),
        source_path=_normalize_text(record.get("source_path")) or default_source_path,
    )


def load_fixture_chunks(chunk_paths: Iterable[Path], paper_id: str, source_path: str) -> list[RetrievalChunk]:
    chunks: list[RetrievalChunk] = []
    for chunk_path in chunk_paths:
        payload = read_json(chunk_path)
        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict) and isinstance(payload.get("chunks"), list):
            records = payload["chunks"]
        else:
            raise ValueError(f"unsupported chunk fixture format: {chunk_path}")
        for record in records:
            if not isinstance(record, dict):
                raise ValueError(f"chunk fixture records must be objects: {chunk_path}")
            chunks.append(_chunk_from_record(record, paper_id, source_path))
    return chunks


def extract_chunks(document, paper_id: str, source_path: str) -> list[RetrievalChunk]:
    payload = document.export_to_dict()
    texts = payload.get("texts", [])
    tables = payload.get("tables", [])
    pictures = payload.get("pictures", [])

    if not isinstance(texts, list):
        texts = []
    if not isinstance(tables, list):
        tables = []
    if not isinstance(pictures, list):
        pictures = []

    chunks: list[RetrievalChunk] = []
    text_index = 0

    for item in texts:
        if not isinstance(item, dict):
            continue
        label = _normalize_text(item.get("label"))
        content = _normalize_text(item.get("text"))
        if not content or label in TEXT_LABELS_TO_SKIP:
            continue
        text_index += 1
        page_no = _first_page_no(item)
        chunks.append(
            RetrievalChunk(
                paper_id=paper_id,
                chunk_id=f"{paper_id}:text:{text_index:03d}",
                source_type="text",
                text=content,
                page_no=page_no,
                source_path=source_path,
            )
        )

    for table_index, item in enumerate(tables, start=1):
        if not isinstance(item, dict):
            continue
        page_no = _first_page_no(item)
        table_id = f"table_{table_index:03d}"
        caption_text = _resolve_text_refs(item.get("captions"), texts)
        table_text = _flatten_table_cells(item.get("data"))
        combined_parts = [part for part in [caption_text, table_text] if part]
        if combined_parts:
            chunks.append(
                RetrievalChunk(
                    paper_id=paper_id,
                    chunk_id=f"{paper_id}:table:{table_index:03d}",
                    source_type="table",
                    text=" ".join(combined_parts),
                    page_no=page_no,
                    table_id=table_id,
                    source_path=source_path,
                )
            )
        if caption_text:
            chunks.append(
                RetrievalChunk(
                    paper_id=paper_id,
                    chunk_id=f"{paper_id}:caption:{table_index:03d}",
                    source_type="caption",
                    text=caption_text,
                    page_no=page_no,
                    table_id=table_id,
                    source_path=source_path,
                )
            )

    for picture_index, item in enumerate(pictures, start=1):
        if not isinstance(item, dict):
            continue
        page_no = _first_page_no(item)
        figure_id = f"fig_{picture_index:03d}"
        caption_text = _resolve_text_refs(item.get("captions"), texts)
        if caption_text:
            chunks.append(
                RetrievalChunk(
                    paper_id=paper_id,
                    chunk_id=f"{paper_id}:caption:{picture_index + len(tables):03d}",
                    source_type="caption",
                    text=caption_text,
                    page_no=page_no,
                    figure_id=figure_id,
                    source_path=source_path,
                )
            )

    return chunks


def build_corpus_from_register(
    register_path: Path,
    library_root: Path,
    output_path: Path,
    manifest_path: Path,
    parse_chunk_provider=None,
) -> dict[str, object]:
    rows = list(csv.DictReader(register_path.open("r", encoding="utf-8-sig", newline="")))
    chunks: list[dict[str, object]] = []
    paper_count = 0

    for row in rows:
        paper_id = str(row["paper_id"]).strip()
        family = str(row.get("family") or "").strip()
        source_path = str(
            _normalize_text(row.get("library_path"))
            or (library_root / family / paper_id / "original.pdf")
        )
        paper_count += 1
        if parse_chunk_provider is None:
            pdf_path = Path(source_path)
            document = _converter().convert(str(pdf_path), raises_on_error=False).document
            extracted = extract_chunks(document, paper_id, source_path)
        else:
            chunk_paths = [Path(path) for path in parse_chunk_provider(paper_id)]
            extracted = load_fixture_chunks(chunk_paths, paper_id, source_path)
        chunks.extend(chunk.to_dict() for chunk in extracted)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    manifest = {
        "source_register": str(register_path),
        "paper_count": paper_count,
        "chunk_count": len(chunks),
    }
    write_json(manifest_path, manifest)
    return manifest


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build retrieval corpus from canonical PDF register")
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER_PATH)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    build_corpus_from_register(args.register, args.library, args.out, args.manifest)
    print(f"corpus written: {args.out}")
    print(f"manifest written: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

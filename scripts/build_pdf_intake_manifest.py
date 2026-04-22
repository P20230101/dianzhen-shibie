from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER_PATH = ROOT / "data" / "01_raw" / "pdfs" / "paper_register.csv"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "02_parsed" / "pdf_intake_manifest.json"


def _normalize_text(value: object | None) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    text = text.replace("\u00ad", "").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _split_subtypes(value: str) -> list[str]:
    text = _normalize_text(value)
    if not text:
        return []
    return [part for part in (piece.strip() for piece in text.split(";")) if part]


def _first_page_excerpt(pdf_path: Path, max_chars: int = 500) -> str:
    reader = PdfReader(str(pdf_path))
    if not reader.pages:
        return ""
    first_page = reader.pages[0].extract_text() or ""
    text = _normalize_text(first_page)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip()


def _page_count(pdf_path: Path) -> int:
    reader = PdfReader(str(pdf_path))
    return len(reader.pages)


def _load_register_rows(register_path: Path) -> list[dict[str, str]]:
    with register_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, str]] = []
        for row in reader:
            rows.append({key: (value or "").strip() for key, value in row.items()})
    return rows


def _pdf_path_from_row(row: dict[str, str]) -> Path:
    candidate = row.get("source_path") or row.get("library_path") or row.get("file_path") or ""
    if not candidate:
        raise KeyError("register row does not contain a PDF path column")
    return Path(candidate)


def build_pdf_intake_manifest(register_path: Path | str = DEFAULT_REGISTER_PATH, output_path: Path | str = DEFAULT_OUTPUT_PATH) -> list[dict[str, object]]:
    register_path = Path(register_path)
    output_path = Path(output_path)

    if not register_path.exists():
        raise FileNotFoundError(f"register not found: {register_path}")

    rows = _load_register_rows(register_path)
    manifest: list[dict[str, object]] = []

    for row in rows:
        pdf_path = _pdf_path_from_row(row)
        if not pdf_path.exists():
            raise FileNotFoundError(f"pdf not found: {pdf_path}")
        manifest.append(
            {
                "paper_id": row["paper_id"],
                "title": row["title"],
                "doi": row["doi"] or None,
                "family": row["family"],
                "structure_main_class": row["structure_main_class"],
                "structure_subtype_list": _split_subtypes(row["structure_subtype_list"]),
                "status": row["status"],
                "file_path": str(pdf_path),
                "page_count": _page_count(pdf_path),
                "first_page_excerpt": _first_page_excerpt(pdf_path),
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a PDF intake manifest from the canonical paper register")
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER_PATH)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    manifest = build_pdf_intake_manifest(args.register, args.out)
    print(f"manifest rows written: {len(manifest)}")
    print(f"manifest written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

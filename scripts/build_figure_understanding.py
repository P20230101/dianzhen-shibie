from __future__ import annotations

import argparse
import csv
from functools import lru_cache
from pathlib import Path
from typing import Callable, Protocol

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from figure_understanding_common import build_figure_record, write_jsonl, write_review_csv
from figure_understanding_vlm import FixtureFigureInterpreter, VlmFigureInterpreter
from retrieval_kg_common import write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER_PATH = ROOT / "data" / "01_raw" / "pdfs" / "paper_register.csv"
DEFAULT_LIBRARY_ROOT = ROOT / "data" / "01_raw" / "pdfs" / "library"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "03_figures" / "figures_v1.jsonl"
DEFAULT_MANIFEST_PATH = ROOT / "data" / "03_figures" / "manifest.json"
DEFAULT_REVIEW_PATH = ROOT / "data" / "03_figures" / "figures_review.csv"


class FigureInterpreter(Protocol):
    def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
        ...


@lru_cache(maxsize=1)
def _converter() -> DocumentConverter:
    pipeline_options = PdfPipelineOptions(
        do_ocr=True,
        force_backend_text=True,
        generate_page_images=True,
        generate_picture_images=True,
        do_picture_classification=True,
        do_picture_description=True,
        do_chart_extraction=True,
        do_code_enrichment=False,
        do_formula_enrichment=False,
    )
    return DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)},
    )


def _load_register_rows(register_path: Path) -> list[dict[str, str]]:
    with register_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def _resolve_caption_text(picture: dict[str, object], texts: list[dict[str, object]]) -> str | None:
    caption_parts: list[str] = []
    captions = picture.get("captions")
    if isinstance(captions, list):
        for item in captions:
            if isinstance(item, dict):
                ref = item.get("$ref")
                if isinstance(ref, str):
                    resolved = _resolve_text_ref(ref, texts)
                    if resolved:
                        caption_parts.append(resolved)
                    continue
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    caption_parts.append(text.strip())
                    continue
            if isinstance(item, str) and item.strip():
                caption_parts.append(item.strip())

    if caption_parts:
        return " ".join(caption_parts).strip()

    for key in ("caption_text", "caption", "text"):
        value = picture.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _resolve_text_ref(ref: str, texts: list[dict[str, object]]) -> str | None:
    if not ref.startswith("#/texts/"):
        return None
    index_text = ref.rsplit("/", 1)[-1]
    try:
        index = int(index_text)
    except ValueError:
        return None
    if index < 0 or index >= len(texts):
        return None
    candidate = texts[index]
    text = candidate.get("text")
    if isinstance(text, str):
        stripped = text.strip()
        if stripped:
            return stripped
    return None


def _resolve_context_text(picture: dict[str, object], caption_text: str | None) -> str | None:
    for key in ("description", "context_text", "summary", "text"):
        value = picture.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return caption_text


def _resolve_page_no(picture: dict[str, object]) -> int | None:
    prov = picture.get("prov")
    if not isinstance(prov, list) or not prov:
        return None
    first = prov[0]
    if not isinstance(first, dict):
        return None
    page_no = first.get("page_no")
    if isinstance(page_no, bool):
        return None
    if isinstance(page_no, int):
        return page_no
    return None


def _resolve_image_path(picture: dict[str, object]) -> str:
    for key in ("image_path", "image_uri", "image_file"):
        value = picture.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError("picture is missing image_path/image_uri/image_file")


def _export_payload(document: object) -> dict[str, object]:
    if hasattr(document, "export_to_dict"):
        payload = document.export_to_dict()
    else:
        payload = document
    if not isinstance(payload, dict):
        raise TypeError("document export must be a dictionary")
    return payload


def extract_figures(
    document: object,
    paper_id: str,
    source_path: str,
    interpreter: FigureInterpreter,
    review_threshold: float,
) -> list[dict[str, object]]:
    payload = _export_payload(document)
    texts = payload.get("texts", [])
    pictures = payload.get("pictures", [])
    if not isinstance(texts, list):
        texts = []
    if not isinstance(pictures, list):
        pictures = []

    records: list[dict[str, object]] = []
    for index, item in enumerate(pictures, start=1):
        if not isinstance(item, dict):
            continue
        figure_id = str(item.get("figure_id") or f"fig_{index:03d}")
        page_no = _resolve_page_no(item)
        image_path = _resolve_image_path(item)
        caption_text = _resolve_caption_text(item, texts)
        context_text = _resolve_context_text(item, caption_text)
        interpretation = interpreter.interpret(
            image_path=image_path,
            caption_text=caption_text,
            context_text=context_text,
        )
        raw = {
            "paper_id": paper_id,
            "figure_id": figure_id,
            "page_no": page_no,
            "image_path": image_path,
            "caption_text": caption_text,
            "context_text": context_text,
        }
        records.append(build_figure_record(raw, interpretation, review_threshold))
    return records


def _load_document(document_provider: Callable[[Path], object] | None, pdf_path: Path) -> object:
    if document_provider is not None:
        return document_provider(pdf_path)
    conversion_result = _converter().convert(str(pdf_path))
    document = getattr(conversion_result, "document", conversion_result)
    return document


def build_figure_understanding_corpus(
    register_path: Path,
    library_root: Path,
    output_path: Path,
    manifest_path: Path,
    review_path: Path,
    interpreter: FigureInterpreter,
    review_threshold: float = 0.85,
    document_provider: Callable[[Path], object] | None = None,
) -> list[dict[str, object]]:
    rows = _load_register_rows(register_path)
    records: list[dict[str, object]] = []
    paper_ids: list[str] = []

    for row in rows:
        paper_id = str(row.get("paper_id") or "").strip()
        pdf_path_value = str(row.get("pdf_path") or "").strip()
        if not paper_id or not pdf_path_value:
            continue
        pdf_path = Path(pdf_path_value)
        if not pdf_path.is_absolute():
            pdf_path = library_root / pdf_path
        paper_ids.append(paper_id)
        document = _load_document(document_provider, pdf_path)
        records.extend(
            extract_figures(
                document=document,
                paper_id=paper_id,
                source_path=str(pdf_path),
                interpreter=interpreter,
                review_threshold=review_threshold,
            )
        )

    write_jsonl(records, output_path)
    write_review_csv(records, review_path)
    write_json(
        manifest_path,
        {
            "register_path": str(register_path),
            "library_root": str(library_root),
            "output_path": str(output_path),
            "review_path": str(review_path),
            "paper_count": len(paper_ids),
            "figure_count": len(records),
            "paper_ids": paper_ids,
        },
    )
    return records


def _build_interpreter(args: argparse.Namespace) -> FigureInterpreter:
    fixture_response = getattr(args, "fixture_response", None)
    if fixture_response is not None:
        return FixtureFigureInterpreter(Path(fixture_response))

    base_url = getattr(args, "base_url", None)
    model = getattr(args, "model", None)
    if not base_url or not model:
        raise SystemExit("provide either --fixture-response or both --base-url and --model")
    return VlmFigureInterpreter(
        base_url=str(base_url),
        model=str(model),
        api_key=getattr(args, "api_key", None),
        timeout_s=float(getattr(args, "timeout_s", 60.0)),
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the figure understanding corpus from canonical PDF inputs")
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER_PATH)
    parser.add_argument("--library-root", type=Path, default=DEFAULT_LIBRARY_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    parser.add_argument("--review-threshold", type=float, default=0.85)
    parser.add_argument("--fixture-response", type=Path)
    parser.add_argument("--base-url")
    parser.add_argument("--model")
    parser.add_argument("--api-key")
    parser.add_argument("--timeout-s", type=float, default=60.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    interpreter = _build_interpreter(args)

    records = build_figure_understanding_corpus(
        register_path=args.register,
        library_root=args.library_root,
        output_path=args.output,
        manifest_path=args.manifest,
        review_path=args.review,
        interpreter=interpreter,
        review_threshold=float(args.review_threshold),
    )
    print(f"figure records written: {len(records)} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
